import argparse
import json
import sys
from pathlib import Path
from typing import Dict, List, Tuple, Union

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


def create_schema(table) -> dict[str, str]:
    """Create a schema dictionary from the given table data.

    Args:
        table: A list of dictionaries containing the table data.

    Returns:
        A dictionary mapping database IDs to schema text.
    """
    schemas: dict[str, str] = {}
    for db in table:
        db_id: str = db["db_id"]
        columns: list = db["column_names_original"]
        tables: list = db["table_names_original"]
        pks: list = db["primary_keys"]
        fks: list = db["foreign_keys"]
        col_types: list = db["column_types"]
        fk_mapping: dict = {}
        db_schema: dict = {}
        for fk in fks:
            fk_idx: int = fk[0]
            target_idx: int = fk[1]
            target_col_name: str = columns[target_idx][1]
            target_table_idx: int = columns[target_idx][0]
            target_table_name: str = tables[target_table_idx]
            fk_mapping[fk_idx] = f"[FK to {target_table_name}.{target_col_name}]"

        for col_idx, col in enumerate(columns):
            current_type: str = col_types[col_idx]
            col_name: str = f"{col[1]} [ {current_type.upper()} ]"
            table_index: int = col[0]
            if col_idx in pks:
                col_name = f"{col_name} [PK]"
            if col_idx in fk_mapping:
                col_name += f" {fk_mapping[col_idx]}"

            if table_index == -1:
                continue

            table_name: str = tables[table_index]

            if table_name not in db_schema:
                db_schema[table_name] = []

            db_schema[table_name].append(col_name)

        schema_parts: list[str] = []
        for table_name, table_cols in db_schema.items():
            columns_string: str = ", ".join(table_cols)

            table_string: str = f"{table_name} : {columns_string}"

            schema_parts.append(table_string)

        final_schema_text: str = " | ".join(schema_parts)

        schemas[db_id] = final_schema_text
    return schemas


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
    parser.add_argument(
        "--data_dir", type=str, default="~/projects/NL2SQL/data/spider_data"
    )
    parser.add_argument(
        "--output_dir", type=str, default="~/projects/NL2SQL/data/formatted_data"
    )
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
    with open(file=path, mode="a", encoding="utf-8") as f:
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
