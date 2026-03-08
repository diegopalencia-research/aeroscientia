"""
AeroScientia — NER Trainer
===========================
Fine-tunes a spaCy transformer model on aerospace technical text.

PIPELINE:
  1. Load annotated corpus (corpus/aerospace_corpus.py)
  2. Convert annotations to spaCy training format
  3. Fine-tune en_core_web_trf with custom entity types
  4. Evaluate: Precision, Recall, F1 per entity type
  5. Save model to models/aerospace_ner_v1/

USAGE:
  python ner_trainer.py --train       # Full training run
  python ner_trainer.py --eval        # Evaluate existing model
  python ner_trainer.py --preview     # Preview training data only
"""

import json
import random
import argparse
from pathlib import Path
from typing import List, Tuple, Dict
from dataclasses import dataclass

# ── spaCy ─────────────────────────────────────────────────────────────────────
try:
    import spacy
    from spacy.tokens import DocBin
    from spacy.training import Example
    from spacy.util import minibatch, compounding
    SPACY_AVAILABLE = True
except ImportError:
    SPACY_AVAILABLE = False
    print("⚠ spaCy not installed. Run: pip install spacy")

import sys
sys.path.insert(0, str(Path(__file__).parent))
from corpus.aerospace_corpus import CORPUS_TEXTS, CORPUS_ES


# ══════════════════════════════════════════════════════════════════════════════
# TRAINING CONFIG
# ══════════════════════════════════════════════════════════════════════════════

@dataclass
class TrainingConfig:
    base_model:       str   = "en_core_web_trf"    # Base spaCy model
    output_dir:       str   = "models/aerospace_ner_v1"
    n_iter:           int   = 30                   # Training iterations
    batch_size_start: int   = 4                    # Initial batch size
    batch_size_end:   int   = 32                   # Max batch size
    dropout:          float = 0.35                 # Dropout rate
    eval_split:       float = 0.20                 # 20% for evaluation
    random_seed:      int   = 42
    
    # Entity types we train on
    entity_types: tuple = (
        "EQUATION",
        "PHYSICAL_LAW",
        "PARAMETER",
        "PHYSICAL_CONSTANT",
        "FORCE",
        "COMPONENT",
        "VEHICLE_TYPE",
        "FLIGHT_PHENOMENON",
        "FLIGHT_REGIME",
        "MANEUVER",
        "ORBITAL_ELEMENT",
        "ORBIT_TYPE",
        "FLUID_CONCEPT",
        "METHODOLOGY",
        "MATERIAL",
    )


# ══════════════════════════════════════════════════════════════════════════════
# DATA PREPARATION
# ══════════════════════════════════════════════════════════════════════════════

class TrainingDataBuilder:
    """Converts annotated corpus to spaCy training format."""

    def __init__(self, config: TrainingConfig):
        self.config = config

    def build_training_examples(self) -> List[Tuple[str, Dict]]:
        """
        Convert corpus annotations to spaCy (text, entities) format.
        
        Returns:
            List of (text, {"entities": [(start, end, label), ...]}) tuples
        """
        training_data = []
        
        all_texts = CORPUS_TEXTS + CORPUS_ES
        print(f"Building training examples from {len(all_texts)} annotated texts...")
        
        for doc_data in all_texts:
            text = doc_data["text"].strip()
            entities = []
            
            for entity_text, entity_label in doc_data.get("entities", []):
                # Skip entity types not in our config
                if entity_label not in self.config.entity_types:
                    continue
                
                # Find all occurrences of the entity in the text
                start = 0
                while True:
                    idx = text.lower().find(entity_text.lower(), start)
                    if idx == -1:
                        break
                    end = idx + len(entity_text)
                    entities.append((idx, end, entity_label))
                    start = idx + 1
            
            # Resolve overlapping entities (keep longer ones)
            entities = self._resolve_overlaps(entities)
            
            if entities:
                training_data.append((text, {"entities": entities}))
        
        print(f"✓ Built {len(training_data)} training examples")
        print(f"  Total entities: {sum(len(d[1]['entities']) for d in training_data)}")
        self._print_entity_distribution(training_data)
        
        return training_data

    def _resolve_overlaps(self, entities: list) -> list:
        """Remove overlapping entity spans, keeping longer spans."""
        if not entities:
            return entities
        
        # Sort by length (descending)
        entities.sort(key=lambda x: -(x[1] - x[0]))
        kept = []
        
        for start, end, label in entities:
            overlaps = False
            for ks, ke, _ in kept:
                # Check overlap
                if not (end <= ks or start >= ke):
                    overlaps = True
                    break
            if not overlaps:
                kept.append((start, end, label))
        
        return sorted(kept, key=lambda x: x[0])

    def _print_entity_distribution(self, training_data: list):
        """Print entity type distribution in training data."""
        from collections import Counter
        counts = Counter()
        for _, ann in training_data:
            for _, _, label in ann["entities"]:
                counts[label] += 1
        
        print("\n  Entity distribution in training data:")
        for label, count in counts.most_common():
            bar = "█" * min(count, 25)
            print(f"    {label:<30} {bar} {count}")

    def split_train_eval(self, data: list) -> Tuple[list, list]:
        """Split data into train/eval sets."""
        random.seed(self.config.random_seed)
        random.shuffle(data)
        split_idx = int(len(data) * (1 - self.config.eval_split))
        return data[:split_idx], data[split_idx:]

    def to_docbin(self, data: list, nlp) -> DocBin:
        """Convert training data to spaCy DocBin format."""
        db = DocBin()
        for text, annotations in data:
            doc = nlp.make_doc(text)
            ents = []
            for start, end, label in annotations.get("entities", []):
                span = doc.char_span(start, end, label=label)
                if span is not None:
                    ents.append(span)
            doc.ents = ents
            db.add(doc)
        return db


# ══════════════════════════════════════════════════════════════════════════════
# TRAINER
# ══════════════════════════════════════════════════════════════════════════════

class AeroNERTrainer:
    """Fine-tunes spaCy NER model on aerospace corpus."""

    def __init__(self, config: TrainingConfig = None):
        self.config = config or TrainingConfig()
        self.data_builder = TrainingDataBuilder(self.config)

    def train(self) -> dict:
        """
        Full training pipeline.
        
        Returns:
            Training metrics dict
        """
        if not SPACY_AVAILABLE:
            raise RuntimeError("spaCy not available.")
        
        print("\n" + "═" * 60)
        print("  AEROSCIENTIA — NER Training Pipeline")
        print(f"  Base model: {self.config.base_model}")
        print(f"  Iterations: {self.config.n_iter}")
        print(f"  Entity types: {len(self.config.entity_types)}")
        print("═" * 60 + "\n")
        
        # 1. Load base model
        print(f"Loading base model: {self.config.base_model}...")
        try:
            nlp = spacy.load(self.config.base_model)
        except OSError:
            print(f"Model not found. Run: python -m spacy download {self.config.base_model}")
            raise
        
        # 2. Add NER pipe if not present
        if "ner" not in nlp.pipe_names:
            ner = nlp.add_pipe("ner", last=True)
        else:
            ner = nlp.get_pipe("ner")
        
        # 3. Add custom entity labels
        for label in self.config.entity_types:
            ner.add_label(label)
        print(f"✓ Added {len(self.config.entity_types)} entity labels")
        
        # 4. Prepare training data
        training_data = self.data_builder.build_training_examples()
        train_data, eval_data = self.data_builder.split_train_eval(training_data)
        
        print(f"\n  Train set: {len(train_data)} examples")
        print(f"  Eval set:  {len(eval_data)} examples\n")
        
        # 5. Training loop
        other_pipes = [p for p in nlp.pipe_names if p != "ner"]
        metrics_history = []
        
        print("Starting training...\n")
        with nlp.disable_pipes(*other_pipes):
            optimizer = nlp.begin_training()
            optimizer.learn_rate = 1e-5  # Low LR for fine-tuning
            
            batch_size = compounding(
                self.config.batch_size_start,
                self.config.batch_size_end,
                1.001
            )
            
            for iteration in range(self.config.n_iter):
                random.shuffle(train_data)
                losses = {}
                
                batches = minibatch(train_data, size=batch_size)
                for batch in batches:
                    texts, annotations = zip(*batch)
                    examples = [
                        Example.from_dict(nlp.make_doc(t), a)
                        for t, a in zip(texts, annotations)
                    ]
                    nlp.update(
                        examples,
                        drop=self.config.dropout,
                        losses=losses
                    )
                
                # Evaluate every 5 iterations
                if (iteration + 1) % 5 == 0:
                    metrics = self._evaluate(nlp, eval_data)
                    metrics["iteration"] = iteration + 1
                    metrics["loss"] = round(losses.get("ner", 0), 4)
                    metrics_history.append(metrics)
                    
                    print(f"  Iter {iteration+1:3}/{self.config.n_iter} | "
                          f"Loss: {metrics['loss']:.4f} | "
                          f"P: {metrics['precision']:.3f} | "
                          f"R: {metrics['recall']:.3f} | "
                          f"F1: {metrics['f1']:.3f}")
        
        # 6. Save model
        output_path = Path(self.config.output_dir)
        output_path.mkdir(parents=True, exist_ok=True)
        nlp.to_disk(output_path)
        print(f"\n✓ Model saved to: {output_path.absolute()}")
        
        # 7. Save training metrics
        metrics_path = output_path / "training_metrics.json"
        with open(metrics_path, 'w') as f:
            json.dump({
                "config": {
                    "base_model": self.config.base_model,
                    "n_iter": self.config.n_iter,
                    "entity_types": list(self.config.entity_types),
                },
                "history": metrics_history,
                "final_metrics": metrics_history[-1] if metrics_history else {}
            }, f, indent=2)
        
        print(f"✓ Training metrics saved to: {metrics_path}")
        
        # Final evaluation
        print("\n" + "─" * 60)
        print("  FINAL EVALUATION")
        print("─" * 60)
        final_metrics = self._evaluate_per_type(nlp, eval_data)
        self._print_evaluation(final_metrics)
        
        return final_metrics

    def _evaluate(self, nlp, eval_data: list) -> dict:
        """Quick evaluation returning P/R/F1."""
        examples = [
            Example.from_dict(nlp.make_doc(text), ann)
            for text, ann in eval_data
        ]
        scores = nlp.evaluate(examples)
        return {
            "precision": round(scores.get("ents_p", 0), 4),
            "recall":    round(scores.get("ents_r", 0), 4),
            "f1":        round(scores.get("ents_f", 0), 4),
        }

    def _evaluate_per_type(self, nlp, eval_data: list) -> dict:
        """Detailed evaluation with per-entity-type breakdown."""
        from collections import defaultdict
        
        tp = defaultdict(int)
        fp = defaultdict(int)
        fn = defaultdict(int)
        
        for text, ann in eval_data:
            doc = nlp(text)
            
            pred_ents = {(e.start_char, e.end_char, e.label_) for e in doc.ents}
            true_ents = set(
                (s, e, l) for s, e, l in ann.get("entities", [])
            )
            
            for ent in pred_ents:
                if ent in true_ents:
                    tp[ent[2]] += 1
                else:
                    fp[ent[2]] += 1
            
            for ent in true_ents:
                if ent not in pred_ents:
                    fn[ent[2]] += 1
        
        results = {}
        all_types = set(list(tp.keys()) + list(fn.keys()))
        
        for etype in all_types:
            p = tp[etype] / (tp[etype] + fp[etype]) if (tp[etype] + fp[etype]) > 0 else 0
            r = tp[etype] / (tp[etype] + fn[etype]) if (tp[etype] + fn[etype]) > 0 else 0
            f1 = 2 * p * r / (p + r) if (p + r) > 0 else 0
            results[etype] = {
                "precision": round(p, 4),
                "recall":    round(r, 4),
                "f1":        round(f1, 4),
                "support":   tp[etype] + fn[etype]
            }
        
        # Overall
        total_tp = sum(tp.values())
        total_fp = sum(fp.values())
        total_fn = sum(fn.values())
        overall_p = total_tp / (total_tp + total_fp) if (total_tp + total_fp) > 0 else 0
        overall_r = total_tp / (total_tp + total_fn) if (total_tp + total_fn) > 0 else 0
        overall_f1 = 2 * overall_p * overall_r / (overall_p + overall_r) if (overall_p + overall_r) > 0 else 0
        
        results["__overall__"] = {
            "precision": round(overall_p, 4),
            "recall":    round(overall_r, 4),
            "f1":        round(overall_f1, 4),
            "support":   total_tp + total_fn
        }
        
        return results

    def _print_evaluation(self, metrics: dict):
        """Print evaluation table."""
        print(f"\n  {'ENTITY TYPE':<30} {'P':>8} {'R':>8} {'F1':>8} {'SUPPORT':>8}")
        print(f"  {'─'*30} {'─'*8} {'─'*8} {'─'*8} {'─'*8}")
        
        for etype, scores in sorted(metrics.items()):
            if etype == "__overall__":
                continue
            p = scores["precision"]
            r = scores["recall"]
            f1 = scores["f1"]
            sup = scores["support"]
            
            # Highlight by F1
            flag = "✓" if f1 >= 0.80 else ("△" if f1 >= 0.60 else "✗")
            print(f"  {etype:<30} {p:>8.3f} {r:>8.3f} {f1:>8.3f} {sup:>8}  {flag}")
        
        if "__overall__" in metrics:
            ov = metrics["__overall__"]
            print(f"  {'─'*30} {'─'*8} {'─'*8} {'─'*8} {'─'*8}")
            print(f"  {'OVERALL':<30} {ov['precision']:>8.3f} {ov['recall']:>8.3f} "
                  f"{ov['f1']:>8.3f} {ov['support']:>8}")
        print()


# ══════════════════════════════════════════════════════════════════════════════
# CLI
# ══════════════════════════════════════════════════════════════════════════════

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="AeroScientia NER Trainer")
    parser.add_argument("--train",   action="store_true", help="Run training")
    parser.add_argument("--eval",    action="store_true", help="Evaluate existing model")
    parser.add_argument("--preview", action="store_true", help="Preview training data")
    parser.add_argument("--model",   type=str, default="models/aerospace_ner_v1",
                        help="Model path to load/save")
    parser.add_argument("--iter",    type=int, default=30, help="Training iterations")
    parser.add_argument("--base",    type=str, default="en_core_web_trf",
                        help="Base spaCy model")
    args = parser.parse_args()

    config = TrainingConfig(
        output_dir=args.model,
        n_iter=args.iter,
        base_model=args.base
    )

    if args.preview:
        builder = TrainingDataBuilder(config)
        data = builder.build_training_examples()
        train, eval_d = builder.split_train_eval(data)
        print(f"\n  Preview complete. Train: {len(train)} | Eval: {len(eval_d)}")

    elif args.train:
        trainer = AeroNERTrainer(config)
        metrics = trainer.train()
        print("\n✓ Training complete.")

    elif args.eval:
        if not SPACY_AVAILABLE:
            print("spaCy not available.")
        else:
            print(f"Loading model: {args.model}")
            nlp = spacy.load(args.model)
            builder = TrainingDataBuilder(config)
            data = builder.build_training_examples()
            _, eval_data = builder.split_train_eval(data)
            trainer = AeroNERTrainer(config)
            metrics = trainer._evaluate_per_type(nlp, eval_data)
            trainer._print_evaluation(metrics)

    else:
        # Default: preview
        builder = TrainingDataBuilder(config)
        data = builder.build_training_examples()
