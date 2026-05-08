import os
import re
import math

print("SCANNER CERTO IMPORTADO", __file__)
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
    print(listaArquivos)
    print(type(listaArquivos))
    relatorios = {}
    erros = {}
    for file in listaArquivos:
        # print('DIRETÓRIO ATUAL')
        # print(os.getcwd())
        
        if not os.path.exists(file): continue
        # Pula caso o arquivo for deletado
    
        relatorio = {}

        try:
            print(f'Arquivo sendo analisado: {file}')
            with open(file, 'r', errors='ignore') as f:
                for i, linha in enumerate(f, 1):
                    # Busca de regex
                    for tipo, padrao in PADROES.items():
                        if re.search(padrao, linha):
                            print(f'DETECTADO -> {file} | Linha {i}')
                            if i not in relatorio:
                                relatorio[i] = []
                            relatorio[i].append(f"{tipo} detectado")

                    # Busca por entropia
                    palavras = linha.split()
                    for palavra in palavras:
                        if len(palavra) > 16 and entropia(palavra) > 4.5: 
                            # Entropia acima de 4.5 é considerado Chaves, Hashes ou Base64
                            if i not in relatorio:
                                relatorio[i] = []
                                # Adiciona apenas se o Regex já não tiver classificado essa linha para evitar mensagens duplicadas na mesma linha

                            if "Possivel Segredo Ofuscado (Alta Entropia)" not in relatorio[i]:
                                print("Possível Segredo Ofuscado (Alta Entropia)")
                                relatorio[i].append("Possivel Segredo Ofuscado (Alta Entropia)")
            
            # Só imprime se o dicionário do arquivo não estiver vazio
            if relatorio:
                relatorios[file] = relatorio
                
        except Exception as e:
            print(f'ERRO: {e}')
            erros[file] = str(e)
    return relatorios
                
