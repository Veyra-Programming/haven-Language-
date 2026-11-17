"""
Haven Standard Library - String, Text & NLP Methods
Standard: Open Digital Continuity Standard (ODCS) & Text Processing Spec
Architecture & Specification: Anirudha Puthraya
Copyright (c) 2026 Haven Language Foundation & Anirudha Puthraya.
"""

import re
import base64
import urllib.parse
import unicodedata
from typing import List, Dict, Sequence


def slugify(text: str) -> str:
    """Converts a string into a URL-friendly slug."""
    text = unicodedata.normalize('NFKD', text).encode('ascii', 'ignore').decode('ascii')
    text = re.sub(r'[^\w\s-]', '', text).strip().lower()
    return re.sub(r'[-\s]+', '-', text)


def camel_case(text: str) -> str:
    """Converts string to camelCase."""
    words = re.findall(r'[a-zA-Z0-9]+', text)
    if not words:
        return ""
    return words[0].lower() + "".join(w.capitalize() for w in words[1:])


def snake_case(text: str) -> str:
    """Converts string to snake_case."""
    text = re.sub(r'([A-Z]+)([A-Z][a-z])', r'\1_\2', text)
    text = re.sub(r'([a-z0-9])([A-Z])', r'\1_\2', text)
    return re.sub(r'[-\s]+', '_', text).lower()


def kebab_case(text: str) -> str:
    """Converts string to kebab-case."""
    return snake_case(text).replace('_', '-')


def pascal_case(text: str) -> str:
    """Converts string to PascalCase."""
    words = re.findall(r'[a-zA-Z0-9]+', text)
    return "".join(w.capitalize() for w in words)


def title_case(text: str) -> str:
    """Converts string to Title Case."""
    return text.title()


def sponge_case(text: str) -> str:
    """Converts string to sPoNgEbOb CaSe."""
    return "".join(c.upper() if i % 2 == 1 else c.lower() for i, c in enumerate(text))


def strip_html(text: str) -> str:
    """Removes HTML and XML tags from a string."""
    return re.sub(r'<[^>]*>', '', text)


def remove_accents(text: str) -> str:
    """Strips diacritical marks/accents from characters."""
    nfkd = unicodedata.normalize('NFKD', text)
    return "".join(c for c in nfkd if not unicodedata.combining(c))


def collapse_whitespace(text: str) -> str:
    """Replaces multiple consecutive whitespaces with a single space."""
    return re.sub(r'\s+', ' ', text).strip()


def truncate_words(text: str, num_words: int, suffix: str = "...") -> str:
    """Truncates string to a specified number of words."""
    words = text.split()
    if len(words) <= num_words:
        return text
    return " ".join(words[:num_words]) + suffix


def truncate_chars(text: str, max_len: int, suffix: str = "...") -> str:
    """Truncates string to a maximum character length."""
    if len(text) <= max_len:
        return text
    cutoff = max(0, max_len - len(suffix))
    return text[:cutoff] + suffix


def wrap_text(text: str, width: int = 80) -> List[str]:
    """Wraps text into a list of lines with maximum character width."""
    import textwrap
    return textwrap.wrap(text, width=width)


def pad_left(text: str, length: int, char: str = " ") -> str:
    """Pads string on the left until it reaches specified length."""
    return text.rjust(length, char)


def pad_right(text: str, length: int, char: str = " ") -> str:
    """Pads string on the right until it reaches specified length."""
    return text.ljust(length, char)


def center_text(text: str, length: int, char: str = " ") -> str:
    """Centers string within specified length."""
    return text.center(length, char)


def word_count(text: str) -> int:
    """Returns number of words in string."""
    return len(text.split())


def char_frequency(text: str) -> Dict[str, int]:
    """Computes character frequency table."""
    counts: Dict[str, int] = {}
    for c in text:
        counts[c] = counts.get(c, 0) + 1
    return counts


def is_palindrome(text: str) -> bool:
    """Checks if string is a palindrome (ignoring casing and whitespace)."""
    cleaned = re.sub(r'[\W_]+', '', text).lower()
    return cleaned == cleaned[::-1]


def is_anagram(s1: str, s2: str) -> bool:
    """Checks if two strings are anagrams of each other."""
    c1 = sorted(re.sub(r'[\W_]+', '', s1).lower())
    c2 = sorted(re.sub(r'[\W_]+', '', s2).lower())
    return c1 == c2


def count_vowels(text: str) -> int:
    """Counts vowels (a, e, i, o, u) in string."""
    return sum(1 for c in text.lower() if c in 'aeiou')


def count_consonants(text: str) -> int:
    """Counts consonants in string."""
    return sum(1 for c in text.lower() if c.isalpha() and c not in 'aeiou')


def levenshtein_distance(s1: str, s2: str) -> int:
    """Computes minimum edit distance between two strings."""
    if len(s1) < len(s2):
        return levenshtein_distance(s2, s1)
    if len(s2) == 0:
        return len(s1)

    previous_row = list(range(len(s2) + 1))
    for i, c1 in enumerate(s1):
        current_row = [i + 1]
        for j, c2 in enumerate(s2):
            insertions = previous_row[j + 1] + 1
            deletions = current_row[j] + 1
            substitutions = previous_row[j] + (c1 != c2)
            current_row.append(min(insertions, deletions, substitutions))
        previous_row = current_row
    return previous_row[-1]


def hamming_distance(s1: str, s2: str) -> int:
    """Computes Hamming distance between two equal-length strings."""
    if len(s1) != len(s2):
        raise ValueError("Hamming distance requires equal length strings.")
    return sum(c1 != c2 for c1, c2 in zip(s1, s2))


def jaccard_similarity(s1: str, s2: str) -> float:
    """Computes character or word set Jaccard similarity [0.0 - 1.0]."""
    set1 = set(s1.split())
    set2 = set(s2.split())
    union = set1 | set2
    if not union:
        return 1.0
    return len(set1 & set2) / len(union)


def to_base64(text: str) -> str:
    """Encodes string to base64."""
    return base64.b64encode(text.encode("utf-8")).decode("utf-8")


def from_base64(b64_str: str) -> str:
    """Decodes base64 string to utf-8 text."""
    return base64.b64decode(b64_str.encode("utf-8")).decode("utf-8")


def to_hex_str(text: str) -> str:
    """Converts string into hex representation."""
    return text.encode("utf-8").hex()


def from_hex_str(hex_str: str) -> str:
    """Decodes hex representation back to string."""
    return bytes.fromhex(hex_str).decode("utf-8")


def url_encode_str(text: str) -> str:
    """URL-encodes string parameters."""
    return urllib.parse.quote_plus(text)


def url_decode_str(text: str) -> str:
    """Decodes URL-encoded parameters."""
    return urllib.parse.unquote_plus(text)


def mask_sensitive(text: str, visible_end: int = 4, mask_char: str = "*") -> str:
    """Masks credit card numbers, passwords, or tokens except trailing characters."""
    if len(text) <= visible_end:
        return text
    return (mask_char * (len(text) - visible_end)) + text[-visible_end:]


def rot13(text: str) -> str:
    """Applies ROT13 Caesar cipher substitution."""
    import codecs
    return codecs.encode(text, 'rot_13')


def reverse_str(text: str) -> str:
    """Reverses characters in a string."""
    return text[::-1]


def contains_any(text: str, substrings: Sequence[str]) -> bool:
    """Checks if text contains any of the substrings."""
    return any(sub in text for sub in substrings)


def contains_all(text: str, substrings: Sequence[str]) -> bool:
    """Checks if text contains all of the substrings."""
    return all(sub in text for sub in substrings)
