from backend.app.heatmap_data import build_heatmap
from frontend.dashboard.paths import DATA_DIR

items = build_heatmap(DATA_DIR)

print(f"Arquivos analisados: {len(items)}")

if items:
    print("Chaves disponíveis:", items[0].keys())
    print("Primeiro item:", items[0])

for item in items:
    print("-" * 60)
    print("Arquivo:", item["path"])
    print("Score:", item["score"])
    print("Commits:", item["commits"])
    print("Linhas alteradas:", item["linhas"])
    print("Inserções:", item["insercoes"])
    print("Exclusões:", item["exclusoes"])
    print("Contribuidores:", item["contribuidores"])
    print("Sensível:", item["sensivel"])
    print("Fatores:", item["fatores"])