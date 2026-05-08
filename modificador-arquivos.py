# PAra fins de teste, modifica os arquivos da pasta adicionando [\n] quebra de linha ao final 
# para eles se tornarem "Modificados" e poderem ser adicionados ao stage "git add".

import os

PASTA_TESTES = "testes"

def adicionar_quebra_de_linha():
    if not os.path.exists(PASTA_TESTES):
        print(f"Erro: A pasta '{PASTA_TESTES}' não foi encontrada.")
        return

    arquivos_modificados = 0
    
    for arquivo in os.listdir(PASTA_TESTES):
        caminho_completo = os.path.join(PASTA_TESTES, arquivo)
        
        # Verifica se é um arquivo (pula subpastas)
        if os.path.isfile(caminho_completo):
            try:
                with open(caminho_completo, 'a', encoding='utf-8') as f:
                    # Adiciona uma quebra de linha ao final do arquivo
                    f.write('\n')
                print(f"Modificado: {arquivo}")
                arquivos_modificados += 1
            except Exception as e:
                print(f"Erro ao modificar {arquivo}: {e}")

    print(f"\nSucesso! {arquivos_modificados} arquivos prontos para o 'git add'.")

if __name__ == "__main__":
    adicionar_quebra_de_linha()
