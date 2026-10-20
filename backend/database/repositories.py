
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
            (user_id,),
        ).fetchone()

    return dict(repo) if repo else None


def buscar_conexao_github(user_id):
    """Verifica se a conta local está vinculada a uma conta GitHub."""
    with get_connection() as con:
        conta = con.execute(
            """
            SELECT github_id, github_login
            FROM github_accounts
            WHERE user_id = ?
            LIMIT 1
            """,
            (user_id,),
        ).fetchone()

    return dict(conta) if conta else None


def salvar_instalacoes_github(user_id, instalacoes):
    """Salva as instalações que o GitHub confirmou para o usuário."""
    with get_connection() as con:
        for instalacao in instalacoes:
            existente = con.execute(
                """
                SELECT user_id
                FROM github_installations
                WHERE installation_id = ?
                """,
                (instalacao["installation_id"],),
            ).fetchone()

            if existente and existente["user_id"] != user_id:
                # Não transfere uma instalação silenciosamente
                # de um usuário local para outro.
                continue

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
                ON CONFLICT(installation_id) DO UPDATE SET
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


def listar_instalacoes_github_usuario(user_id):
    """Retorna somente as instalações vinculadas ao usuário local."""
    with get_connection() as con:
        instalacoes = con.execute(
            """
            SELECT
                installation_id,
                account_id,
                account_login,
                account_type
            FROM github_installations
            WHERE user_id = ?
            ORDER BY account_login
            """,
            (user_id,),
        ).fetchall()

    return [dict(instalacao) for instalacao in instalacoes]
