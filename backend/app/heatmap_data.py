from pathlib import Path

import numpy as np
import pandas as pd

from backend.app.simulation import prepare

MAX_ARQUIVOS = 15            # mais que isso vira poeira no treemap
COLUNAS_DATA = ("date", "datetime", "timestamp", "committed_at")   # ajuste ao seu CSV


def _norm(serie):
    """Escala logarítmica de 0 a 1, para um arquivo gigante não achatar os demais."""
    s = np.log1p(serie.astype(float))
    topo = s.max()
    return s / topo if topo > 0 else s * 0


def _fatores(linha, limites):
    fatores = []
    if linha["sensivel"]:
        fatores.append({"texto": "Arquivo sensível (segurança) alterado", "nivel": "critico"})
    if linha["linhas"] >= limites["linhas"]:
        fatores.append({"texto": f"{int(linha['linhas'])} linhas alteradas, entre as maiores do repositório",
                        "nivel": "alto"})
    if linha["commits"] >= limites["commits"]:
        fatores.append({"texto": f"Alta frequência de alterações ({int(linha['commits'])} commits)",
                        "nivel": "alto"})
    if linha["contribuidores"] >= max(limites["contribuidores"], 3):
        fatores.append({"texto": f"Muitos contribuidores distintos ({int(linha['contribuidores'])})",
                        "nivel": "medio"})
    return fatores

def is_security(path):
    """Identifica arquivos potencialmente sensíveis pelo caminho."""

    path = str(path).lower().replace("\\", "/")

    indicadores = (
        ".env",
        "settings.py",
        "config.py",
        "secrets",
        "credentials",
        "password",
        "private_key",
        ".pem",
        ".key",
        "auth/",
        "security/",
    )

    return any(indicador in path for indicador in indicadores)

def build_heatmap(data_dir):
    caminho = Path(data_dir) / "file_changes.csv"
    if not caminho.exists():
        return []
    files = pd.read_csv(caminho)
    if files.empty:
        return []

    df = prepare(files)
    if df.empty:
        return []

    col_data = next((c for c in COLUNAS_DATA if c in df.columns), None)
    if col_data:
        df = df.assign(_data=pd.to_datetime(df[col_data], errors="coerce", utc=True))

    agg = df.groupby("path").agg(
        commits=("hash", "nunique"),
        linhas=("changes", "sum"),
        contribuidores=("person", "nunique"),
    )

    sensiveis = set(df.loc[df["is_security"].astype(str).str.lower() == "true", "path"])
    agg["sensivel"] = agg.index.isin(sensiveis)

    # Score 0-100: 50% linhas alteradas, 30% commits, 20% contribuidores (+10 se sensível).
    base = 100 * (0.5 * _norm(agg["linhas"]) + 0.3 * _norm(agg["commits"])
                  + 0.2 * _norm(agg["contribuidores"]))
    agg["score"] = (base + 10 * agg["sensivel"]).clip(upper=100)

    limites = {c: agg[c].quantile(0.9) for c in ("linhas", "commits", "contribuidores")}

    janela, ultimas = None, None
    if col_data:
        validas = df.dropna(subset=["_data"])
        if not validas.empty:
            janela = max(int((validas["_data"].max() - validas["_data"].min()).days), 1)
            ultimas = (validas.sort_values("_data").groupby("path").tail(1).set_index("path"))

    agora = pd.Timestamp.now(tz="UTC")
    itens = []
    for path, r in agg.sort_values("score", ascending=False).head(MAX_ARQUIVOS).iterrows():
        item = {
            "path": str(path),
            "score": float(r["score"]),
            "commits": int(r["commits"]),
            "linhas": int(r["linhas"]),
            "insercoes": int(
                df.loc[df["path"] == path, "insertions"].sum()
            ),
            "exclusoes": int(
                df.loc[df["path"] == path, "deletions"].sum()
            ),
            "contribuidores": int(r["contribuidores"]),
            "sensivel": bool(r["sensivel"]),
            "fatores": _fatores(r, limites),
        }
        if "/" in str(path):
            item["modulo"] = str(path).split("/")[0]
        if janela:
            item["janela_dias"] = janela
        if ultimas is not None and path in ultimas.index:
            u = ultimas.loc[path]
            item["ultima_mod_dias"] = max((agora - u["_data"]).days, 0)
            item["ultima_mod_autor"] = str(u["person"])
        itens.append(item)
    return itens