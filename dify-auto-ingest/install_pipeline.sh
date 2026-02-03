#!/bin/bash

echo "🚀 Installation du pipeline Dify Auto-Ingest..."

# 1. Installer les dépendances Python
# On suppose qu'on est dans le dossier dify-auto-ingest ou à la racine
# On détecte où on est
if [ -f "scripts/requirements.txt" ]; then
    # Exécuté depuis dify-auto-ingest/
    pip3 install -r scripts/requirements.txt
elif [ -f "dify-auto-ingest/scripts/requirements.txt" ]; then
    # Exécuté depuis la racine
    pip3 install -r dify-auto-ingest/scripts/requirements.txt
else
    pip3 install requests python-dotenv
fi

# 2. Installer le hook Git
# Si exécuté depuis la racine, le hook est dans .git/hooks
# Si exécuté depuis dify-auto-ingest, il faut remonter (../../.git/hooks) 
# MAIS dify-auto-ingest n'est plus un repo Git, donc on est censé être dans un repo Git parent.
# On cherche le dossier .git le plus proche
GIT_DIR=$(git rev-parse --git-dir)
HOOK_PATH="$GIT_DIR/hooks/pre-push"

# Créer le contenu du hook
cat > $HOOK_PATH << 'EOF'
#!/bin/bash

echo ""
echo "📤 PUSH DÉTECTÉ - Analyse des documents..."
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

# Lire les informations du push (remote & url)
read local_ref local_sha remote_ref remote_sha
remote_name="$1"
remote_url="$2"

echo "🔗 Push vers: $remote_name ($remote_url)"
echo ""

# Récupérer les fichiers ajoutés/modifiés dans dify-auto-ingest/docs/
# Note : Le chemin doit être relatif à la racine du repo
DOCS_PATH="dify-auto-ingest/docs/"

if [ "$remote_sha" = "0000000000000000000000000000000000000000" ]; then
    new_files=$(git diff --name-only HEAD~1 HEAD -- $DOCS_PATH)
else
    new_files=$(git diff --name-only $remote_sha $local_sha -- $DOCS_PATH)
fi

if [ -n "$new_files" ]; then
    echo "📄 Documents détectés :"
    echo "$new_files" | while read file; do
        echo "  ✓ $file"
    done
    echo ""
    echo "🚀 Upload vers Dify en cours..."
    # Convertir les newlines en espaces pour passer en arguments
    files_list=$(echo "$new_files" | tr '\n' ' ')
    
    # Détection de la commande Python (python3 ou python)
    if command -v python3 &>/dev/null; then
        PY_CMD="python3"
    else
        PY_CMD="python"
    fi

    # Trouver le script python (chemin absolu ou relatif racine)
    # On assume que le script est lancé depuis la racine git
    $PY_CMD dify-auto-ingest/scripts/upload_to_dify.py $files_list
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
else
    echo "ℹ️  Aucun nouveau document dans $DOCS_PATH"
fi
EOF

chmod +x $HOOK_PATH
echo "✅ Hook Git installé dans $HOOK_PATH"

# 3. Configuration .env
if [ ! -f ".env" ]; then
    cp .env.example .env
    echo "⚠️  Fichier .env créé. Veuillez éditer .env avec vos clés API !"
else
    echo "ℹ️  Fichier .env existant conservé."
fi

echo "✅ Installation terminée ! Prêt à pusher."
