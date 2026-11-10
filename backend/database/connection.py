import sqlite3
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parents[2]
DB_PATH = BASE_DIR / "data" / "gitforesight.db" 

def get_connection():
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)

    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")

    return conn


def init_db():
    with get_connection() as con:
        con.executescript("""
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                email TEXT UNIQUE,
                password_hash TEXT
            );

            CREATE TABLE IF NOT EXISTS tokens (
                token_hash TEXT PRIMARY KEY,
                user_id INTEGER NOT NULL,
                kind TEXT NOT NULL,
                expires_at TEXT NOT NULL,

                FOREIGN KEY (user_id) REFERENCES users(id)
            );

            CREATE TABLE IF NOT EXISTS repositories (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                name TEXT NOT NULL,
                url TEXT NOT NULL,
                connected_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

                FOREIGN KEY (user_id) REFERENCES users(id),
                UNIQUE(user_id, url)
            );
            
            CREATE TABLE IF NOT EXISTS repository_settings (
                repository_id INTEGER PRIMARY KEY,

                ignored_directories TEXT NOT NULL DEFAULT
                    'node_modules/, .venv/, dist/',

                analyze_on_commit INTEGER NOT NULL DEFAULT 1,
                scan_frequency TEXT NOT NULL DEFAULT 'Diariamente',
                scan_time TEXT NOT NULL DEFAULT '02:00',

                scan_dependencies INTEGER NOT NULL DEFAULT 1,
                update_ai_projections INTEGER NOT NULL DEFAULT 1,

                notify_critical INTEGER NOT NULL DEFAULT 1,
                notify_score_increase INTEGER NOT NULL DEFAULT 1,
                notify_weekly_summary INTEGER NOT NULL DEFAULT 1,
                notify_no_alerts INTEGER NOT NULL DEFAULT 0,

                updated_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,

                FOREIGN KEY (repository_id)
                    REFERENCES repositories(id)
                    ON DELETE CASCADE
            );
            
            CREATE TABLE IF NOT EXISTS github_accounts (
                github_id INTEGER PRIMARY KEY,
                user_id INTEGER NOT NULL UNIQUE,
                github_login TEXT NOT NULL,
                connected_at TEXT DEFAULT CURRENT_TIMESTAMP,

                FOREIGN KEY (user_id)
                    REFERENCES users(id)
                    ON DELETE CASCADE
            );
            
            CREATE TABLE IF NOT EXISTS oauth_attempts (
                state_hash TEXT PRIMARY KEY,
                code_verifier TEXT NOT NULL,
                expires_at INTEGER NOT NULL
            );
            
            CREATE TABLE IF NOT EXISTS github_installations (
                installation_id INTEGER PRIMARY KEY,
                user_id INTEGER NOT NULL,
                account_id INTEGER NOT NULL,
                account_login TEXT NOT NULL,
                account_type TEXT NOT NULL,
                connected_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,

                FOREIGN KEY (user_id)
                    REFERENCES users(id)
                    ON DELETE CASCADE
            );
            
            CREATE TABLE IF NOT EXISTS github_oauth_tokens (
                user_id INTEGER PRIMARY KEY,
                encrypted_token TEXT NOT NULL,
                updated_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,

                FOREIGN KEY (user_id)
                    REFERENCES users(id)
                    ON DELETE CASCADE
            );
            CREATE TABLE IF NOT EXISTS billing_subscriptions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,

                user_id INTEGER NOT NULL UNIQUE,

                stripe_customer_id TEXT UNIQUE,
                stripe_subscription_id TEXT UNIQUE,

                plan_key TEXT NOT NULL DEFAULT 'explorar',
                price_id TEXT,

                status TEXT NOT NULL DEFAULT 'inactive',

                current_period_start TEXT,
                current_period_end TEXT,

                cancel_at_period_end INTEGER NOT NULL DEFAULT 0,

                created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
                updated_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,

                FOREIGN KEY (user_id)
                    REFERENCES users(id)
                    ON DELETE CASCADE
            );
        """)
        colunas = {
            row["name"]
            for row in con.execute("PRAGMA table_info(repositories)")
        }

        if "selected_branch" not in colunas:
            con.execute(
                "ALTER TABLE repositories ADD COLUMN selected_branch TEXT"
            )

        if "last_analysis_at" not in colunas:
            con.execute(
                "ALTER TABLE repositories ADD COLUMN last_analysis_at TEXT"
            )

if __name__ == "__main__":
    print("Criando o banco de dados e as tabelas...")
    init_db()
    print("Banco de dados inicializado com sucesso em:", DB_PATH)