"""
services/deck_service.py - Multi-format hierarchical deck loader.
Supports scanning nested folders (e.g. decks/B1, decks/B2, decks/C1),
detecting CEFR levels, and building structured Flashcard domain models.
"""

import os
import csv
import re
from typing import List, Dict, Tuple, Optional
from core.models import Flashcard, CEFRLevel, ExerciseType
from core.grammar import parse_german_grammar, infer_cefr_level


def create_flashcard(
    german: str,
    english: str,
    category: str,
    level: Optional[CEFRLevel] = None,
    file_path: str = ""
) -> Flashcard:
    """Factory function to build a Flashcard with parsed grammar and inferred CEFR level."""
    clean_prompt, plural, grammar_note = parse_german_grammar(german)
    actual_level = level if level is not None else infer_cefr_level(category, file_path)
    
    # Infer exercise type based on markers or grammar note
    ex_type = ExerciseType.STANDARD
    if "nvr" in category.lower() or "nomen-verb" in category.lower():
        ex_type = ExerciseType.NVR
    elif "lückentext" in category.lower() or "cloze" in category.lower():
        ex_type = ExerciseType.CLOZE
    elif "nominalstil" in category.lower() or "passiversatz" in category.lower():
        ex_type = ExerciseType.TRANSFORMATION

    return Flashcard(
        german=german,
        english=english,
        category=category,
        level=actual_level,
        exercise_type=ex_type,
        clean_prompt=clean_prompt,
        plural=plural,
        grammar_note=grammar_note
    )


def load_deck_file(filepath: str, default_category: Optional[str] = None) -> List[Flashcard]:
    """Parse a single deck file with multi-encoding and flexible delimiters."""
    cards: List[Flashcard] = []
    category = default_category or os.path.splitext(os.path.basename(filepath))[0]
    inferred_level = infer_cefr_level(category, filepath)

    encodings = ["utf-8-sig", "utf-8", "cp1252", "latin-1"]
    content = None

    for enc in encodings:
        try:
            with open(filepath, "r", encoding=enc) as f:
                content = f.read()
            break
        except (UnicodeDecodeError, OSError):
            continue

    if not content:
        return cards

    lines = content.splitlines()
    for line in lines:
        line = line.strip()
        if not line or line.startswith("#"):
            continue

        delim = None
        for candidate in [";", "\t", "|", " - ", ","]:
            if candidate in line:
                delim = candidate
                break

        if not delim:
            continue

        parts = line.split(delim, 1)
        if len(parts) == 2:
            ger = parts[0].strip()
            eng = parts[1].strip()

            # Skip header rows if present
            if ger.lower() in ("german", "deutsch", "vokabel", "front") and eng.lower() in ("english", "englisch", "bedeutung", "back"):
                continue
            if ger and eng:
                card = create_flashcard(
                    german=ger,
                    english=eng,
                    category=category,
                    level=inferred_level,
                    file_path=filepath
                )
                cards.append(card)

    return cards


def scan_decks(base_dir: Optional[str] = None) -> Dict[str, List[Flashcard]]:
    """
    Scan application directory and any decks/ folder (including subdirectories for B1, B2, C1).
    Returns a dict mapping category name -> list of Flashcard objects.
    """
    if base_dir is None:
        base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

    decks: Dict[str, List[Flashcard]] = {}
    seen_files = set()

    decks_folder = os.path.join(base_dir, "decks")
    scan_paths = [decks_folder] if os.path.exists(decks_folder) else [base_dir]

    for root_scan in scan_paths:
        for root, _, files in os.walk(root_scan):
            rel = os.path.relpath(root, base_dir)
            if any(part in rel for part in ["__pycache__", "audio_cache", ".git", "ui", "core", "services"]):
                continue

            for file in sorted(files):
                ext = os.path.splitext(file)[1].lower()
                if ext in [".txt", ".csv", ".tsv"]:
                    full_path = os.path.normpath(os.path.join(root, file))
                    if full_path in seen_files:
                        continue
                    seen_files.add(full_path)

                    cards = load_deck_file(full_path)
                    if cards:
                        cat_name = cards[0].category
                        if cat_name in decks:
                            decks[cat_name].extend(cards)
                        else:
                            decks[cat_name] = cards

    return decks
