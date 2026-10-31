
import pandas as pd

from backend.app.predictive import build_predictive, calculate_scenario_score, simulate_projection
from frontend.dashboard.paths import DATA_DIR

analysis = pd.read_csv(DATA_DIR / "analysis.csv")
risk = pd.read_csv(DATA_DIR / "risk.csv")

resultado = build_predictive(analysis, risk)

print("STATUS:", resultado["status"])

if resultado["status"] == "ok":
    print("\nRISCO ATUAL:")
    print(resultado["current"])

    print("\nHISTÓRICO:")
    print(resultado["history"][["week", "commits", "risk_score"]])

    print("\nTENDÊNCIAS:")
    for tendencia in resultado["trends"]:
        print("-", tendencia)

    print("\nPROJEÇÃO:", resultado["projection"])

else:
    print("MENSAGEM:", resultado["message"])

score = calculate_scenario_score(
    total_changes=156,
    avg_files_per_commit=7.5,
    security_files_changed=1,
)

print("\nSCORE DO CENÁRIO:", score)

projection = simulate_projection(risk)

print("\nPROJEÇÃO:")
print(projection.to_string(index=False))

print("\nÚLTIMA SEMANA:")
print(
    risk.sort_values("week").iloc[-1][[
        "week",
        "commits",
        "total_changes",
        "avg_files_per_commit",
        "security_files_changed",
        "risk_score",
    ]]
)