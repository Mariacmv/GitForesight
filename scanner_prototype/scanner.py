import os
import re
import math
from rich import print #lib para colorir texto
#print("SCANNER CERTO IMPORTADO", __file__)
# PADRÕES DE BUSCA - REGEX
# OS valores podem tanto estar entre aspas " " ou sem.
PADROES = {
    "Chave API": r"(?i)(api|key|token|secret|access[_-]?key)\s*[:=]\s*['\"]?[a-zA-Z0-9/+=_-]{3,100}['\"]?",
    "Senha/Password" : r"(?i)(password|passwd|senha|pwd|pass)\s*[:=]\s*['\"]?.+['\"]?",
    "String de Conexão" : r"(mongodb\+srv:\/\/|postgres:\/\/|mysql:\/\/|jdbc:)"
}

# CÁLCULO DE ENTROPIA - Shannon Entropy
def entropia(content):
    if not content: return 0
    prob = [float(content.count(c)) / len(content) for c in dict.fromkeys(list(content))]
    # formula entropia de SHannon
    entropia = - sum([ p * math.log(p,2) for p in prob])
    return entropia

def analisa_arquivos(listaArquivos):
    #print(listaArquivos)
    #print(type(listaArquivos))
    problemas = {}
    erros = {}
    for file in listaArquivos:
        # print(file)
        # print(os.path.exists(file)) 
        
        if not os.path.exists(file): 
            print('Caminho não existe')
            continue
        # Pula caso o arquivo for deletado
    
        problema = []

        try:
            #print(f'Arquivo sendo analisado: {file}')
            with open(file, 'r', errors='ignore') as f:
                for i, linha in enumerate(f, 1):
                    # Busca de regex
                    for tipo, padrao in PADROES.items():
                        if re.search(padrao, linha):
                            estrutura_problema = {
                                "linha": i,
                                "risco": "ALTO",
                                "motivo": f"{tipo} detectado",
                                "conteudo": linha.strip(),
                                "sugestao": "Remova ou proteja o segredo"
                            }
                            problema.append(estrutura_problema)
                            if file not in problema:
                                problema.append(file)
                            problema.append(f"Linha: {i}: {tipo} detectado")

                            print("[red]Problema identificado![/red]")
                            print(f"  Arquivo: {file}")
                            print(f"  Linha: {estrutura_problema['linha']}")
                            print(f"  Risco: {estrutura_problema['risco']}")
                            print()
                            print(f"        {estrutura_problema['conteudo']}")
                            print()
                            print(f"  Motivo: {estrutura_problema['motivo']}")
                            print(f"  Sugestão: ")
                            print(f"  -  {estrutura_problema['sugestao']}")
                            print()
                            print("[red]Commit bloqueado![/red]")
                            print()
                            
                    # Busca por entropia
                    palavras = linha.split()
                    for palavra in palavras:
                        if len(palavra) > 16 and entropia(palavra) > 4.5: 
                            # Entropia acima de 4.5 é considerado Chaves, Hashes ou Base64
                            if file not in problema:
                                problema = []
                                # Adiciona apenas se o Regex já não tiver classificado essa linha para evitar mensagens duplicadas na mesma linha

                            msg = "Possivel Segredo Ofuscado (Alta Entropia)"
                            if msg not in problema:
                                print("Possível Segredo Ofuscado (Alta Entropia)")
                                problema.append(msg)
            
            # Só imprime se o dicionário do arquivo não estiver vazio
            if problema:
                problemas[file] = problema
                
        except Exception as e:
            print(f'ERRO: {e}')
            erros[file] = str(e)
    return problemas
                
