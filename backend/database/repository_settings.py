
from backend.database.connection import get_connection

def buscar_configuracoes_repositorio(repository_id, user_id):
    #verifica se o repositório pertence ao usuário, cria configurações padrão caso necessário e retorna os dados
    with get_connection() as con:
        repo = con.execute(
            """
            SELECT id, name, url, selected_branch
            FROM repositories
            WHERE id = ? AND user_id = ?
            """,
            (repository_id, user_id),
        ).fetchone()

        if not repo:
            return None

        con.execute(
            """
            INSERT OR IGNORE INTO repository_settings (repository_id)
            VALUES (?)
            """,
            (repository_id,),
        )

        configuracoes = con.execute(
            """
            SELECT *
            FROM repository_settings
            WHERE repository_id = ?
            """,
            (repository_id,),
        ).fetchone()

    dados = dict(configuracoes)
    dados["repo_nome"] = repo["name"]
    dados["repo_url"] = repo["url"]
    dados["selected_branch"] = repo["selected_branch"]

    return dados


def salvar_configuracoes_repositorio(repository_id, user_id, dados):
    #atualiza as configurações e impede que um usuário altere as configurações de outro
    with get_connection() as con:
        # Confirma a propriedade do repositório.
        repo = con.execute(
            """
            SELECT id
            FROM repositories
            WHERE id = ? AND user_id = ?
            """,
            (repository_id, user_id),
        ).fetchone()

        if not repo:
            return False

        con.execute(
            """
            INSERT OR IGNORE INTO repository_settings (repository_id)
            VALUES (?)
            """,
            (repository_id,),
        )

        con.execute(
            """
            UPDATE repository_settings
            SET
                ignored_directories = ?,
                analyze_on_commit = ?,
                scan_frequency = ?,
                scan_time = ?,
                scan_dependencies = ?,
                update_ai_projections = ?,
                notify_critical = ?,
                notify_score_increase = ?,
                notify_weekly_summary = ?,
                notify_no_alerts = ?,
                updated_at = CURRENT_TIMESTAMP
            WHERE repository_id = ?
            """,
            (
                dados["ignored_directories"],
                int(dados["analyze_on_commit"]),
                dados["scan_frequency"],
                dados["scan_time"],
                int(dados["scan_dependencies"]),
                int(dados["update_ai_projections"]),
                int(dados["notify_critical"]),
                int(dados["notify_score_increase"]),
                int(dados["notify_weekly_summary"]),
                int(dados["notify_no_alerts"]),
                repository_id,
            ),
        )

        con.execute(
            """
            UPDATE repositories
            SET selected_branch = ?
            WHERE id = ? AND user_id = ?
            """,
            (
                dados["selected_branch"],
                repository_id,
                user_id,
            ),
        )

    return True
