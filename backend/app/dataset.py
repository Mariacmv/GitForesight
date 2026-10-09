import pandas as pd
import os

def create_dataset(
    commits,
    output_path="data/commits.csv"
):
    rows = []

    for commit in commits:
        rows.append({
            "hash": commit["hash"],
            "author": commit["author"],
            "date": commit["date"],
            "message": commit["message"],
            "files_count": commit["files_count"],
            "security_files_changed": commit["security_files_changed"],
            "insertions": commit["insertions"],
            "deletions": commit["deletions"],
            "changes": commit["changes"],
        })

    dataframe = pd.DataFrame(rows)

    os.makedirs("data", exist_ok=True)

    dataframe.to_csv(
        output_path,
        index=False,
        encoding="utf-8"
    )

    return dataframe