import pandas as pd


def normalize(series):
    minimum = series.min()
    maximum = series.max()

    if maximum == minimum:
        return pd.Series(0, index=series.index)

    return (series - minimum) / (maximum - minimum)


def calculate_risk(input_path="data/analysis.csv",
                   output_path="data/risk.csv"):

    df = pd.read_csv(input_path)

    if df.empty:
        raise ValueError("A análise está vazia.")

    # Normalização dos indicadores
    df["changes_score"] = normalize(df["total_changes"])
    df["files_score"] = normalize(df["avg_files_per_commit"])
    df["security_score"] = normalize(df["security_files_changed"])
    df["contributors_score"] = normalize(df["contributors"])

    # Score de risco heurístico
    df["risk_score"] = (
        df["changes_score"] * 0.30
        + df["files_score"] * 0.20
        + df["security_score"] * 0.40
        + df["contributors_score"] * 0.10
    ) * 100

    df["risk_score"] = df["risk_score"].round(2)

    df.to_csv(
        output_path,
        index=False,
        encoding="utf-8"
    )

    return df