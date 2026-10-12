
import pandas as pd

from backend.app.hotspot import calculate_hotspots


files = pd.read_csv("data/file_changes.csv")

hotspots = calculate_hotspots(files)

print("\n===== ANÁLISE DE HOTSPOTS =====\n")

if hotspots.empty:
    print("Nenhum arquivo elegível encontrado.")
else:
    print(
        hotspots[
            [
                "path",
                "commits",
                "total_changes",
                "contributors",
                "is_security",
                "hotspot_score",
                "is_hotspot"
            ]
        ].to_string(index=False)
    )

    print("\n===== RESUMO =====\n")

    print("Arquivos analisados:", len(hotspots))

    print(
        "Hotspots identificados:",
        int(hotspots["is_hotspot"].sum())
    )

    print("\n===== TOP 5 =====\n")

    print(
        hotspots[
            ["path", "hotspot_score"]
        ].head(5).to_string(index=False)
    )
