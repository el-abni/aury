#!/usr/bin/env bash
set -euo pipefail

FISH_FUNCTIONS_DIR="$HOME/.config/fish/functions"
SHARE_DIR="$HOME/.local/share/aury"

echo ""
echo "🗑 Removendo a Aury v1.6.1..."
echo ""

rm -f "$FISH_FUNCTIONS_DIR/aury.fish"
rm -f "$FISH_FUNCTIONS_DIR/ay.fish"
rm -rf "$SHARE_DIR"

echo ""
echo "✅ A Aury foi removida do sistema."
echo ""
