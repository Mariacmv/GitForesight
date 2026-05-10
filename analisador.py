import subprocess as s
import os
from pprint import pprint #para imprimir dicionários
from scanner_prototype.scanner import analisa_arquivos
import emoji
from rich import print
#PARA FUNCIONAR É NECESSÁRIO PASSAR ESSE ARQUIVO PARA O HOOK
#para remover a adição do arquivo: git reset nome_arquivo
#1- identificar os arquivos para commit
#executar o comando git diff --cached --name-only para descobrir quais arquivos estão sendo enviados para commit
#o comando diff mostra alterações realizadas em um arquivo ou pasta

#sintaxe comando para visualizar arquivos adicionados: check_output(["programa", "arg1", "arg2", "arg3"]) em lista para separar comandos de argumentos

def pegar_arquivos_para_commit():
    #pegar arquivos para commit
    arquivos = s.check_output(
        ["git", "diff", "--cached", "--name-only"], #programa, arg1, arg2, arg3
        text=True
    )

    #print(arquivos) #ok
    #armazená-los em uma lista
    listaArquivos = arquivos.splitlines() #não usa list porque essa quebra em caracteres
    
    arquivosECaminhos = []
    for arquivo in listaArquivos:
        # caminho_arquivo = f'./{arquivo}'
        caminho_arquivo = arquivo.strip()
        arquivosECaminhos.append(caminho_arquivo)
        #print(caminho_arquivo)

    #print(listaArquivos)
    # return listaArquivos
    return arquivosECaminhos

def identifica_extensao(arquivosECaminhos):
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

    s_extensao = {}
    c_extensao = {}
    ext_especial = {}

    #print('Arquivos identificados: ')
    for arquivo in arquivosECaminhos:
        #print(f"Arquivo: {arquivo}")
        extensao = os.path.splitext(arquivo)[1].lower()
        nome_arquivo = os.path.basename(arquivo).lower()
        extensao_especial = os.path.basename(nome_arquivo)
        if extensao in extensoes:
            # print(f'Extensão identificada: {extensao}')
            #print(f"Extensão do arquivo '{arquivo}' -> {extensao}")
            c_extensao[arquivo] = extensao #adiciona nome do arquivo e extensão ao dicionário 
            # print(f'{arquivo} adicionado à c_extensao \n')
        elif nome_arquivo.startswith('.'):
            # print(f'Extensão especial identificada: {extensao_especial}')
            #print(f"Extensão do arquivo '{arquivo}' -> {extensao_especial}")
            ext_especial[arquivo] = extensao_especial
            # print(f'{arquivo} adicionado à ext_especial \n')
        elif not extensao:
            s_extensao[arquivo] = extensao
            # print(f'Arquivos sem extensão: {s_extensao}')
            #print(f'{arquivo} adicionado à s_extensao \n')
        else: continue

    return s_extensao, c_extensao, ext_especial

def emojis():
    lis_emojis = []
    lupa = emoji.emojize(":rocket:")
    xis = emoji.emojize(":cross_mark:")
    atencao = emoji.emojize(":warning:")
    certo = emoji.emojize(":check_mark_button:")
    lis_emojis.append(certo)
    lis_emojis.append(atencao)
    lis_emojis.append(xis)
    lis_emojis.append(lupa)
    
    return lis_emojis

if __name__ == "__main__":
    emoj_lupa = emojis()
    print(f'[yellow]{emoj_lupa[3]} Scanneando arquivos...[/yellow]')
    listaArquivos = pegar_arquivos_para_commit()
    s_extensao, c_extensao, ext_especial = identifica_extensao(listaArquivos)
    
    # print('ARQUIVOS SEM EXTENSÃO\n')
    # pprint(s_extensao, width=1)
    # print()
    # print('ARQUIVOS COM EXTENSÃO\n')
    # pprint(c_extensao, width=1)
    # print()
    # print('ARQUIVOS COM EXTENSÃO ESPECIAL\n')
    # pprint(ext_especial, width=1)
    #print('Importando analisa_arquivos')
    
    relatorio = analisa_arquivos(listaArquivos)
    #print(relatorio)



    
    
       
    


