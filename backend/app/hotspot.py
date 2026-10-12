
import pandas as pd

from backend.app.simulation import prepare


HOTSPOT_WEIGHTS = {
    "frequency": 0.50,
    "churn": 0.35,
    "security": 0.15,
}

HOTSPOT_THRESHOLD = 60


def calculate_hotspots(file_changes):
    """
    Identifica arquivos com maior exposição histórica.

    Recebe o dataframe de file_changes.csv.
    Retorna um ranking por arquivo.
    """

    # Reutiliza o tratamento já existente:
    # aliases, renomeações, exclusões e pastas ignoradas.
    df = prepare(file_changes)

    if df.empty:
        return pd.DataFrame()

    # Agrupa o histórico por arquivo
    hotspots = df.groupby("path").agg(
        module=("module", "last"),
        commits=("hash", "nunique"),
        total_changes=("changes", "sum"),
        insertions=("insertions", "sum"),
        deletions=("deletions", "sum"),
        contributors=("person", "nunique"),
        is_security=("is_security", "max")
    ).reset_index()

    # Normalização relativa ao repositório
    max_commits = hotspots["commits"].max()
    max_changes = hotspots["total_changes"].max()

    hotspots["frequency_score"] = (
        hotspots["commits"] / max_commits
        if max_commits > 0 else 0
    )

    hotspots["churn_score"] = (
        hotspots["total_changes"] / max_changes
        if max_changes > 0 else 0
    )

    hotspots["security_score"] = (
        hotspots["is_security"].astype(int)
    )

    # Cálculo do Hotspot Score
    hotspots["hotspot_score"] = (
        hotspots["frequency_score"] * HOTSPOT_WEIGHTS["frequency"]
        + hotspots["churn_score"] * HOTSPOT_WEIGHTS["churn"]
        + hotspots["security_score"] * HOTSPOT_WEIGHTS["security"]
    ) * 100

    hotspots["hotspot_score"] = (
        hotspots["hotspot_score"].round(2)
    )

    # Critério inicial para hotspot:
    # score >= 60 e pelo menos 2 commits distintos.
    hotspots["is_hotspot"] = (
        (hotspots["hotspot_score"] >= HOTSPOT_THRESHOLD)
        & (hotspots["commits"] >= 2)
    )

    return hotspots.sort_values(
        "hotspot_score",
        ascending=False
    ).reset_index(drop=True)
