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

def salvar_instalacoes_github(user_id, instalacoes):
    with get_connection() as con:
        for instalacao in instalacoes:
            con.execute(
                """
                INSERT INTO github_installations (
                    installation_id,
                    user_id,
                    account_id,
                    account_login,
                    account_type
                )
                VALUES (?, ?, ?, ?, ?)

                ON CONFLICT(installation_id)
                DO UPDATE SET
                    account_id = excluded.account_id,
                    account_login = excluded.account_login,
                    account_type = excluded.account_type

                WHERE github_installations.user_id = excluded.user_id
                """,
                (
                    instalacao["installation_id"],
                    user_id,
                    instalacao["account_id"],
                    instalacao["account_login"],
                    instalacao["account_type"],
                ),
            )