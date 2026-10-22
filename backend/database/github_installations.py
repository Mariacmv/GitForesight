"""
Uma observação: essa estrutura inicial considera uma instalação vinculada a um usuário por vez. 
Antes de disponibilizar instalações organizacionais para vários usuários, vamos evoluir o relacionamento no banco. 
Também não devemos permitir que uma associação existente seja transferida silenciosamente para outra conta.
"""
from backend.database.connection import get_connection


def salvar_instalacao_usuario(user_id, instalacao):
    with get_connection() as conn:
        conn.execute(
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
                user_id = excluded.user_id,
                account_id = excluded.account_id,
                account_login = excluded.account_login,
                account_type = excluded.account_type
            """,
            (
                instalacao["installation_id"],
                user_id,
                instalacao["account_id"],
                instalacao["account_login"],
                instalacao["account_type"],
            ),
        )


def buscar_instalacao_usuario(user_id):
    with get_connection() as conn:
        rows = conn.execute(
            """
            SELECT
                installation_id,
                account_id,
                account_login,
                account_type
            FROM github_installations
            WHERE user_id = ?
            ORDER BY connected_at DESC
            """,
            (user_id,),
        ).fetchall()

    return [dict(row) for row in rows]