import pandas as pd


def analyze_commits(input_path="data/commits.csv",
                    output_path="data/analysis.csv"):

    df = pd.read_csv(input_path)

    if df.empty:
        raise ValueError("O dataset está vazio.")

    # Converte a coluna de data
    df["date"] = pd.to_datetime(df["date"], utc=True)

    # Ordena cronologicamente
    df = df.sort_values("date")

    # Cria período semanal
    df["week"] = (
        df["date"]
        .dt.tz_localize(None)
        .dt.to_period("W")
        .apply(lambda period: period.start_time)
    )

    # Agrega os commits por semana
    analysis = (
        df.groupby("week")
        .agg(
            commits=("hash", "count"),
            contributors=("author", "nunique"),
            files_changed=("files_count", "sum"),
            insertions=("insertions", "sum"),
            deletions=("deletions", "sum"),
            total_changes=("changes", "sum"),
            security_files_changed=(
                "security_files_changed",
                "sum"
            ),
        )
        .reset_index()
    )

    # Média de alterações por commit
    analysis["avg_changes_per_commit"] = (
        analysis["total_changes"] /
        analysis["commits"]
    )

    # Quantidade média de arquivos modificados por commit
    analysis["avg_files_per_commit"] = (
        analysis["files_changed"] /
        analysis["commits"]
    )

    # Salva o resultado
    analysis.to_csv(
        output_path,
        index=False,
        encoding="utf-8"
    )

    return analysis