
from backend.database.connection import get_connection
from backend.app.plans import get_plan


ACTIVE_STATUSES = {"active", "trialing"}



def get_billing_owner_id(user_id):
    """Retorna o titular da assinatura do usuário."""
    with get_connection() as con:
        row = con.execute(
            """
            SELECT t.owner_user_id
            FROM team_members tm
            JOIN teams t ON t.id = tm.team_id
            WHERE tm.user_id = ?
              AND tm.status = 'active'
            LIMIT 1
            """,
            (user_id,),
        ).fetchone()

    return row["owner_user_id"] if row else user_id


def get_account_subscription(user_id):
    """Retorna a assinatura do titular da conta."""
    billing_user_id = get_billing_owner_id(user_id)

    with get_connection() as con:
        row = con.execute(
            """
            SELECT plan_key, status, stripe_customer_id,
                   stripe_subscription_id, current_period_end,
                   cancel_at_period_end
            FROM billing_subscriptions
            WHERE user_id = ?
            """,
            (billing_user_id,),
        ).fetchone()

    if row is None:
        return {
            "plan_key": "explorar",
            "status": "inactive",
        }

    return dict(row)


def get_account_plan(user_id):
    """
    Retorna o plano efetivamente disponível.
    Planos pagos só são liberados com assinatura ativa ou em teste.
    """
    subscription = get_account_subscription(user_id)

    plan_key = subscription["plan_key"]
    status = subscription["status"]

    if plan_key != "explorar" and status not in ACTIVE_STATUSES:
        plan_key = "explorar"

    return get_plan(plan_key)


def get_effective_plan_key(user_id):
    """Retorna a chave do plano efetivamente disponível."""
    return get_account_plan(user_id)["name"].lower().replace("ã", "a")


def get_feature_access(user_id, feature):
    """
    Retorna o nível de acesso à funcionalidade:
    True, False, 'limited' ou 'preview'.
    """
    plan = get_account_plan(user_id)
    return plan["features"].get(feature, False)


def has_permission(user_id, feature):
    """Verifica se o usuário possui acesso completo à funcionalidade."""
    access = get_feature_access(user_id, feature)
    return access is True or access == "full"


def get_limit(user_id, limit):
    """Retorna o limite definido pelo plano."""
    plan = get_account_plan(user_id)
    return plan["limits"].get(limit)


def get_team_owner(team_id):
    """Identifica o administrador responsável pela equipe."""
    with get_connection() as con:
        row = con.execute(
            """
            SELECT owner_user_id
            FROM teams
            WHERE id = ?
            """,
            (team_id,),
        ).fetchone()

    return row["owner_user_id"] if row else None


def get_user_team(user_id):
    """Retorna a equipe da qual o usuário é membro."""
    with get_connection() as con:
        row = con.execute(
            """
            SELECT t.id, t.owner_user_id, tm.id AS member_id, tm.role
            FROM team_members tm
            JOIN teams t ON t.id = tm.team_id
            WHERE tm.user_id = ?
              AND tm.status = 'active'
            LIMIT 1
            """,
            (user_id,),
        ).fetchone()

    return dict(row) if row else None


def get_user_role(user_id, team_id):
    """Identifica se o usuário é administrador ou visualizador."""
    with get_connection() as con:
        team = con.execute(
            """
            SELECT owner_user_id
            FROM teams
            WHERE id = ?
            """,
            (team_id,),
        ).fetchone()

        if not team:
            return None

        if team["owner_user_id"] == user_id:
            return "admin"

        member = con.execute(
            """
            SELECT role
            FROM team_members
            WHERE team_id = ?
              AND user_id = ?
              AND status = 'active'
            """,
            (team_id, user_id),
        ).fetchone()

    return member["role"] if member else None


def can_manage_team(user_id, team_id):
    """Somente o administrador de uma conta premium pode gerenciar a equipe."""
    if get_user_role(user_id, team_id) != "admin":
        return False

    return has_permission(user_id, "team_management")


def can_add_repository(user_id):
    """Verifica se a conta pode adicionar outro repositório."""
    limit = get_limit(user_id, "repositories")

    if limit is None:
        return True

    with get_connection() as con:
        row = con.execute(
            """
            SELECT COUNT(*) AS total
            FROM repositories
            WHERE user_id = ?
            """,
            (user_id,),
        ).fetchone()

    return row["total"] < limit


def can_add_member(user_id):
    """Verifica se o administrador pode adicionar outro membro."""
    if not has_permission(user_id, "team_management"):
        return False

    limit = get_limit(user_id, "members")

    if limit is None:
        return True

    with get_connection() as con:
        row = con.execute(
            """
            SELECT COUNT(*) AS total
            FROM teams t
            LEFT JOIN team_members tm
                ON tm.team_id = t.id
                AND tm.status = 'active'
            WHERE t.owner_user_id = ?
            GROUP BY t.id
            """,
            (user_id,),
        ).fetchone()

    total = row["total"] + 1 if row else 1
    return total < limit


def can_access_repository(user_id, repository_id):
    """
    Verifica se o usuário é proprietário do repositório
    ou recebeu autorização como visualizador.
    """
    with get_connection() as con:
        repository = con.execute(
            """
            SELECT user_id
            FROM repositories
            WHERE id = ?
            """,
            (repository_id,),
        ).fetchone()

        if not repository:
            return False

        if repository["user_id"] == user_id:
            return True

        permission = con.execute(
            """
            SELECT 1
            FROM team_member_repositories tmr
            JOIN team_members tm
                ON tm.id = tmr.member_id
               AND tm.team_id = tmr.team_id
            WHERE tm.user_id = ?
              AND tm.status = 'active'
              AND tmr.repository_id = ?
            LIMIT 1
            """,
            (user_id, repository_id),
        ).fetchone()

    return permission is not None
