import logging
import os

import typer

from .file_writer import create_run_directory, write_file_with_metadata
from .git_utils import Repository, extract_commits
from .settings import settings
from .summariser import summarise_commits

app = typer.Typer()
logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")


@app.command()
def main(
    repository: str = typer.Argument(..., help="Path to the Git repository."),
    authors: list[str] = typer.Option(
        None,
        "--author",
        "-a",
        help="Filter commits by author names (can specify multiple).",
    ),
    summarise: bool = typer.Option(
        False,
        "--summarise",
        "-s",
        help="Summarise the extracted commit logs using OpenAI.",
    ),
):
    """
    Extract commit logs from the specified Git repository and optionally summarise them.
    """
    repo_path = repository
    if not os.path.isdir(os.path.join(repo_path, ".git")):
        typer.echo(
            f"The directory '{repo_path}' does not appear to be a Git repository."
        )
        raise typer.Exit()

    try:
        commits = extract_commits(repo_path, authors)
    except Exception as e:
        typer.echo(f"Error extracting commits: {e}")
        raise typer.Exit()

    repository_obj = Repository(path=repo_path, commits=commits)
    repo_name = os.path.basename(os.path.abspath(repo_path))

    # Define the base output directory: commit_reports/<repo_name>
    base_dir = os.path.join(os.getcwd(), settings.base_output_dir, repo_name)
    os.makedirs(base_dir, exist_ok=True)

    # Create a unique run directory that includes the repo name and a
    # human-readable timestamp.
    run_dir, timestamp = create_run_directory(base_dir, repo_name)

    # Construct commit info content.
    commit_info_content = f"Repository: {repo_path}\n"
    for commit in repository_obj.commits:
        commit_info_content += (
            f"{commit.commit_hash} | {commit.author} "
            f"| {commit.date} | {commit.message}\n"
        )
    commit_info_content += "\n"

    # Define commit info file name (without model details).
    commit_info_file = os.path.join(run_dir, f"commit_info_{timestamp}_{repo_name}.txt")
    header_info = f"Timestamp: {timestamp}\n" + "=" * 80 + "\n\n"
    write_file_with_metadata(commit_info_file, header_info, commit_info_content)
    logging.info(f"Commit logs written to {commit_info_file}")

    if summarise:
        commit_text = commit_info_content
        summary = summarise_commits(commit_text)
        # Define commit summary file name (include model details).
        commit_summary_file = os.path.join(
            run_dir, f"commit_summary_{timestamp}_{repo_name}_{settings.model_used}.txt"
        )
        header_summary = (
            f"Timestamp: {timestamp}\n"
            f"Model Used: {settings.model_used}\n"
            "Prompt Used:\n"
            f"{settings.system_prompt}\n\n{settings.user_prompt}\n" + "=" * 80 + "\n\n"
        )
        write_file_with_metadata(commit_summary_file, header_summary, summary)
        logging.info(f"Commit summary written to {commit_summary_file}")


if __name__ == "__main__":
    app()
