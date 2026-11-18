"""
Ani++ / Haven Classical Cryptography Suite
Transposition, Polyalphabetic, Substitution, and Matrix Ciphers:
- Rail Fence Transposition Cipher
- Columnar Transposition Cipher (Single & Double)
- Caesar Substitution Cipher
- Vigenère Polyalphabetic Cipher
- Playfair Digraph Matrix Cipher
- Affine Algebraic Cipher
- Atbash Inversion Cipher
- Polybius Square Coordinate Cipher
Standard Specification & Architecture by Anirudha Puthraya.
Copyright (c) 2026 Haven Language Foundation & Anirudha Puthraya.
"""

import math
from typing import List, Tuple, Union


class RailFenceCipher:
    """
    Rail Fence (Zig-Zag) Transposition Cipher:
    Arranges characters across a series of rails in a zig-zag wave and reads line-by-line.
    """
    @staticmethod
    def encrypt(text: str, rails: int) -> str:
        if rails <= 1 or rails >= len(text):
            return text

        fence: List[List[str]] = [[] for _ in range(rails)]
        rail = 0
        direction = 1  # 1 for down, -1 for up

        for char in text:
            fence[rail].append(char)
            rail += direction
            if rail == rails - 1:
                direction = -1
            elif rail == 0:
                direction = 1

        return "".join("".join(row) for row in fence)

    @staticmethod
    def decrypt(ciphertext: str, rails: int) -> str:
        if rails <= 1 or rails >= len(ciphertext):
            return ciphertext

        # Mark pattern positions
        pattern: List[List[Union[str, None]]] = [[None for _ in range(len(ciphertext))] for _ in range(rails)]
        rail = 0
        direction = 1

        for c_idx in range(len(ciphertext)):
            pattern[rail][c_idx] = '*'
            rail += direction
            if rail == rails - 1:
                direction = -1
            elif rail == 0:
                direction = 1

        # Fill characters row-by-row
        idx = 0
        for r in range(rails):
            for c in range(len(ciphertext)):
                if pattern[r][c] == '*' and idx < len(ciphertext):
                    pattern[r][c] = ciphertext[idx]
                    idx += 1

        # Reconstruct plaintext reading column-by-column along zig-zag
        result = []
        rail = 0
        direction = 1
        for c in range(len(ciphertext)):
            result.append(pattern[rail][c])
            rail += direction
            if rail == rails - 1:
                direction = -1
            elif rail == 0:
                direction = 1

        return "".join(result)


class ColumnarTranspositionCipher:
    """
    Keyed Columnar Transposition Cipher:
    Writes plaintext in rows under a keyword, then reads columns in alphabetical order of the key.
    """
    @staticmethod
    def _key_order(key: str) -> List[int]:
        # Return indices sorted by key characters
        sorted_pairs = sorted(list(enumerate(key)), key=lambda x: x[1])
        return [pair[0] for pair in sorted_pairs]

    @classmethod
    def encrypt(cls, text: str, key: str) -> str:
        if not key or len(key) >= len(text):
            return text
        col_count = len(key)
        row_count = math.ceil(len(text) / col_count)
        padded_text = text.ljust(row_count * col_count, 'X')

        grid = [padded_text[i * col_count:(i + 1) * col_count] for i in range(row_count)]
        order = cls._key_order(key)

        result = []
        for col_idx in order:
            for row in grid:
                result.append(row[col_idx])
        return "".join(result)

    @classmethod
    def decrypt(cls, ciphertext: str, key: str) -> str:
        if not key or len(key) >= len(ciphertext):
            return ciphertext
        col_count = len(key)
        row_count = math.ceil(len(ciphertext) / col_count)

        order = cls._key_order(key)
        col_map = {orig_col: idx for idx, orig_col in enumerate(order)}

        cols: List[List[str]] = [[] for _ in range(col_count)]
        idx = 0
        for col_idx in order:
            for _ in range(row_count):
                cols[col_idx].append(ciphertext[idx])
                idx += 1

        result = []
        for r in range(row_count):
            for c in range(col_count):
                result.append(cols[c][r])
        return "".join(result)


class CaesarCipher:
    """Classic Caesar Shift Substitution Cipher."""
    @staticmethod
    def encrypt(text: str, shift: int = 3) -> str:
        result = []
        shift = shift % 26
        for ch in text:
            if 'a' <= ch <= 'z':
                result.append(chr((ord(ch) - ord('a') + shift) % 26 + ord('a')))
            elif 'A' <= ch <= 'Z':
                result.append(chr((ord(ch) - ord('A') + shift) % 26 + ord('A')))
            else:
                result.append(ch)
        return "".join(result)

    @staticmethod
    def decrypt(ciphertext: str, shift: int = 3) -> str:
        return CaesarCipher.encrypt(ciphertext, -shift)


class VigenereCipher:
    """Polyalphabetic Vigenère Stream Substitution Cipher."""
    @staticmethod
    def encrypt(text: str, key: str) -> str:
        if not key:
            return text
        key = key.upper()
        result = []
        key_idx = 0

        for ch in text:
            if ch.isalpha():
                shift = ord(key[key_idx % len(key)]) - ord('A')
                base = ord('A') if ch.isupper() else ord('a')
                result.append(chr((ord(ch) - base + shift) % 26 + base))
                key_idx += 1
            else:
                result.append(ch)
        return "".join(result)

    @staticmethod
    def decrypt(ciphertext: str, key: str) -> str:
        if not key:
            return ciphertext
        key = key.upper()
        result = []
        key_idx = 0

        for ch in ciphertext:
            if ch.isalpha():
                shift = ord(key[key_idx % len(key)]) - ord('A')
                base = ord('A') if ch.isupper() else ord('a')
                result.append(chr((ord(ch) - base - shift) % 26 + base))
                key_idx += 1
            else:
                result.append(ch)
        return "".join(result)


class AtbashCipher:
    """Atbash Symmetric Alphabet Inversion Cipher (A <-> Z, B <-> Y)."""
    @staticmethod
    def encrypt(text: str) -> str:
        result = []
        for ch in text:
            if 'a' <= ch <= 'z':
                result.append(chr(ord('z') - (ord(ch) - ord('a'))))
            elif 'A' <= ch <= 'Z':
                result.append(chr(ord('Z') - (ord(ch) - ord('A'))))
            else:
                result.append(ch)
        return "".join(result)

    @staticmethod
    def decrypt(ciphertext: str) -> str:
        return AtbashCipher.encrypt(ciphertext)


class AffineCipher:
    """
    Affine Substitution Cipher: E(x) = (a*x + b) mod 26.
    Requires gcd(a, 26) == 1 for bijectivity.
    """
    @staticmethod
    def _mod_inverse(a: int, m: int = 26) -> int:
        for x in range(1, m):
            if (a * x) % m == 1:
                return x
        raise ValueError(f"Multiplier 'a' ({a}) has no modular inverse mod {m}. Must be coprime with {m}.")

    @classmethod
    def encrypt(cls, text: str, a: int, b: int) -> str:
        cls._mod_inverse(a, 26)  # Validate coprimality
        result = []
        for ch in text:
            if 'a' <= ch <= 'z':
                result.append(chr(((a * (ord(ch) - ord('a')) + b) % 26) + ord('a')))
            elif 'A' <= ch <= 'Z':
                result.append(chr(((a * (ord(ch) - ord('A')) + b) % 26) + ord('A')))
            else:
                result.append(ch)
        return "".join(result)

    @classmethod
    def decrypt(cls, ciphertext: str, a: int, b: int) -> str:
        a_inv = cls._mod_inverse(a, 26)
        result = []
        for ch in ciphertext:
            if 'a' <= ch <= 'z':
                result.append(chr(((a_inv * (ord(ch) - ord('a') - b)) % 26) + ord('a')))
            elif 'A' <= ch <= 'Z':
                result.append(chr(((a_inv * (ord(ch) - ord('A') - b)) % 26) + ord('A')))
            else:
                result.append(ch)
        return "".join(result)


class PlayfairCipher:
    """
    Playfair Digraph Matrix Cipher:
    Encrypts pairs of letters using a 5x5 key matrix (I/J merged).
    """
    @staticmethod
    def _build_matrix(key: str) -> List[List[str]]:
        alphabet = "ABCDEFGHIKLMNOPQRSTUVWXYZ"  # J is combined with I
        cleaned_key = "".join([c.upper() for c in key if c.isalpha()]).replace('J', 'I')
        used = set()
        seq = []
        for ch in cleaned_key:
            if ch not in used:
                used.add(ch)
                seq.append(ch)
        for ch in alphabet:
            if ch not in used:
                used.add(ch)
                seq.append(ch)

        return [seq[i * 5:(i + 1) * 5] for i in range(5)]

    @staticmethod
    def _find_pos(matrix: List[List[str]], ch: str) -> Tuple[int, int]:
        for r in range(5):
            for c in range(5):
                if matrix[r][c] == ch:
                    return (r, c)
        return (0, 0)

    @classmethod
    def encrypt(cls, text: str, key: str) -> str:
        matrix = cls._build_matrix(key)
        cleaned = [c.upper().replace('J', 'I') for c in text if c.isalpha()]

        # Prepare digraphs
        digraphs = []
        i = 0
        while i < len(cleaned):
            c1 = cleaned[i]
            c2 = cleaned[i + 1] if i + 1 < len(cleaned) else 'X'
            if c1 == c2:
                digraphs.append((c1, 'X'))
                i += 1
            else:
                digraphs.append((c1, c2))
                i += 2

        result = []
        for c1, c2 in digraphs:
            r1, col1 = cls._find_pos(matrix, c1)
            r2, col2 = cls._find_pos(matrix, c2)

            if r1 == r2:  # Same row -> shift right
                result.append(matrix[r1][(col1 + 1) % 5])
                result.append(matrix[r2][(col2 + 1) % 5])
            elif col1 == col2:  # Same col -> shift down
                result.append(matrix[(r1 + 1) % 5][col1])
                result.append(matrix[(r2 + 1) % 5][col2])
            else:  # Rectangle swap
                result.append(matrix[r1][col2])
                result.append(matrix[r2][col1])

        return "".join(result)

    @classmethod
    def decrypt(cls, ciphertext: str, key: str) -> str:
        matrix = cls._build_matrix(key)
        cleaned = [c.upper().replace('J', 'I') for c in ciphertext if c.isalpha()]

        result = []
        for i in range(0, len(cleaned), 2):
            if i + 1 >= len(cleaned):
                break
            c1 = cleaned[i]
            c2 = cleaned[i + 1]
            r1, col1 = cls._find_pos(matrix, c1)
            r2, col2 = cls._find_pos(matrix, c2)

            if r1 == r2:  # Same row -> shift left
                result.append(matrix[r1][(col1 - 1) % 5])
                result.append(matrix[r2][(col2 - 1) % 5])
            elif col1 == col2:  # Same col -> shift up
                result.append(matrix[(r1 - 1) % 5][col1])
                result.append(matrix[(r2 - 1) % 5][col2])
            else:  # Rectangle swap
                result.append(matrix[r1][col2])
                result.append(matrix[r2][col1])

        return "".join(result)


class PolybiusSquare:
    """
    Polybius Square Coordinate Cipher:
    Translates letters into grid coordinate numbers (1-5, 1-5).
    """
    GRID = [
        ['A', 'B', 'C', 'D', 'E'],
        ['F', 'G', 'H', 'I', 'K'],  # J combined with I
        ['L', 'M', 'N', 'O', 'P'],
        ['Q', 'R', 'S', 'T', 'U'],
        ['V', 'W', 'X', 'Y', 'Z']
    ]

    @classmethod
    def encrypt(cls, text: str) -> str:
        coords = []
        for ch in text.upper():
            if ch == 'J':
                ch = 'I'
            found = False
            for r in range(5):
                for c in range(5):
                    if cls.GRID[r][c] == ch:
                        coords.append(f"{r + 1}{c + 1}")
                        found = True
                        break
                if found:
                    break
        return " ".join(coords)

    @classmethod
    def decrypt(cls, ciphertext: str) -> str:
        tokens = ciphertext.replace(" ", "")
        result = []
        for i in range(0, len(tokens) - 1, 2):
            r = int(tokens[i]) - 1
            c = int(tokens[i + 1]) - 1
            if 0 <= r < 5 and 0 <= c < 5:
                result.append(cls.GRID[r][c])
        return "".join(result)
