"""
Storage Manager - MVP
Gère l'organisation et le stockage des documents dans knowledge/
"""

import hashlib
from pathlib import Path
from typing import Dict, Any
from datetime import datetime


class StorageManager:
    """Gestionnaire de stockage des documents"""
    
    def __init__(self, knowledge_path: Path):
        """
        Args:
            knowledge_path: Chemin vers le dossier knowledge/
        """
        self.knowledge_path = Path(knowledge_path)
        self.knowledge_path.mkdir(parents=True, exist_ok=True)
        
        # Créer sous-dossiers
        (self.knowledge_path / "by_product").mkdir(exist_ok=True)
        (self.knowledge_path / "by_type").mkdir(exist_ok=True)
    
    def store(self, document: str, source_file: str, metadata: Dict[str, Any]) -> Dict[str, Any]:
        """
        Stocke un document validé
        
        Args:
            document: Document complet (frontmatter + markdown)
            source_file: Nom du fichier source
            metadata: Métadonnées du document (classification, etc.)
            
        Returns:
            Dict avec chemins des fichiers créés
        """
        try:
            # Générer hash court du fichier source
            hash_short = self._generate_hash(source_file)[:8]
            
            # Extraire infos pour nommage
            doc_type = metadata.get("type", "unknown")
            products = metadata.get("products", [])
            
            # Générer nom de fichier
            base_name = self._sanitize_filename(source_file)
            filename = f"{base_name}_{hash_short}.md"
            
            # Chemins de destination
            paths_created = []
            
            # 1. Stockage par type
            type_dir = self.knowledge_path / "by_type" / doc_type
            type_dir.mkdir(parents=True, exist_ok=True)
            type_path = type_dir / filename
            
            type_path.write_text(document, encoding="utf-8")
            paths_created.append(str(type_path))
            
            # 2. Stockage par produit (si identifié)
            for product in products:
                product_dir = self.knowledge_path / "by_product" / product
                product_dir.mkdir(parents=True, exist_ok=True)
                product_path = product_dir / filename
                
                product_path.write_text(document, encoding="utf-8")
                paths_created.append(str(product_path))
            
            return {
                "success": True,
                "paths": paths_created,
                "filename": filename
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }
    
    def _generate_hash(self, content: str) -> str:
        """Génère un hash SHA256"""
        return hashlib.sha256(content.encode()).hexdigest()
    
    def _sanitize_filename(self, filename: str) -> str:
        """Nettoie un nom de fichier"""
        # Retirer l'extension
        name = Path(filename).stem
        
        # Remplacer caractères non alphanumériques
        safe_name = "".join(c if c.isalnum() or c in ("-", "_") else "_" for c in name)
        
        # Limiter longueur
        return safe_name[:50].lower()


def main():
    """Test du storage manager"""
    import tempfile
    
    with tempfile.TemporaryDirectory() as tmpdir:
        manager = StorageManager(Path(tmpdir) / "knowledge")
        
        test_doc = """---
source:
  file: "test.docx"
classification:
  type: "FAQ"
  products: ["OSE"]
---

# Test
## Content
"""
        
        result = manager.store(
            document=test_doc,
            source_file="FAQ OSE v3.2.docx",
            metadata={"type": "FAQ", "products": ["OSE"]}
        )
        
        if result["success"]:
            print("✅ Stockage réussi")
            print(f"📁 Fichiers créés:")
            for path in result["paths"]:
                print(f"  - {path}")
        else:
            print(f"❌ Erreur: {result['error']}")


if __name__ == "__main__":
    main()
