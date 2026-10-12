import pandas as pd

import backend.app.simulation as sim

df = sim.prepare(pd.read_csv("data/file_changes.csv"))

print("Pessoas:", df["person"].nunique())
print()
print(sim.simulate_all(df).to_string())
print()

print("Pesos em game/views.py:")
print(df[df["path"] == "game/views.py"].groupby("person")["weight"].sum())
print()

for t in (0.7, 0.8, 0.9):
    sim.ORPHAN_THRESHOLD = t
    print("Limite", t)
    print(sim.simulate_all(df)[["pessoa", "arquivos_sem_segundo_mantenedor", "risco"]].to_string(index=False))
    print()