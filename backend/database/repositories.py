from backend.database.connection import get_connection


def buscar_repositorio_usuario(user_id):
    with get_connection() as con:
        repo = con.execute(
            """
            SELECT id, user_id, name, url, connected_at
            FROM repositories
            WHERE user_id = ?
            ORDER BY connected_at DESC, id DESC
            LIMIT 1
            """,
            (user_id,)
        ).fetchone()

    return dict(repo) if repo else None