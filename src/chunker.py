from typing import Any, Dict, List


def chunk_live_schema(ddl_commands: List[str]) -> List[Dict[str, Any]]:
    """
    Takes raw SQL DDL strings and turns them into organized chunks with table name metadata.
    """
    chunks = []

    for ddl in ddl_commands:
        clean_ddl = ddl.strip()
        if not clean_ddl:
            continue
        chunks.append(
            {
                "ddl": clean_ddl,
            }
        )

    return chunks
