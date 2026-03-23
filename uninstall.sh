#!/usr/bin/env bash
set -euo pipefail

FISH_FUNCTIONS_DIR="$HOME/.config/fish/functions"
SHARE_DIR="$HOME/.local/share/aury"
AURY_VERSION="$(tr -d '\n' < VERSION 2>/dev/null || true)"

echo ""
echo "🗑 Removendo a Aury ${AURY_VERSION:-versão-indisponível}..."
echo ""

rm -f "$FISH_FUNCTIONS_DIR/aury.fish"
rm -f "$FISH_FUNCTIONS_DIR/ay.fish"
rm -rf "$SHARE_DIR"

echo ""
echo "✅ A Aury foi removida do sistema."
echo ""
