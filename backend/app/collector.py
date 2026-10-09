from pathlib import Path

from git import Repo


SENSITIVE_FILE_NAMES = {
    ".env",
    ".env.local",
    ".env.production",
    ".env.development",
    "settings.py",
    "config.py",
    "security.py",
    "auth.py",
    "authentication.py",
    "authorization.py",
    "permissions.py",
}

SENSITIVE_DIRECTORIES = {
    "auth",
    "authentication",
    "authorization",
    "security",
    "secrets",
    "credentials",
    "config",
}

SENSITIVE_EXTENSIONS = {
    ".pem",
    ".key",
    ".crt",
    ".p12",
    ".pfx",
    ".conf",
    ".cfg",
}


def collect_commits(repository_path):
    repository = Repo(repository_path)

    commits = []

    for commit in repository.iter_commits():
        files_changed = []
        security_files_changed = 0

        insertions = 0
        deletions = 0

        if commit.parents:
            parent = commit.parents[0]
            diff = parent.diff(commit, create_patch=True)

            for item in diff:
                file_path = item.a_path or item.b_path

                if not file_path:
                    continue

                files_changed.append(file_path)

                path = Path(file_path)
                file_name = path.name.lower()
                extension = path.suffix.lower()

                path_parts = {
                    part.lower()
                    for part in path.parts
                }

                is_sensitive = (
                    file_name in SENSITIVE_FILE_NAMES
                    or extension in SENSITIVE_EXTENSIONS
                    or bool(path_parts & SENSITIVE_DIRECTORIES)
                )

                if is_sensitive:
                    security_files_changed += 1

                try:
                    patch = item.diff.decode(
                        "utf-8",
                        errors="ignore"
                    )

                    for line in patch.splitlines():

                        if line.startswith("+") and not line.startswith("+++"):
                            insertions += 1

                        elif line.startswith("-") and not line.startswith("---"):
                            deletions += 1

                except Exception:
                    pass

        commits.append({
            "hash": commit.hexsha,
            "author": commit.author.name,
            "date": commit.committed_datetime,
            "message": commit.message.strip(),
            "files_changed": files_changed,
            "files_count": len(files_changed),
            "security_files_changed": security_files_changed,
            "insertions": insertions,
            "deletions": deletions,
            "changes": insertions + deletions,
        })

    return commits