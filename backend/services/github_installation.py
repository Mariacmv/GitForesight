import time
from pathlib import Path

import jwt
import requests
import streamlit as st

API = "https://api.github.com"


def _headers(token):
    return {
        "Authorization": f"Bearer {token}",
        "Accept": "application/vnd.github+json",
        "X-GitHub-Api-Version": "2022-11-28",
    }


def gerar_app_jwt():
    app_id = st.secrets["GITHUB_APP_ID"]

    caminho = Path(
        st.secrets["GITHUB_PRIVATE_KEY_PATH"]
    ).expanduser()

    private_key = caminho.read_text(encoding="utf-8")

    agora = int(time.time())

    payload = {
        "iat": agora - 60,
        "exp": agora + 540,
        "iss": str(app_id),
    }

    return jwt.encode(
        payload,
        private_key,
        algorithm="RS256",
    )


def gerar_installation_token(installation_id):
    app_jwt = gerar_app_jwt()

    resposta = requests.post(
        f"{API}/app/installations/{int(installation_id)}/access_tokens",
        headers=_headers(app_jwt),
        timeout=15,
    )

    resposta.raise_for_status()

    return resposta.json()["token"]


def listar_repositorios_instalacao(installation_id):
    token = gerar_installation_token(installation_id)

    repositorios = []
    pagina = 1

    while True:
        resposta = requests.get(
            f"{API}/installation/repositories",
            headers=_headers(token),
            params={
                "per_page": 100,
                "page": pagina,
            },
            timeout=15,
        )

        resposta.raise_for_status()

        lote = resposta.json()["repositories"]

        repositorios.extend(
            {
                "github_repo_id": repo["id"],
                "full_name": repo["full_name"],
                "private": repo["private"],
                "description": repo.get("description"),
                "language": repo.get("language") or "—",
                "pushed_at": repo.get("pushed_at"),
                "default_branch": repo["default_branch"],
            }
            for repo in lote
        )

        if len(lote) < 100:
            break

        pagina += 1

    return repositorios

def consultar_instalacao(installation_id):
    app_jwt = gerar_app_jwt()

    resposta = requests.get(
        f"{API}/app/installations/{int(installation_id)}",
        headers=_headers(app_jwt),
        timeout=15,
    )

    resposta.raise_for_status()

    dados = resposta.json()

    return {
        "installation_id": dados["id"],
        "account_id": dados["account"]["id"],
        "account_login": dados["account"]["login"],
        "account_type": dados["account"]["type"],
        "repository_selection": dados["repository_selection"],
        "suspended_at": dados.get("suspended_at"),
    }
    
def listar_instalacoes_app():
    """
        Lista instalações de toda a aplicação
    """
    app_jwt = gerar_app_jwt()

    resposta = requests.get(
        f"{API}/app/installations",
        headers=_headers(app_jwt),
        params={"per_page": 100},
        timeout=15,
    )

    resposta.raise_for_status()

    return [
        {
            "installation_id": item["id"],
            "account_login": item["account"]["login"],
            "account_id": item["account"]["id"],
        }
        for item in resposta.json()
    ]

def listar_instalacoes_usuario(user_token):
    """
        Lista instalações do usuário autenticado
    """
    resposta = requests.get(
        f"{API}/user/installations",
        headers=_headers(user_token),
        params={"per_page": 100},
        timeout=15,
    )

    resposta.raise_for_status()

    return [
        {
            "installation_id": item["id"],
            "account_id": item["account"]["id"],
            "account_login": item["account"]["login"],
            "account_type": item["account"]["type"],
        }
        for item in resposta.json().get("installations", [])
    ]