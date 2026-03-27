import json


def load_files(path) -> list:
    """Load a JSON file from the given path."""
    with open(file=path, mode="r") as file:
        return json.load(fp=file)


def create_schema(table) -> dict[str, str]:
    """Create a schema dictionary from the given table data."""
    all_schemas: dict[str, str] = {}
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

        all_schemas[db_id] = final_schema_text
    return all_schemas


def format_chat_template(all_schemas, train_data) -> list[dict]:
    """Formats the chat template for the training data."""
    formatted_dataset: list[dict] = []
    for item in train_data:
        db_id: str = item["db_id"]
        question: str = item["question"]
        query: str = item["query"]
        schema_text: str = all_schemas[db_id]
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


if __name__ == "__main__":
    table: list[dict] = load_files(
        path="/home/hojja/projects/NL2SQL/data/spider_data/tables.json"
    )
    test_tables: list[dict] = load_files(
        path="/home/hojja/projects/NL2SQL/data/spider_data/test_tables.json"
    )
    train_data: list[dict] = load_files(
        path="/home/hojja/projects/NL2SQL/data/spider_data/train_spider.json"
    )

    second_train_data: list[dict] = load_files(
        path="/home/hojja/projects/NL2SQL/data/spider_data/train_others.json"
    )
    train_data += second_train_data
    val_data: list[dict] = load_files(
        path="/home/hojja/projects/NL2SQL/data/spider_data/dev.json"
    )
    test_data: list[dict] = load_files(
        path="/home/hojja/projects/NL2SQL/data/spider_data/test.json"
    )
    all_schemas: dict[str, str] = create_schema(table)
    test_schemas: dict[str, str] = create_schema(test_tables)
    formatted_dataset: list[dict] = format_chat_template(all_schemas, train_data)
    formatted_val_dataset: list[dict] = format_chat_template(all_schemas, val_data)
    formatted_test_dataset: list[dict] = format_chat_template(test_schemas, test_data)

    print(len(formatted_dataset))
    print(formatted_dataset[1000])
