from backend.app.collector import collect_commits
from backend.app.dataset import create_dataset
from backend.app.analyzer import analyze_commits
from backend.app.risk import calculate_risk

def main():
    repository_path = input("Caminho do repositório: ").strip()

    print("\n[1/3] Coletando commits...")

    commits = collect_commits(repository_path)

    if not commits:
        print("Nenhum commit encontrado.")
        return

    print(f"Commits encontrados: {len(commits)}")

    print("\n[2/3] Criando dataset...")

    dataframe = create_dataset(commits)

    print(f"Dataset criado: {len(dataframe)} registros")

    print("\n[3/3] Analisando histórico...")

    analysis = analyze_commits()

    print("\nAnálise concluída!")
    print("Arquivo: data/analysis.csv")

    print("\nResultado:")
    print(analysis)

    print("\n[4/4] Calculando Risk Score...")

    risk = calculate_risk()

    print("\nRisk Score calculado!")
    print("Arquivo: data/risk.csv")
    print("\nResultado:")
    print(risk[
        [
            "week",
            "changes_score",
            "files_score",
            "security_score",
            "contributors_score",
            "risk_score"
        ]
    ])


if __name__ == "__main__":
    main()