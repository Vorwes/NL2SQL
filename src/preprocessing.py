import argparse
import json
import sys
from pathlib import Path


def load_files(path) -> list:
    """Load a JSON file from the given path."""
    try:
        with open(file=path, mode="r") as file:
            return json.load(fp=file)
    except FileNotFoundError:
        print(f"File not found: {path}")
        sys.exit(1)


def create_schema(table) -> dict[str, str]:
    """Create a schema dictionary from the given table data."""
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


def format_chat_template(schemas, data) -> list[dict]:
    """Formats the chat template for the training data."""
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
                    {"role": "assistant", "content": query},
                ]
            }
        )
    return formatted_dataset


def save_dataset(dataset: list[dict], path: Path) -> None:
    with open(file=path, mode="w") as f:
        for item in dataset:
            f.write(json.dumps(obj=item) + "\n")
        print(f"Dataset saved to {path}")


if __name__ == "__main__":
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
    output_base: Path = output_path
    output_base.mkdir(parents=True, exist_ok=True)
    tables_path: Path = input_path / "tables.json"
    train_path: Path = input_path / "train_spider.json"
    test_tables_path: Path = input_path / "test_tables.json"
    val_path: Path = input_path / "dev.json"
    test_path: Path = input_path / "test.json"
    train_others_path: Path = input_path / "train_others.json"

    table: list[dict] = load_files(path=tables_path)
    test_tables: list[dict] = load_files(path=test_tables_path)
    train_data: list[dict] = load_files(path=train_path)

    second_train_data: list[dict] = load_files(path=train_others_path)
    train_data += second_train_data
    val_data: list[dict] = load_files(path=val_path)
    test_data: list[dict] = load_files(path=test_path)
    all_schemas: dict[str, str] = create_schema(table=table)
    test_schemas: dict[str, str] = create_schema(table=test_tables)
    formatted_dataset: list[dict] = format_chat_template(
        schemas=all_schemas, data=train_data
    )
    formatted_val_dataset: list[dict] = format_chat_template(
        schemas=all_schemas, data=val_data
    )
    formatted_test_dataset: list[dict] = format_chat_template(
        schemas=test_schemas, data=test_data
    )
    save_dataset(dataset=formatted_dataset, path=output_path / "train_dataset.jsonl")
    save_dataset(dataset=formatted_val_dataset, path=output_path / "val_dataset.jsonl")
    save_dataset(
        dataset=formatted_test_dataset, path=output_path / "test_dataset.jsonl"
    )
