import hashlib
import secrets
import time

import streamlit as st

from backend.database.connection import get_connection
from backend.database.github_accounts import autenticar_usuario_github
from backend.services.github_token_storage import (
    salvar_token_github,
)

from backend.services.github_oauth import (
    gerar_pkce,
    github_login_url,
    trocar_codigo_por_token,
    buscar_usuario_github,
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
                agora + 600
            )
        )
    print("OAuth iniciado:", hash_state(state)[:12])

    return github_login_url(state, challenge)


def consumir_tentativa(state):
    agora = int(time.time())
    state_hash = hash_state(state)

    with get_connection() as con:
        registro = con.execute(
            """
            DELETE FROM oauth_attempts
            WHERE state_hash = ?
            RETURNING code_verifier, expires_at
            """,
            (state_hash,)
        ).fetchone()

        if registro is None:
            return None

        if registro["expires_at"] <= agora:
            return None

        return registro["code_verifier"]

def processar_callback():
    params = st.query_params

    if "error" in params:
        st.query_params.clear()
        st.error("A autorização pelo GitHub foi cancelada ou recusada.")
        return True

    if "code" not in params:
        return False

    code = params.get("code")
    state = params.get("state")
    st.session_state.pop("github_oauth_url", None)
    
    # Limpa a URL para evitar reutilização acidental do código
    st.query_params.clear()

    if not code or not state:
        st.error("Retorno de autenticação incompleto.")
        return True

    print("OAuth recebido:", hash_state(state)[:12])

    verifier = consumir_tentativa(state)

    if verifier is None:
        st.error(
            "Tentativa de autenticação inválida, expirada ou já utilizada."
        )
        return True

    try:
        token = trocar_codigo_por_token(
            code,
            code_verifier=verifier
        )

        usuario = buscar_usuario_github(token)
        st.session_state.github_user_token = token #token para consultar as instalações disponíveis

    except Exception as e:
        st.error(
            "Não foi possível concluir a autenticação pelo GitHub. "
        )
        
        st.exception(e)
        return True

    try:
        usuario_local = autenticar_usuario_github(usuario)

        salvar_token_github(
            usuario_local["id"],
            token,
        )

    except Exception as e:
        st.error(
            "Não foi possível concluir a autenticação pelo GitHub."
        )
        st.exception(e)
        return True

    # Entrega o usuário autenticado ao app.py
    st.session_state.github_usuario_pendente = usuario_local

    return True
