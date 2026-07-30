#!/bin/bash
# build-extension.sh – Crée un ZIP pour le Chrome Web Store et un pour Firefox

set -e

EXT_DIR="extension"
OUTPUT_CHROME="luciole-extension-chrome.zip"
OUTPUT_FIREFOX="luciole-extension-firefox.zip"

# Nettoyer les anciens
rm -f "$OUTPUT_CHROME" "$OUTPUT_FIREFOX"

# Vérifier la présence des fichiers essentiels
if [ ! -f "$EXT_DIR/manifest.json" ]; then
    echo "❌ manifest.json manquant"
    exit 1
fi

# --- Chrome ---
cd "$EXT_DIR"
zip -r "../$OUTPUT_CHROME" . -x "*.git*" "*.DS_Store" "manifest.firefox.json" "generate_icons.py"
cd ..

# --- Firefox (on utilise manifest.firefox.json comme manifeste) ---
cd "$EXT_DIR"
# On remplace temporairement manifest.json par manifest.firefox.json
mv manifest.json manifest.chrome.json
cp manifest.firefox.json manifest.json
zip -r "../$OUTPUT_FIREFOX" . -x "*.git*" "*.DS_Store" "manifest.chrome.json" "generate_icons.py"
# Restaurer
mv manifest.chrome.json manifest.json
cd ..

echo "✅ Extensions empaquetées :"
echo "  - $OUTPUT_CHROME (pour Chrome)"
echo "  - $OUTPUT_FIREFOX (pour Firefox)"