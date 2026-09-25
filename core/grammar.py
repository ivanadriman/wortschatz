"""
core/grammar.py - Pure functions for German dictionary grammar and notation parsing.
Includes detection of articles, plurals, parenthetical notes, and CEFR level inference.
"""

import re
from typing import Tuple, Optional
from core.models import CEFRLevel


def parse_german_grammar(raw_german: str) -> Tuple[str, Optional[str], Optional[str]]:
    """
    Parse natural in-line German dictionary notation.
    Detects:
      - Noun plurals after comma: 'das Buch, die Bücher', 'das Buch, -¨er', 'das Auto, -s'
      - Parenthetical notes: 'die Bank (Geldinstitut)', 'sprechen (spricht, sprach)'
    Guarantees that full dialogue sentences with commas (e.g. 'Guten Tag, wie geht es Ihnen?')
    are NOT falsely parsed as plurals.
    Returns: (clean_prompt, plural, grammar_note)
    """
    raw = raw_german.strip()
    grammar_note = None
    plural = None

    # 1. Extract parenthetical hints
    paren_match = re.search(r'\((.*?)\)', raw)
    if paren_match:
        grammar_note = paren_match.group(1).strip()
        raw_without_paren = (raw[:paren_match.start()] + raw[paren_match.end():]).strip()
    else:
        raw_without_paren = raw

    # 2. Check for plural after comma
    if "," in raw_without_paren:
        parts = raw_without_paren.split(",", 1)
        base = parts[0].strip()
        rest = parts[1].strip()

        words = base.split()
        is_noun_candidate = (
            len(words) <= 3
            and not any(char in base for char in ".!?")
            and (words[0].lower() in ("der", "die", "das") or (words and words[0][0].isupper()))
        )

        if is_noun_candidate and rest:
            rest_lower = rest.lower()
            is_plural = False

            if rest_lower.startswith("die ") and len(rest.split()) <= 2:
                is_plural = True
            elif re.match(r'^[-–—]\s*([a-zA-ZäöüÄÖÜ¨]+|\"?[a-zA-ZäöüÄÖÜ¨]+)$', rest):
                is_plural = True
            elif re.match(r'^(pl\.?|plural)\s*:\s*', rest_lower):
                is_plural = True
                rest = re.sub(r'^(pl\.?|plural)\s*:\s*', '', rest, flags=re.IGNORECASE).strip()

            if is_plural:
                plural = rest
                clean_prompt = base
                return clean_prompt, plural, grammar_note

    clean_prompt = raw_without_paren if grammar_note else raw
    return clean_prompt, plural, grammar_note


def infer_cefr_level(category_name: str, file_path: str = "") -> CEFRLevel:
    """
    Infer CEFR Level (B1, B2, C1, etc.) from directory hierarchy or filename prefix.
    """
    combined = f"{file_path} {category_name}".upper()
    
    # Check explicit patterns
    if re.search(r'(^|[\\/_\-\s])C1([\\/_\-\s]|$)', combined):
        return CEFRLevel.C1
    if re.search(r'(^|[\\/_\-\s])B2([\\/_\-\s]|$)', combined):
        return CEFRLevel.B2
    if re.search(r'(^|[\\/_\-\s])B1([\\/_\-\s]|$)', combined):
        return CEFRLevel.B1
    if re.search(r'(^|[\\/_\-\s])A2([\\/_\-\s]|$)', combined):
        return CEFRLevel.A2
    if re.search(r'(^|[\\/_\-\s])A1([\\/_\-\s]|$)', combined):
        return CEFRLevel.A1
        
    return CEFRLevel.ALL
