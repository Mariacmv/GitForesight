import os
import re
import math
from rich import print #lib para colorir texto
from scanner_prototype.relatorios import print_relatorios

#print("SCANNER CERTO IMPORTADO", __file__)
# PADRÕES DE BUSCA - REGEX
# OS valores podem tanto estar entre aspas " " ou sem.
PADROES = {
    "Chave API": {
        "regex":r"(?i)(api|key|token|secret|access[_-]?key)\s*[:=]\s*['\"]?[a-zA-Z0-9/+=_-]{3,100}['\"]?",
        "peso":50,
        "risco":"ALTO",
        "descricao":"Possível chave de API exposta",
        "sugestao":"Remova ou proteja o segredo"
    },
    "Senha/Password" : {
        "regex":r"(?i)(password|passwd|senha|pwd|pass)\s*[:=]\s*['\"]?.+['\"]?",
        "peso":40,
        "risco":"ALTO",
        "descricao":"Senha encontrada em arquivo",
        "sugestao":"Remova ou proteja o segredo"
    },
    "String de Conexão" : {
        "regex":r"(mongodb\+srv:\/\/|postgres:\/\/|mysql:\/\/|jdbc:)",
        "peso":60,
        "risco":"CRÍTICO",
        "descricao":"String de conexão exposta",
        "sugestao":"Remova ou proteja o segredo"
    }
}

# CÁLCULO DE ENTROPIA - Shannon Entropy
def entropia(content):
    if not content: return 0
    prob = [float(content.count(c)) / len(content) for c in dict.fromkeys(list(content))]
    # formula entropia de SHannon
    entropia = - sum([ p * math.log(p,2) for p in prob])
    return entropia


def analisa_arquivos(listaArquivos):
    eventos = {}
    erros = {}
    for file in listaArquivos:
        if not os.path.exists(file): 
            print('Caminho não existe')
            continue
        # Pula caso o arquivo for deletado
        evento = []

        try:
            with open(file, 'r', errors='ignore') as f:
                for i, linha in enumerate(f, 1):
                    regex_detectado = False

                    # REGEX
                    for tipo, padrao in PADROES.items():

                        if re.search(padrao["regex"], linha):

                            regex_detectado = True

                            estrutura_evento = {
                                "tipo": tipo,
                                "linha": i,
                                "risco": padrao["risco"],
                                "score": padrao["peso"],
                                "motivo": padrao["descricao"],
                                "conteudo": linha.strip(),
                                "sugestao": padrao["sugestao"]
                            }

                            evento.append(estrutura_evento)

                    # ENTROPIA
                    # se regex já classificou,
                    # não precisa rodar entropia
                    if regex_detectado:
                        continue

                    palavras = linha.split()

                    for palavra in palavras:
                        # PRÉ-FILTROS
                        if len(palavra) < 20:
                            continue

                        # ignora palavras comuns
                        if palavra.isalpha():
                            continue

                        # precisa misturar caracteres
                        tem_numero = any(c.isdigit() for c in palavra)
                        tem_maiuscula = any(c.isupper() for c in palavra)

                        if not (tem_numero and tem_maiuscula):
                            continue

                        # ENTROPIA
                        valor_entropia = entropia(palavra)

                        if valor_entropia > 4.5:

                            estrutura_evento = {
                                "tipo": "Alta Entropia",
                                "linha": i,
                                "risco": "MÉDIO",
                                "score": 30,
                                "motivo": "Possível segredo ofuscado",
                                "conteudo": palavra,
                                "entropia": round(valor_entropia, 2),
                                "sugestao": "Verifique se este valor é um token, chave ou hash"
                            }

                            evento.append(estrutura_evento)
            #print("Resumo da análise")
            # Só imprime se o dicionário do arquivo não estiver vazio
            if evento:
                eventos[file] = evento
                
                
        except Exception as e:
            print(f'ERRO: {e}')
            erros[file] = str(e)
    return eventos, erros
                   #, file, estrutura_evento, palavras
                
