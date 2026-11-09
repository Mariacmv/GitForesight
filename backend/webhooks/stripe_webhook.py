
import stripe
import streamlit as st

from fastapi import FastAPI, Request, HTTPException
from datetime import datetime, timezone

from backend.app.billing import (
    salvar_assinatura_stripe,
)
def converter_data_stripe(timestamp):
    if not timestamp:
        return None

    return datetime.fromtimestamp(
        timestamp,
        tz=timezone.utc
    ).isoformat()


def processar_assinatura(subscription, customer_id):
    if hasattr(subscription, "to_dict"):
        subscription = subscription.to_dict()
    else:
        subscription = dict(subscription)

    items = subscription.get("items", {}).get("data", [])

    if not items:
        raise ValueError(
            "Assinatura Stripe sem itens."
        )

    item = items[0]
    price_id = item["price"]["id"]

    metadata = subscription.get("metadata", {})
    user_id = metadata.get("user_id")

    if not user_id:
        print(
            "Assinatura ignorada: user_id ausente nos metadados."
        )
        return

    plan_key = metadata.get("plan_key", "equipe")

    periodo_inicio = (
        item.get("current_period_start")
        or subscription.get("current_period_start")
    )

    periodo_fim = (
        item.get("current_period_end")
        or subscription.get("current_period_end")
    )

    salvar_assinatura_stripe(
        user_id=int(user_id),
        customer_id=customer_id,
        subscription_id=subscription["id"],
        plan_key=plan_key,
        price_id=price_id,
        status=subscription["status"],
        current_period_start=converter_data_stripe(
            periodo_inicio
        ),
        current_period_end=converter_data_stripe(
            periodo_fim
        ),
        cancel_at_period_end=subscription.get(
            "cancel_at_period_end", False
        ),
    )
app = FastAPI(
    title="GitForesight Stripe Webhook"
)


@app.post("/webhooks/stripe")
async def receber_evento_stripe(request: Request):

    payload = await request.body()

    assinatura = request.headers.get(
        "stripe-signature"
    )

    if not assinatura:
        raise HTTPException(
            status_code=400,
            detail="Assinatura Stripe ausente."
        )

    try:
        evento = stripe.Webhook.construct_event(
            payload=payload,
            sig_header=assinatura,
            secret=st.secrets["STRIPE_WEBHOOK_SECRET"],
        )

    except ValueError as e:
        print("ERRO — Payload inválido:", repr(e))

        raise HTTPException(
            status_code=400,
            detail="Payload inválido."
        )

    except stripe.SignatureVerificationError as e:
        print("ERRO — Assinatura Stripe:", repr(e))

        raise HTTPException(
            status_code=400,
            detail="Assinatura do webhook inválida."
        )

    tipo_evento = evento["type"]
    dados = evento["data"]["object"]

    if hasattr(dados, "to_dict"):
        dados = dados.to_dict()

    print("Evento Stripe recebido:", tipo_evento)

    try:
        if tipo_evento == "checkout.session.completed":

            if dados.get("mode") == "subscription":
                subscription_id = dados.get("subscription")
                customer_id = dados.get("customer")

                if subscription_id and customer_id:
                    stripe.api_key = st.secrets["STRIPE_SECRET_KEY"]
                    subscription = stripe.Subscription.retrieve(
                        subscription_id
                    )

                    processar_assinatura(
                        subscription,
                        customer_id
                    )

        elif tipo_evento in (
            "customer.subscription.updated",
            "customer.subscription.deleted",
        ):
            processar_assinatura(
                dados,
                dados["customer"]
            )
        return {
            "received": True, 
            "event": tipo_evento,
        }
    except Exception as e:
        print(
            "ERRO — Processamento da assinatura:",
            repr(e)
        )

        raise HTTPException(
            status_code=500,
            detail="Erro ao processar evento Stripe."
        )
        

