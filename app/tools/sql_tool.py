from app.database.connection import get_connection


def execute_readonly_sql(query: str):
    """
    Execute a read-only SQL query against the enterprise database.
    """

    normalized_query = query.strip().lower()

    if not normalized_query.startswith("select"):
        raise ValueError(
            "Only SELECT statements are allowed."
        )

    connection = get_connection()

    try:
        cursor = connection.execute(query)
        rows = cursor.fetchall()

        return [dict(row) for row in rows]

    finally:
        connection.close()