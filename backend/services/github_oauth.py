import requests, secrets, base64, hashlib
import streamlit as st
from urllib.parse import urlencode

def trocar_codigo_por_token(code, code_verifier=None):
    """
        Redirecionamento ao github, implementação do PKCE (mecanismo de proteção do fluxo OAuth)
        Realiza-se a requisição, identifica erros HTTP, como 400 ou 500, transforma a resposta JSON em um dicionário python
        Retorna o token 
    """
    
    dados = {
        "client_id": st.secrets["GITHUB_CLIENT_ID"],
        "client_secret": st.secrets["GITHUB_CLIENT_SECRET"],
        "code": code,
        "redirect_uri": st.secrets["GITHUB_REDIRECT_URI"],
    }

    if code_verifier:
        dados["code_verifier"] = code_verifier
        
    resposta = requests.post(
        "https://github.com/login/oauth/access_token",
        headers={"Accept": "application/json"},
        data=dados,
        timeout=15
    )
    
    resposta.raise_for_status()
    resultado = resposta.json()
    
    if "access_token" not in resultado:
        raise ValueError("Não foi possível obter o token do GitHub.")
    
    return resultado["access_token"]

def buscar_usuario_github(token):
    """
        Faz uma requisição GET para consultar informações do endpoint /user
        Define a autorização passando o token no cabeçalho 
        Confere se houve um erro HTTP
    """
    
    resposta = requests.get(
        "https://api.github.com/user",
        headers={
            "Authorization": f"Bearer {token}",
            "Accept": "application/vnd.github+json",
        },
        timeout=15
    )
    
    resposta.raise_for_status()
    return resposta.json()

def github_login_url(state, code_challenge=None):
    """
        Constrói o endereço em que o usuário será redirecionado
        state define se o retorno recebido do github foi tentativa de autenticação do gitforesight
    """
    
    parametros = {
        "client_id": st.secrets["GITHUB_CLIENT_ID"],
        "redirect_uri": st.secrets["GITHUB_REDIRECT_URI"],
        "state": state,
    }
    
    if code_challenge:
        parametros["code_challenge"] = code_challenge
        parametros["code_challenge_method"] = "S256"
        
    return (
        "https://github.com/login/oauth/authorize?"
        + urlencode(parametros)
    )
    
def gerar_pkce():
    """
        verifier é o valor secreto gerado pela aplicação
        challenge é o valor que deriva do verifier
    """
    verifier = secrets.token_urlsafe(64)
    digest = hashlib.sha256(
        verifier.encode("ascii")
    ).digest()
    
    challenge = base64.urlsafe_b64encode(
        digest
    ).decode("ascii").rstrip("=")
    
    return verifier, challenge