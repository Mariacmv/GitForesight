import pandas as pd

from backend.app.predictive import build_predictive
from frontend.dashboard.paths import DATA_DIR


risk = pd.read_csv(DATA_DIR / "risk.csv")

result = build_predictive(
    analysis=None,
    risk=risk,
)

print("Status:", result["status"])

if result["status"] == "ok":
    print("\nDados atuais:")
    print(result["current"])

    print("\nTendências:")
    for trend in result["trends"]:
        print("-", trend)

    print("\nHistórico:")
    print(result["history"][["week", "commits", "risk_score"]])

else:
    print(result["message"])