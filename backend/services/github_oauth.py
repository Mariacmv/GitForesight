import requests, hashlib, base64, secrets
import streamlit as st

from urllib.parse import urlencode

def gerar_pkce():
    verifier = secrets.token_urlsafe(64)

    digest = hashlib.sha256(
        verifier.encode("ascii")
    ).digest()

    challenge = (
        base64.urlsafe_b64encode(digest)
        .decode("ascii")
        .rstrip("=")
    )

    return verifier, challenge

def github_login_url(state, code_challenge):
    parametros = {
        "client_id": st.secrets["GITHUB_CLIENT_ID"].strip(),
        "redirect_uri": st.secrets["GITHUB_REDIRECT_URI"].strip(),
        "state": state,
        "code_challenge": code_challenge,
        "code_challenge_method": "S256",
    }

    return (
        "https://github.com/login/oauth/authorize?"
        + urlencode(parametros)
    )

def trocar_codigo_por_token(code, code_verifier=None):
    dados = {
        "client_id": st.secrets["GITHUB_CLIENT_ID"],
        "client_secret": st.secrets["GITHUB_CLIENT_SECRET"],
        "code": code,
        "redirect_uri": st.secrets["GITHUB_REDIRECT_URI"],
    }

    if code_verifier:
        dados["code_verifier"] = code_verifier

    resposta = requests.post(
        "https://github.com/login/oauth/access_token",
        headers={"Accept": "application/json"},
        data=dados,
        timeout=15
    )

    resposta.raise_for_status()
    resultado = resposta.json()

    if "access_token" not in resultado:
        raise ValueError("Não foi possível obter o token do GitHub.")

    return resultado["access_token"]


def buscar_usuario_github(token):
    resposta = requests.get(
        "https://api.github.com/user",
        headers={
            "Authorization": f"Bearer {token}",
            "Accept": "application/vnd.github+json",
        },
        timeout=15
    )

    resposta.raise_for_status()

    return resposta.json()

