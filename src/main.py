from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException
from fastapi.responses import StreamingResponse
from pydantic import BaseModel

from .fetch_schema import get_schema
from .inference.model_inference import LLM
from .inference.vector_db import retrieve_tables, store_raw_ddl_in_vector_db
from .retrieval import get_chroma_collection

app_state = {"llm": None, "collection": None, "db_uri": None, "db_name": None}

MODEL_PATH = "./models/qwen-1.5b_nl2sql-q8_0.gguf"


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Executes once during startup. Loads ONLY the LLM into memory.
    """
    print("Starting up: Loading LLM into memory...")
    llm = LLM(model_path=MODEL_PATH)
    llm.load()
    app_state["llm"] = llm

    print("API is ready to receive requests!")
    yield

    app_state.clear()
    print("Shutting down API...")


app = FastAPI(lifespan=lifespan, title="NL2SQL API")


class ConnectRequest(BaseModel):
    db_uri: str


class QueryRequest(BaseModel):
    query: str


@app.post("/connect")
async def connect_db(request: ConnectRequest) -> dict:
    """
    Called ONCE to set up the database. Extracts the schema, saves it
    to the vector database, and saves the connection to the app_state.
    """
    db_name = request.db_uri.split("/")[-1]

    try:
        if request.db_uri == app_state.get("db_uri"):
            return {"message": f"Already connected to {db_name}. Ready for queries."}

        print(f"Fetching schema for {db_name}...")
        schema = get_schema(db_uri=request.db_uri)

        print("Storing schema in Vector DB...")
        store_raw_ddl_in_vector_db(ddl_commands=schema, db_name=db_name)

        print("Connecting to ChromaDB collection...")
        app_state["collection"] = get_chroma_collection(collection_name=db_name)
        app_state["db_uri"] = request.db_uri
        app_state["db_name"] = db_name

        return {"message": f"Successfully processed schema and connected to {db_name}."}

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/generate_sql")
async def generate_sql(request: QueryRequest) -> StreamingResponse:
    """
    Accepts ONLY a natural language query. Relies entirely on the
    app_state memory to access the connected database and stream SQL.
    """
    llm = app_state.get("llm")
    collection = app_state.get("collection")

    if not llm:
        raise HTTPException(status_code=500, detail="LLM not initialized properly.")

    if not collection:
        raise HTTPException(
            status_code=400,
            detail="No active database found. Please call the /connect endpoint first.",
        )

    try:
        print("Retrieving relevant tables from memory state...")
        retrieval = retrieve_tables(query=request.query, collection=collection)

        def stream_generator():
            for chunk in llm.generate(schema=retrieval, question=request.query):
                yield chunk

        return StreamingResponse(stream_generator(), media_type="text/plain")

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, port=8000)
