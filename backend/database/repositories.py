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
            

def salvar_repositorio_usuario(user_id, nome, url):
    with get_connection() as con:
        con.execute(
            """
            INSERT INTO repositories (user_id, name, url, connected_at)
            VALUES (?, ?, ?, CURRENT_TIMESTAMP)
            ON CONFLICT(user_id, url)
            DO UPDATE SET
                name = excluded.name,
                connected_at = CURRENT_TIMESTAMP
            """,
            (user_id, nome, url),
        )

        repo = con.execute(
            """
            SELECT id, user_id, name, url, connected_at
            FROM repositories
            WHERE user_id = ? AND url = ?
            """,
            (user_id, url),
        ).fetchone()

    return dict(repo)


def listar_repositorios_usuario(user_id):
    with get_connection() as con:
        repos = con.execute(
            """
            SELECT id, user_id, name, url, connected_at
            FROM repositories
            WHERE user_id = ?
            ORDER BY connected_at DESC, id DESC
            """,
            (user_id,),
        ).fetchall()

    return [dict(repo) for repo in repos]


def migrar_repositorios():
    """Adiciona colunas necessárias para persistir o contexto."""

    with get_connection() as con:
        colunas = [
            c[1]
            for c in con.execute("PRAGMA table_info(repositories)")
        ]

        if "last_analysis_at" not in colunas:
            con.execute(
                "ALTER TABLE repositories ADD COLUMN last_analysis_at TEXT"
            )

        if "selected_branch" not in colunas:
            con.execute(
                "ALTER TABLE repositories ADD COLUMN selected_branch TEXT"
            )
            
def salvar_branch_repositorio(user_id, url, branch):
    with get_connection() as con:
        con.execute(
            """
            UPDATE repositories
            SET selected_branch = ?
            WHERE user_id = ? AND url = ?
            """,
            (branch, user_id, url),
        )


def marcar_repositorio_analisado(user_id, url):
    with get_connection() as con:
        con.execute(
            """
            UPDATE repositories
            SET last_analysis_at = CURRENT_TIMESTAMP
            WHERE user_id = ? AND url = ?
            """,
            (user_id, url),
        )


def buscar_repositorio_analisado(user_id):
    """O repositório mais recentemente analisado com sucesso."""
    with get_connection() as con:
        repo = con.execute(
            """
            SELECT
                id,
                user_id,
                name,
                url,
                connected_at,
                last_analysis_at,
                selected_branch
            FROM repositories
            WHERE user_id = ? AND last_analysis_at IS NOT NULL
            ORDER BY last_analysis_at DESC, id DESC
            LIMIT 1
            """,
            (user_id,),
        ).fetchone()

    return dict(repo) if repo else None


def remover_repositorio_usuario(user_id, repo_id):
    with get_connection() as con:
        con.execute(
            "DELETE FROM repositories WHERE id = ? AND user_id = ?",
            (repo_id, user_id),
        )
        
def buscar_ultima_analise_usuario(user_id):
    with get_connection() as con:
        analise = con.execute(
            """
            SELECT
                a.id,
                a.repository_id,
                a.branch,
                a.analyzed_at,
                a.commits_count,
                a.artifact_dir,
                r.name AS repository_name,
                r.url AS repository_url
            FROM analyses a
            INNER JOIN repositories r
                ON r.id = a.repository_id
            WHERE r.user_id = ?
            ORDER BY a.analyzed_at DESC, a.id DESC
            LIMIT 1
            """,
            (user_id,),
        ).fetchone()

    return dict(analise) if analise else None

def registrar_analise(user_id, url, branch, commits_count, artifact_dir):
    with get_connection() as con:
        repo = con.execute(
            """
            SELECT id
            FROM repositories
            WHERE user_id = ? AND url = ?
            LIMIT 1
            """,
            (user_id, url),
        ).fetchone()

        if not repo:
            raise ValueError(
                "Repositório não encontrado no banco de dados."
            )

        cursor = con.execute(
            """
            INSERT INTO analyses (
                repository_id,
                branch,
                commits_count,
                artifact_dir
            )
            VALUES (?, ?, ?, ?)
            """,
            (
                repo["id"],
                branch,
                commits_count,
                artifact_dir,
            ),
        )

        return cursor.lastrowid