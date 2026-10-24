from pathlib import Path
import pandas as pd

DATA = Path("data")

arquivos = [
    "commits.csv",
    "file_changes.csv",
    "analysis.csv",
    "risk.csv",
]

for nome in arquivos:
    caminho = DATA / nome

    print(f"\n{'=' * 50}")
    print(nome)

    if not caminho.exists():
        print("ARQUIVO NÃO ENCONTRADO")
        continue

    df = pd.read_csv(caminho)

    print("Linhas:", len(df))
    print("Colunas:", df.columns.tolist())
    print("\nPrimeiros registros:")
    print(df.head(3).to_string(index=False))

    print("\nValores ausentes:")
    print(df.isna().sum().to_string())