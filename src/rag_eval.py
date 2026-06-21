from __future__ import annotations

import argparse
import csv
import json
import re
import sys
from collections import defaultdict
from pathlib import Path
from typing import Any, Dict, List, Set, Tuple

import chromadb

from src.retrieval import get_chroma_collection

from .preprocessing import load_files

_TABLE_INTRODUCERS = re.compile(
    r"\b(?:FROM|JOIN)\s+([A-Za-z_][A-Za-z0-9_\.]*)", re.IGNORECASE
)
_GOLD_SQL_KEYS = ("query", "gold_sql", "sql_query", "SQL")


def extract_gold_tables(gold_sql: str) -> Set[str]:
    """Extract base table names referenced after FROM/JOIN in a SQL query.

    Args:
        gold_sql: Raw gold SQL string.

    Returns:
        Set of lower-cased table names (schema-qualified prefixes stripped).
    """
    tables: Set[str] = set()
    for match in _TABLE_INTRODUCERS.finditer(gold_sql):
        name = match.group(1).lower().split(".")[-1]  # handle schema.table
        if name and name != "select":  # skip "FROM (SELECT ...)" subqueries
            tables.add(name)
    return tables


def get_gold_sql(item: Dict[str, Any]) -> str:
    """Return the gold SQL string from a test item, tolerating key variants."""
    for key in _GOLD_SQL_KEYS:
        value = item.get(key)
        if isinstance(value, str) and value.strip():
            return value
    return ""


def build_db_table_index(tables_data: list) -> Dict[str, Set[str]]:
    """Map each db_id to its set of valid lower-cased table names.

    Args:
        tables_data: Parsed test_tables.json content.

    Returns:
        Dict mapping db_id to a set of lower-cased table names.
    """
    return {
        db["db_id"]: {t.lower() for t in db["table_names_original"]}
        for db in tables_data
    }


def retrieve_tables(
    collection: chromadb.Collection, db_id: str, question: str, top_k: int
) -> List[str]:
    """Retrieve the Top-K ranked table names for a question within a db.

    Args:
        collection: ChromaDB collection of table-level schema chunks.
        db_id: Database to restrict the search to.
        question: Natural-language question.
        top_k: Number of tables to retrieve.

    Returns:
        Ordered list of lower-cased table names (best match first, deduped).
    """
    results = collection.query(
        query_texts=[question], n_results=top_k, where={"db_id": db_id}
    )
    metadatas = results.get("metadatas") or [[]]
    retrieved: List[str] = []
    for meta in metadatas[0]:
        name = str(meta.get("table_name", "")).lower()
        if name and name not in retrieved:
            retrieved.append(name)
    return retrieved


def score_question(gold: Set[str], retrieved: List[str]) -> Dict[str, float]:
    """Compute retrieval metrics for one question.

    Args:
        gold: Set of required (gold) table names.
        retrieved: Ordered list of retrieved table names.

    Returns:
        Dict with recall, precision, full_coverage (0/1), reciprocal_rank.
    """
    retrieved_set = set(retrieved)
    hits = gold & retrieved_set
    recall = len(hits) / len(gold)
    precision = len(hits) / len(retrieved) if retrieved else 0.0
    full_coverage = 1.0 if gold <= retrieved_set else 0.0

    reciprocal_rank = 0.0
    for rank, name in enumerate(retrieved, start=1):
        if name in gold:
            reciprocal_rank = 1.0 / rank
            break

    return {
        "recall": recall,
        "precision": precision,
        "full_coverage": full_coverage,
        "reciprocal_rank": reciprocal_rank,
    }


def _mean(values: List[float]) -> float:
    """Arithmetic mean; returns 0.0 for an empty list."""
    return sum(values) / len(values) if values else 0.0


def evaluate(
    test_data: list,
    tables_data: list,
    collection: chromadb.Collection,
    top_k: int,
) -> Tuple[Dict[str, Any], List[Dict[str, Any]]]:
    """Run retrieval evaluation over the test split.

    Returns:
        Tuple of (aggregate_report, per_question_rows).
    """
    table_index = build_db_table_index(tables_data)

    per_question: List[Dict[str, Any]] = []
    by_complexity: Dict[int, List[Dict[str, float]]] = defaultdict(list)
    all_scores: List[Dict[str, float]] = []
    skipped_no_gold = 0
    skipped_no_db = 0

    for item in test_data:
        db_id = item.get("db_id", "")
        question = item.get("question", "")
        gold_sql = get_gold_sql(item)

        valid = table_index.get(db_id)
        if valid is None:
            skipped_no_db += 1
            continue

        gold = extract_gold_tables(gold_sql) & valid
        if not gold:
            skipped_no_gold += 1
            continue

        retrieved = retrieve_tables(collection, db_id, question, top_k)
        scores = score_question(gold, retrieved)

        all_scores.append(scores)
        by_complexity[len(gold)].append(scores)
        per_question.append(
            {
                "db_id": db_id,
                "question": question,
                "gold_tables": "|".join(sorted(gold)),
                "retrieved_tables": "|".join(retrieved),
                "recall": round(scores["recall"], 4),
                "precision": round(scores["precision"], 4),
                "full_coverage": int(scores["full_coverage"]),
                "reciprocal_rank": round(scores["reciprocal_rank"], 4),
            }
        )

    report: Dict[str, Any] = {
        "top_k": top_k,
        "num_evaluated": len(all_scores),
        "num_skipped_no_gold_tables": skipped_no_gold,
        "num_skipped_unknown_db": skipped_no_db,
        "full_coverage_rate": round(_mean([s["full_coverage"] for s in all_scores]), 4),
        "recall_at_k": round(_mean([s["recall"] for s in all_scores]), 4),
        "precision_at_k": round(_mean([s["precision"] for s in all_scores]), 4),
        "mrr": round(_mean([s["reciprocal_rank"] for s in all_scores]), 4),
        "by_num_gold_tables": {
            str(n): {
                "count": len(scores),
                "full_coverage_rate": round(
                    _mean([s["full_coverage"] for s in scores]), 4
                ),
                "recall_at_k": round(_mean([s["recall"] for s in scores]), 4),
            }
            for n, scores in sorted(by_complexity.items())
        },
    }
    return report, per_question


def main() -> None:
    """CLI entry point."""
    parser = argparse.ArgumentParser(
        description="Evaluate RAG table retrieval (Spider test)."
    )
    parser.add_argument("--data_dir", type=str, default="../data/spider_data")
    parser.add_argument("--test_file", type=str, default="test.json")
    parser.add_argument("--tables_file", type=str, default="test_tables.json")
    parser.add_argument("--top_k", type=int, default=5)
    parser.add_argument("--db_path", type=str, default="./chroma_db_storage")
    parser.add_argument("--collection", type=str, default="spider_schemas")
    parser.add_argument(
        "--report", type=str, default="evaluation/rag_retrieval_report.json"
    )
    parser.add_argument(
        "--per_question_csv",
        type=str,
        default="evaluation/rag_retrieval_per_question.csv",
    )
    args = parser.parse_args()

    data_dir = Path(args.data_dir).expanduser()
    test_path = data_dir / args.test_file
    tables_path = data_dir / args.tables_file
    for p in (test_path, tables_path):
        if not p.exists():
            print(f"Required file not found: {p}")
            sys.exit(1)

    print("1. Loading Spider test + tables...")
    test_data = load_files(test_path)
    tables_data = load_files(tables_path)

    print("2. Connecting to ChromaDB...")
    try:
        collection = get_chroma_collection(
            db_path=args.db_path, collection_name=args.collection
        )
    except Exception as exc:
        print(
            f"Could not load collection '{args.collection}' at '{args.db_path}': {exc}"
        )
        print("Build it first with: python -m src.build_vector_db")
        sys.exit(1)

    print(
        f"3. Evaluating retrieval @ top_k={args.top_k} over {len(test_data)} questions..."
    )
    report, rows = evaluate(test_data, tables_data, collection, args.top_k)

    report_path = Path(args.report).expanduser()
    csv_path = Path(args.per_question_csv).expanduser()
    report_path.parent.mkdir(parents=True, exist_ok=True)
    csv_path.parent.mkdir(parents=True, exist_ok=True)

    with open(report_path, "w", encoding="utf-8") as f:
        json.dump(report, f, indent=2)
    if rows:
        with open(csv_path, "w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
            writer.writeheader()
            writer.writerows(rows)

    print("\n=== RAG Retrieval Report ===")
    print(json.dumps(report, indent=2))
    print(f"\nSaved report  -> {report_path}")
    print(f"Saved details -> {csv_path}")


if __name__ == "__main__":
    main()
