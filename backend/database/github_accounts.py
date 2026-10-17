from backend.database.connection import get_connection


def autenticar_usuario_github(usuario_github):
    github_id = int(usuario_github["id"])
    github_login = usuario_github["login"]
    nome = usuario_github.get("name") or github_login

    con = get_connection()

    try:
        con.execute("BEGIN IMMEDIATE")

        # Verifica se essa conta GitHub já está vinculada
        row = con.execute(
            """
            SELECT u.id, u.name, u.email
            FROM github_accounts g
            JOIN users u ON u.id = g.user_id
            WHERE g.github_id = ?
            """,
            (github_id,)
        ).fetchone()

        if row is not None:
            con.execute(
                """
                UPDATE github_accounts
                SET github_login = ?
                WHERE github_id = ?
                """,
                (github_login, github_id)
            )

            con.commit()
            return dict(row)

        # Primeiro acesso: cria uma conta local
        cursor = con.execute(
            """
            INSERT INTO users (name, email, password_hash)
            VALUES (?, NULL, NULL)
            """,
            (nome,)
        )

        user_id = cursor.lastrowid

        con.execute(
            """
            INSERT INTO github_accounts
                (github_id, user_id, github_login)
            VALUES (?, ?, ?)
            """,
            (github_id, user_id, github_login)
        )

        con.commit()

        return {
            "id": user_id,
            "name": nome,
            "email": None
        }

    except Exception:
        con.rollback()
        raise

    finally:
        con.close()