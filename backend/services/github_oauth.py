import secrets, base64, hashlib
from urllib.parse import urlencode

import streamlit as st


def github_login_url(state, code_challenge=None):
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
    verifier = secrets.token_urlsafe(64)

    digest = hashlib.sha256(
        verifier.encode("ascii")
    ).digest()

    challenge = base64.urlsafe_b64encode(
        digest
    ).decode("ascii").rstrip("=")

    return verifier, challenge

    