import argparse
import json
import sys
from pathlib import Path
from typing import Dict, List, Literal, Tuple, Union, overload

from typing_extensions import Any


def load_files(path) -> list:
    """Load a JSON file from the given path.

    Args:
        path: The path to the JSON file.

    Returns:
        The loaded JSON data as a list.
    """
    try:
        with open(file=path, mode="r") as file:
            return json.load(fp=file)
    except FileNotFoundError:
        print(f"File not found: {path}")
        sys.exit(1)


@overload
def create_schema(
    table: list, return_as_chunks: Literal[False] = False
) -> dict[str, str]: ...


@overload
def create_schema(table: list, return_as_chunks: Literal[True]) -> list[dict]: ...


def create_schema(
    table: list, return_as_chunks: bool = False
) -> Union[Dict[str, str], List[dict]]:
    """
    Create a standard DDL (SQL) schema dictionary or vector chunks from the given table data.

    Args:
        table: A list of dictionaries containing the table data.
        return_as_chunks: If True, returns a list of chunks for Vector DB.
                          If False, returns a dict mapping db_id to schema text.

    Returns:
        A dictionary of DDL schemas OR a list of chunk dictionaries.
    """
    schemas: dict[str, str] = {}
    chunks: list[dict] = []

    for db in table:
        db_id: str = db["db_id"]
        columns: list = db["column_names_original"]
        tables: list = db["table_names_original"]
        pks: list = db["primary_keys"]
        fks: list = db["foreign_keys"]
        col_types: list = db["column_types"]

        db_schema = {t_name: {"cols": [], "fks": []} for t_name in tables}

        col_idx_to_info = {}
        for col_idx, col in enumerate(columns):
            table_idx = col[0]
            if table_idx == -1:
                continue
            col_idx_to_info[col_idx] = {"table": tables[table_idx], "name": col[1]}

        for fk in fks:
            fk_idx, target_idx = fk[0], fk[1]
            if fk_idx in col_idx_to_info and target_idx in col_idx_to_info:
                src_table = col_idx_to_info[fk_idx]["table"]
                src_col = col_idx_to_info[fk_idx]["name"]
                target_table = col_idx_to_info[target_idx]["table"]
                target_col = col_idx_to_info[target_idx]["name"]

                fk_str = (
                    f"FOREIGN KEY ({src_col}) REFERENCES {target_table}({target_col})"
                )
                db_schema[src_table]["fks"].append(fk_str)

        for col_idx, col in enumerate(columns):
            table_idx = col[0]
            if table_idx == -1:
                continue

            table_name = tables[table_idx]
            col_name = col[1]

            c_type = col_types[col_idx].upper()
            if c_type == "TEXT":
                c_type = "VARCHAR"
            elif c_type == "NUMBER":
                c_type = "INTEGER"

            col_def = f"{col_name} {c_type}"

            if col_idx in pks:
                col_def += " PRIMARY KEY"

            db_schema[table_name]["cols"].append(col_def)

        if return_as_chunks:
            for table_name, table_data in db_schema.items():
                all_elements = table_data["cols"] + table_data["fks"]
                elements_str = ",\n  ".join(all_elements)

                chunk_text = f"CREATE TABLE {table_name} (\n  {elements_str}\n);"

                chunks.append(
                    {"db_id": db_id, "table_name": table_name, "text": chunk_text}
                )
        else:
            schema_parts: list[str] = []
            for table_name, table_data in db_schema.items():
                all_elements = table_data["cols"] + table_data["fks"]
                elements_str = ",\n  ".join(all_elements)

                table_string = f"CREATE TABLE {table_name} (\n  {elements_str}\n);"
                schema_parts.append(table_string)

            final_schema_text: str = "\n\n".join(schema_parts)
            schemas[db_id] = final_schema_text

    return chunks if return_as_chunks else schemas


def format_chat_template(schemas, data, split_name) -> list[dict]:
    """Formats the chat template for the training data.

    Args:
        schemas: A dictionary mapping database IDs to schema text.
        data: A list of dictionaries containing the training data.

    Returns:
        A list of dictionaries representing the formatted chat dataset.
    """
    formatted_dataset: list[dict] = []
    for item in data:
        db_id: str = item["db_id"]
        question: str = item["question"]
        query: str = item["query"]
        schema_text: str = schemas[db_id]
        formatted_dataset.append(
            {
                "messages": [
                    {
                        "role": "system",
                        "content": "You are a helpful database assistant. Your task is to generate correct SQL queries based on the provided database schema and user question.",
                    },
                    {
                        "role": "user",
                        "content": f"Here is a database schema:\n{schema_text}\n\nQuestion: {question}",
                    },
                ]
            }
        )
        if split_name == "test":
            formatted_dataset[-1]["messages"] += [{"role": "assistant", "content": ""}]
        else:
            formatted_dataset[-1]["messages"] += [
                {"role": "assistant", "content": query}
            ]
    return formatted_dataset


def get_path() -> Tuple[Dict[str, Union[Path, List[Path]]], Path]:
    """
    Parses command line arguments for data directory and output directory paths.

    Returns:
        A tuple containing a dictionary of path mappings and the output path.
    """

    parser: argparse.ArgumentParser = argparse.ArgumentParser()
    parser.add_argument("--data_dir", type=str, default="../data/spider_data")

    parser.add_argument("--output_dir", type=str, default="../data/formatted_data")
    args: argparse.Namespace = parser.parse_args()

    input_path: Path = Path(args.data_dir).expanduser()
    output_path: Path = Path(args.output_dir).expanduser()
    output_path.mkdir(parents=True, exist_ok=True)

    paths: dict[str, Union[Path, List[Path]]] = {
        "tables": input_path / "tables.json",
        "test_tables": input_path / "test_tables.json",
        "train": [input_path / "train_spider.json", input_path / "train_others.json"],
        "val": [input_path / "dev.json"],
        "test": [input_path / "test.json"],
    }

    return paths, output_path


def load_data(paths: Dict[str, Union[Path, List[Path]]]) -> dict:
    """
    Loads data from the given paths.

    Args:
        paths: A dictionary mapping keys to file paths or lists of file paths.

    Returns:
        A dictionary mapping keys to the loaded data.
    """
    data: dict[str, Any] = {}
    for key, path in paths.items():
        if isinstance(path, list):
            data[key] = []
            for p in path:
                data[key].extend(load_files(path=p))
        else:
            data[key] = load_files(path)
    return data


def save_dataset(dataset: list[dict], path: Path) -> None:
    """
    Saves the given dataset to the specified path.

    Args:
        dataset: The dataset to save.
        path: The path to save the dataset to.
    """
    with open(file=path, mode="w", encoding="utf-8") as f:
        for item in dataset:
            f.write(json.dumps(obj=item) + "\n")
    print(f"Dataset saved to {path}")


if __name__ == "__main__":
    print("1. Initializing paths")
    paths, output_path = get_path()

    print("2. Loading data")
    data: dict[str, Any] = load_data(paths)

    print("3. Building schemas")
    trun_schemas: dict[str, str] = create_schema(table=data["tables"])
    test_schemas: dict[str, str] = create_schema(table=data["test_tables"])

    print("4. Formatting datasets")
    train_dataset: list[dict] = format_chat_template(
        schemas=trun_schemas, data=data["train"], split_name="train"
    )

    val_dataset: list[dict] = format_chat_template(
        schemas=trun_schemas, data=data["val"], split_name="val"
    )

    test_dataset: list[dict] = format_chat_template(
        schemas=test_schemas, data=data["test"], split_name="test"
    )

    print("5. Saving formatted datasets")
    save_dataset(dataset=train_dataset, path=output_path / "train.jsonl")
    save_dataset(dataset=val_dataset, path=output_path / "val.jsonl")
    save_dataset(dataset=test_dataset, path=output_path / "test.jsonl")
