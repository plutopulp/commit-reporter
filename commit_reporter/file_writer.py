import datetime
import os


def create_run_directory(base_dir: str, repo_name: str) -> tuple[str, str]:
    """
    Create a unique run directory under the given base directory using a
    human-readable timestamp and repo name.
    Returns the run directory path and the timestamp.
    """
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    run_dir = os.path.join(base_dir, f"run_{repo_name}_{timestamp}")
    os.makedirs(run_dir, exist_ok=True)
    return run_dir, timestamp


def write_file_with_metadata(file_path: str, header: str, content: str):
    """
    Write content to a file preceded by a header.
    """
    with open(file_path, "w") as f:
        f.write(header)
        f.write(content)
