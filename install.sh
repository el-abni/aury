#!/usr/bin/env bash

set -e

echo "💜 Instalando Aury..."

mkdir -p ~/.config/fish/functions

cp bin/aury.fish ~/.config/fish/functions/

echo "✅ Aury instalada!"
echo ""
echo "Teste com:"
echo "aury ajuda"
