import hashlib
import secrets
import time

import streamlit as st

from backend.database.connection import get_connection

from backend.services.github_oauth import (
    gerar_pkce,
    github_login_url,
)


def hash_state(state):
    return hashlib.sha256(
        state.encode("utf-8")
    ).hexdigest()


def iniciar_oauth():
    # Gera valores exclusivos para esta tentativa
    state = secrets.token_urlsafe(32)
    verifier, challenge = gerar_pkce()

    agora = int(time.time())

    with get_connection() as con:
        # Remove tentativas expiradas
        con.execute(
            "DELETE FROM oauth_attempts WHERE expires_at <= ?",
            (agora,)
        )

        # Armazena os dados temporários
        con.execute(
            """
            INSERT INTO oauth_attempts
                (state_hash, code_verifier, expires_at)
            VALUES (?, ?, ?)
            """,
            (
                hash_state(state),
                verifier,
                agora + 300
            )
        )

    return github_login_url(state, challenge)


def consumir_tentativa(state):
    agora = int(time.time())

    with get_connection() as con:
        # Impede que duas requisições consumam a mesma tentativa
        con.execute("BEGIN IMMEDIATE")

        registro = con.execute(
            """
            SELECT code_verifier, expires_at
            FROM oauth_attempts
            WHERE state_hash = ?
            """,
            (hash_state(state),)
        ).fetchone()

        if registro is None:
            return None

        # Remove a tentativa mesmo que esteja expirada
        con.execute(
            "DELETE FROM oauth_attempts WHERE state_hash = ?",
            (hash_state(state),)
        )

        if registro["expires_at"] <= agora:
            return None

        return registro["code_verifier"]


# def processar_callback():
#     params = st.query_params

#     if "error" in params:
#         st.query_params.clear()
#         st.error("A autorização pelo GitHub foi cancelada ou recusada.")
#         return True

#     if "code" not in params:
#         return False

#     code = params.get("code")
#     state = params.get("state")

#     # Limpa a URL para evitar reutilização acidental do código
#     st.query_params.clear()

#     if not code or not state:
#         st.error("Retorno de autenticação incompleto.")
#         return True

#     verifier = consumir_tentativa(state)

#     if verifier is None:
#         st.error(
#             "Tentativa de autenticação inválida, expirada ou já utilizada."
#         )
#         return True

#     try:
#         token = trocar_codigo_por_token(
#             code,
#             code_verifier=verifier
#         )

#         usuario = buscar_usuario_github(token)

#     except Exception:
#         st.error(
#             "Não foi possível concluir a autenticação pelo GitHub. "
#             "Tente novamente."
#         )
#         return True

#     # Resultado temporário para testar a integração.
#     # Não exibimos nem armazenamos o access token na interface.
#     st.success("Autenticação com GitHub realizada com sucesso!")

#     st.write("ID GitHub:", usuario["id"])
#     st.write("Login:", usuario["login"])
#     st.write("Nome:", usuario.get("name"))

#     return True