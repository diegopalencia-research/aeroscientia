"""
AeroScientia — Level 1: NLP Extractor Pipeline
===============================================
Pipeline principal de extracción de entidades técnicas aeroespaciales.

PIPELINE:
  1. Ingest    → Lee texto crudo (PDF, TXT, string)
  2. Clean     → Limpia y normaliza el texto
  3. NER       → Extrae entidades técnicas (ecuaciones, leyes, parámetros...)
  4. Classify  → Asigna dominio (aeronautics / astrodynamics / propulsion...)
  5. Align     → Alinea términos EN↔ES con el glosario
  6. Export    → Exporta a JSON / CSV / HTML

USAGE:
  python extractor.py --input "path/to/document.pdf"
  python extractor.py --text "The lift coefficient CL increases with angle of attack"
  python extractor.py --demo
"""

import re
import json
import argparse
from pathlib import Path
from dataclasses import dataclass, field, asdict
from typing import Optional
from collections import defaultdict, Counter

# ── Try imports (graceful fallback if not installed) ──────────────────────────
try:
    import spacy
    SPACY_AVAILABLE = True
except ImportError:
    SPACY_AVAILABLE = False
    print("⚠  spaCy not installed. Run: pip install spacy && python -m spacy download en_core_web_trf")

try:
    import pdfplumber
    PDF_AVAILABLE = True
except ImportError:
    PDF_AVAILABLE = False

try:
    from rich.console import Console
    from rich.table import Table
    from rich.panel import Panel
    from rich import print as rprint
    RICH_AVAILABLE = True
    console = Console()
except ImportError:
    RICH_AVAILABLE = False
    console = None

# ── Local imports ─────────────────────────────────────────────────────────────
import sys
sys.path.insert(0, str(Path(__file__).parent))
from bilingual_glossary import GLOSSARY, ENTITY_TYPES, DOMAINS, search_glossary


# ══════════════════════════════════════════════════════════════════════════════
# DATA CLASSES
# ══════════════════════════════════════════════════════════════════════════════

@dataclass
class ExtractedEntity:
    """A single extracted technical entity."""
    text: str                          # The extracted text
    entity_type: str                   # EQUATION, PARAMETER, PHYSICAL_LAW, etc.
    domain: str                        # aeronautics, astrodynamics, etc.
    start_char: int                    # Start position in source text
    end_char: int                      # End position in source text
    confidence: float                  # Model confidence score (0-1)
    context: str                       # Surrounding text for reference
    translation_es: Optional[str] = None   # Spanish translation if found
    definition_en: Optional[str] = None    # English definition from glossary
    definition_es: Optional[str] = None    # Spanish definition from glossary
    symbol: Optional[str] = None          # Mathematical symbol
    unit: Optional[str] = None            # SI unit


@dataclass
class ExtractionResult:
    """Full result of a document extraction."""
    source: str                              # Source file/text identifier
    total_chars: int                         # Total characters processed
    entities: list = field(default_factory=list)
    domain_distribution: dict = field(default_factory=dict)
    entity_type_distribution: dict = field(default_factory=dict)
    unmapped_terms: list = field(default_factory=list)  # Entities not in glossary

    @property
    def total_entities(self):
        return len(self.entities)

    @property
    def unique_terms(self):
        return len(set(e.text.lower() for e in self.entities))


# ══════════════════════════════════════════════════════════════════════════════
# RULE-BASED PATTERNS (works without spaCy)
# ══════════════════════════════════════════════════════════════════════════════

# Mathematical equation patterns
EQUATION_PATTERNS = [
    r'\b[A-Za-z_]+\s*=\s*[\w\s\*\+\-\/\(\)\^\.]+',   # General: X = expression
    r'\bL\s*=\s*\(1\/2\)\s*\*?\s*rho',                 # Lift equation
    r'\bDelta-?v\s*=\s*v[_e]*\s*\*?\s*ln',             # Tsiolkovsky
    r'\bF\s*=\s*G\s*\*\s*m',                           # Newton gravitation
    r'\bv\^2\s*=\s*GM',                                 # Vis-viva
    r'\bRe\s*=\s*rho\s*\*\s*v',                        # Reynolds
    r'\bMa?\s*=\s*v\s*\/\s*a',                         # Mach
    r'\bP\s*=\s*sigma\s*\*\s*A',                       # Stefan-Boltzmann
    r'\bda\/dN\s*=\s*C',                               # Paris law
    r'\bT\s*=\s*m_dot',                                # Thrust equation
]

# Physical law patterns
PHYSICAL_LAW_PATTERNS = [
    r"Bernoulli['\s]s?\s+[Pp]rinciple",
    r"Newton['\s]s?\s+(?:Third|Second|First|Law|Laws)",
    r"Kepler['\s]s?\s+[Ll]aws?",
    r"Tsiolkovsk[yi]['\s]s?\s+[Rr]ocket\s+[Ee]quation",
    r"Navier[\-\s]Stokes\s+[Ee]quations?",
    r"Stefan[\-\s]Boltzmann\s+[Ll]aw",
    r"[Bb]rayton\s+[Cc]ycle",
    r"[Pp]aris\s+[Ll]aw",
    r"[Ww]hitcomb\s+[Aa]rea\s+[Rr]ule",
    r"[Oo]berth\s+[Ee]ffect",
    r"[Hh]all[\-\s][Ee]ffect",
]

# Physical constants and parameters
PARAMETER_PATTERNS = [
    (r'\bC_?L\b', 'Lift Coefficient', 'PARAMETER'),
    (r'\bC_?D\b', 'Drag Coefficient', 'PARAMETER'),
    (r'\bC_?m\b', 'Pitching Moment Coefficient', 'PARAMETER'),
    (r'\bIsp\b', 'Specific Impulse', 'PARAMETER'),
    (r'\bDelta-?v\b', 'Delta-v', 'PARAMETER'),
    (r'\bBPR\b', 'Bypass Ratio', 'PARAMETER'),
    (r'\bSFC\b', 'Specific Fuel Consumption', 'PARAMETER'),
    (r'\bOPR\b', 'Overall Pressure Ratio', 'PARAMETER'),
    (r'\bAR\b', 'Aspect Ratio', 'PARAMETER'),
    (r'\bW\/S\b', 'Wing Loading', 'PARAMETER'),
    (r'\bt\/c\b', 'Thickness-to-Chord Ratio', 'PARAMETER'),
    (r'\bMach\s+\d+[\.\d]*', 'Mach Number', 'FLIGHT_REGIME'),
    (r'\bM\s*[<>=]\s*\d+[\.\d]*', 'Mach Number Range', 'FLIGHT_REGIME'),
    (r'\bRe\b', 'Reynolds Number', 'PARAMETER'),
    (r'\bRAAN\b', 'Right Ascension of Ascending Node', 'ORBITAL_ELEMENT'),
    (r'\bLEO\b', 'Low Earth Orbit', 'ORBIT_TYPE'),
    (r'\bGEO\b', 'Geostationary Orbit', 'ORBIT_TYPE'),
    (r'\bMEO\b', 'Medium Earth Orbit', 'ORBIT_TYPE'),
    (r'\bHEO\b', 'Highly Elliptical Orbit', 'ORBIT_TYPE'),
    (r'\bISS\b', 'International Space Station', 'VEHICLE_TYPE'),
    (r'\bCFD\b', 'Computational Fluid Dynamics', 'METHODOLOGY'),
    (r'\bRANS\b', 'Reynolds-Averaged Navier-Stokes', 'METHODOLOGY'),
    (r'\bEDL\b', 'Entry, Descent and Landing', 'MANEUVER'),
    (r'\bRCS\b', 'Reaction Control System', 'COMPONENT'),
    (r'\bADCS\b', 'Attitude Determination and Control System', 'COMPONENT'),
    (r'\bTPS\b', 'Thermal Protection System', 'COMPONENT'),
    (r'\bCFRP\b', 'Carbon Fiber Reinforced Polymer', 'MATERIAL'),
    (r'\bHET\b', 'Hall-Effect Thruster', 'COMPONENT'),
    (r'\bNTP\b', 'Nuclear Thermal Propulsion', 'COMPONENT'),
    (r'\bSEP\b', 'Solar Electric Propulsion', 'COMPONENT'),
]

# Domain keyword maps for classification
DOMAIN_KEYWORDS = {
    "aeronautics": [
        "lift", "drag", "thrust", "airfoil", "wing", "aileron", "flap", "rudder",
        "elevator", "fuselage", "boundary layer", "turbulence", "stall", "mach",
        "nozzle", "turbofan", "turbojet", "propeller", "angle of attack", "camber",
        "chord", "extrados", "intrados", "bernoulli", "reynolds", "navier-stokes",
        "compressor", "combustion", "bypass ratio", "aspect ratio", "swept wing",
        "subsonic", "transonic", "supersonic", "hypersonic", "aerodynamic",
        "sustentación", "arrastre", "perfil alar", "ángulo de ataque", "turbulencia",
    ],
    "astrodynamics": [
        "orbit", "orbital", "satellite", "spacecraft", "trajectory", "kepler",
        "hohmann", "delta-v", "delta v", "specific impulse", "isp", "rocket",
        "apoapsis", "periapsis", "inclination", "eccentricity", "semi-major axis",
        "raan", "true anomaly", "leo", "geo", "meo", "iss", "free fall",
        "gravitational", "escape velocity", "orbital velocity", "maneuver",
        "interplanetary", "reentry", "aerobraking", "sphere of influence",
        "microgravity", "weightlessness", "caída libre", "órbita", "astrodinámica",
    ],
    "propulsion": [
        "thrust", "isp", "specific impulse", "exhaust", "propellant", "fuel",
        "oxidizer", "nozzle", "combustion", "turbofan", "turbojet", "ramjet",
        "scramjet", "ion thruster", "hall effect", "electric propulsion",
        "nuclear thermal", "mass flow", "bypass ratio", "pressure ratio",
        "thermal efficiency", "brayton cycle", "propulsive efficiency",
        "empuje", "propulsión", "propelente", "cámara de combustión",
    ],
    "materials": [
        "aluminum", "titanium", "cfrp", "composite", "alloy", "carbon fiber",
        "fatigue", "stress", "strain", "yield strength", "thermal protection",
        "ablative", "ceramic", "heat shield", "tps", "pica", "hrsi",
        "material", "structural", "weight ratio", "stiffness", "paris law",
        "aleación", "material compuesto", "fibra de carbono", "escudo térmico",
    ],
    "avionics": [
        "navigation", "gnss", "gps", "inertial", "ins", "radar", "lidar",
        "autopilot", "fly-by-wire", "fms", "tcas", "adcs", "rcs",
        "telemetry", "communication", "sensor", "star tracker", "gyroscope",
        "reaction wheel", "attitude control", "avionics", "navegación",
    ],
}


# ══════════════════════════════════════════════════════════════════════════════
# TEXT CLEANER
# ══════════════════════════════════════════════════════════════════════════════

class TextCleaner:
    """Cleans and normalizes aerospace technical text."""

    @staticmethod
    def clean(text: str) -> str:
        """Full cleaning pipeline."""
        text = TextCleaner.remove_pdf_artifacts(text)
        text = TextCleaner.normalize_equations(text)
        text = TextCleaner.normalize_whitespace(text)
        return text.strip()

    @staticmethod
    def remove_pdf_artifacts(text: str) -> str:
        """Remove common PDF extraction artifacts."""
        # Remove page headers/footers patterns
        text = re.sub(r'\n\d+\n', '\n', text)
        # Remove excessive hyphens from line wrapping
        text = re.sub(r'-\n\s*', '', text)
        # Clean reference numbers like [1] [23]
        text = re.sub(r'\[\d+\]', '', text)
        return text

    @staticmethod
    def normalize_equations(text: str) -> str:
        """Normalize mathematical notation."""
        # Normalize multiplication: 1/2*rho → 1/2 * rho
        text = re.sub(r'(\w)\*(\w)', r'\1 * \2', text)
        # Normalize subscripts: CL → CL (keep as is, flag for entity extraction)
        text = re.sub(r'C_L', 'CL', text)
        text = re.sub(r'C_D', 'CD', text)
        return text

    @staticmethod
    def normalize_whitespace(text: str) -> str:
        """Normalize whitespace."""
        text = re.sub(r'\n{3,}', '\n\n', text)
        text = re.sub(r' {2,}', ' ', text)
        return text

    @staticmethod
    def split_sentences(text: str) -> list:
        """Split text into sentences for context extraction."""
        sentences = re.split(r'(?<=[.!?])\s+(?=[A-Z])', text)
        return [s.strip() for s in sentences if len(s.strip()) > 20]


# ══════════════════════════════════════════════════════════════════════════════
# DOMAIN CLASSIFIER
# ══════════════════════════════════════════════════════════════════════════════

class DomainClassifier:
    """Classifies text segments by aerospace domain."""

    def __init__(self):
        self.keyword_map = DOMAIN_KEYWORDS

    def classify_text(self, text: str) -> dict:
        """
        Classify text by domain using keyword scoring.
        Returns dict of {domain: score} normalized to sum 1.0
        """
        text_lower = text.lower()
        scores = {domain: 0 for domain in self.keyword_map}

        for domain, keywords in self.keyword_map.items():
            for kw in keywords:
                count = text_lower.count(kw.lower())
                scores[domain] += count

        # Normalize
        total = sum(scores.values()) or 1
        return {d: round(s / total, 3) for d, s in scores.items()}

    def primary_domain(self, text: str) -> str:
        """Return the primary domain for a text."""
        scores = self.classify_text(text)
        return max(scores, key=scores.get)

    def classify_entity(self, entity_text: str, context: str = "") -> str:
        """Classify a single entity by looking at it + its context."""
        combined = f"{entity_text} {context}"
        return self.primary_domain(combined)


# ══════════════════════════════════════════════════════════════════════════════
# GLOSSARY ALIGNER
# ══════════════════════════════════════════════════════════════════════════════

class GlossaryAligner:
    """Aligns extracted entities with the bilingual glossary."""

    def __init__(self):
        # Build lookup indexes
        self._en_index = {e["en"].lower(): e for e in GLOSSARY}
        self._es_index = {e["es"].lower(): e for e in GLOSSARY}
        # Also index by related terms and partial matches
        self._partial_index = {}
        for entry in GLOSSARY:
            for key in [entry["en"].lower()] + [r.lower() for r in entry.get("related", [])]:
                self._partial_index[key] = entry

    def align(self, entity_text: str) -> Optional[dict]:
        """
        Find the best glossary match for an extracted entity.
        Returns glossary entry or None.
        """
        text_lower = entity_text.lower().strip()

        # Exact match
        if text_lower in self._en_index:
            return self._en_index[text_lower]
        if text_lower in self._es_index:
            return self._es_index[text_lower]

        # Partial match in English terms
        for key, entry in self._partial_index.items():
            if text_lower in key or key in text_lower:
                return entry

        # Fuzzy: check if entity is a substring of any term
        for entry in GLOSSARY:
            if (text_lower in entry["en"].lower() or
                text_lower in entry["es"].lower()):
                return entry

        return None

    def enrich_entity(self, entity: ExtractedEntity) -> ExtractedEntity:
        """Enrich an entity with glossary information."""
        match = self.align(entity.text)
        if match:
            entity.translation_es = match.get("es")
            entity.definition_en = match.get("definition_en")
            entity.definition_es = match.get("definition_es")
            entity.symbol = match.get("symbol")
            entity.unit = match.get("unit")
        return entity


# ══════════════════════════════════════════════════════════════════════════════
# RULE-BASED NER (works without spaCy)
# ══════════════════════════════════════════════════════════════════════════════

class RuleBasedNER:
    """
    Rule-based Named Entity Recognizer for aerospace technical text.
    Uses regex patterns + glossary matching.
    Fallback for when spaCy transformer model is not available.
    """

    def __init__(self):
        self.classifier = DomainClassifier()
        self.aligner = GlossaryAligner()
        self.cleaner = TextCleaner()

    def extract(self, text: str, source: str = "unknown") -> ExtractionResult:
        """
        Main extraction method. Runs full pipeline on input text.
        """
        clean_text = self.cleaner.clean(text)
        result = ExtractionResult(
            source=source,
            total_chars=len(clean_text)
        )

        found_spans = []  # Track (start, end) to avoid duplicates

        # ── 1. Extract equations ───────────────────────────────────────────
        for pattern in EQUATION_PATTERNS:
            for match in re.finditer(pattern, clean_text, re.IGNORECASE):
                span = (match.start(), match.end())
                if not self._overlaps(span, found_spans):
                    found_spans.append(span)
                    entity = self._make_entity(
                        text=match.group().strip(),
                        entity_type="EQUATION",
                        start=match.start(),
                        end=match.end(),
                        source_text=clean_text,
                        confidence=0.85
                    )
                    result.entities.append(entity)

        # ── 2. Extract physical laws ───────────────────────────────────────
        for pattern in PHYSICAL_LAW_PATTERNS:
            for match in re.finditer(pattern, clean_text, re.IGNORECASE):
                span = (match.start(), match.end())
                if not self._overlaps(span, found_spans):
                    found_spans.append(span)
                    entity = self._make_entity(
                        text=match.group().strip(),
                        entity_type="PHYSICAL_LAW",
                        start=match.start(),
                        end=match.end(),
                        source_text=clean_text,
                        confidence=0.90
                    )
                    result.entities.append(entity)

        # ── 3. Extract known parameters / symbols ─────────────────────────
        for pattern, canonical_name, entity_type in PARAMETER_PATTERNS:
            for match in re.finditer(pattern, clean_text):
                span = (match.start(), match.end())
                if not self._overlaps(span, found_spans):
                    found_spans.append(span)
                    entity = self._make_entity(
                        text=match.group().strip(),
                        entity_type=entity_type,
                        start=match.start(),
                        end=match.end(),
                        source_text=clean_text,
                        confidence=0.80,
                        canonical=canonical_name
                    )
                    result.entities.append(entity)

        # ── 4. Glossary-based extraction ───────────────────────────────────
        for entry in GLOSSARY:
            for term in [entry["en"]] + entry.get("related", []):
                if len(term) < 4:
                    continue  # Skip very short terms
                for match in re.finditer(re.escape(term), clean_text, re.IGNORECASE):
                    span = (match.start(), match.end())
                    if not self._overlaps(span, found_spans):
                        found_spans.append(span)
                        entity = self._make_entity(
                            text=match.group().strip(),
                            entity_type=entry["entity_type"],
                            start=match.start(),
                            end=match.end(),
                            source_text=clean_text,
                            confidence=0.75
                        )
                        entity.translation_es = entry.get("es")
                        entity.definition_en = entry.get("definition_en")
                        entity.definition_es = entry.get("definition_es")
                        entity.symbol = entry.get("symbol")
                        entity.unit = entry.get("unit")
                        result.entities.append(entity)

        # ── 5. Enrich unmapped entities via aligner ────────────────────────
        unmapped = []
        for entity in result.entities:
            if entity.translation_es is None:
                enriched = self.aligner.enrich_entity(entity)
                if enriched.translation_es is None:
                    unmapped.append(entity.text)

        result.unmapped_terms = list(set(unmapped))

        # ── 6. Compute distributions ───────────────────────────────────────
        result.domain_distribution = dict(Counter(e.domain for e in result.entities))
        result.entity_type_distribution = dict(Counter(e.entity_type for e in result.entities))

        return result

    def _make_entity(self, text, entity_type, start, end, source_text,
                     confidence, canonical=None) -> ExtractedEntity:
        """Create an ExtractedEntity with context."""
        # Extract surrounding context (±150 chars)
        ctx_start = max(0, start - 150)
        ctx_end = min(len(source_text), end + 150)
        context = source_text[ctx_start:ctx_end].replace('\n', ' ')

        # Determine domain
        domain = self.classifier.classify_entity(text, context)

        return ExtractedEntity(
            text=canonical or text,
            entity_type=entity_type,
            domain=domain,
            start_char=start,
            end_char=end,
            confidence=confidence,
            context=f"...{context}..."
        )

    def _overlaps(self, span: tuple, existing: list) -> bool:
        """Check if a span overlaps with any existing spans."""
        for s, e in existing:
            if not (span[1] <= s or span[0] >= e):
                return True
        return False


# ══════════════════════════════════════════════════════════════════════════════
# SPACY-BASED NER (when available — higher accuracy)
# ══════════════════════════════════════════════════════════════════════════════

class SpacyNER:
    """
    spaCy-based NER using a fine-tuned transformer model.
    Higher accuracy than rule-based, especially for multi-word entities.
    """

    def __init__(self, model_path: str = None):
        """
        Args:
            model_path: Path to fine-tuned model. If None, uses base model
                       with custom patterns as fallback.
        """
        if not SPACY_AVAILABLE:
            raise RuntimeError("spaCy not available. Install: pip install spacy")

        self.rule_ner = RuleBasedNER()  # Always used as augmentation

        # Try to load fine-tuned model first, then base model
        if model_path and Path(model_path).exists():
            print(f"Loading fine-tuned model: {model_path}")
            self.nlp = spacy.load(model_path)
            self.model_type = "fine-tuned"
        else:
            try:
                self.nlp = spacy.load("en_core_web_trf")
                self.model_type = "base-transformer"
                print("✓ Loaded en_core_web_trf (base transformer model)")
            except OSError:
                try:
                    self.nlp = spacy.load("en_core_web_sm")
                    self.model_type = "base-small"
                    print("⚠ Loaded en_core_web_sm (small model — less accurate)")
                except OSError:
                    raise RuntimeError(
                        "No spaCy model found.\n"
                        "Run: python -m spacy download en_core_web_trf"
                    )

        # Add custom entity ruler for aerospace terms
        self._add_entity_ruler()

    def _add_entity_ruler(self):
        """Add custom patterns for aerospace entities to spaCy pipeline."""
        if "entity_ruler" not in self.nlp.pipe_names:
            ruler = self.nlp.add_pipe("entity_ruler", before="ner")
        else:
            ruler = self.nlp.get_pipe("entity_ruler")

        patterns = []
        for entry in GLOSSARY:
            # Add EN term
            patterns.append({
                "label": entry["entity_type"],
                "pattern": entry["en"]
            })
            # Add ES term
            patterns.append({
                "label": entry["entity_type"],
                "pattern": entry["es"]
            })
            # Add symbol if it's a clean symbol (no special chars)
            if entry.get("symbol") and len(entry["symbol"]) < 30:
                sym = entry["symbol"].split("=")[0].strip()
                if sym and len(sym) < 10:
                    patterns.append({"label": entry["entity_type"], "pattern": sym})

        ruler.add_patterns(patterns)
        print(f"✓ Added {len(patterns)} custom aerospace entity patterns")

    def extract(self, text: str, source: str = "unknown") -> ExtractionResult:
        """Extract entities using spaCy + rule augmentation."""
        clean_text = RuleBasedNER().cleaner.clean(text)

        # spaCy processing
        doc = self.nlp(clean_text)
        aligner = GlossaryAligner()
        classifier = DomainClassifier()

        result = ExtractionResult(source=source, total_chars=len(clean_text))
        found_spans = []

        for ent in doc.ents:
            span = (ent.start_char, ent.end_char)
            found_spans.append(span)

            ctx_start = max(0, ent.start_char - 150)
            ctx_end = min(len(clean_text), ent.end_char + 150)
            context = clean_text[ctx_start:ctx_end]
            domain = classifier.classify_entity(ent.text, context)

            entity = ExtractedEntity(
                text=ent.text,
                entity_type=ent.label_,
                domain=domain,
                start_char=ent.start_char,
                end_char=ent.end_char,
                confidence=ent.kb_id_ if ent.kb_id_ else 0.75,
                context=f"...{context}..."
            )
            entity = aligner.enrich_entity(entity)
            result.entities.append(entity)

        # Augment with rule-based results for equations/symbols
        rule_result = self.rule_ner.extract(text, source)
        existing = set(e.text.lower() for e in result.entities)
        for ent in rule_result.entities:
            if ent.entity_type in ("EQUATION", "PARAMETER") and ent.text.lower() not in existing:
                result.entities.append(ent)

        result.domain_distribution = dict(Counter(e.domain for e in result.entities))
        result.entity_type_distribution = dict(Counter(e.entity_type for e in result.entities))
        return result


# ══════════════════════════════════════════════════════════════════════════════
# EXTRACTOR — Main Interface
# ══════════════════════════════════════════════════════════════════════════════

class AeroExtractor:
    """
    Main extractor interface. Automatically selects the best available backend.
    
    Usage:
        extractor = AeroExtractor()
        result = extractor.extract_text("The lift coefficient CL...")
        result = extractor.extract_pdf("path/to/paper.pdf")
        extractor.export_json(result, "output.json")
        extractor.export_csv(result, "output.csv")
    """

    def __init__(self, model_path: str = None, force_rules: bool = False):
        """
        Args:
            model_path: Path to fine-tuned spaCy model (optional)
            force_rules: If True, always use rule-based NER (faster, no GPU needed)
        """
        if not force_rules and SPACY_AVAILABLE:
            try:
                self.ner = SpacyNER(model_path)
                self.backend = "spacy"
            except Exception as e:
                print(f"⚠ spaCy NER failed ({e}), falling back to rule-based.")
                self.ner = RuleBasedNER()
                self.backend = "rules"
        else:
            self.ner = RuleBasedNER()
            self.backend = "rules"

        print(f"✓ AeroExtractor initialized [backend: {self.backend}]")

    def extract_text(self, text: str, source: str = "direct_input") -> ExtractionResult:
        """Extract entities from a raw text string."""
        return self.ner.extract(text, source)

    def extract_pdf(self, pdf_path: str) -> ExtractionResult:
        """Extract entities from a PDF file."""
        if not PDF_AVAILABLE:
            raise RuntimeError("pdfplumber not installed. Run: pip install pdfplumber")

        import pdfplumber
        path = Path(pdf_path)
        if not path.exists():
            raise FileNotFoundError(f"PDF not found: {pdf_path}")

        full_text = ""
        with pdfplumber.open(pdf_path) as pdf:
            print(f"📄 Processing {len(pdf.pages)} pages...")
            for i, page in enumerate(pdf.pages):
                page_text = page.extract_text() or ""
                full_text += page_text + "\n"
                if (i + 1) % 10 == 0:
                    print(f"   Page {i+1}/{len(pdf.pages)}...")

        return self.ner.extract(full_text, source=path.name)

    def extract_folder(self, folder_path: str, extensions: list = ['.txt', '.pdf']) -> list:
        """Extract from all documents in a folder."""
        folder = Path(folder_path)
        results = []
        files = [f for f in folder.iterdir() if f.suffix.lower() in extensions]
        print(f"📁 Found {len(files)} files in {folder_path}")
        for f in files:
            print(f"  Processing: {f.name}")
            if f.suffix == '.pdf':
                result = self.extract_pdf(str(f))
            else:
                result = self.extract_text(f.read_text(encoding='utf-8', errors='ignore'), f.name)
            results.append(result)
        return results

    # ── Export methods ────────────────────────────────────────────────────

    def export_json(self, result: ExtractionResult, output_path: str = "extraction_result.json"):
        """Export result to JSON."""
        data = {
            "source": result.source,
            "total_chars": result.total_chars,
            "total_entities": result.total_entities,
            "unique_terms": result.unique_terms,
            "domain_distribution": result.domain_distribution,
            "entity_type_distribution": result.entity_type_distribution,
            "entities": [asdict(e) for e in result.entities],
            "unmapped_terms": result.unmapped_terms
        }
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        print(f"✓ JSON exported: {output_path}")

    def export_csv(self, result: ExtractionResult, output_path: str = "extraction_result.csv"):
        """Export result to CSV."""
        try:
            import pandas as pd
            rows = [asdict(e) for e in result.entities]
            df = pd.DataFrame(rows)
            # Reorder columns
            cols = ['text', 'entity_type', 'domain', 'confidence',
                    'translation_es', 'definition_en', 'symbol', 'unit', 'context']
            cols = [c for c in cols if c in df.columns]
            df = df[cols]
            df.to_csv(output_path, index=False, encoding='utf-8')
            print(f"✓ CSV exported: {output_path} ({len(df)} rows)")
            return df
        except ImportError:
            print("⚠ pandas not available. Install: pip install pandas")

    def export_glossary_json(self, result: ExtractionResult,
                             output_path: str = "extracted_glossary.json"):
        """
        Export a clean bilingual glossary from extraction results.
        Only includes entities that were matched in the glossary.
        """
        glossary = []
        seen = set()
        for entity in result.entities:
            key = entity.text.lower()
            if key not in seen and entity.translation_es:
                seen.add(key)
                glossary.append({
                    "en": entity.text,
                    "es": entity.translation_es,
                    "entity_type": entity.entity_type,
                    "domain": entity.domain,
                    "definition_en": entity.definition_en or "",
                    "definition_es": entity.definition_es or "",
                    "symbol": entity.symbol or "",
                    "unit": entity.unit or "",
                })

        # Sort by entity_type then en
        glossary.sort(key=lambda x: (x["entity_type"], x["en"]))

        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(glossary, f, indent=2, ensure_ascii=False)
        print(f"✓ Glossary exported: {output_path} ({len(glossary)} bilingual terms)")
        return glossary

    def print_report(self, result: ExtractionResult):
        """Print a formatted extraction report to terminal."""
        print("\n" + "═" * 65)
        print(f"  AEROSCIENTIA — Extraction Report")
        print(f"  Source: {result.source}")
        print("═" * 65)
        print(f"  Characters processed:  {result.total_chars:,}")
        print(f"  Total entities found:  {result.total_entities}")
        print(f"  Unique terms:          {result.unique_terms}")
        print(f"  Backend:               {self.backend}")

        print(f"\n  Domain Distribution:")
        for domain, count in sorted(result.domain_distribution.items(),
                                    key=lambda x: -x[1]):
            bar = "█" * min(count, 30)
            print(f"    {domain:20} {bar} {count}")

        print(f"\n  Entity Types:")
        for etype, count in sorted(result.entity_type_distribution.items(),
                                   key=lambda x: -x[1]):
            print(f"    {etype:30} {count:4}")

        print(f"\n  Sample Entities (first 10):")
        print(f"  {'ENTITY':<35} {'TYPE':<20} {'ES TRANSLATION':<30}")
        print(f"  {'─'*35} {'─'*20} {'─'*30}")
        for e in result.entities[:10]:
            es = (e.translation_es or "—")[:28]
            print(f"  {e.text[:33]:<35} {e.entity_type:<20} {es}")

        if result.unmapped_terms:
            print(f"\n  ⚠ Unmapped terms ({len(result.unmapped_terms)} — candidates for glossary expansion):")
            for t in result.unmapped_terms[:8]:
                print(f"    • {t}")
        print("═" * 65 + "\n")


# ══════════════════════════════════════════════════════════════════════════════
# DEMO
# ══════════════════════════════════════════════════════════════════════════════

DEMO_TEXT = """
The lift equation L = (1/2) * rho * v^2 * S * CL is fundamental to understanding 
aerodynamic performance. The lift coefficient CL depends critically on the angle of 
attack and the airfoil geometry — specifically the camber and thickness-to-chord ratio.
As the angle of attack increases beyond the critical value, flow separation over the 
extrados leads to a stall condition where CL drops sharply.

Bernoulli's principle and Newton's Third Law together explain how a wing generates 
lift: higher velocity over the extrados creates lower static pressure, while downwash 
deflection provides direct momentum transfer. The Navier-Stokes equations govern the 
complete viscous flow field and are solved numerically via Computational Fluid Dynamics.

The bypass ratio BPR of a turbofan engine directly affects specific fuel consumption SFC.
Modern high-BPR engines achieve thermal efficiency gains by increasing the overall 
pressure ratio OPR to values exceeding 50:1.

For space propulsion, the Tsiolkovsky rocket equation Delta-v = ve * ln(m0/mf) governs 
all orbital maneuvers. The specific impulse Isp of ion thrusters (1500-10000 seconds) 
far exceeds that of chemical systems (250-450 seconds). The Hohmann transfer orbit 
provides the minimum Delta-v path between two circular orbits. Kepler's laws of 
planetary motion define orbital parameters including semi-major axis, eccentricity, 
and inclination. In Low Earth Orbit (LEO), the ISS maintains orbital velocity by 
staying in perpetual free fall — microgravity is NOT the absence of gravity.
"""

def run_demo():
    """Run extraction on demo text."""
    print("\n" + "▓" * 65)
    print("  AEROSCIENTIA — NLP Level 1 Demo")
    print("▓" * 65)

    extractor = AeroExtractor(force_rules=True)
    result = extractor.extract_text(DEMO_TEXT, source="demo_text")
    extractor.print_report(result)

    # Export outputs
    output_dir = Path("output")
    output_dir.mkdir(exist_ok=True)

    extractor.export_json(result, str(output_dir / "demo_extraction.json"))
    extractor.export_glossary_json(result, str(output_dir / "demo_glossary.json"))

    try:
        extractor.export_csv(result, str(output_dir / "demo_extraction.csv"))
    except Exception:
        pass

    print(f"\n✓ Output files saved to: {output_dir.absolute()}")
    return result


# ══════════════════════════════════════════════════════════════════════════════
# CLI
# ══════════════════════════════════════════════════════════════════════════════

if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="AeroScientia NLP Extractor — Aerospace Technical Term Extractor"
    )
    parser.add_argument("--demo",   action="store_true",
                        help="Run on built-in demo text")
    parser.add_argument("--text",   type=str,
                        help="Extract from a text string directly")
    parser.add_argument("--input",  type=str,
                        help="Path to PDF or TXT file to process")
    parser.add_argument("--folder", type=str,
                        help="Path to folder containing PDF/TXT files")
    parser.add_argument("--output", type=str, default="output",
                        help="Output directory (default: ./output)")
    parser.add_argument("--rules",  action="store_true",
                        help="Force rule-based NER (no spaCy needed)")
    parser.add_argument("--model",  type=str,
                        help="Path to fine-tuned spaCy model")

    args = parser.parse_args()

    # Default to demo if no args
    if not any([args.demo, args.text, args.input, args.folder]):
        args.demo = True

    if args.demo:
        run_demo()

    elif args.text:
        extractor = AeroExtractor(model_path=args.model, force_rules=args.rules)
        result = extractor.extract_text(args.text)
        extractor.print_report(result)
        Path(args.output).mkdir(exist_ok=True)
        extractor.export_json(result, f"{args.output}/extraction.json")
        extractor.export_glossary_json(result, f"{args.output}/glossary.json")

    elif args.input:
        extractor = AeroExtractor(model_path=args.model, force_rules=args.rules)
        if args.input.endswith('.pdf'):
            result = extractor.extract_pdf(args.input)
        else:
            text = Path(args.input).read_text(encoding='utf-8', errors='ignore')
            result = extractor.extract_text(text, source=Path(args.input).name)
        extractor.print_report(result)
        Path(args.output).mkdir(exist_ok=True)
        extractor.export_json(result, f"{args.output}/extraction.json")
        extractor.export_glossary_json(result, f"{args.output}/glossary.json")
        extractor.export_csv(result, f"{args.output}/extraction.csv")

    elif args.folder:
        extractor = AeroExtractor(model_path=args.model, force_rules=args.rules)
        results = extractor.extract_folder(args.folder)
        Path(args.output).mkdir(exist_ok=True)
        for i, result in enumerate(results):
            extractor.export_json(result, f"{args.output}/extraction_{i+1}.json")
        print(f"\n✓ Processed {len(results)} documents")
