#!/usr/bin/env bash
# Launcher script for PDF to Markdown Desktop App

SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )"
VENV_DIR="$SCRIPT_DIR/venv"

if [ ! -d "$VENV_DIR" ]; then
    echo "Configurando entorno virtual en $VENV_DIR..."
    python3 -m venv "$VENV_DIR"
    "$VENV_DIR/bin/pip" install -r "$SCRIPT_DIR/requirements.txt"
fi

echo "Iniciando PDF to Markdown Converter Desktop App..."
"$VENV_DIR/bin/python" "$SCRIPT_DIR/main.py" "$@"
