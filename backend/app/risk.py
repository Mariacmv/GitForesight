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


def calculate_risk(input_path="data/analysis.csv",
                   output_path="data/risk.csv"):

    df = pd.read_csv(input_path)

    if df.empty:
        raise ValueError("A análise está vazia.")

    df["changes_score"] = scale(df["total_changes"], CAPS["total_changes"])
    df["files_score"] = scale(df["avg_files_per_commit"], CAPS["avg_files_per_commit"])
    df["security_score"] = scale(df["security_files_changed"], CAPS["security_files_changed"])

    df["risk_score"] = sum(df[col] * w for col, w in WEIGHTS.items()) * 100
    df["risk_score"] = df["risk_score"].round(2)

    df.to_csv(output_path, index=False, encoding="utf-8")
    return df