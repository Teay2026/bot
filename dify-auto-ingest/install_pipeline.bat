@echo off
setlocal
chcp 65001 >nul

echo 🚀 Installation du pipeline Dify Auto-Ingest (Windows)...

:: 1. Installer les dépendances Python
if exist "scripts\requirements.txt" (
    pip install -r scripts\requirements.txt
) else if exist "dify-auto-ingest\scripts\requirements.txt" (
    pip install -r dify-auto-ingest\scripts\requirements.txt
) else (
    pip install requests python-dotenv
)

:: 2. Trouver le dossier .git
:: On cherche le dossier .git à la racine
if exist ".git" (
    set "GIT_DIR=.git"
) else (
    echo ❌ Erreur : Dossier .git introuvable. Etes-vous a la racine du projet ?
    pause
    exit /b 1
)

:: 3. Créer le hook via un script temporaire Bash (Git Bash est requis pour Git sur Windows)
:: On utilise le script .sh pour générer le hook car le hook lui-même doit être un script Bash pour Git
echo ℹ️ Utilisation de install_pipeline.sh via Git Bash...

if exist "dify-auto-ingest\install_pipeline.sh" (
    "C:\Program Files\Git\bin\bash.exe" dify-auto-ingest\install_pipeline.sh
) else if exist "install_pipeline.sh" (
    "C:\Program Files\Git\bin\bash.exe" install_pipeline.sh
) else (
    echo ❌ Script d'installation introuvable.
    pause
    exit /b 1
)

echo ✅ Installation terminee pour Windows !
pause
