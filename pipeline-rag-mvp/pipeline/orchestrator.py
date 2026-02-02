#!/usr/bin/env python3
"""
Orchestrateur Principal - MVP Pipeline RAG
Traite les fichiers de inbox/ et génère les docs dans knowledge/
"""

import sys
from pathlib import Path
import yaml
from datetime import datetime

# Ajouter le dossier parent au path
sys.path.insert(0, str(Path(__file__).parent))

from extractors import DocxExtractor
from enrichment import LLMAnalyzer
from quality import QualityGate
from storage import StorageManager


class PipelineOrchestrator:
    """Orchestrateur de la pipeline complète"""
    
    def __init__(self, config_path: Path):
        """
        Args:
            config_path: Chemin vers config.yaml
        """
        # Charger config
        with open(config_path) as f:
            self.config = yaml.safe_load(f)
        
        # Initialiser composants
        self.extractor = DocxExtractor()
        self.analyzer = LLMAnalyzer(config_path)
        self.quality_gate = QualityGate(min_score=self.config["quality"]["min_score"])
        
        knowledge_path = Path(self.config["paths"]["knowledge"])
        self.storage = StorageManager(knowledge_path)
        
        self.inbox_path = Path(self.config["paths"]["inbox"])
    
    def process_all(self):
        """Traite tous les fichiers dans inbox/"""
        print("🚀 Démarrage de la pipeline RAG")
        print(f"📂 Inbox: {self.inbox_path}")
        print()
        
        # Trouver fichiers DOCX
        docx_files = list(self.inbox_path.glob("*.docx"))
        
        if not docx_files:
            print("⚠️  Aucun fichier .docx trouvé dans inbox/")
            return
        
        print(f"📄 {len(docx_files)} fichier(s) trouvé(s)")
        print()
        
        stats = {
            "total": len(docx_files),
            "success": 0,
            "failed": 0
        }
        
        for docx_file in docx_files:
            success = self.process_file(docx_file)
            if success:
                stats["success"] += 1
            else:
                stats["failed"] += 1
            print()
        
        # Rapport final
        print("=" * 60)
        print("📊 RAPPORT FINAL")
        print(f"✅ Succès: {stats['success']}/{stats['total']}")
        print(f"❌ Échecs: {stats['failed']}/{stats['total']}")
        print("=" * 60)
    
    def process_file(self, file_path: Path) -> bool:
        """
        Traite un fichier via la pipeline complète
        
        Args:
            file_path: Chemin vers le fichier
            
        Returns:
            True si succès, False sinon
        """
        print(f"🔄 Traitement: {file_path.name}")
        
        # 1. EXTRACTION
        print("  📤 Extraction...")
        extract_result = self.extractor.extract(file_path)
        
        if not extract_result["success"]:
            print(f"  ❌ Échec extraction: {extract_result['error']}")
            return False
        
        text = extract_result["text"]
        metadata = extract_result["metadata"]
        print(f"  ✅ {len(text)} caractères extraits")
        
        # 2. ENRICHISSEMENT LLM
        print("  🤖 Enrichissement LLM...")
        analyze_result = self.analyzer.analyze(text, metadata)
        
        if not analyze_result["success"]:
            print(f"  ❌ Échec analyse: {analyze_result['error']}")
            return False
        
        document = analyze_result["document"]
        print("  ✅ Document enrichi généré")
        
        # 3. QUALITY GATE
        print("  ✅ Validation qualité...")
        validation = self.quality_gate.validate(document)
        
        print(f"  📊 Score: {validation['score']}")
        
        if not validation["is_valid"]:
            print(f"  ❌ Document rejeté:")
            for error in validation["errors"]:
                print(f"     - {error}")
            return False
        
        print(f"  ✅ Validation OK")
        
        # 4. STORAGE
        print("  💾 Stockage...")
        
        # Extraire métadonnées pour storage
        import yaml as yaml_parser
        parts = document.split("---")
        frontmatter = yaml_parser.safe_load(parts[1])
        classification = frontmatter.get("classification", {})
        
        storage_result = self.storage.store(
            document=document,
            source_file=file_path.name,
            metadata=classification
        )
        
        if not storage_result["success"]:
            print(f"  ❌ Échec stockage: {storage_result['error']}")
            return False
        
        print(f"  ✅ Stocké: {storage_result['filename']}")
        for path in storage_result["paths"]:
            print(f"     📁 {path}")
        
        return True


def main():
    """Point d'entrée principal"""
    # Chemin config
    base_dir = Path(__file__).parent.parent
    config_path = base_dir / "config.yaml"
    
    if not config_path.exists():
        print(f"❌ Erreur: {config_path} introuvable")
        sys.exit(1)
    
    # Lancer orchestrateur
    orchestrator = PipelineOrchestrator(config_path)
    orchestrator.process_all()


if __name__ == "__main__":
    main()
