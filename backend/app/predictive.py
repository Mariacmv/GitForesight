import pandas as pd


def build_predictive(analysis, risk):
    required = {
        "week",
        "commits",
        "risk_score",
        "contributors",
        "files_changed",
        "total_changes",
        "security_files_changed",
    }

    if risk is None or risk.empty:
        return {
            "status": "insufficient_data",
            "message": "Nenhum histórico de risco disponível.",
        }

    if not required.issubset(risk.columns):
        missing = required - set(risk.columns)

        return {
            "status": "error",
            "message": f"Colunas ausentes no risk.csv: {sorted(missing)}",
        }

    history = risk.copy()

    history["week"] = pd.to_datetime(
        history["week"],
        errors="coerce",
        utc=True,
    )

    numeric_columns = required - {"week"}

    for col in numeric_columns:
        history[col] = pd.to_numeric(
            history[col],
            errors="coerce",
        )

    history = (
        history.dropna(subset=["week", "risk_score"])
        .sort_values("week")
        .drop_duplicates(subset="week", keep="last")
        .reset_index(drop=True)
    )

    if history.empty:
        return {
            "status": "insufficient_data",
            "message": "Não há registros históricos válidos.",
        }

    current = history.iloc[-1]

    total_commits = int(history["commits"].sum())

    previous_score = (
        float(history.iloc[-2]["risk_score"])
        if len(history) >= 2
        else None
    )

    current_score = float(current["risk_score"])

    variation = (
        current_score - previous_score
        if previous_score is not None
        else None
    )

    if variation is None:
        trend_label = "Histórico insuficiente"
    elif variation > 0:
        trend_label = "Alta em relação à semana anterior registrada"
    elif variation < 0:
        trend_label = "Queda em relação à semana anterior registrada"
    else:
        trend_label = "Estabilidade em relação à semana anterior registrada"

    trends = [
        f"{len(history)} semanas com registros de risco.",
        f"{total_commits} commits registrados nas semanas analisadas.",
        f"{int(current['files_changed'])} arquivos alterados na última semana registrada.",
        f"{int(current['security_files_changed'])} arquivos sensíveis alterados na última semana registrada.",
    ]

    return {
        "status": "ok",
        "current": {
            "score": current_score,
            "commits": total_commits,
            "reference_date": current["week"],
            "previous_score": previous_score,
            "variation": variation,
            "trend": trend_label,
        },
        "history": history,
        "projection": None,
        "trends": trends,
        "factors": [],
        "recommendations": [],
        "methodology": {
            "horizon_commits": 50,
            "model": None,
        },
    }