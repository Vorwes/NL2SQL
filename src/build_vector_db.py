from typing import cast

import chromadb
from chromadb.api.models.CollectionCommon import Metadata
from chromadb.api.types import EmbeddingFunction
from chromadb.utils import embedding_functions

from .preprocessing import create_schema, get_path, load_data


def build_chroma_db(tables_data: list) -> None:
    """
    Builds a ChromaDB collection from the given tables data.
    Args:
        tables_data (list): A list of tables data to build the collection from.
    Returns:
        None
    """
    print("1. Initializing ChromaDB Client...")
    client = chromadb.PersistentClient(path="./chroma_db_storage")

    sentence_transformer_ef: EmbeddingFunction = (
        embedding_functions.SentenceTransformerEmbeddingFunction(
            model_name="BAAI/bge-small-en-v1.5"
        )
    )

    print("2. Creating or Loading Collection...")
    collection: chromadb.Collection = client.get_or_create_collection(
        name="spider_schemas",
        embedding_function=cast(EmbeddingFunction, sentence_transformer_ef),
    )

    print("3. Chunking Tables...")
    chunks: list[dict] = create_schema(table=tables_data, return_as_chunks=True)

    print("4. Preparing Data for ChromaDB...")
    documents: list[str] = []
    metadatas: list[Metadata] = []
    ids: list[str] = []

    for chunk in chunks:
        documents.append(chunk["text"])
        metadatas.append({"db_id": chunk["db_id"], "table_name": chunk["table_name"]})
        ids.append(f"{chunk['db_id']}_{chunk['table_name']}")

    print("5. Inserting into Vector Database (This might take a moment)...")
    collection.add(documents=documents, metadatas=metadatas, ids=ids)
    print("Done! Vector DB is ready.")


if __name__ == "__main__":
    paths, _ = get_path()
    data: dict = load_data(paths)
    build_chroma_db(tables_data=data["tables"])
    build_chroma_db(tables_data=data["test_tables"])
