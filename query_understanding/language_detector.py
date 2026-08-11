"""
Step 6 — Language Detection

Unicode-script detection first (fast, reliable even on short queries),
falling back to statistical detection (langdetect) only for longer
Latin-script text where script alone can't distinguish English from
e.g. French or Spanish.

Statistical language ID (langdetect) is unreliable on short strings —
"How much?" gets misclassified constantly — so short queries default to
English rather than trusting a low-confidence statistical guess.
"""

from __future__ import annotations

import re

# (unicode block start, end, ISO 639-1 code)
_SCRIPT_RANGES = [
    (0x0900, 0x097F, "hi"),   # Devanagari (Hindi, Marathi)
    (0x0600, 0x06FF, "ar"),   # Arabic
    (0x0B80, 0x0BFF, "ta"),   # Tamil
    (0x0C00, 0x0C7F, "te"),   # Telugu
    (0x0C80, 0x0CFF, "kn"),   # Kannada
    (0x0D00, 0x0D7F, "ml"),   # Malayalam
    (0x0980, 0x09FF, "bn"),   # Bengali
]

_MIN_WORDS_FOR_STATISTICAL_DETECTION = 6

# Common English function words. If a query is dominated by these,
# it's English regardless of what a statistical detector guesses —
# langdetect is unreliable on short strings and will happily call
# "Do I get refund?" Danish. This check runs BEFORE langdetect and
# short-circuits it, rather than just raising the word-count cutoff,
# because the misclassification isn't specific to short queries —
# it's specific to function-word-heavy queries at any length.
_ENGLISH_FUNCTION_WORDS = {
    "i", "a", "the", "is", "are", "do", "does", "can", "could", "will",
    "would", "how", "what", "where", "when", "why", "who", "my", "me",
    "you", "your", "it", "to", "for", "in", "on", "at", "get", "have",
    "has", "with", "of", "and", "or", "if", "this", "that",
}


def _looks_english(text: str) -> bool:
    words = re.findall(r"[a-zA-Z']+", text.lower())
    if not words:
        return False
    english_ratio = sum(1 for w in words if w in _ENGLISH_FUNCTION_WORDS) / len(words)
    return english_ratio >= 0.3


def detect_language(text: str) -> str:
    for ch in text:
        codepoint = ord(ch)
        for start, end, lang in _SCRIPT_RANGES:
            if start <= codepoint <= end:
                return lang

    if _looks_english(text):
        return "en"

    
    if len(text.split()) >= _MIN_WORDS_FOR_STATISTICAL_DETECTION:
        try:
            from langdetect import detect

            return detect(text)
        except Exception:
            return "en"

    return "en"
