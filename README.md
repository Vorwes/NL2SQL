# NL2SQL

Turns English questions into SQL for a PostgreSQL database.

The model is Qwen 1.5B fine-tuned on [Spider](https://yale-lily.github.io/spider), quantized to 8-bit GGUF and run on CPU through llama.cpp. Its context window is 4096 tokens, which a large schema will not fit into, so the schema is retrieved per question. When you connect a database, the backend reads every table definition from the Postgres catalog, embeds each one with `BAAI/bge-small-en-v1.5`, and stores them in ChromaDB. Each question then pulls the five closest tables into the prompt.

It writes the query and stops there. Nothing is executed against your database.

If the output contains a write or DDL keyword (`drop`, `delete`, `insert`, `update`, `alter`, `create`, `truncate`, `grant`, `revoke`), generation is cut off and replaced with a refusal. The check is a substring match on the output, so a column named `created_at` trips it as well.

## Running it

The model file is not in the repo. Put it at `models/qwen-1.5b_nl2sql-q8_0.gguf` first.

```bash
docker compose -f compose.yml up --build
```

The chat UI is at http://localhost:8001. Open the settings panel, paste a Postgres URI (`postgresql://user:password@host:5432/db_name`), and ask a question. The first connect is slow because it downloads the embedding model.

The backend runs in a container, so `localhost` in the URI means the container. For a database on your own machine use `host.docker.internal` (Docker Desktop) or the host's IP.

Without Docker, with Python 3.12 and [uv](https://docs.astral.sh/uv/):

```bash
uv sync --group backend --group frontend
uv run python -m src.app.main                                 # API on :8000
uv run chainlit run src/app/user_interface.py --port 8001     # UI on :8001
```

The UI finds the API through `API_URL`, which defaults to `http://localhost:8000`.

## Test database

`docker-compose.yml` starts Postgres 15 loaded with [Chinook](https://github.com/lerocha/chinook-database). It expects the dump at `test_database/Chinook_PostgreSql.sql` and a `.env` file that sets `POSTGRES_USER`, `POSTGRES_PASSWORD` and `POSTGRES_DB`.

```bash
docker compose -f docker-compose.yml up -d
```

## API

The UI is a thin client over two endpoints. The backend holds one database at a time, and a new `/connect` replaces it.

```bash
curl -X POST localhost:8000/connect \
  -H 'Content-Type: application/json' \
  -d '{"db_uri": "postgresql://user:password@localhost:5432/chinook"}'

curl -N -X POST localhost:8000/generate_sql \
  -H 'Content-Type: application/json' \
  -d '{"query": "How many tracks are in the Rock genre?"}'
```

`/generate_sql` streams the query back as plain text.

## Training data and evaluation

The scripts in `src/` build the fine-tuning data from Spider and measure how well retrieval finds the right tables. They read the Spider JSON files from `--data_dir`.

```bash
# Spider to chat-format JSONL, full schema in every prompt
uv run python -m src.preprocessing --data_dir data/spider_data --output_dir data/formatted_data

# index the Spider schemas in ChromaDB, one document per table
uv run python -m src.build_vector_db --data_dir data/spider_data

# same JSONL, but val and test prompts carry only the top 5 retrieved tables
uv run python -m src.retrieval --data_dir data/spider_data --output_dir data/formatted_data

# recall@k, precision@k, MRR and full-coverage rate on the Spider test split
uv run python -m src.rag_eval --data_dir data/spider_data --top_k 5
```

The retrieval report is written to `evaluation/`.

The model itself is scored by execution accuracy on Chinook against the base model without fine-tuning. The plan is in `docs/eval_metrics.md` and the questions with gold SQL are in `test_data/test_dataset.json`.
