
import stripe
import streamlit as st
from backend.database.connection import get_connection

def obter_ou_criar_customer_stripe(user_id):
    """Recupera ou cria o Customer do usuário no Stripe."""

    stripe.api_key = st.secrets["STRIPE_SECRET_KEY"]

    # Verifica se o usuário já possui um Customer.
    assinatura = buscar_assinatura_usuario(user_id)

    if assinatura and assinatura.get("stripe_customer_id"):
        return assinatura["stripe_customer_id"]

    # Recupera os dados do usuário no banco local.
    with get_connection() as con:
        usuario = con.execute(
            """
            SELECT name, email
            FROM users
            WHERE id = ?
            """,
            (user_id,),
        ).fetchone()

    if usuario is None:
        raise ValueError("Usuário não encontrado.")

    dados_customer = {
        "name": usuario["name"],
        "metadata": {
            "user_id": str(user_id),
        },
    }

    if usuario["email"]:
        dados_customer["email"] = usuario["email"]

    # Cria o Customer no Stripe.
    customer = stripe.Customer.create(
        **dados_customer,
        idempotency_key=f"gitforesight-customer-{user_id}",
    )

    # Persiste o identificador retornado.
    salvar_customer_stripe(user_id, customer.id)

    return customer.id

def criar_checkout_session(user_id):
    """Cria uma sessão de pagamento recorrente para o plano Equipe."""

    stripe.api_key = st.secrets["STRIPE_SECRET_KEY"]

    price_id = st.secrets["STRIPE_PRICE_EQUIPE"]

    # Recupera ou cria o Customer.
    customer_id = obter_ou_criar_customer_stripe(user_id)

    # URL base da aplicação.
    base_url = st.secrets.get(
        "APP_URL",
        "http://localhost:8501"
    ).rstrip("/")

    session = stripe.checkout.Session.create(
        mode="subscription",

        customer=customer_id,

        line_items=[
            {
                "price": price_id,
                "quantity": 1,
            }
        ],

        success_url=(
            f"{base_url}/?pagamento=sucesso"
            "&session_id={CHECKOUT_SESSION_ID}"
        ),

        cancel_url=(
            f"{base_url}/?pagamento=cancelado"
        ),

        client_reference_id=str(user_id),

        metadata={
            "user_id": str(user_id),
            "plan_key": "equipe",
        },

        subscription_data={
            "metadata": {
                "user_id": str(user_id),
                "plan_key": "equipe",
            }
        },
    )

    return session.url

def buscar_assinatura_usuario(user_id):
    """Retorna os dados de cobrança de um usuário."""

    with get_connection() as con:
        assinatura = con.execute(
            """
            SELECT
                id,
                user_id,
                stripe_customer_id,
                stripe_subscription_id,
                plan_key,
                price_id,
                status,
                current_period_start,
                current_period_end,
                cancel_at_period_end,
                created_at,
                updated_at
            FROM billing_subscriptions
            WHERE user_id = ?
            """,
            (user_id,),
        ).fetchone()

    return dict(assinatura) if assinatura else None


def salvar_customer_stripe(user_id, customer_id):
    """Registra o Customer ID associado ao usuário."""

    with get_connection() as con:
        con.execute(
            """
            INSERT INTO billing_subscriptions (
                user_id,
                stripe_customer_id
            )
            VALUES (?, ?)
            ON CONFLICT(user_id)
            DO UPDATE SET
                stripe_customer_id = excluded.stripe_customer_id,
                updated_at = CURRENT_TIMESTAMP
            """,
            (user_id, customer_id),
        )


def salvar_assinatura_stripe(
    user_id,
    customer_id,
    subscription_id,
    plan_key,
    price_id,
    status,
    current_period_start=None,
    current_period_end=None,
    cancel_at_period_end=False,
):
    """Insere ou atualiza os dados de uma assinatura."""

    with get_connection() as con:
        con.execute(
            """
            INSERT INTO billing_subscriptions (
                user_id,
                stripe_customer_id,
                stripe_subscription_id,
                plan_key,
                price_id,
                status,
                current_period_start,
                current_period_end,
                cancel_at_period_end
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)

            ON CONFLICT(user_id)
            DO UPDATE SET
                stripe_customer_id = excluded.stripe_customer_id,
                stripe_subscription_id = excluded.stripe_subscription_id,
                plan_key = excluded.plan_key,
                price_id = excluded.price_id,
                status = excluded.status,
                current_period_start = excluded.current_period_start,
                current_period_end = excluded.current_period_end,
                cancel_at_period_end = excluded.cancel_at_period_end,
                updated_at = CURRENT_TIMESTAMP
            """,
            (
                user_id,
                customer_id,
                subscription_id,
                plan_key,
                price_id,
                status,
                current_period_start,
                current_period_end,
                int(cancel_at_period_end),
            ),
        )