import pandas as pd

# Valores de referência: a partir deles, o indicador conta como "máximo".
# São sugestões minhas. Calibre com repositórios reais.
CAPS = {
    "total_changes": 2000,           # linhas alteradas por semana
    "avg_files_per_commit": 8,       # arquivos por commit
    "security_files_changed": 5,     # alterações em arquivos sensíveis por semana
}

WEIGHTS = {
    "changes_score": 0.35,
    "files_score": 0.25,
    "security_score": 0.40,
}


def scale(series, cap):
    return (series / cap).clip(0, 1)

def score_risk(df):
    """
    Calcula o score de risco a partir dos indicadores agregados.
    Não modifica o DataFrame original.
    """

    result = df.copy()

    result["changes_score"] = scale(
        result["total_changes"],
        CAPS["total_changes"],
    )

    result["files_score"] = scale(
        result["avg_files_per_commit"],
        CAPS["avg_files_per_commit"],
    )

    result["security_score"] = scale(
        result["security_files_changed"],
        CAPS["security_files_changed"],
    )

    result["risk_score"] = (
        sum(
            result[col] * weight
            for col, weight in WEIGHTS.items()
        ) * 100
    ).round(2)

    return result

def calculate_risk(
    input_path="data/analysis.csv",
    output_path="data/risk.csv",
):
    df = pd.read_csv(input_path)

    if df.empty:
        raise ValueError("A análise está vazia.")

    df = score_risk(df)

    df.to_csv(
        output_path,
        index=False,
        encoding="utf-8",
    )

    return df