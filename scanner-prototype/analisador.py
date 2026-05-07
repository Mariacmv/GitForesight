import subprocess as s
import os

#PARA FUNCIONAR É NECESSÁRIO PASSAR ESSE ARQUIVO PARA O HOOK
#para remover a adição do arquivo: git reset nome_arquivo
#1- identificar os arquivos para commit
#executar o comando git diff --cached --name-only para descobrir quais arquivos estão sendo enviados para commit
#o comando diff mostra alterações realizadas em um arquivo ou pasta

#sintaxe comando para visualizar arquivos adicionados: check_output(["programa", "arg1", "arg2", "arg3"]) em lista para separar comandos de argumentos

#pegar arquivos para commit
arquivos = s.check_output(
    ["git", "diff", "--cached", "--name-only"], #programa, arg1, arg2, arg3
    text=True
)

#print(arquivos) #ok
#armazená-los em uma lista
listaArquivos = arquivos.splitlines() #não usa list porque essa quebra em caracteres

#print(listaArquivos)

#2- identificar a extensão do arquivo 
extensoes = { #dicionário com extensões analisadas
    ".txt":{"tipo":"texto", "analisar":True},
    ".env":{"tipo":"sensível", "analisar":True},
    ".json":{"tipo":"json", "analisar":True},
    ".log":{"tipo":"log", "analisar":True},
    ".py":{"tipo":"código", "analisar":True},
    ".sql":{"tipo":"banco de dados", "analisar":True},
    ".yaml":{"tipo":"config", "analisar":True}
}

s_extensao = []

for arquivo in listaArquivos:
    print(f"Arquivo: {arquivo}")
    extensao = os.path.splitext(arquivo)[1].lower()
    nome_arquivo = os.path.basename(arquivo).lower()
    extensao_especial = os.path.basename(nome_arquivo)
    if extensao in extensoes:
        print(f'Extensão identificada: {extensao}')
        print(f"Extensão do arquivo '{arquivo}' -> {extensao}\n")
    elif nome_arquivo.startswith('.'):
        print(f'Extensão especial identificada: {extensao_especial}')
        print(f"Extensão do arquivo '{arquivo}' -> {extensao_especial}\n")
    elif not extensao:
        s_extensao.append(arquivo)
        print(f'Arquivos sem extensão: {s_extensao}\n')

    
#3- escanear os arquivos
    
    
       
    


