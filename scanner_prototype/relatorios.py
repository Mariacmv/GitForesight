from rich import print
from rich.rule import Rule

def print_relatorios(eventos):
    # print("[red]Problema identificado![/red]")
    # print(f"  Arquivo: {file}")
    # print(f"  Linha: {estrutura_problema['linha']}")
    # print(f"  Risco: {estrutura_problema['risco']}")
    # print()
    # print(f"        {estrutura_problema['conteudo']}")
    # print()
    # print(f"  Motivo: {estrutura_problema['motivo']}")
    # print(f"  Sugestão: ")
    # print(f"  -  {estrutura_problema['sugestao']}")
    # print()
    # print("[red]Commit bloqueado![/red]")
    # print()
    
    for file, lista_eventos in eventos.items():
        print(Rule('[bold][Scanning Files...]'))
        print(f"\nARQUIVO: {file}")

        for evento in lista_eventos:
            print(f"[{evento['risco']}] Linha {evento['linha']}")
            print(f"{evento['conteudo']}")
            print(f"Motivo: {evento['motivo']}")
            print(f"Sugestão:")
            print(f"- {evento['sugestao']}\n")

    print("\n[red]Commit bloqueado![/red]")