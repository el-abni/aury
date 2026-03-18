#!/usr/bin/env bash

echo ""
echo "💜 Instalando a Aury v1.5.0..."
echo ""

mkdir -p ~/.config/fish/functions

cp bin/aury.fish ~/.config/fish/functions/
cp bin/ay.fish ~/.config/fish/functions/

echo ""
echo "✅A Aury foi instalada com sucesso!"
echo ""
echo "Para começar, execute:"
echo ""
echo "aury ajuda"
echo ""
