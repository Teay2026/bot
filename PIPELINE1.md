# Pipeline RAG - Standardisation Documentaire (Git-Driven)

> **Architecture automatisée pour transformer des documents bruts en Markdown enrichi par IA**

---

## Table des matières

1. [Vue d'ensemble](#vue-densemble)
2. [Architecture complète](#architecture-complète)
3. [Composants détaillés](#composants-détaillés)
4. [Format de sortie](#format-de-sortie)
5. [Workflow CI/CD](#workflow-cicd)
6. [Organisation repository](#organisation-repository)
7. [Déploiement](#déploiement)

---

## Vue d'ensemble

### Objectif

Automatiser la transformation de documents hétérogènes (DOCX, PDF, TXT, emails) en documentation Markdown standardisée, enrichie par LLM, et optimisée pour l'ingestion RAG.

### Flux simplifié

```mermaid
flowchart LR
    A[📄 Documents bruts<br/>inbox/] --> B[🤖 Pipeline<br/>Automatique]
    B --> C[📚 Markdown enrichi<br/>knowledge/]
    C --> D[🔮 RAG]
```

### Principe

- **Input** : L'équipe dépose des fichiers dans `inbox/` via Git
- **Processing** : Pipeline automatique (extraction + enrichissement LLM + validation)
- **Output** : Markdown avec métadonnées YAML dans `knowledge/`
- **Trigger** : GitHub Actions (zéro intervention manuelle)

---

## Architecture complète

### Vue d'ensemble des composants

```mermaid
graph TB
    subgraph "📥 INPUT - Zone Humaine"
        User[👤 Équipe Support]
        Inbox[📂 inbox/]
        User -->|Commit fichiers| Inbox
    end
    
    subgraph "⚙️ PROCESSING - Pipeline Automatique"
        Trigger[🔔 GitHub Actions]
        Detector[🔍 Détecteur Format]
        
        subgraph Extracteurs
            ExtDOCX[DOCX Extractor]
            ExtPDF[PDF Extractor]
            ExtTXT[TXT Extractor]
        end
        
        LLM[🤖 LLM Analyzer]
        QualityGate[✅ Quality Gate]
        Storage[💾 Storage Manager]
        
        Inbox -->|Push trigger| Trigger
        Trigger --> Detector
        Detector --> ExtDOCX
        Detector --> ExtPDF
        Detector --> ExtTXT
        
        ExtDOCX --> LLM
        ExtPDF --> LLM
        ExtTXT --> LLM
        
        LLM --> QualityGate
        QualityGate -->|Validé| Storage
        QualityGate -->|Rejeté| Rejected[❌ Queue manuelle]
    end
    
    subgraph "📚 OUTPUT - Zone Machine"
        Knowledge[📁 knowledge/]
        RAG[🔮 RAG Engine]
        
        Storage --> Knowledge
        Knowledge --> RAG
    end
    
    subgraph "🔧 Infrastructure"
        Ollama[🐳 Ollama LLM<br/>Mistral 7B]
        Metrics[📊 Metrics DB]
        
        LLM -.->|Appels| Ollama
        QualityGate -.->|Logs| Metrics
        Storage -.->|Logs| Metrics
    end
```

### Flux de données détaillé

```mermaid
sequenceDiagram
    participant User as 👤 Support
    participant Git as 📂 Git Repo
    participant CI as ⚙️ GitHub Actions
    participant Extractor as 📤 Extracteur
    participant LLM as 🤖 LLM Analyzer
    participant Ollama as 🐳 Ollama API
    participant QG as ✅ Quality Gate
    participant Store as 💾 Storage
    participant KB as 📚 knowledge/

    User->>Git: git push inbox/FAQ.docx
    Git->>CI: Webhook trigger
    
    activate CI
    CI->>Extractor: Détecter + Router
    activate Extractor
    Extractor->>Extractor: Extraction texte + metadata
    Extractor-->>LLM: Texte brut normalisé
    deactivate Extractor
    
    activate LLM
    LLM->>Ollama: Prompt 1: Classification
    Ollama-->>LLM: Type, produits, tags
    
    LLM->>Ollama: Prompt 2: Chunking sémantique
    Ollama-->>LLM: Sections structurées
    
    LLM->>Ollama: Prompt 3: Glossaire
    Ollama-->>LLM: Termes techniques
    
    LLM->>LLM: Assembler Markdown + YAML
    LLM-->>QG: Document complet
    deactivate LLM
    
    activate QG
    QG->>QG: Validation schéma
    QG->>QG: Check qualité
    QG->>QG: Détection doublons
    
    alt Document valide
        QG-->>Store: ✅ Approuvé
        activate Store
        Store->>KB: Écrire fichier
        Store->>Git: Commit automatique
        deactivate Store
    else Document invalide
        QG->>User: ⚠️ Notification échec
    end
    deactivate QG
    deactivate CI
```

### États d'un document

```mermaid
stateDiagram-v2
    [*] --> Inbox: Commit humain
    
    Inbox --> Detection: CI triggered
    Detection --> Extraction: Format identifié
    
    Extraction --> ExtractionOK: Succès
    Extraction --> ExtractionFailed: Fichier corrompu
    
    ExtractionOK --> Enrichissement
    ExtractionFailed --> ManualQueue
    
    Enrichissement --> QualityCheck: LLM terminé
    
    QualityCheck --> Approved: Score >= 0.8
    QualityCheck --> Rejected: Score < 0.8
    
    Approved --> Knowledge
    Rejected --> ManualQueue
    
    Knowledge --> RAG
    RAG --> [*]
    
    ManualQueue --> Inbox: Correction
```

---

## Composants détaillés

### 1. Extracteurs - Couche de conversion

```mermaid
flowchart TB
    Input[Fichier source] --> Detect{Détection<br/>format}
    
    Detect -->|.docx| DOCX[DOCX Extractor]
    Detect -->|.pdf| PDF[PDF Extractor]
    Detect -->|.txt/.md| TXT[TXT Extractor]
    Detect -->|.eml| Email[Email Extractor]
    
    DOCX -->|python-docx| ExtractDOCX[Texte + Tableaux<br/>+ Images]
    PDF -->|PyMuPDF| CheckPDF{PDF natif<br/>ou scanné?}
    TXT -->|chardet| ExtractTXT[Texte + Encodage]
    Email -->|email parser| ExtractEmail[Corps + Metadata]
    
    CheckPDF -->|Natif| ExtractPDFNative[Texte direct]
    CheckPDF -->|Scanné| OCR[Tesseract OCR]
    OCR --> ExtractPDFScan[Texte OCR]
    
    ExtractDOCX --> Normalize[Normalisation]
    ExtractPDFNative --> Normalize
    ExtractPDFScan --> Normalize
    ExtractTXT --> Normalize
    ExtractEmail --> Normalize
    
    Normalize --> Output[Texte brut<br/>+ Metadata dict]
```

**Métadonnées extraites** :
- Auteur (si disponible)
- Date de création/modification
- Titre (depuis metadata ou H1)
- Images (exportées vers `assets/`)

**Bibliothèques** :
- `python-docx` : Extraction DOCX
- `PyMuPDF` : PDFs natifs
- `Tesseract` : OCR pour PDFs scannés
- `chardet` : Détection encodage
- `Unstructured.io` : Extraction avancée (optionnel)

---

### 2. LLM Analyzer - Enrichissement intelligent

```mermaid
flowchart TB
    Input[Texte brut] --> Phase1[Phase 1:<br/>Classification]
    
    Phase1 -->|Prompt 1| LLM1[🤖 LLM]
    LLM1 --> R1[Type: FAQ/Procedure/etc.<br/>Produits: OSE/OSM<br/>Tags: api, auth, etc.]
    
    R1 --> Phase2[Phase 2:<br/>Chunking Sémantique]
    Phase2 -->|Prompt 2| LLM2[🤖 LLM]
    LLM2 --> R2[Sections cohérentes<br/>H2/H3 structure<br/>Keywords par section]
    
    R2 --> Phase3[Phase 3:<br/>Glossaire]
    Phase3 -->|Prompt 3| LLM3[🤖 LLM]
    LLM3 --> R3[Termes techniques<br/>Acronymes<br/>Variations]
    
    R1 --> Assembler[Assembler]
    R2 --> Assembler
    R3 --> Assembler
    
    Assembler --> YAML[Frontmatter YAML]
    Assembler --> MD[Corps Markdown]
    
    YAML --> Final[Document final]
    MD --> Final
```

#### Prompts système

**Prompt 1 - Classification** :
```
Tu es un bibliothécaire technique expert OSE/OSM.
Analyse ce document et retourne un JSON avec :
{
  "type": "FAQ|Procedure|Troubleshooting|Architecture|Release_Notes",
  "products": ["liste produits mentionnés"],
  "tags": ["max 5 tags techniques"],
  "summary": "résumé en 2 phrases"
}
```

**Prompt 2 - Chunking** :
```
Découpe ce texte en sections cohérentes.
Règles :
- Une procédure complète = 1 section
- Une Q&A = 1 section
- Préserver la hiérarchie (H2, H3)
Retourne la structure Markdown avec titres.
```

**Prompt 3 - Glossaire** :
```
Identifie les termes techniques, acronymes, noms de produits.
Pour chaque terme :
- Forme canonique
- Variantes observées
- Définition si évidente
```

**Cache** : Utilise Redis pour éviter de re-traiter des docs identiques (basé sur hash du contenu source).

---

### 3. Quality Gate - Validation automatique

```mermaid
flowchart TB
    Doc[Document généré] --> Check1{Schema YAML<br/>valide?}
    
    Check1 -->|Non| Reject1[❌ Rejet]
    Check1 -->|Oui| Check2{Métadonnées<br/>obligatoires?}
    
    Check2 -->|Manquantes| Reject2[❌ Rejet]
    Check2 -->|OK| Check3{Chunking<br/>cohérent?}
    
    Check3 -->|< 20 mots/chunk| Reject3[❌ Rejet]
    Check3 -->|OK| Check4{Doublons<br/>détectés?}
    
    Check4 -->|Similarité > 95%| Reject4[❌ Rejet]
    Check4 -->|OK| Score[Calcul score<br/>global]
    
    Score --> Decision{Score<br/>>= 0.8?}
    
    Decision -->|Non| Reject5[❌ Rejet]
    Decision -->|Oui| Approve[✅ Approuvé]
    
    Reject1 --> Log[Log raison]
    Reject2 --> Log
    Reject3 --> Log
    Reject4 --> Log
    Reject5 --> Log
    
    Approve --> Next[Stockage]
```

**Critères de qualité pondérés** :

| Critère | Poids | Vérification |
|---------|-------|--------------|
| Complétude métadonnées | 30% | Tous les champs obligatoires présents |
| Qualité chunking | 25% | Chunks cohérents, mots-clés présents |
| Richesse glossaire | 15% | Au moins 3 termes identifiés |
| Clarté structure | 20% | Hiérarchie titres correcte |
| Cohérence technique | 10% | Produits/versions identifiés |

**Score final** = Somme pondérée → Seuil d'acceptation : 0.8/1.0

---

### 4. Storage Manager - Organisation & versioning

```mermaid
flowchart TD
    Input[Doc approuvé] --> Hash[Calculer SHA256<br/>fichier source]
    
    Hash --> Exists{Fichier avec<br/>ce hash existe?}
    
    Exists -->|Oui| Skip[Skip: déjà traité]
    Exists -->|Non| Organize[Organiser]
    
    Organize --> ByProduct[Copie dans<br/>by_product/OSE/]
    Organize --> ByType[Copie dans<br/>by_type/FAQ/]
    
    ByProduct --> Write[Écrire fichier]
    ByType --> Write
    
    Write --> UpdateIndex[MAJ index.json]
    UpdateIndex --> MergeGlossary[Fusion glossary_master.json]
    MergeGlossary --> GitCommit[Git commit auto]
```

**Organisation du dossier `knowledge/`** :

```
knowledge/
├── by_product/
│   ├── OSE/
│   │   ├── v3.2/
│   │   │   ├── faq_auth_e8f2a1.md
│   │   │   └── procedure_deploy_92b3c4.md
│   │   └── v3.3/
│   └── OSM/
│
├── by_type/
│   ├── FAQ/
│   ├── Procedures/
│   └── Troubleshooting/
│
├── index.json              # Index global des docs
├── glossary_master.json    # Glossaire consolidé
└── archives/               # Anciennes versions
```

**Nommage** : `{type}_{sujet}_{hash-court}.md`

Exemple : `faq_auth_e8f2a1.md`

---

## Format de sortie

### Structure Markdown + YAML frontmatter

```markdown
---
# === MÉTADONNÉES ===
source:
  file: "FAQ_OSE_v3.2.docx"
  hash: "sha256:e8f2a1b3c4d5..."
  author: "Support Team"
  ingestionDate: "2026-02-02T22:00:00Z"
  lastModified: "2026-01-15"

classification:
  type: "FAQ"
  products: ["OSE", "Orange Smart Energies"]
  versions: ["3.2", "3.x"]
  audience: ["L1", "L2"]
  tags: ["troubleshooting", "api", "authentication"]

quality:
  score: 0.92
  completeness: 0.89
  lastReviewed: "2026-02-02"
  reviewedBy: "pipeline_v1.0"

obsolescence:
  isObsolete: false
  deprecationDate: null
  supersededBy: null

glossary:
  OSE:
    canonical: "Orange Smart Energies"
    aliases: ["Smart Energies", "plateforme OSE"]
  JWT:
    canonical: "JSON Web Token"
    aliases: ["token", "access token"]

references:
  internal:
    - title: "Architecture OSE"
      path: "knowledge/architecture/ose_overview.md"
  external:
    - title: "JWT.io"
      url: "https://jwt.io"
---

# FAQ - Authentification API OSE v3.2

> **Résumé** : Documentation des erreurs courantes d'authentification et leurs résolutions pour l'API OSE version 3.2+

---

## 🔐 Erreurs d'Authentification

### Comment résoudre l'erreur 401 Unauthorized ?

**Problème** : L'erreur 401 survient quand le token JWT est invalide ou expiré.

**Solution** :
1. Régénérer le token via l'endpoint `/auth/refresh`
2. Utiliser le nouveau token dans vos requêtes

**Tags** : `401` `JWT` `token` `authentication`
**Produits** : OSE v3.2, v3.3
**Niveau** : L1

---

## 🔄 Procédures

### Renouvellement du Token API

**Étapes** :

1. **Appeler l'endpoint de refresh**
   ```bash
   POST /auth/refresh
   Content-Type: application/json
   
   {
     "refresh_token": "votre_refresh_token"
   }
   ```

2. **Récupérer le nouveau token**
   ```json
   {
     "access_token": "nouveau_token",
     "expires_in": 3600
   }
   ```

3. **Mettre à jour vos headers**
   ```bash
   Authorization: Bearer nouveau_token
   ```

**Tags** : `refresh` `token` `API`
**Difficulté** : Simple
**Temps estimé** : 2 minutes

---

## 📚 Glossaire

- **OSE** (Orange Smart Energies) : Plateforme de gestion intelligente de l'énergie
- **JWT** (JSON Web Token) : Standard d'authentification par jeton
```

**Avantages** :
- ✅ Lisible par humains (Git review facile)
- ✅ Parsable par machines (frontmatter YAML structuré)
- ✅ Versioning clair (diffs Git propres)
- ✅ Métadonnées riches pour filtrage RAG

---

## Workflow CI/CD

### GitHub Actions Pipeline

```mermaid
flowchart TB
    Trigger[Push sur inbox/**] --> Checkout[Checkout repo]
    Checkout --> Setup[Setup Python 3.11]
    Setup --> InstallDeps[Install dependencies]
    InstallDeps --> StartOllama[Start Ollama container]
    
    StartOllama --> Orchestrator[python orchestrator.py]
    
    Orchestrator --> Detect[Détecter nouveaux fichiers]
    Detect --> Extract[Extraction parallèle]
    Extract --> Enrich[Enrichissement LLM]
    Enrich --> Validate[Validation qualité]
    
    Validate --> Decision{Résultat?}
    
    Decision -->|Succès| Commit[Git commit + push]
    Decision -->|Échec| Notify[Notification Slack/Email]
    
    Commit --> UpdateMetrics[Update dashboard]
    Notify --> UpdateMetrics
```

**Fichier** : `.github/workflows/doc_pipeline.yml`

```yaml
name: Document Standardization Pipeline

on:
  push:
    paths:
      - 'inbox/**'

jobs:
  process:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      
      - name: Setup Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.11'
      
      - name: Install dependencies
        run: pip install -r pipeline/requirements.txt
      
      - name: Start Ollama
        run: |
          docker run -d -p 11434:11434 ollama/ollama
          docker exec ollama ollama pull mistral:7b
      
      - name: Run Pipeline
        run: python pipeline/orchestrator.py --input inbox/ --output knowledge/
        env:
          LLM_MODEL: "mistral:7b"
          QUALITY_THRESHOLD: "0.8"
      
      - name: Commit Results
        run: |
          git config user.name "Pipeline Bot"
          git config user.email "pipeline@ose.local"
          git add knowledge/
          git commit -m "🤖 Pipeline: $(date)" || echo "No changes"
          git push
```

**Performance** :
- Temps moyen : 15-30s par document
- Parallélisation : Plusieurs docs en simultané
- Cache LLM : Réduit le temps pour docs similaires

---

## Organisation repository

### Structure complète

```
repo-rag-support/
├── inbox/                          # Zone humaine (write-only)
│   ├── FAQ_OSE.docx
│   ├── GUIDE_API.pdf
│   └── troubleshooting.txt
│
├── knowledge/                      # Zone bot (write-only)
│   ├── by_product/
│   ├── by_type/
│   ├── index.json
│   └── glossary_master.json
│
├── pipeline/                       # Code de la pipeline
│   ├── extractors/
│   │   ├── __init__.py
│   │   ├── docx_extractor.py
│   │   ├── pdf_extractor.py
│   │   ├── text_extractor.py
│   │   └── email_extractor.py
│   │
│   ├── enrichment/
│   │   ├── llm_analyzer.py
│   │   └── prompts/
│   │       ├── classify_v1.txt
│   │       ├── chunk_v1.txt
│   │       └── glossary_v1.txt
│   │
│   ├── quality/
│   │   └── validator.py
│   │
│   ├── storage/
│   │   └── knowledge_store.py
│   │
│   ├── orchestrator.py
│   ├── requirements.txt
│   └── config.yaml
│
├── docs/                           # Documentation
│   ├── DATA_CONTRACT.md
│   ├── TAXONOMY.md
│   └── CONTRIBUTOR_GUIDE.md
│
├── tests/                          # Tests
│   ├── fixtures/
│   ├── test_extractors.py
│   ├── test_llm_analyzer.py
│   └── test_validator.py
│
└── .github/
    └── workflows/
        └── doc_pipeline.yml
```

### Permissions Git

| Rôle | `inbox/` | `knowledge/` | `pipeline/` |
|------|----------|--------------|-------------|
| Support Team | ✅ Write | 🔒 Read only | 🔒 Read only |
| Pipeline Bot | 🔒 Read only | ✅ Write | ✅ Read |
| Admin | ✅ Write | ✅ Write | ✅ Write |

**Protection** : Branch rules empêchent commits humains directs dans `knowledge/`

---

## Déploiement

### Timeline - 4 semaines

```mermaid
gantt
    title Roadmap Déploiement Pipeline
    dateFormat YYYY-MM-DD
    
    section Semaine 1: Infra
    Setup repo Git               :s1_1, 2026-02-03, 2d
    Install Ollama               :s1_2, after s1_1, 1d
    Config GitHub Actions        :s1_3, after s1_2, 2d
    
    section Semaine 2: Extracteurs
    Développer extracteurs       :s2_1, 2026-02-08, 5d
    Tests extracteurs            :s2_2, after s2_1, 2d
    
    section Semaine 3: LLM + QG
    LLM Analyzer                 :s3_1, 2026-02-15, 4d
    Prompts système              :s3_2, after s3_1, 1d
    Quality Gate                 :s3_3, after s3_2, 2d
    
    section Semaine 4: Intégration
    Storage Manager              :s4_1, 2026-02-22, 2d
    Tests E2E                    :s4_2, after s4_1, 2d
    POC 5 docs réels             :milestone, s4_3, after s4_2, 0d
    Documentation                :s4_4, after s4_3, 1d
    Démo équipe                  :milestone, s4_5, after s4_4, 0d
```

### Checklist de lancement

**Phase 1 : Setup (Jours 1-3)**
- [ ] Créer repo Git
- [ ] Installer Ollama + Mistral 7B
- [ ] Configurer GitHub Actions (webhook)
- [ ] Créer structure dossiers

**Phase 2 : Développement (Jours 4-14)**
- [ ] Implémenter extracteurs (DOCX, PDF, TXT)
- [ ] Créer prompts LLM (classification, chunking, glossaire)
- [ ] Développer Quality Gate
- [ ] Coder Storage Manager

**Phase 3 : Tests (Jours 15-21)**
- [ ] Tests unitaires extracteurs
- [ ] Tests LLM avec fixtures
- [ ] Tests E2E sur 10 docs historiques
- [ ] Validation qualité outputs

**Phase 4 : POC (Jours 22-28)**
- [ ] Traiter 5 documents réels de l'équipe
- [ ] Mesurer temps de traitement
- [ ] Évaluer qualité des docs générés
- [ ] Démo à l'équipe support
- [ ] Ajustements selon feedback

---

## Métriques & Observabilité

### KPIs à tracker

| Métrique | Objectif | Critique |
|----------|----------|----------|
| **Temps de traitement** | < 30s / doc | Moyen |
| **Taux de succès** | > 90% | Élevé |
| **Score qualité moyen** | > 0.85/1.0 | Élevé |
| **Doublons détectés** | < 5% | Moyen |
| **Uptime pipeline** | > 99% | Élevé |

### Dashboard métriques

```mermaid
flowchart LR
    subgraph Sources
        P[Pipeline Events]
        Q[Quality Checks]
        S[Storage Ops]
    end
    
    subgraph Collection
        M[Metrics Collector]
        DB[(SQLite / Prometheus)]
    end
    
    subgraph Visualisation
        D1[Pipeline Health]
        D2[Quality Trends]
        D3[Processing Time]
    end
    
    P --> M
    Q --> M
    S --> M
    
    M --> DB
    
    DB --> D1
    DB --> D2
    DB --> D3
```

**Métriques collectées** :
- Total docs traités
- Taux succès/échec
- Temps moyen par format
- Distribution scores qualité
- Usage tokens LLM
- Taille des docs générés

---

## Stack Technique

| Composant | Technologie | Raison |
|-----------|-------------|--------|
| **Extraction DOCX** | python-docx | Standard, bien maintenu |
| **Extraction PDF** | PyMuPDF | Rapide, support natif + OCR |
| **OCR** | Tesseract | Open-source, multi-langue |
| **LLM** | Ollama + Mistral 7B | Local, gratuit, performant |
| **Format sortie** | Markdown + YAML | Lisible humain + machine |
| **Parsing YAML** | PyYAML | Standard Python |
| **CI/CD** | GitHub Actions | Gratuit, intégré |
| **Versioning** | Git | Source de vérité unique |
| **Métriques** | SQLite ou Prometheus | Simple ou scalable |
| **Language** | Python 3.11 | Écosystème riche |

---

## Points clés

### ✅ Avantages

- **Automatisation totale** : Zéro intervention post-dépôt
- **Git-native** : Versioning, review, rollback gratuits
- **Qualité garantie** : Validation automatique stricte
- **Scalable** : Traite 100-1000 docs sans modifications
- **Pas de coût LLM** : Modèle local (Ollama)
- **Observabilité** : Métriques complètes

### ⚠️ Limitations

- Nécessite que l'équipe crée des fichiers (docs brutes)
- Dépend de la qualité du LLM (ajustement prompts)
- Pas adapté pour connaissance orale pure
- Nécessite infra Ollama (GPU optionnel mais recommandé)

### 🎯 Cas d'usage idéaux

- Documentation procédurale existante à standardiser
- Guides techniques à migrer vers Git
- FAQs dispersées à centraliser
- Release notes à structurer
- Architectures à documenter

---

## Prochaines étapes

**Validation concept** :
1. Tester extraction sur 5 docs réels
2. Valider prompts LLM avec l'équipe
3. Définir taxonomy (types, produits, tags)

**Implémentation** :
1. Setup infra (Git + Ollama + CI/CD)
2. Développer composants par ordre
3. Tests continus

**Déploiement** :
1. POC sur sous-ensemble de docs
2. Ajustements selon feedback
3. Rollout progressif

---

**Version** : 1.0  
**Date** : 2026-02-03  
**Équipe** : Support OSE/OSM
