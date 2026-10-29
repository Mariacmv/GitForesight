
import pandas as pd

from backend.app.risk import score_risk
from frontend.dashboard.paths import DATA_DIR

analysis = pd.read_csv(DATA_DIR / "analysis.csv")
result = score_risk(analysis)

risk_atual = pd.read_csv(DATA_DIR / "risk.csv")

comparacao = pd.DataFrame({
    "score_atual": risk_atual["risk_score"],
    "score_calculado": result["risk_score"],
})

print(comparacao)
print("\nDiferenças:")
print(
    (
        comparacao["score_atual"]
        - comparacao["score_calculado"]
    ).abs()
)
