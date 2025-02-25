.PHONY: formatting lint

# Define a variable for the common paths
CODE_PATHS=./commit_digest

formatting:
	poetry run poetry run black $(CODE_PATHS) && isort $(CODE_PATHS)

lint:
	poetry run flake8 $(CODE_PATHS)
