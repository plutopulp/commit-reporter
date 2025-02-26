import logging
import os
import re
import subprocess
import datetime
from dataclasses import dataclass, field
from typing import List, Optional

import openai
import typer
from dotenv import load_dotenv
from openai import OpenAI

# Load environment variables from .env file.
load_dotenv()

# Retrieve the API key from the environment variables.
openai.api_key = os.getenv("OPENAI_API_KEY")
client = OpenAI()

app = typer.Typer()

# Set up basic logging.
logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")

# Global constants for model and prompt.
MODEL_USED = "gpt-4-turbo"
SYSTEM_PROMPT = (
    "You are an expert software engineer and technical communicator. Your task is to analyze a series of git commit logs "
    "and generate a clear, concise, and insightful summary. Focus on extracting the major changes, key improvements, and any recurring themes. "
    "If multiple repositories or dates are included, group the insights accordingly. Avoid unnecessary low-level details, "
    "and ensure the summary is actionable for both technical and business audiences."
)
USER_PROMPT = (
    "Please summarize the following commit logs:\n\n{commit_text}\n\n"
    "The summary should include an overall overview and a bullet-point list of key changes, highlighting new features, bug fixes, "
    "refactorings, and any breaking changes."
)
# Combined prompt text for metadata output.
PROMPT_USED_FOR_OUTPUT = f"System Prompt: {SYSTEM_PROMPT}\n\nUser Prompt: {USER_PROMPT}"

# Custom exceptions for Git-related errors.
class GitRepoError(Exception):
    """Raised when a Git repository is not found or accessible."""
    pass

class CommitExtractionError(Exception):
    """Raised when there is an error extracting commit data."""
    pass

# Dataclasses to structure commit and repository data.
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

def find_git_repos(directory: str) -> List[str]:
    """
    Recursively search for Git repositories within the given directory.
    A repository is detected if a folder contains a '.git' subdirectory.
    """
    repos = []
    for root, dirs, _ in os.walk(directory):
        if ".git" in dirs:
            repos.append(root)
            # Skip subdirectories within the repository.
            dirs[:] = []
    if not repos:
        logging.warning(f"No Git repositories found in {directory}")
    return repos

def extract_commits(repo_path: str, authors: Optional[List[str]] = None) -> List[Commit]:
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
        raise CommitExtractionError(
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

def process_directories(directories: List[str], authors: Optional[List[str]] = None) -> List[Repository]:
    """
    Process a list of directories, extract commit logs from all found Git repositories,
    and structure them into Repository objects.
    """
    repositories = []
    for directory in directories:
        repos = find_git_repos(directory)
        for repo_path in repos:
            try:
                commits = extract_commits(repo_path, authors)
                repositories.append(Repository(path=repo_path, commits=commits))
            except CommitExtractionError as ce:
                logging.error(ce)
    return repositories

def summarize_commits(commit_text: str) -> str:
    """
    Query an OpenAI model to summarize the essential points from commit logs.
    """
    try:
        response = client.chat.completions.create(
            model=MODEL_USED,
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": USER_PROMPT.format(commit_text=commit_text)},
            ],
            temperature=0.5,
            max_tokens=500,
        )
        summary = response.choices[0].message.content
        return summary
    except Exception as e:
        logging.error(f"Failed to summarize commit logs: {e}")
        return "Summary unavailable."

@app.command()
def main(
    directories: List[str] = typer.Argument(..., help="Directories to search for Git repositories."),
    authors: List[str] = typer.Option(None, "--author", "-a", help="Filter commits by author names (can specify multiple)."),
    summarize: bool = typer.Option(False, "--summarize", "-s", help="Summarize the extracted commit logs using OpenAI."),
):
    """
    Extract commit logs from Git repositories in the given directories and optionally summarize them.
    """
    repositories = process_directories(directories, authors)

    # Set up file organization under a dedicated directory (commit_reports).
    base_dir = os.path.join(os.getcwd(), "commit_reports")
    os.makedirs(base_dir, exist_ok=True)

    # Get current timestamp for unique run identification.
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")

    # Create a unique run directory under base_dir with timestamp and model info.
    run_dir = os.path.join(base_dir, f"run_{timestamp}_{MODEL_USED}")
    os.makedirs(run_dir, exist_ok=True)

    # Construct output file names.
    commit_info_file = os.path.join(run_dir, f"commit_info_{timestamp}_{MODEL_USED}.txt")
    commit_summary_file = os.path.join(run_dir, f"commit_summary_{timestamp}_{MODEL_USED}.txt")

    # Write commit details to the commit_info file with metadata header.
    with open(commit_info_file, "w") as f:
        f.write(f"Timestamp: {timestamp}\n")
        f.write(f"Model Used: {MODEL_USED}\n")
        f.write("Prompt Used:\n")
        f.write(PROMPT_USED_FOR_OUTPUT + "\n")
        f.write("=" * 80 + "\n\n")
        for repo in repositories:
            f.write(f"Repository: {repo.path}\n")
            for commit in repo.commits:
                f.write(f"{commit.commit_hash} | {commit.author} | {commit.date} | {commit.message}\n")
            f.write("\n")
    logging.info(f"Commit logs written to {commit_info_file}")

    # If summarization is requested, process the commit text and write the summary file.
    if summarize:
        commit_text = ""
        for repo in repositories:
            commit_text += f"Repository: {repo.path}\n"
            for commit in repo.commits:
                commit_text += f"{commit.commit_hash} | {commit.author} | {commit.date} | {commit.message}\n"
            commit_text += "\n"
        summary = summarize_commits(commit_text)
        with open(commit_summary_file, "w") as f:
            f.write(f"Timestamp: {timestamp}\n")
            f.write(f"Model Used: {MODEL_USED}\n")
            f.write("Prompt Used:\n")
            f.write(PROMPT_USED_FOR_OUTPUT + "\n")
            f.write("=" * 80 + "\n\n")
            f.write(summary)
        logging.info(f"Commit summary written to {commit_summary_file}")

if __name__ == "__main__":
    app()