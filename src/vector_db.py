from typing import Any, Dict, List

import chromadb
from chromadb.utils import embedding_functions

from .chunker import chunk_live_schema
from .fetch_schema import get_schema


def store_raw_ddl_in_vector_db(
    ddl_commands: List[str], storage_path: str = "./chroma_db_storage"
):
    chunks = chunk_live_schema(ddl_commands)

    if not chunks:
        print("No valid chunks found to store.")
        return

    client = chromadb.PersistentClient(path=storage_path)

    bge_embedding_fn = embedding_functions.SentenceTransformerEmbeddingFunction(
        model_name="BAAI/bge-small-en-v1.5"
    )

    collection = client.get_or_create_collection(
        name="db_schemas_chunked_and_embeded", embedding_function=bge_embedding_fn
    )

    documents = [c["ddl"] for c in chunks]
    ids = [f"table_{i}" for i in range(len(chunks))]

    collection.add(documents=documents, ids=ids)
    print(f"Successfully chunked  {len(documents)} tables into the Vector DB!")
    print(f"Total items now in ChromaDB: {collection.count()}")


if __name__ == "__main__":
    print("--- Starting Schema Processing Pipeline ---")

    db_uri = ""

    print("Step 1: Fetching live schema from DB...")
    raw_ddl_list = get_schema(db_uri)

    if not raw_ddl_list:
        print("Failed to fetch schema. Exiting...")
        exit(1)

    print("Step 2: Processing and storing in Vector DB...")
    result = store_raw_ddl_in_vector_db(ddl_commands=raw_ddl_list)
