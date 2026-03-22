#!/usr/bin/env bash
set -euo pipefail

FISH_FUNCTIONS_DIR="$HOME/.config/fish/functions"
SHARE_DIR="$HOME/.local/share/aury"

echo ""
echo "💜 Instalando a Aury v1.6.1..."
echo ""

mkdir -p "$FISH_FUNCTIONS_DIR"
mkdir -p "$SHARE_DIR"

rm -rf "$SHARE_DIR/python" "$SHARE_DIR/resources"

cp bin/aury.fish "$FISH_FUNCTIONS_DIR/"
cp bin/ay.fish "$FISH_FUNCTIONS_DIR/"
cp -R python "$SHARE_DIR/"
cp -R resources "$SHARE_DIR/"
cp VERSION "$SHARE_DIR/"
cp LICENSE.md "$SHARE_DIR/"

echo ""
echo "✅ A Aury foi instalada com sucesso!"
echo ""
echo "Base instalada em:"
echo ""
echo "$FISH_FUNCTIONS_DIR"
echo "$SHARE_DIR"
echo ""
echo "Abra um novo shell Fish ou execute:"
echo ""
echo "source ~/.config/fish/functions/aury.fish"
echo "source ~/.config/fish/functions/ay.fish"
echo ""
echo "Depois disso, teste com:"
echo ""
echo "aury ajuda"
echo ""
