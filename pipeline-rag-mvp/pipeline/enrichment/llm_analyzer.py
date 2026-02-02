"""
LLM Analyzer - MVP
Enrichit le texte brut avec Ollama
"""

import json
import requests
from pathlib import Path
from typing import Dict, Any
import yaml


class LLMAnalyzer:
    """Analyseur utilisant Ollama pour enrichir les documents"""
    
    def __init__(self, config_path: Path):
        """
        Initialise l'analyzer avec la configuration
        
        Args:
            config_path: Chemin vers config.yaml
        """
        with open(config_path) as f:
            self.config = yaml.safe_load(f)
        
        self.api_url = self.config["llm"]["api_url"]
        self.model = self.config["llm"]["model"]
        self.temperature = self.config["llm"]["temperature"]
        self.max_tokens = self.config["llm"]["max_tokens"]
        
        # Charger les prompts
        prompts_dir = Path(__file__).parent / "prompts"
        with open(prompts_dir / "classify.txt") as f:
            self.classify_prompt = f.read()
        with open(prompts_dir / "chunk.txt") as f:
            self.chunk_prompt = f.read()
    
    def analyze(self, text: str, metadata: Dict[str, Any]) -> Dict[str, Any]:
        """
        Analyse et enrichit le texte
        
        Args:
            text: Texte brut à analyser
            metadata: Métadonnées extraites
            
        Returns:
            Dict avec document enrichi (frontmatter + markdown)
        """
        try:
            # Phase 1: Classification
            print("🤖 Classification du document...")
            classification = self._classify(text)
            
            # Phase 2: Structuration Markdown
            print("📝 Structuration en Markdown...")
            markdown_content = self._structure_markdown(text)
            
            # Assemblage final
            doc = self._assemble_document(metadata, classification, markdown_content)
            
            return {
                "success": True,
                "document": doc
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }
    
    def _classify(self, text: str) -> Dict:
        """Classifie le document via LLM"""
        prompt = f"{self.classify_prompt}\n\n---\n\nTEXTE À ANALYSER:\n\n{text[:2000]}"  # Limiter à 2000 chars
        
        response = self._call_llm(prompt)
        
        # Parser la réponse JSON
        try:
            # Extraire le JSON de la réponse
            json_start = response.find("{")
            json_end = response.rfind("}") + 1
            if json_start != -1 and json_end > json_start:
                json_str = response[json_start:json_end]
                return json.loads(json_str)
            else:
                # Fallback si pas de JSON trouvé
                return self._default_classification()
        except json.JSONDecodeError:
            return self._default_classification()
    
    def _structure_markdown(self, text: str) -> str:
        """Structure le texte en Markdown"""
        prompt = f"{self.chunk_prompt}\n\n---\n\nTEXTE À STRUCTURER:\n\n{text}"
        
        response = self._call_llm(prompt)
        return response.strip()
    
    def _call_llm(self, prompt: str) -> str:
        """Appelle l'API Ollama"""
        payload = {
            "model": self.model,
            "prompt": prompt,
            "stream": False,
            "options": {
                "temperature": self.temperature,
                "num_predict": self.max_tokens
            }
        }
        
        response = requests.post(self.api_url, json=payload, timeout=60)
        response.raise_for_status()
        
        return response.json()["response"]
    
    def _assemble_document(self, metadata: Dict, classification: Dict, markdown: str) -> str:
        """Assemble le document final avec frontmatter YAML"""
        
        # Créer le frontmatter
        frontmatter = {
            "source": {
                "file": metadata.get("source_file"),
                "author": metadata.get("author"),
                "created": metadata.get("created"),
                "ingestionDate": metadata.get("extraction_date")
            },
            "classification": {
                "type": classification.get("type", "Unknown"),
                "products": classification.get("products", []),
                "audience": classification.get("audience", []),
                "tags": classification.get("tags", [])
            },
            "quality": {
                "generatedBy": "pipeline_mvp_v1.0",
                "needsReview": True
            }
        }
        
        # Assembler
        yaml_str = yaml.dump(frontmatter, allow_unicode=True, sort_keys=False)
        
        title = metadata.get("title", "Document sans titre")
        summary = classification.get("summary", "")
        
        document = f"""---
{yaml_str}---

# {title}

> **Résumé** : {summary}

---

{markdown}
"""
        
        return document
    
    def _default_classification(self) -> Dict:
        """Classification par défaut en cas d'échec"""
        return {
            "type": "Unknown",
            "products": [],
            "audience": ["L1"],
            "tags": [],
            "summary": "Document à classifier manuellement"
        }


def main():
    """Test de l'analyzer"""
    config_path = Path(__file__).parent.parent.parent / "config.yaml"
    
    analyzer = LLMAnalyzer(config_path)
    
    test_text = """
    Comment résoudre l'erreur 503 sur l'API OSE?
    
    L'erreur 503 survient généralement quand le load balancer bloque la requête.
    
    Solution:
    1. Vérifier la whitelist IP
    2. Ajouter l'IP du client
    3. Tester à nouveau
    """
    
    test_metadata = {
        "source_file": "test.docx",
        "author": "Test",
        "title": "FAQ API OSE",
        "extraction_date": "2026-02-03T00:00:00"
    }
    
    result = analyzer.analyze(test_text, test_metadata)
    
    if result["success"]:
        print("✅ Analyse réussie\n")
        print(result["document"])
    else:
        print(f"❌ Erreur: {result['error']}")


if __name__ == "__main__":
    main()
