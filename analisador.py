import subprocess as s
import os
from pprint import pprint #para imprimir dicionários
from scanner_prototype.scanner import analisa_arquivos
import emoji
from scanner_prototype.relatorios import print_relatorios
from rich import print

#PARA FUNCIONAR É NECESSÁRIO PASSAR ESSE ARQUIVO PARA O HOOK
#para remover a adição do arquivo: git reset nome_arquivo
#1- identificar os arquivos para commit
#executar o comando git diff --cached --name-only para descobrir quais arquivos estão sendo enviados para commit
#o comando diff mostra alterações realizadas em um arquivo ou pasta

#sintaxe comando para visualizar arquivos adicionados: check_output(["programa", "arg1", "arg2", "arg3"]) em lista para separar comandos de argumentos

EXTENSOES = { #dicionário com extensões analisadas
    ".txt":{"tipo":"texto", "analisar":True, "peso": 5},
    ".env":{"tipo":"sensível", "analisar":True, "peso":range(30,50)},
    ".json":{"tipo":"json", "analisar":True, "peso":15},
    ".log":{"tipo":"log", "analisar":True, "peso":10},
    ".py":{"tipo":"código", "analisar":True, "peso":(10-20)},
    ".sql":{"tipo":"banco de dados", "analisar":True, "peso":20}, 
    ".yaml":{"tipo":"config", "analisar":True, "peso":30} 
}

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

def identifica_extensao(arquivosECaminhos, EXTENSOES):
    #2- identificar a extensão do arquivo 
    s_extensao = {}
    c_extensao = {}
    ext_especial = {}

    #print('Arquivos identificados: ')
    for arquivo in arquivosECaminhos:
        #print(f"Arquivo: {arquivo}")
        extensao = os.path.splitext(arquivo)[1].lower()
        nome_arquivo = os.path.basename(arquivo).lower()
        extensao_especial = os.path.basename(nome_arquivo)
        if extensao in EXTENSOES:
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
    s_extensao, c_extensao, ext_especial = identifica_extensao(listaArquivos, EXTENSOES)
    
    
    
    eventos, erros = analisa_arquivos(listaArquivos)
    #print(relatorio)
    
    # for file, lista in problemas.items():
    #     for estrutura_problema in lista:
    #         print_relatorios(file, estrutura_problema)

    print_relatorios(eventos)


    
    
       
    


