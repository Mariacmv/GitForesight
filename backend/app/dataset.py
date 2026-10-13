import os

import pandas as pd


def create_dataset(
    commits,
    file_changes=None,
    output_path="data/commits.csv",
    file_changes_path="data/file_changes.csv",
):
    rows = []

    for commit in commits:
        rows.append({
            "hash": commit["hash"],
            "author": commit["author"],
            "email": commit["email"],
            "date": commit["date"],
            "message": commit["message"],
            "files_count": commit["files_count"],
            "security_files_changed": commit["security_files_changed"],
            "insertions": commit["insertions"],
            "deletions": commit["deletions"],
            "changes": commit["changes"],
        })

    dataframe = pd.DataFrame(rows)

    os.makedirs(os.path.dirname(output_path) or ".", exist_ok=True)
    dataframe.to_csv(output_path, index=False, encoding="utf-8")

    if file_changes is not None:
        files_dataframe = pd.DataFrame(file_changes)

        os.makedirs(os.path.dirname(file_changes_path) or ".", exist_ok=True)
        files_dataframe.to_csv(file_changes_path, index=False, encoding="utf-8")

    return dataframe