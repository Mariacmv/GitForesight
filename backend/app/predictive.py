import pandas as pd
from backend.app.risk import score_risk


def calculate_scenario_score(
    total_changes,
    avg_files_per_commit,
    security_files_changed,
):
    """
    Calcula o risco de um cenário utilizando
    a mesma fórmula do risk.py.
    """

    indicators = pd.DataFrame([{
        "total_changes": total_changes,
        "avg_files_per_commit": avg_files_per_commit,
        "security_files_changed": security_files_changed,
    }])

    result = score_risk(indicators)

    return float(result.iloc[0]["risk_score"])

def calculate_risk_factors(current):
    """
    Identifica os principais fatores que contribuem
    para o score de risco atual do repositório.
    """

    factors = [
        {
            "name": "Volume de alterações",
            "value": float(current["total_changes"]),
            "contribution": min(float(current["total_changes"]) / 2000, 1) * 0.35 * 100,
            "description": "Quantidade total de linhas adicionadas e removidas.",
        },
        {
            "name": "Arquivos por commit",
            "value": float(current["avg_files_per_commit"]),
            "contribution": min(float(current["avg_files_per_commit"]) / 8, 1) * 0.25 * 100,
            "description": "Média de arquivos modificados por commit.",
        },
        {
            "name": "Arquivos sensíveis",
            "value": float(current["security_files_changed"]),
            "contribution": min(float(current["security_files_changed"]) / 5, 1) * 0.40 * 100,
            "description": "Quantidade de arquivos sensíveis alterados.",
        },
    ]

    factors.sort(
        key=lambda factor: factor["contribution"],
        reverse=True,
    )

    for factor in factors:
        factor["contribution"] = round(factor["contribution"], 2)

    return factors


def simulate_projection(history, horizon_commits=50, step=10):
    """
    Simula cenários de risco para diferentes horizontes de commits.

    Continuidade: mantém o score atual.
    Com ações: simula redução de 20% nos indicadores.
    Faixa: testa sensibilidade de -20% a +20% nos indicadores.

    É uma simulação heurística, não uma previsão estatística.
    """

    if history is None or history.empty:
        return pd.DataFrame()

    history = history.sort_values("week").copy()

    required = {
        "week",
        "commits",
        "total_changes",
        "avg_files_per_commit",
        "security_files_changed",
        "risk_score",
    }

    if not required.issubset(history.columns):
        return pd.DataFrame()

    current = history.iloc[-1]

    current_score = float(current["risk_score"])
    current_changes = float(current["total_changes"])
    current_files = float(current["avg_files_per_commit"])
    current_security = float(current["security_files_changed"])

    actions_score = calculate_scenario_score(
        current_changes * 0.8,
        current_files * 0.8,
        current_security * 0.8,
    )

    upper_score = calculate_scenario_score(
        current_changes * 1.2,
        current_files * 1.2,
        current_security * 1.2,
    )

    points = []

    for future_commits in range(0, horizon_commits + 1, step):
        points.append({
            "commits": future_commits,
            "continuidade": current_score,
            "com_acoes": actions_score,
            "faixa_min": min(actions_score, current_score),
            "faixa_max": max(upper_score, current_score),
        })

    return pd.DataFrame(points)




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
        round(current_score - previous_score, 2)
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

    security_count = int(current["security_files_changed"])

    security_label = (
        "arquivo sensível alterado"
        if security_count == 1
        else "arquivos sensíveis alterados"
    )

    trends = [
        f"{len(history)} semanas com registros de risco.",
        f"{total_commits} commits registrados nas semanas analisadas.",
        f"{int(current['files_changed'])} arquivos alterados na última semana registrada.",
        f"{security_count} {security_label} na última semana registrada.",
    ]

    projection = simulate_projection(history)
    factors = calculate_risk_factors(current)

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
        "projection": projection,
        "trends": trends,
        "factors": factors,
        "recommendations": [],
        "recommendations": [],
        "methodology": {
            "horizon_commits": 50,
            "model": None,
        },
    }