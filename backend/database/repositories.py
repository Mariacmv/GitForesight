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

def buscar_conexao_github(user_id):
    """
        Verifica se a conta conectada está vinculada a uma conta do github
    """
    
    with get_connection() as con:
        conta = con.execute(
            """
            SELECT github_id, github_login
            FROM github_accounts
            WHERE user_id = ?
            LIMIT 1
            """,
            (user_id,)
        ).fetchone()

    return dict(conta) if conta else None