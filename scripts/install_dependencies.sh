#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd -- "${SCRIPT_DIR}/.." && pwd)"
VENV_DIR="${PROJECT_ROOT}/.venv"

say() { printf '[SciAI Wiki] %s\n' "$1"; }

command -v python3 >/dev/null 2>&1 || { say "Error: python3 is required."; exit 1; }
command -v git >/dev/null 2>&1 || { say "Error: git is required."; exit 1; }

python3 -c 'import sys; raise SystemExit(0 if sys.version_info >= (3, 9) else 1)' \
  || { say "Error: Python 3.9 or newer is required."; exit 1; }

if [[ ! -d "${VENV_DIR}" ]]; then
  say "Creating the project virtual environment..."
  python3 -m venv "${VENV_DIR}"
else
  say "Virtual environment already exists; keeping it."
fi

VENV_PYTHON="${VENV_DIR}/bin/python"
"${VENV_PYTHON}" -c 'import yaml' >/dev/null 2>&1 || {
  say "Installing the only runtime dependency (PyYAML)..."
  "${VENV_DIR}/bin/python" -m pip install PyYAML
}

say "Dependencies are ready. Activate with: source \"${VENV_DIR}/bin/activate\""
say "Project root: ${PROJECT_ROOT}"
