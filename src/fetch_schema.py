import psycopg


def get_schema(db_uri: str):
    dynamic_ddl_query = """
    SELECT
        'CREATE TABLE ' || c.relname || ' (' || chr(10) ||
        array_to_string(
            array_agg(
                '    "' || a.attname || '" ' || pg_catalog.format_type(a.atttypid, a.atttypmod) ||
                CASE WHEN a.attnotnull THEN ' NOT NULL' ELSE '' END
                ORDER BY a.attnum
            ), ',' || chr(10)
        ) ||
        COALESCE((
            SELECT ',' || chr(10) || array_to_string(array_agg('    CONSTRAINT "' || con.conname || '" ' || pg_get_constraintdef(con.oid)), ',' || chr(10))
            FROM pg_catalog.pg_constraint con
            WHERE con.conrelid = c.oid AND con.contype IN ('p', 'f')
        ), '') || chr(10) || ');' AS ddl_schema
    FROM pg_catalog.pg_class c
    JOIN pg_catalog.pg_namespace n ON n.oid = c.relnamespace
    JOIN pg_catalog.pg_attribute a ON a.attrelid = c.oid
    WHERE n.nspname = 'public'
    AND c.relkind = 'r'
    AND a.attnum > 0
    AND NOT a.attisdropped
    AND has_table_privilege(current_user, c.oid, 'SELECT')
    GROUP BY c.oid, c.relname;
    """

    try:
        with psycopg.connect(db_uri) as conn:
            with conn.cursor() as cursor:
                cursor.execute(dynamic_ddl_query)
                rows = cursor.fetchall()

                schema_strings = [row[0] for row in rows]

                return schema_strings

    except psycopg.OperationalError as e:
        print(f"Connection failed. Verify your host, port, and credentials: {e}")

    except Exception as e:
        print(f"Database extraction failed: {e}")
