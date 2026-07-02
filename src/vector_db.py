import chromadb
from chromadb.utils import embedding_functions

from .fetch_schema import get_schema


def store_raw_ddl_in_vector_db(
    ddl_commands: list[str], db_name: str, storage_path: str = "./chroma_db_storage"
):
    documents = [ddl.strip() for ddl in ddl_commands if ddl.strip()]
    client = chromadb.PersistentClient(path=storage_path)

    bge_embedding_fn = embedding_functions.SentenceTransformerEmbeddingFunction(
        model_name="BAAI/bge-small-en-v1.5"
    )

    collection = client.get_or_create_collection(
        name=db_name, embedding_function=bge_embedding_fn
    )

    ids = [f"table_{i}" for i in range(len(documents))]

    collection.upsert(documents=documents, ids=ids)
    print(f"Successfully stored {len(documents)} tables into the Vector DB!")
    print(f"Total items now in ChromaDB: {collection.count()}")
