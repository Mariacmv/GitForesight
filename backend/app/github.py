import os
import re
from concurrent.futures import ThreadPoolExecutor
import requests

API = "https://api.github.com"

URL_RE = re.compile(
    r"^(?:https?://)?(?:www\.)?github\.com/([\w.-]+)/([\w.-]+?)(?:\.git)?/?$"
)


def parse_repo_url(url):
    match = URL_RE.match(url.strip())
    if not match:
        raise ValueError(
            "Informe uma URL válida do GitHub, "
            "ex.: https://github.com/usuario/repositorio"
        )
    return match.group(1), match.group(2)


def _headers(token=None):
    """
        Impede que uma consulta sem token utilize silenciosamente as credenciais configuradas no servidor
    """
    headers = {
        "Accept": "application/vnd.github+json",
        "X-GitHub-Api-Version": "2022-11-28",
    }
    if token:
        headers["Authorization"] = f"Bearer {token}"
    return headers


def _get(path, token=None, **params):
    response = requests.get(
        f"{API}{path}", params=params, headers=_headers(token), timeout=10
    )

    if response.status_code == 404:
        raise ValueError(
            "Não encontrado. Se for privado, é preciso conectar sua conta do GitHub."
        )
    if response.status_code == 403 and response.headers.get("X-RateLimit-Remaining") == "0":
        raise ValueError(
            "Limite de consultas ao GitHub atingido. Tente de novo mais tarde "
            "ou conecte sua conta."
        )
    if response.status_code in (401, 403):
        raise ValueError("Acesso negado pelo GitHub.")

    response.raise_for_status()
    return response


def _count(path, token=None, **params):
    response = _get(path, token=token, per_page=1, **params)
    if response.status_code == 204 or not response.content:
        return 0
    last = response.links.get("last")
    if last:
        return int(re.search(r"[?&]page=(\d+)", last["url"]).group(1))
    return len(response.json())


def list_accounts(token):
    """Conta do usuário + organizações das quais ele participa."""
    me = _get("/user", token=token).json()
    orgs = _get("/user/orgs", token=token, per_page=100).json()

    accounts = [{"login": me["login"], "type": "Usuário"}]
    accounts += [{"login": o["login"], "type": "Organização"} for o in orgs]
    return accounts


def list_repos(login, is_user, token=None, limit=100):
    """Repositórios da conta, do mais recentemente atualizado ao mais antigo."""
    if token and is_user:
        path, extra = "/user/repos", {"affiliation": "owner"}
    elif token:
        path, extra = f"/orgs/{login}/repos", {"type": "all"}
    else:
        path, extra = f"/users/{login}/repos", {}   # sem token: só repositórios públicos

    data = _get(path, token=token, sort="pushed", direction="desc",
                per_page=limit, **extra).json()

    return [
        {
            "full_name": r["full_name"],
            "private": r["private"],
            "description": r.get("description"),
            "language": r.get("language") or "—",
            "pushed_at": r.get("pushed_at"),
        }
        for r in data
    ]


def fetch_repo_stats(full_name, token=None):
    owner, repo = full_name.split("/", 1)
    try:
        return {
            "commits": _count(f"/repos/{owner}/{repo}/commits", token=token),
            "contributors": _count(f"/repos/{owner}/{repo}/contributors", token=token),
        }
    except (ValueError, requests.RequestException):
        return {"commits": None, "contributors": None}


def fetch_many_stats(full_names, token=None, workers=8):
    with ThreadPoolExecutor(max_workers=workers) as pool:
        results = list(pool.map(lambda n: fetch_repo_stats(n, token), full_names))
    return dict(zip(full_names, results))

def fetch_repo_info(url, token=None):
    owner, repo = parse_repo_url(url)
    return fetch_repo_stats(f"{owner}/{repo}", token)