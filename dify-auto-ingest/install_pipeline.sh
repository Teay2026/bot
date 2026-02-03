#!/bin/bash

echo "🚀 Installation du pipeline Dify Auto-Ingest..."

# 1. Installer les dépendances Python
if [ -f "scripts/requirements.txt" ]; then
    pip3 install -r scripts/requirements.txt
else
    pip3 install requests python-dotenv
fi

# 2. Installer le hook Git
HOOK_PATH=".git/hooks/pre-push"
SCRIPT_PATH=".git/hooks/install_hook_content"

# Créer le contenu du hook si nécessaire (pour distribution)
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

# Récupérer les fichiers ajoutés/modifiés dans docs/
# On regarde la différence entre le SHA local et le SHA distant (ou HEAD précédent)
# Si c'est un nouveau commit (remote_sha = 000...), on compare avec HEAD~1 ou vide
if [ "$remote_sha" = "0000000000000000000000000000000000000000" ]; then
    # Nouveau commit pas encore sur remote -> diff avec le dernier commit connu localement
    # Ou simplement lister les fichiers changés dans les commits qu'on push
    new_files=$(git diff --name-only HEAD~1 HEAD -- docs/)
else
    new_files=$(git diff --name-only $remote_sha $local_sha -- docs/)
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
    python3 scripts/upload_to_dify.py $files_list
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
else
    echo "ℹ️  Aucun nouveau document dans docs/"
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
