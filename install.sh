---

**install.sh**

```bash
#!/bin/bash
# install.sh - Install Commit Reporter CLI
# This script checks for Poetry, creates a default .env file at the project root if needed,
# and installs project dependencies using Poetry.

set -e

# Define ANSI colour codes for pretty-printing
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'  # No Colour

# Function: pretty_print
pretty_print() {
    local message="$1"
    echo -e "${GREEN}============================================${NC}"
    echo -e "${GREEN}$message${NC}"
    echo -e "${GREEN}============================================${NC}"
}

pretty_print "Welcome to Commit Reporter CLI Installer"

echo -e "${YELLOW}Checking for Poetry...${NC}"
if ! command -v poetry >/dev/null 2>&1; then
    echo -e "${RED}ERROR: Poetry not found. Please install Poetry from https://python-poetry.org/docs/#installation${NC}"
    exit 1
fi
echo -e "${GREEN}Poetry is installed.${NC}"

# Assume the project root is the directory where this script resides.
project_root="$(dirname "$0")"
pretty_print "Project root detected at: $project_root"

# Ensure the .env file exists at the project root.
env_file="$project_root/.env"
pretty_print "Checking for .env file at the project root"
if [ ! -f "$env_file" ]; then
    cat <<EOF > "$env_file"
# OpenAI API key: Replace 'your_openai_api_key_here' with your actual key.
OPENAI_API_KEY=your_openai_api_key_here
EOF
    pretty_print ".env file created at $env_file. Please update OPENAI_API_KEY."
else
    pretty_print ".env file already exists at $env_file. Skipping creation."
fi

pretty_print "Installing project dependencies using Poetry"
cd "$project_root"
poetry install

pretty_print "Installation complete. Enjoy using Commit Reporter CLI!"