"""
Extracteur DOCX - MVP
Extrait le texte et les métadonnées d'un fichier DOCX
"""

from docx import Document
from pathlib import Path
from typing import Dict, Any
from datetime import datetime


class DocxExtractor:
    """Extracteur pour fichiers DOCX"""
    
    def extract(self, file_path: Path) -> Dict[str, Any]:
        """
        Extrait le contenu d'un fichier DOCX
        
        Args:
            file_path: Chemin vers le fichier DOCX
            
        Returns:
            Dict contenant:
                - text: Texte brut extrait
                - metadata: Dict des métadonnées
        """
        try:
            doc = Document(file_path)
            
            # Extraction du texte
            text_content = []
            for para in doc.paragraphs:
                if para.text.strip():
                    text_content.append(para.text.strip())
            
            # Extraction métadonnées natives
            core_props = doc.core_properties
            
            metadata = {
                "source_file": file_path.name,
                "author": core_props.author or "Unknown",
                "created": core_props.created.isoformat() if core_props.created else None,
                "modified": core_props.modified.isoformat() if core_props.modified else None,
                "title": core_props.title or self._extract_title_from_text(text_content),
                "extraction_date": datetime.now().isoformat()
            }
            
            return {
                "text": "\n\n".join(text_content),
                "metadata": metadata,
                "success": True
            }
            
        except Exception as e:
            return {
                "text": "",
                "metadata": {},
                "success": False,
                "error": str(e)
            }
    
    def _extract_title_from_text(self, text_lines: list) -> str:
        """Extrait un titre depuis les premières lignes"""
        if text_lines:
            # Prendre la première ligne non vide comme titre
            return text_lines[0][:100]  # Max 100 caractères
        return "Sans titre"


def main():
    """Test de l'extracteur"""
    import sys
    
    if len(sys.argv) < 2:
        print("Usage: python docx_extractor.py <fichier.docx>")
        return
    
    file_path = Path(sys.argv[1])
    if not file_path.exists():
        print(f"Erreur: {file_path} n'existe pas")
        return
    
    extractor = DocxExtractor()
    result = extractor.extract(file_path)
    
    if result["success"]:
        print("✅ Extraction réussie")
        print(f"\nMétadonnées:")
        for key, value in result["metadata"].items():
            print(f"  {key}: {value}")
        print(f"\nTexte extrait ({len(result['text'])} caractères):")
        print(result["text"][:500] + "..." if len(result["text"]) > 500 else result["text"])
    else:
        print(f"❌ Erreur: {result['error']}")


if __name__ == "__main__":
    main()
