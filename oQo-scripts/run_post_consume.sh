#!/usr/bin/env bash
# ^-- on passe en bash pour garder "source" et l’expansion ||=

set -euo pipefail

# dossier du script
SCRIPT_DIR="$(cd -- "$(dirname -- "$0")" && pwd)"

# 1. Charger .env (chemin absolu évite les surprises)
if [[ -f "$SCRIPT_DIR/.env" ]]; then
  set -a           # exporte automatiquement les variables lues
  source "$SCRIPT_DIR/.env"
  set +a
fi

# 2. Activer le virtual-env **si vous en avez vraiment besoin**
if [[ -f "$INCLUDE_PATH/script-venv/bin/activate" ]]; then
  source "$INCLUDE_PATH/script-venv/bin/activate"
fi

# 3. Paramètres fournis par Paperless
DOC_ID="$1"              # premier argument
# (doc_title="$2", file_path="$3", … si vous voulez les autres)

# 4. PYTHONPATH pour votre code
export PYTHONPATH="$SCRIPT_DIR/src:${PYTHONPATH:-}"

# 5. Exécution de votre hook Python
exec python3 "$SCRIPT_DIR/src/webhook_paperless.py" "$DOC_ID"
