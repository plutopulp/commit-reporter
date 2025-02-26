import re
import subprocess
from dataclasses import dataclass, field
from typing import List, Optional


@dataclass
class Commit:
    commit_hash: str
    author: str
    date: str
    message: str


@dataclass
class Repository:
    path: str
    commits: List[Commit] = field(default_factory=list)


def extract_commits(
    repo_path: str, authors: Optional[List[str]] = None
) -> List[Commit]:
    """
    Extract commit logs from a Git repository.
    Optionally filter commits by a list of author names.
    """
    cmd = ["git", "-C", repo_path, "log", "--pretty=format:%h | %an | %ad | %s"]
    if authors:
        author_pattern = r"\|".join(re.escape(author) for author in authors)
        cmd.extend(["--author", author_pattern])
    try:
        output = subprocess.check_output(
            cmd, universal_newlines=True, stderr=subprocess.STDOUT
        )
    except subprocess.CalledProcessError as e:
        raise Exception(
            f"Failed to extract commits for repo {repo_path}. Error: {e.output}"
        )

    commits = []
    if output:
        for line in output.splitlines():
            parts = line.split(" | ")
            if len(parts) >= 4:
                commit_hash = parts[0]
                author = parts[1]
                date = parts[2]
                message = " | ".join(parts[3:])
                commits.append(Commit(commit_hash, author, date, message))
    return commits
