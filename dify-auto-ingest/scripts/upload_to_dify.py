import os
import sys
import requests
import mimetypes
from pathlib import Path

# Load environment variables
from dotenv import load_dotenv
load_dotenv()

# Configuration
API_KEY = os.getenv("DIFY_API_KEY")
DATASET_ID = os.getenv("DIFY_DATASET_ID")
API_URL = os.getenv("Dify_API_URL")

def upload_file(file_path):
    """Upload a single file to Dify Dataset"""
    if not API_KEY or not DATASET_ID or not API_URL:
        # print("⚠️ Configuration Dify manquante (.env)")
        return False

    path = Path(file_path)
    if not path.exists():
        # print(f"❌ Fichier introuvable : {file_path}")
        return False

    # Check extension
    if path.suffix.lower() not in ['.txt', '.md', '.pdf', '.html', '.docx', '.csv']:
        return True # Skip silently

    # print(f"📤 Upload de {path.name}...")

    url = f"{API_URL}/datasets/{DATASET_ID}/document/create_by_file"
    headers = {
        "Authorization": f"Bearer {API_KEY}"
    }
    
    # Payload verified during E2E testing
    try:
        with open(path, 'rb') as f:
            # Verified working payload for Dify API v1
            import json
            payload_data = {
                "indexing_technique": "economy",
                "process_rule": {"mode": "automatic"}
            }
            
            files = {
                'file': (path.name, f, mimetypes.guess_type(path)[0] or 'application/octet-stream'),
                'data': (None, json.dumps(payload_data))
            }
            
            # headers must NOT contain Content-Type (requests sets it)
            response = requests.post(url, headers=headers, files=files, timeout=30)
            
            if response.status_code == 200:
                print(f"✅ Upload Dify réussi : {path.name}")
                return True
            else:
                print(f"❌ Erreur Dify ({response.status_code}) : {response.text}")
                return False
    except Exception as e:
        print(f"❌ Exception : {str(e)}")
        return False

def main():
    if len(sys.argv) < 2:
        sys.exit(0)

    files = sys.argv[1:]
    
    # print(f"🔄 Traitement Dify pour {len(files)} fichier(s)...")
    
    for file in files:
        upload_file(file)

if __name__ == "__main__":
    main()
