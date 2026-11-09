
import tomllib
from pathlib import Path

import stripe 
from backend.database.connection import get_connection 



# Carrega as configurações do projeto.
ROOT_DIR = Path(__file__).resolve().parent
SECRETS_PATH = ROOT_DIR / ".streamlit" / "secrets.toml"

with open(SECRETS_PATH, "rb") as arquivo:
    secrets = tomllib.load(arquivo)

stripe.api_key = secrets["STRIPE_SECRET_KEY"]

PRICE_ID = secrets["STRIPE_PRICE_EQUIPE"]
APP_URL = secrets.get("APP_URL", "http://localhost:8501").rstrip("/")


def testar_customer(user_id):
    print("\n[1] Verificando usuário no SQLite...")

    with get_connection() as con:
        usuario = con.execute(
            "SELECT id, name, email FROM users WHERE id = ?",
            (user_id,),
        ).fetchone()

        assinatura = con.execute(
            """
            SELECT stripe_customer_id
            FROM billing_subscriptions
            WHERE user_id = ?
            """,
            (user_id,),
        ).fetchone()

    if usuario is None:
        raise ValueError("Usuário não encontrado no SQLite.")

    print(f"Usuário encontrado: {usuario['name']}")

    customer_id = (
        assinatura["stripe_customer_id"]
        if assinatura else None
    )

    print(f"Customer salvo: {customer_id}")

    if customer_id:
        print("\n[2] Consultando Customer no Stripe...")

        try:
            customer = stripe.Customer.retrieve(customer_id)

            print("Customer encontrado!")
            print(f"ID: {customer.id}")
            print(f"Email: {customer.email}")

            return customer.id

        except stripe.InvalidRequestError as erro:
            if erro.code != "resource_missing":
                raise

            print("Customer não existe na conta Stripe atual.")
            print("Será necessário criar outro.")

    print("\n[3] Criando novo Customer...")

    dados = {
        "name": usuario["name"],
        "metadata": {"user_id": str(user_id)},
    }

    if usuario["email"]:
        dados["email"] = usuario["email"]

    customer = stripe.Customer.create(**dados)

    print(f"Novo Customer criado: {customer.id}")

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
            (user_id, customer.id),
        )

    print("Novo Customer salvo no SQLite.")

    return customer.id


def testar_price():
    print("\n[4] Verificando Price do plano Equipe...")

    price = stripe.Price.retrieve(PRICE_ID)

    print(f"Price ID: {price.id}")
    print(f"Ativo: {price.active}")
    print(f"Moeda: {price.currency}")
    print(f"Tipo: {price.type}")

    if not price.active:
        raise ValueError("O Price está inativo.")

    if price.type != "recurring":
        raise ValueError("O Price não está configurado como recorrente.")


def testar_checkout(user_id, customer_id):
    print("\n[5] Criando sessão de Checkout...")

    session = stripe.checkout.Session.create(
        mode="subscription",
        customer=customer_id,
        line_items=[
            {
                "price": PRICE_ID,
                "quantity": 1,
            }
        ],
        success_url=(
            f"{APP_URL}/?pagamento=sucesso"
            "&session_id={CHECKOUT_SESSION_ID}"
        ),
        cancel_url=f"{APP_URL}/?pagamento=cancelado",
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

    print("Checkout criado com sucesso!")
    print(f"Session ID: {session.id}")
    print(f"URL: {session.url}")


def main():
    print("================================")
    print(" TESTE DE INTEGRAÇÃO - STRIPE")
    print("================================")

    print(
        "Ambiente:",
        "TESTE" if stripe.api_key.startswith("sk_test_") else "PRODUÇÃO"
    )

    user_id = input("\nInforme o ID do usuário no SQLite: ").strip()

    if not user_id:
        raise ValueError("Informe um ID válido.")

    try:
        customer_id = testar_customer(user_id)
        testar_price()
        testar_checkout(user_id, customer_id)

        print("\nTESTE FINALIZADO COM SUCESSO.")

    except stripe.StripeError as erro:
        print("\nERRO NA API STRIPE:")
        print(type(erro).__name__)
        print(erro)

    except Exception as erro:
        print("\nERRO NO TESTE:")
        print(type(erro).__name__)
        print(erro)


if __name__ == "__main__":
    main()
