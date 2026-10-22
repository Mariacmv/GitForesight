import hashlib
import hmac
import secrets
import sqlite3
from datetime import datetime, timedelta, timezone
from pathlib import Path
from backend.database.connection import get_connection

DB_PATH = Path(__file__).resolve().parents[2] / "data" / "users.db"
ITERATIONS = 600_000

def _hash_password(password):
    salt = secrets.token_bytes(16)
    digest = hashlib.pbkdf2_hmac("sha256", password.encode(), salt, ITERATIONS)
    return f"{ITERATIONS}${salt.hex()}${digest.hex()}"


def _check_password(password, stored):
    iterations, salt, digest = stored.split("$")
    test = hashlib.pbkdf2_hmac(
        "sha256", password.encode(), bytes.fromhex(salt), int(iterations)
    )
    return hmac.compare_digest(test.hex(), digest)


def _sha(text):
    return hashlib.sha256(text.encode()).hexdigest()


def _now():
    return datetime.now(timezone.utc)


def create_user(name, email, password):
    try:
        with get_connection() as con:
            cursor = con.execute(
                """
                INSERT INTO users (name, email, password_hash)
                VALUES (?, ?, ?)
                """,
                (
                    name,
                    email.strip().lower(),
                    _hash_password(password)
                )
            )

            return cursor.lastrowid

    except sqlite3.IntegrityError:
        raise ValueError("Já existe uma conta com esse e-mail.")

def verify_user(email, password):
    with get_connection() as con:
        row = con.execute(
            "SELECT * FROM users WHERE email = ?", (email.lower(),)
        ).fetchone()
        
    if row is None or row["password_hash"] is None:
        return None
    if row and _check_password(password, row["password_hash"]):
        return dict(row)
    return None


def _issue_token(user_id, kind, minutes):
    raw = secrets.token_urlsafe(32)
    expires = (_now() + timedelta(minutes=minutes)).isoformat()
    with get_connection() as con:
        con.execute(
            "INSERT INTO tokens VALUES (?, ?, ?, ?)",
            (_sha(raw), user_id, kind, expires),
        )
    return raw


def _find_token(raw, kind, consume):
    with get_connection() as con:
        row = con.execute(
            "SELECT * FROM tokens WHERE token_hash = ? AND kind = ?",
            (_sha(raw), kind),
        ).fetchone()
        if not row or datetime.fromisoformat(row["expires_at"]) < _now():
            return None
        if consume:
            con.execute("DELETE FROM tokens WHERE token_hash = ?", (row["token_hash"],))
        return row["user_id"]


def request_password_reset(email):
    """Devolve o token (a ser ENVIADO POR E-MAIL) ou None se o e-mail não existe."""
    with get_connection() as con:
        row = con.execute(
            "SELECT id FROM users WHERE email = ?", (email.lower(),)
        ).fetchone()
    return _issue_token(row["id"], "reset", 30) if row else None


def reset_password(raw_token, new_password):
    user_id = _find_token(raw_token, "reset", consume=True)
    if user_id is None:
        return False
    with get_connection() as con:
        con.execute(
            "UPDATE users SET password_hash = ? WHERE id = ?",
            (_hash_password(new_password), user_id),
        )
    return True


def issue_remember_token(user_id, days=30):
    return _issue_token(user_id, "remember", days * 24 * 60)


def user_from_remember_token(raw):
    user_id = _find_token(raw, "remember", consume=False)
    if user_id is None:
        return None
    with get_connection() as con:
        row = con.execute("SELECT * FROM users WHERE id = ?", (user_id,)).fetchone()
    return dict(row) if row else None

