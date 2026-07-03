import chromadb
from chromadb.api import ClientAPI
from chromadb.utils import embedding_functions


def store_raw_ddl_in_vector_db(
    ddl_commands: list[str], db_name: str, storage_path: str = "./chroma_db_storage"
) -> None:
    """
    Store raw DDL commands in a ChromaDB vector database with the specified name and storage path.
    """

    documents: list[str] = [ddl.strip() for ddl in ddl_commands if ddl.strip()]
    client: ClientAPI = chromadb.PersistentClient(path=storage_path)

    bge_embedding_fn: embedding_functions.SentenceTransformerEmbeddingFunction = (
        embedding_functions.SentenceTransformerEmbeddingFunction(
            model_name="BAAI/bge-small-en-v1.5"
        )
    )

    collection: chromadb.Collection = client.get_or_create_collection(
        name=db_name, embedding_function=bge_embedding_fn
    )

    ids: list[str] = [f"table{i}" for i in range(len(documents))]

    collection.upsert(documents=documents, ids=ids)
    print(f"Successfully stored {len(documents)} tables into the Vector DB!")
    print(f"Total items now in ChromaDB: {collection.count()}")


def retrieve_tables(query: str, collection: chromadb.Collection, top_k: int = 5) -> str:
    """
    Retrieve the most relevant tables from the ChromaDB collection based on the query.
    """
    results: chromadb.QueryResult = collection.query(
        query_texts=[query], n_results=top_k
    )

    if results["documents"] and results["documents"][0]:
        retrieved_chunks: list[str] = results["documents"][0]
        return "\n\n".join(retrieved_chunks)
    else:
        return "No schema found."
