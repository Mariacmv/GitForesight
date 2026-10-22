
import streamlit as st

from cryptography.fernet import Fernet
from backend.database.connection import get_connection


def _fernet():
    chave = st.secrets["GITHUB_TOKEN_ENCRYPTION_KEY"]
    return Fernet(chave.encode("utf-8"))


def salvar_token_github(user_id, token):
    criptografado = _fernet().encrypt(
        token.encode("utf-8")
    ).decode("utf-8")

    with get_connection() as con:
        con.execute(
            """
            INSERT INTO github_oauth_tokens
                (user_id, encrypted_token, updated_at)
            VALUES (?, ?, CURRENT_TIMESTAMP)
            ON CONFLICT(user_id) DO UPDATE SET
                encrypted_token = excluded.encrypted_token,
                updated_at = CURRENT_TIMESTAMP
            """,
            (user_id, criptografado),
        )


def obter_token_github(user_id):
    with get_connection() as con:
        row = con.execute(
            """
            SELECT encrypted_token
            FROM github_oauth_tokens
            WHERE user_id = ?
            """,
            (user_id,),
        ).fetchone()
    print("DEBUG — Credencial encontrada no banco:", row is not None)

    if row is None:
        return None

    try:
        token = _fernet().decrypt(
            row["encrypted_token"].encode("utf-8")
        )
        return token.decode("utf-8")
    except Exception:
        # Não utiliza credenciais que não podem ser descriptografadas.
        return None
