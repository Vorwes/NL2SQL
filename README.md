# NL2SQL

Ask questions about a PostgreSQL database in plain English and get SQL back.

NL2SQL uses a fine-tuned **Qwen 1.5B** small language model (quantized to GGUF `q8_0`, run on CPU with `llama.cpp`). It is paired with a **RAG schema retriever**: when you connect a database, its table definitions are embedded into ChromaDB. For each question, only the most relevant tables go into the model's prompt, so the system works on schemas too large to fit in the context window.

## How it works

```
┌──────────────┐   question    ┌────────────────────────────────────────────┐
│  Chainlit UI │ ────────────▶ │  FastAPI backend                           │
│   :8001      │ ◀──────────── │   :8000                                    │
└──────────────┘  streamed SQL │                                            │
                               │  /connect                                  │
                               │    1. read DDL from PostgreSQL catalog     │
                               │    2. embed each table (bge-small-en-v1.5) │
                               │    3. store in ChromaDB                    │
                               │                                            │
                               │  /generate_sql                             │
                               │    1. retrieve top-5 relevant tables       │
                               │    2. prompt fine-tuned Qwen 1.5B (GGUF)   │
                               │    3. stream SQL tokens back               │
                               └────────────────────────────────────────────┘
```

- **Schema extraction** (`src/fetch_schema.py`): builds `CREATE TABLE` statements, including primary and foreign keys, for every table in the `public` schema that the connected user can `SELECT` from.
- **Retrieval** (`src/inference/vector_db.py`): one ChromaDB document per table, embedded with `BAAI/bge-small-en-v1.5`. The top 5 tables are retrieved for each question.
- **Generation** (`src/inference/model_inference.py`): streams the model's output. As a safety guard, generation stops and the request is refused if the output contains a data- or schema-modifying keyword (`DROP`, `DELETE`, `INSERT`, `UPDATE`, `ALTER`, `CREATE`, `TRUNCATE`, `GRANT`, `REVOKE`). Only read queries are returned.

> NL2SQL **generates** SQL; it does not execute it. You can run the returned query yourself.

## Project structure

```
src/
├── app/
│   ├── main.py              # FastAPI backend (/connect, /generate_sql)
│   └── user_interface.py    # Chainlit chat frontend
├── inference/
│   ├── model_inference.py   # llama.cpp wrapper + DDL guard
│   └── vector_db.py         # store/retrieve live-database schemas in ChromaDB
├── fetch_schema.py          # extract DDL from PostgreSQL
├── preprocessing.py         # Spider → chat-format JSONL (train/val/test)
├── build_vector_db.py       # index Spider schemas into ChromaDB
├── retrieval.py             # build RAG-formatted Spider datasets
└── rag_eval.py              # retrieval metrics (recall@k, precision@k, MRR, coverage)
docs/                        # evaluation plan and test questions
test_data/test_dataset.json  # Chinook evaluation questions with gold SQL
Dockerfile                   # multi-stage build: backend + frontend images
compose.yml                  # runs the backend and frontend
docker-compose.yml           # optional Chinook PostgreSQL test database
```

## Requirements

- Docker with Compose, **or** Python 3.12+ and [uv](https://docs.astral.sh/uv/)
- The fine-tuned model file at `models/qwen-1.5b_nl2sql-q8_0.gguf` (not tracked in git)
- A PostgreSQL database to query

## Quick start (Docker)

1. Put the model file in `models/`:

   ```
   models/qwen-1.5b_nl2sql-q8_0.gguf
   ```

2. Build and start the backend and frontend:

   ```bash
   docker compose -f compose.yml up --build
   ```

3. Open the UI at **http://localhost:8001**, open the **Settings** panel, and enter your database URI:

   ```
   postgresql://user:password@host:5432/db_name
   ```

   The backend runs inside a container, so `localhost` points to the container, not your machine. To reach a database on your host, use `host.docker.internal` (Docker Desktop) or your host's IP address.

4. Ask a question, for example: *"Which support representative manages the most customers?"*

The backend API also has interactive docs at **http://localhost:8000/docs**.

### Optional: Chinook test database

`docker-compose.yml` starts a PostgreSQL 15 instance loaded with the [Chinook](https://github.com/lerocha/chinook-database) sample database. Place `Chinook_PostgreSql.sql` in `test_database/`, create a `.env` file:

```env
POSTGRES_USER=postgres
POSTGRES_PASSWORD=postgres
POSTGRES_DB=chinook
```

then run:

```bash
docker compose -f docker-compose.yml up -d
```

From the containerized backend, connect with `postgresql://postgres:postgres@host.docker.internal:5432/chinook`.

## Running locally (without Docker)

```bash
# install dependencies (CPU-only PyTorch is configured in pyproject.toml)
uv sync --group backend --group frontend

# terminal 1: backend on :8000
uv run python -m src.app.main

# terminal 2: frontend on :8001
uv run chainlit run src/app/user_interface.py --port 8001
```

When running locally, the frontend reads the backend address from `API_URL` (default `http://localhost:8000`).

## API

| Method | Endpoint        | Body                       | Description                                                                 |
| ------ | --------------- | -------------------------- | --------------------------------------------------------------------------- |
| POST   | `/connect`      | `{"db_uri": "postgresql://..."}` | Extracts the schema, indexes it in ChromaDB, and sets it as the active database. |
| POST   | `/generate_sql` | `{"query": "..."}`         | Streams generated SQL (`text/plain`) for the active database.              |

```bash
curl -X POST localhost:8000/connect \
  -H 'Content-Type: application/json' \
  -d '{"db_uri": "postgresql://postgres:postgres@localhost:5432/chinook"}'

curl -N -X POST localhost:8000/generate_sql \
  -H 'Content-Type: application/json' \
  -d '{"query": "How many tracks are in the Rock genre?"}'
```

## Training data and evaluation

The model was fine-tuned on the [Spider](https://yale-lily.github.io/spider) text-to-SQL dataset. The scripts in `src/` prepare the data and evaluate retrieval. They expect the Spider files (`tables.json`, `train_spider.json`, `dev.json`, ...) in `--data_dir` (default `../data/spider_data`):

```bash
# format Spider into chat-style JSONL with full schemas
uv run python -m src.preprocessing --data_dir data/spider_data --output_dir data/formatted_data

# index Spider table schemas into ChromaDB
uv run python -m src.build_vector_db --data_dir data/spider_data

# build datasets whose val/test schemas come from RAG retrieval (top-5 tables)
uv run python -m src.retrieval --data_dir data/spider_data --output_dir data/formatted_data

# measure retrieval quality on the Spider test split
uv run python -m src.rag_eval --data_dir data/spider_data --top_k 5
```

`rag_eval` reports full-coverage rate, recall@k, precision@k, and MRR, both overall and by the number of tables each query needs. Results are written to `evaluation/`.

End-to-end quality is measured with **execution accuracy** on the Chinook database, comparing the fine-tuned model against the untuned base model. See `docs/eval_metrics.md`, `docs/questions.md`, and `test_data/test_dataset.json`.
