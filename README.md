# AeroScientia — Level 1: NLP Terminology Extractor

**An NLP pipeline that reads aerospace technical documents and automatically extracts, classifies, and translates technical terminology EN↔ES.**

---

## What This Does

```
Input:  PDF / TXT (NASA papers, FAA handbooks, AIAA journals)
          ↓
      [Clean]  → Remove PDF artifacts, normalize equations
          ↓
      [NER]    → Extract: equations, laws, parameters, components...
          ↓
      [Classify] → aeronautics / astrodynamics / propulsion / materials
          ↓
      [Align]  → Match to bilingual EN↔ES glossary
          ↓
Output: Structured JSON / CSV + bilingual glossary
```

## Quick Start

```bash
# 1. Install dependencies
pip install -r requirements.txt
python -m spacy download en_core_web_trf

# 2. Run demo (no input needed)
python extractor.py --demo

# 3. Extract from your own text
python extractor.py --text "The lift coefficient CL increases with angle of attack..."

# 4. Extract from a PDF
python extractor.py --input path/to/nasa_paper.pdf

# 5. Process a folder of documents
python extractor.py --folder corpus/raw/ --output output/

# 6. Explore in Jupyter
jupyter notebook notebooks/01_corpus_exploration.ipynb
```

## File Structure

```
level_1_nlp/
│
├── extractor.py              ← Main pipeline (run this)
├── bilingual_glossary.py     ← EN↔ES glossary database (34+ terms, expandable)
├── ner_trainer.py            ← Fine-tune spaCy NER on aerospace corpus
├── requirements.txt          ← Dependencies
│
├── corpus/
│   ├── aerospace_corpus.py   ← Annotated training texts (NASA/FAA/AIAA style)
│   └── raw/                  ← Drop your PDFs here
│
├── models/
│   └── aerospace_ner_v1/     ← Fine-tuned model saved here after training
│
├── notebooks/
│   └── 01_corpus_exploration.ipynb  ← EDA + visualization
│
└── output/                   ← Extraction results (JSON, CSV, glossary)
```

## Entity Types Extracted

| Type | Description | Example |
|------|-------------|---------|
| `EQUATION` | Mathematical expressions | `L = ½ρv²SCL` |
| `PHYSICAL_LAW` | Named physics principles | `Bernoulli's Principle` |
| `PARAMETER` | Measurable variables | `Lift Coefficient (CL)` |
| `PHYSICAL_CONSTANT` | Fixed values | `Reynolds Number` |
| `FORCE` | Aerodynamic/gravitational forces | `Induced Drag` |
| `COMPONENT` | Physical parts | `Airfoil`, `Turbine` |
| `VEHICLE_TYPE` | Aircraft/spacecraft categories | `Turbofan`, `ISS` |
| `FLIGHT_PHENOMENON` | Observable conditions | `Stall`, `Free Fall` |
| `FLIGHT_REGIME` | Speed classifications | `Hypersonic (M>5)` |
| `MANEUVER` | Trajectory changes | `Hohmann Transfer` |
| `ORBITAL_ELEMENT` | Keplerian parameters | `Semi-Major Axis` |
| `ORBIT_TYPE` | Orbit classifications | `LEO`, `GEO` |
| `METHODOLOGY` | Analytical methods | `CFD`, `RANS` |
| `MATERIAL` | Aerospace materials | `CFRP`, `Ti-6Al-4V` |

## Training the NER Model

The rule-based extractor works out of the box. For higher accuracy on novel texts:

```bash
# Preview training data
python ner_trainer.py --preview

# Train (requires GPU for transformer, ~30 min)
python ner_trainer.py --train --iter 30

# Evaluate trained model
python ner_trainer.py --eval

# Use trained model in extractor
python extractor.py --input paper.pdf --model models/aerospace_ner_v1
```

## Data Sources for Expanding Corpus

| Source | URL | Type |
|--------|-----|------|
| NASA NTRS | ntrs.nasa.gov | Research papers |
| FAA Handbooks | faa.gov/regulations_policies | Pilot/tech manuals |
| ESA Publications | publications.esa.int | Space mission docs |
| AIAA Papers | arc.aiaa.org | Engineering research |
| OpenSky Network | opensky-network.org | Flight data |

## Output Format

```json
{
  "source": "nasa_paper.pdf",
  "total_chars": 45231,
  "total_entities": 87,
  "unique_terms": 43,
  "domain_distribution": {
    "aeronautics": 45,
    "astrodynamics": 28,
    "propulsion": 14
  },
  "entities": [
    {
      "text": "Lift Coefficient",
      "entity_type": "PARAMETER",
      "domain": "aeronautics",
      "confidence": 0.92,
      "translation_es": "Coeficiente de Sustentación",
      "definition_en": "Dimensionless number quantifying lift...",
      "definition_es": "Número adimensional que cuantifica...",
      "symbol": "CL",
      "unit": "dimensionless",
      "context": "...the lift coefficient CL increases with..."
    }
  ]
}
```

## Portfolio Value

This module demonstrates:
- **NLP Pipeline Design**: End-to-end from raw PDF to structured knowledge
- **Custom NER**: Domain-specific entity recognition (not generic NLP)
- **Transfer Learning**: Fine-tuning transformer models on technical corpus
- **Bilingual NLP**: Cross-language semantic alignment EN↔ES
- **Technical Domain Expertise**: Physics-informed feature understanding

---

*Part of AeroScientia — An End-to-End Aerospace Knowledge Engine*  
*Next: Level 3 (ML Flight Analytics) → Level 2 (RAG Chatbot)*
