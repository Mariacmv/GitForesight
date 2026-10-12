import pandas as pd

from insights import knowledge_concentration
from simulation import prepare, simulate_all

def main():
    file_changes = pd.read_csv("C:\\Users\\maria\\OneDrive\\Área de Trabalho\\GitForesight\\data\\file_changes.csv")

    # Análise de concentração de conhecimento
    resultado = knowledge_concentration(file_changes)

    print("\n=== CONCENTRAÇÃO DE CONHECIMENTO ===")

    for chave, valor in resultado.items():
        print(f"{chave}: {valor}")

    # Simulação de saída dos desenvolvedores
    df = prepare(file_changes)

    simulacoes = simulate_all(df)

    print("\n=== SIMULAÇÃO DE SAÍDA ===")
    print(simulacoes.to_string(index=False))


if __name__ == "__main__":
    main()