.PHONY: install formatting lint

# Define a variable for the common paths
CODE_PATHS = ./commit_reporter

install:
	./install.sh

formatting:
	poetry run black $(CODE_PATHS) && isort $(CODE_PATHS)

lint:
	poetry run flake8 $(CODE_PATHS)