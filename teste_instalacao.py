from backend.services.github_installation import (
    listar_instalacoes_app,
    listar_repositorios_instalacao,
)

instalacoes = listar_instalacoes_app()

for instalacao in instalacoes:
    print("Conta:", instalacao["account_login"])

    repositorios = listar_repositorios_instalacao(
        instalacao["installation_id"]
    )

    for repo in repositorios:
        print("  →", repo["full_name"])