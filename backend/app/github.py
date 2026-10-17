#para acessar os repositórios
import re
from urllib.parse import urlparse, unquote

import requests


API = "https://api.github.com"


def extrair_repositorio(url):
    parsed = urlparse(url.strip())

    if parsed.scheme != "https":
        raise ValueError("Informe uma URL HTTPS do GitHub.")

    if parsed.hostname not in ("github.com", "www.github.com"):
        raise ValueError("O link precisa pertencer ao GitHub.")

    partes = parsed.path.strip("/").split("/")

    if len(partes) != 2:
        raise ValueError(
            "Use o formato: https://github.com/usuario/repositorio"
        )

    owner, repo = map(unquote, partes)
    repo = repo.removesuffix(".git")

    padrao = r"[A-Za-z0-9_.-]+"

    if not re.fullmatch(padrao, owner):
        raise ValueError("Proprietário inválido.")

    if not re.fullmatch(padrao, repo):
        raise ValueError("Nome do repositório inválido.")

    return owner, repo


def fetch_repo_info(url, token=None):
    owner, repo = extrair_repositorio(url)

    headers = {
        "Accept": "application/vnd.github+json",
    }

    if token:
        headers["Authorization"] = f"Bearer {token}"

    base = f"{API}/repos/{owner}/{repo}"

    def consultar(endpoint, params=None):
        resposta = requests.get(
            endpoint,
            headers=headers,
            params=params,
            timeout=20
        )

        if resposta.status_code == 404:
            raise ValueError(
                "Repositório não encontrado ou sem permissão de acesso."
            )

        if resposta.status_code in (401, 403):
            raise ValueError(
                "Acesso negado pelo GitHub. Verifique a autorização "
                "e as permissões da GitHub App."
            )

        resposta.raise_for_status()
        return resposta

    # Informações gerais
    dados = consultar(base).json()

    # Lista de branches, incluindo paginação
    branches = []
    pagina = 1

    while True:
        resposta = consultar(
            f"{base}/branches",
            {"per_page": 100, "page": pagina}
        )

        lote = resposta.json()
        branches.extend(item["name"] for item in lote)

        if len(lote) < 100:
            break

        pagina += 1

    # Prévia de commits (não é a contagem total)
    commits = consultar(
        f"{base}/commits",
        {
            "sha": dados["default_branch"],
            "per_page": 100
        }
    ).json()

    # Prévia de contribuidores
    contribuidores = consultar(
        f"{base}/contributors",
        {"per_page": 100, "anon": "true"}
    ).json()

    return {
        "full_name": dados["full_name"],
        "url": dados["html_url"],
        "private": dados["private"],
        "language": dados.get("language") or "Não identificada",
        "default_branch": dados["default_branch"],
        "branches": branches,
        "commits": len(commits),
        "contributors": len(contribuidores),
    }