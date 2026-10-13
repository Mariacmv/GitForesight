
import pandas as pd

from backend.app.risk import calculate_risk

# Executa novamente o cálculo com a fórmula atual
risk = calculate_risk(
    input_path="data/analysis.csv",
    output_path="data/risk.csv"
)

# Resultados esperados calculados independentemente
expected = pd.DataFrame({
    "week": ["2025-06-09", "2025-06-16"],
    "risk_score": [74.94, 46.90]
})

result = risk[["week", "risk_score"]]

comparison = result.merge(
    expected,
    on="week",
    suffixes=("_obtido", "_esperado"),
    validate="one_to_one"
)

comparison["correto"] = (
    comparison["risk_score_obtido"]
    .sub(comparison["risk_score_esperado"])
    .abs()
    .le(0.01)
)

print("\nVALIDAÇÃO DO RISK SCORE")
print(comparison.to_string(index=False))

assert len(comparison) == len(expected)
assert comparison["correto"].all(), "Erro no cálculo de risco!"

print("\nTodos os cálculos foram validados.")
