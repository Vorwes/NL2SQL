from pathlib import Path
from typing import cast

import chromadb
from chromadb.api.types import EmbeddingFunction
from chromadb.utils import embedding_functions

from .preprocessing import (
    create_schema,
    format_chat_template,
    get_path,
    load_data,
    save_dataset,
)


def get_chroma_collection(
    db_path: str = "./chroma_db_storage", collection_name: str = "spider_schemas"
) -> chromadb.Collection:
    """
    Initializes the ChromaDB client and returns the specified collection.
    """
    print("Initializing ChromaDB Client for Retrieval...")
    client = chromadb.PersistentClient(path=db_path)

    sentence_transformer_ef: EmbeddingFunction = (
        embedding_functions.SentenceTransformerEmbeddingFunction(
            model_name="BAAI/bge-small-en-v1.5"
        )
    )

    return client.get_collection(
        name=collection_name,
        embedding_function=cast(EmbeddingFunction, sentence_transformer_ef),
    )


def retrieve_relevant_schema(db_id: str, question: str, top_k: int = 3) -> str:
    """
    Searches ChromaDB for the most relevant tables to the question for a specific database.
    """
    results: chromadb.QueryResult = collection.query(
        query_texts=[question], n_results=top_k, where={"db_id": db_id}
    )

    if results["documents"] and results["documents"][0]:
        retrieved_chunks: list[str] = results["documents"][0]
        return "\n\n".join(retrieved_chunks)
    else:
        return "-- No schema found."


def build_rag_schemas(data_split: list, split_name: str, top_k: int = 3) -> dict:
    """
    Iterates over questions in the split, retrieves the relevant schema,
    and returns a dictionary compatible with the format_chat_template function.
    """
    print(f"Retrieving schemas for {split_name} split ({len(data_split)} questions)...")
    rag_schemas: dict[str, str] = {}

    for i, item in enumerate(data_split):
        db_id: str = item["db_id"]
        question: str = item["question"]

        relevant_schema_text: str = retrieve_relevant_schema(db_id, question, top_k)

        unique_key: str = f"{db_id}_{i}"
        item["original_db_id"] = db_id
        item["db_id"] = unique_key

        rag_schemas[unique_key] = relevant_schema_text

        if (i + 1) % 500 == 0:
            print(f"  Processed {i + 1}/{len(data_split)} questions...")

    return rag_schemas


if __name__ == "__main__":
    print("Initializing Vector Store...")
    collection: chromadb.Collection = get_chroma_collection()

    print("1. Loading Data...")
    paths, output_path = get_path()

    rag_output_path: Path = output_path.parent / "formatted_data_rag"
    rag_output_path.mkdir(parents=True, exist_ok=True)

    data: dict = load_data(paths)

    TOP_K_TABLES = 5

    print("  Formatting train dataset (Using FULL Schemas to avoid hallucination)...")
    full_train_schemas: dict[str, str] = create_schema(table=data["tables"])

    train_dataset: list[dict] = format_chat_template(
        schemas=full_train_schemas, data=data["train"], split_name="train"
    )

    val_schemas: dict[str, str] = build_rag_schemas(
        data_split=data["val"], split_name="val", top_k=TOP_K_TABLES
    )
    print("  Formatting val dataset...")
    val_dataset: list[dict] = format_chat_template(
        schemas=val_schemas, data=data["val"], split_name="val"
    )

    test_schemas: dict[str, str] = build_rag_schemas(
        data_split=data["test"], split_name="test", top_k=TOP_K_TABLES
    )
    print("  Formatting test dataset...")
    test_dataset: list[dict] = format_chat_template(
        schemas=test_schemas, data=data["test"], split_name="test"
    )

    print(f"\n2. Saving Formatted RAG Datasets to {rag_output_path}")
    save_dataset(dataset=train_dataset, path=rag_output_path / "train.jsonl")
    save_dataset(dataset=val_dataset, path=rag_output_path / "val.jsonl")
    save_dataset(dataset=test_dataset, path=rag_output_path / "test.jsonl")

    print("Process Complete!")
