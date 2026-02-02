"""
Quality Gate - MVP
Validator basique pour vérifier les documents générés
"""

import yaml
from typing import Dict, Any


class QualityGate:
    """Validateur de qualité des documents"""
    
    def __init__(self, min_score: float = 0.7):
        """
        Args:
            min_score: Score minimum pour validation (0-1)
        """
        self.min_score = min_score
    
    def validate(self, document: str) -> Dict[str, Any]:
        """
        Valide un document
        
        Args:
            document: Document complet (frontmatter + markdown)
            
        Returns:
            Dict avec:
                - is_valid: bool
                - score: float (0-1)
                - errors: list
        """
        errors = []
        score_components = {}
        
        # 1. Vérifier présence frontmatter
        if not document.startswith("---"):
            errors.append("Pas de frontmatter YAML")
            return {"is_valid": False, "score": 0.0, "errors": errors}
        
        try:
            # Extraire le frontmatter
            parts = document.split("---")
            if len(parts) < 3:
                errors.append("Format frontmatter invalide")
                return {"is_valid": False, "score": 0.0, "errors": errors}
            
            frontmatter_str = parts[1]
            markdown_content = "---".join(parts[2:]).strip()
            
            # Parser YAML
            frontmatter = yaml.safe_load(frontmatter_str)
            
            # 2. Vérifier schéma frontmatter
            schema_score = self._validate_schema(frontmatter, errors)
            score_components["schema"] = schema_score
            
            # 3. Vérifier complétude métadonnées
            metadata_score = self._validate_metadata(frontmatter, errors)
            score_components["metadata"] = metadata_score
            
            # 4. Vérifier qualité du contenu Markdown
            content_score = self._validate_content(markdown_content, errors)
            score_components["content"] = content_score
            
            # Score final (pondéré)
            total_score = (
                schema_score * 0.3 +
                metadata_score * 0.4 +
                content_score * 0.3
            )
            
            is_valid = total_score >= self.min_score and len(errors) == 0
            
            return {
                "is_valid": is_valid,
                "score": round(total_score, 2),
                "score_components": score_components,
                "errors": errors
            }
            
        except yaml.YAMLError as e:
            errors.append(f"Erreur YAML: {str(e)}")
            return {"is_valid": False, "score": 0.0, "errors": errors}
    
    def _validate_schema(self, frontmatter: Dict, errors: list) -> float:
        """Valide la structure du frontmatter"""
        required_keys = ["source", "classification", "quality"]
        missing = [key for key in required_keys if key not in frontmatter]
        
        if missing:
            errors.append(f"Clés manquantes: {', '.join(missing)}")
            return 0.0
        
        return 1.0
    
    def _validate_metadata(self, frontmatter: Dict, errors: list) -> float:
        """Valide la complétude des métadonnées"""
        score = 1.0
        
        # Vérifier classification
        classification = frontmatter.get("classification", {})
        if not classification.get("type") or classification.get("type") == "Unknown":
            errors.append("Type de document non identifié")
            score -= 0.3
        
        if not classification.get("products"):
            errors.append("Aucun produit identifié")
            score -= 0.2
        
        if not classification.get("tags"):
            errors.append("Aucun tag identifié")
            score -= 0.2
        
        # Vérifier source
        source = frontmatter.get("source", {})
        if not source.get("file"):
            errors.append("Fichier source manquant")
            score -= 0.3
        
        return max(0, score)
    
    def _validate_content(self, content: str, errors: list) -> float:
        """Valide la qualité du contenu Markdown"""
        score = 1.0
        
        # Vérifier longueur minimale
        if len(content) < 100:
            errors.append("Contenu trop court (< 100 caractères)")
            return 0.0
        
        # Vérifier présence de titres
        has_h1 = content.count("\n# ") > 0
        has_h2 = content.count("\n## ") > 0
        
        if not has_h1:
            errors.append("Pas de titre H1")
            score -= 0.2
        
        if not has_h2:
            errors.append("Pas de structure (H2)")
            score -= 0.3
        
        # Vérifier qu'il n'est pas vide ou juste des titres
        lines = [l.strip() for l in content.split("\n") if l.strip()]
        content_lines = [l for l in lines if not l.startswith("#")]
        
        if len(content_lines) < 5:
            errors.append("Contenu insuffisant (< 5 lignes)")
            score -= 0.4
        
        return max(0, score)


def main():
    """Test du quality gate"""
    test_doc = """---
source:
  file: "test.docx"
  author: "Test"
classification:
  type: "FAQ"
  products: ["OSE"]
  tags: ["api"]
quality:
  generatedBy: "test"
---

# Test Document

## Section 1

Contenu de la section 1.

## Section 2

Contenu de la section 2.
"""
    
    gate = QualityGate(min_score=0.7)
    result = gate.validate(test_doc)
    
    print(f"✅ Valide: {result['is_valid']}")
    print(f"📊 Score: {result['score']}")
    print(f"📈 Détail: {result['score_components']}")
    if result['errors']:
        print(f"❌ Erreurs: {result['errors']}")


if __name__ == "__main__":
    main()
