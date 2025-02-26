# Commit Reporter CLI

Commit Reporter CLI is a command-line tool that extracts commit logs from a specific Git repository and, optionally, generates a summary using OpenAI's API. Reports are organised by run, with output neatly tagged by repository name and a human-readable timestamp.

## Features

- Extract commit logs from a given Git repository.
- Optionally summarise commit logs using an advanced OpenAI model.
- Organised output with run-specific directories and filenames.

## Requirements

- Python 3.13
- [Poetry](https://python-poetry.org/docs/)
- An OpenAI API key (set in a `.env` file)

## Installation

Before installing, ensure you have [Poetry](https://python-poetry.org/docs/#installation) installed.

### Using the Makefile Installer

From the project root, run:

```bash
make install
```

This command will:

1. **Install Project Dependencies:**  
   The installer verifies Poetry is installed and runs `poetry install` to install all required dependencies.

2. **Create a Default `.env` File:**  
   If a `.env` file does not exist at the project root, one will be created with a placeholder for the OpenAI API key.

**Note: After installation, you should update your `.env` file with your actual OpenAI API key.**

## Usage

Run the CLI tool with:

```bash
poetry run python -m commit_reporter.main <repository_path> [--author AUTHOR] [--summarise]
```

For example, to extract commits from a repository at /path/to/repository while filtering by the author “John Doe” and generating a summary:

```bash
poetry run python -m commit_reporter.main /path/to/repository --author "John Doe" --summarise

```

## Configuration

If you wish to customise output directories, prompts, or model details, modify the corresponding settings in commit_reporter/settings.py.
