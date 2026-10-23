from pathlib import Path

import pandas as pd

from backend.app.simulation import prepare


def nivel_risco(score):
    """Mesmas faixas do heatmap (risk_level em components/cards.py). São sugestões."""
    if score >= 40:
        return "CRÍTICO"
    if score >= 20:
        return "ALTO"
    if score >= 8:
        return "MÉDIO"
    if score >= 3:
        return "BAIXO"
    return "SEGURO"


def _ler(caminho):
    return pd.read_csv(caminho) if caminho.exists() else None


def build_summary(data_dir):
    data_dir = Path(data_dir)

    resumo = {
        "score": None,
        "nivel": None,
        "commits": None,
        "contribuidores": None,
        "pessoa": None,
        "participacao": None,
        "arquivos_sensiveis": 0,
        "top_arquivos": [],
    }

    commits = _ler(data_dir / "commits.csv")
    if commits is not None:
        resumo["commits"] = len(commits)

    risk = _ler(data_dir / "risk.csv")
    if risk is not None and not risk.empty:
        score = float(risk.sort_values("week")["risk_score"].iloc[-1])
        resumo["score"] = score
        resumo["nivel"] = nivel_risco(score)

    files = _ler(data_dir / "file_changes.csv")
    if files is None or files.empty:
        return resumo

    df = prepare(files)
    if df.empty:
        return resumo

    resumo["contribuidores"] = int(df["person"].nunique())

    por_pessoa = df.groupby("person")["weight"].sum().sort_values(ascending=False)
    resumo["pessoa"] = str(por_pessoa.index[0])
    resumo["participacao"] = float(por_pessoa.iloc[0] / por_pessoa.sum())

    por_arquivo = (
        df.groupby("path")
        .agg(commits=("hash", "nunique"), linhas=("changes", "sum"))
        .sort_values(["linhas", "commits"], ascending=False)
    )
    resumo["top_arquivos"] = [
        {"path": caminho, "linhas": int(r["linhas"]), "commits": int(r["commits"])}
        for caminho, r in por_arquivo.head(2).iterrows()
    ]

    sensiveis = df[df["is_security"].astype(str).str.lower() == "true"]
    resumo["arquivos_sensiveis"] = int(sensiveis["path"].nunique())

    return resumo