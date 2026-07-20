#!/usr/bin/env bash
# ╔══════════════════════════════════════════════════════════════╗
# ║  WM Project Launcher                                        ║
# ║  Because the boring part should take 10 seconds, not 10 min ║
# ╚══════════════════════════════════════════════════════════════╝
#
# PACKAGE MANAGER: uv ONLY. Do not replace with plain pip/pip3 for installs.
# - Uses the project .venv via `uv pip install --python "$VENV_DIR/bin/python"`.
# - Re-running this script refreshes editable installs; it does not reinstall
#   system Python or global toolchains.
#
set -euo pipefail

SCRIPT_DIR="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
WM_NOTECARDS_DIR="$SCRIPT_DIR"
CURRENT_WORKSPACE="$(pwd)"

# ── Colors ──
CYAN='\033[0;36m'
GOLD='\033[0;33m'
GREEN='\033[0;32m'
DIM='\033[2m'
BOLD='\033[1m'
NC='\033[0m'

banner() {
    echo ""
    echo -e "${CYAN}${BOLD}  ┌─────────────────────────────────────┐${NC}"
    echo -e "${CYAN}${BOLD}  │     WM Notebook Project Setup       │${NC}"
    echo -e "${CYAN}${BOLD}  │     Let's build something good.     │${NC}"
    echo -e "${CYAN}${BOLD}  └─────────────────────────────────────┘${NC}"
    echo ""
}

step() { echo -e "  ${CYAN}▸${NC} $1"; }
done_step() { echo -e "  ${GREEN}✓${NC} $1"; }
warn_step() { echo -e "  ${GOLD}!${NC} $1"; }

# ── Pick workspace ──
banner

echo -e "  ${BOLD}Where does this project live?${NC}"
echo ""
echo -e "  ${DIM}1)${NC} $CURRENT_WORKSPACE"
echo -e "  ${DIM}2)${NC} I'll type a custom path"
echo ""
read -rp "  Pick [1/2]: " workspace_choice

case "$workspace_choice" in
    1) WORKSPACE="$CURRENT_WORKSPACE" ;;
    2) read -rp "  Full path: " WORKSPACE ;;
    *) echo "  Invalid choice."; exit 1 ;;
esac

# ── New or existing? ──
echo ""
echo -e "  ${BOLD}New folder or existing one?${NC}"
echo ""
echo -e "  ${DIM}n)${NC} Create a new project folder"
echo -e "  ${DIM}e)${NC} Use an existing folder"
echo ""
read -rp "  Pick [n/e]: " folder_choice

if [[ "$folder_choice" == "n" || "$folder_choice" == "N" ]]; then
    read -rp "  Project name (spaces OK): " PROJECT_NAME
    PROJECT_DIR="$WORKSPACE/$PROJECT_NAME"
    if [ -d "$PROJECT_DIR" ]; then
        warn_step "Folder already exists: $PROJECT_DIR"
        read -rp "  Continue anyway? [y/n]: " confirm
        [[ "$confirm" != "y" ]] && exit 0
    else
        mkdir -p "$PROJECT_DIR"
        done_step "Created $PROJECT_DIR"
    fi
else
    echo ""
    echo -e "  ${DIM}Folders in $WORKSPACE:${NC}"
    ls -1d "$WORKSPACE"/*/ 2>/dev/null | while read -r d; do
        echo -e "    ${DIM}$(basename "$d")${NC}"
    done
    echo ""
    read -rp "  Folder name: " EXISTING_NAME
    PROJECT_DIR="$WORKSPACE/$EXISTING_NAME"
    if [ ! -d "$PROJECT_DIR" ]; then
        echo "  That folder doesn't exist. Creating it."
        mkdir -p "$PROJECT_DIR"
    fi
fi

KERNEL_NAME="$(basename "$PROJECT_DIR" | tr ' ' '-' | tr '[:upper:]' '[:lower:]')"
KERNEL_DISPLAY="$(basename "$PROJECT_DIR")"
VENV_DIR="$PROJECT_DIR/.venv"

echo ""
echo -e "  ${BOLD}Setting up:${NC} $PROJECT_DIR"
echo -e "  ${DIM}Kernel:${NC}     Python ($KERNEL_DISPLAY)"
echo ""

# ── 1. Create venv ──
if [ ! -d "$VENV_DIR" ]; then
    step "Creating .venv..."
    uv venv "$VENV_DIR" --quiet 2>/dev/null || uv venv "$VENV_DIR"
    done_step ".venv ready"
else
    done_step ".venv already exists"
fi

export VIRTUAL_ENV="$VENV_DIR"
export PATH="$VENV_DIR/bin:$PATH"
UV_PY="$VENV_DIR/bin/python"

# ── 2. Install wm-notecards ──
step "Installing wm-notecards (uv, project venv)..."
uv pip install --python "$UV_PY" -e "$WM_NOTECARDS_DIR" --quiet
done_step "wm-notecards installed (editable)"

# ── 3. Install project deps ──
if [ -f "$PROJECT_DIR/pyproject.toml" ]; then
    step "Installing project deps from pyproject.toml..."
    uv pip install --python "$UV_PY" -e "$PROJECT_DIR" --quiet
    done_step "Project dependencies installed"
else
    warn_step "No pyproject.toml yet — only wm-notecards installed"
    echo -e "    ${DIM}Create one later, then run: uv pip install -e .${NC}"
fi

# ── 4. Register kernel ──
step "Registering Jupyter kernel..."
if ! "$UV_PY" -c "import ipykernel" 2>/dev/null; then
    uv pip install --python "$UV_PY" ipykernel --quiet
    done_step "ipykernel installed into project venv"
else
    done_step "ipykernel already present — skipping reinstall"
fi
"$UV_PY" -m ipykernel install --user --name "$KERNEL_NAME" \
    --display-name "Python ($KERNEL_DISPLAY)" 2>/dev/null
done_step "Kernel registered: Python ($KERNEL_DISPLAY)"

# ── 5. Init git if needed ──
if [ ! -d "$PROJECT_DIR/.git" ]; then
    step "Initializing git..."
    git -C "$PROJECT_DIR" init --quiet
    done_step "Git initialized"
else
    done_step "Git already initialized"
fi

# ── Done ──
echo ""
echo -e "${GREEN}${BOLD}  ┌─────────────────────────────────────┐${NC}"
echo -e "${GREEN}${BOLD}  │          You're ready.               │${NC}"
echo -e "${GREEN}${BOLD}  │                                      │${NC}"
echo -e "${GREEN}${BOLD}  │  Open VSCode → pick the kernel →     │${NC}"
echo -e "${GREEN}${BOLD}  │  start teaching.                     │${NC}"
echo -e "${GREEN}${BOLD}  └─────────────────────────────────────┘${NC}"
echo ""
echo -e "  ${DIM}cd \"$PROJECT_DIR\" && code .${NC}"
echo ""

# Offer to open in VSCode
read -rp "  Open in VSCode now? [y/n]: " open_vscode
if [[ "$open_vscode" == "y" || "$open_vscode" == "Y" ]]; then
    code "$PROJECT_DIR"
fi
