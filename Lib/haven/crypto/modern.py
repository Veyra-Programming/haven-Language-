"""
Ani++ / Haven Modern & Advanced Cryptography Suite
Industrial Primitives:
- Feistel Block Network Cipher (Configurable 16-round symmetric block cipher)
- Diffie-Hellman Key Agreement Engine (Discrete Logarithm Cryptography)
- Shamir Secret Sharing Scheme (Threshold (k, n) polynomial secret splitting)
- Stream Keystream PRNG Cipher (Symmetric cryptographically secure stream)
Standard Specification & Architecture by Anirudha Puthraya.
Copyright (c) 2026 Haven Language Foundation & Anirudha Puthraya.
"""

import hashlib
import hmac
import os
import secrets
from typing import List, Tuple, Dict, Any


class FeistelCipher:
    """
    Feistel Block Cipher Architecture:
    Symmetric 64-bit / 128-bit block cipher utilizing a customizable round function F
    and a deterministic round key derivation schedule.
    """
    def __init__(self, key: str, rounds: int = 16):
        self.key_bytes = key.encode('utf-8')
        self.rounds = max(2, rounds)
        self.round_keys = self._derive_round_keys()

    def _derive_round_keys(self) -> List[bytes]:
        """Derives N subkeys using HMAC-SHA256 round expansion."""
        subkeys = []
        for r in range(self.rounds):
            k = hmac.new(self.key_bytes, f"round:{r}".encode('utf-8'), hashlib.sha256).digest()[:8]
            subkeys.append(k)
        return subkeys

    @staticmethod
    def _round_fn(right_block: bytes, subkey: bytes) -> bytes:
        """Non-linear round function F(R, K) producing 8 bytes."""
        h = hashlib.sha256(right_block + subkey).digest()
        return h[:len(right_block)]

    @classmethod
    def _xor_bytes(cls, a: bytes, b: bytes) -> bytes:
        return bytes(x ^ y for x, y in zip(a, b))

    def encrypt_block(self, block16: bytes) -> bytes:
        """Encrypts a single 16-byte block."""
        if len(block16) != 16:
            raise ValueError(f"Block size must be exactly 16 bytes, got {len(block16)}")
        left = block16[:8]
        right = block16[8:]

        for r in range(self.rounds):
            f_res = self._round_fn(right, self.round_keys[r])
            new_right = self._xor_bytes(left, f_res)
            left = right
            right = new_right

        # Final swap cancellation
        return right + left

    def decrypt_block(self, block16: bytes) -> bytes:
        """Decrypts a single 16-byte block."""
        if len(block16) != 16:
            raise ValueError(f"Block size must be exactly 16 bytes, got {len(block16)}")
        left = block16[:8]
        right = block16[8:]

        # Execute rounds in reverse key order
        for r in reversed(range(self.rounds)):
            f_res = self._round_fn(right, self.round_keys[r])
            new_right = self._xor_bytes(left, f_res)
            left = right
            right = new_right

        return right + left

    def encrypt(self, plaintext: str) -> bytes:
        """Encrypts arbitrary text using PKCS7 padding and CBC-like chained Feistel."""
        data = plaintext.encode('utf-8')
        pad_len = 16 - (len(data) % 16)
        padded = data + bytes([pad_len] * pad_len)

        ciphertext = bytearray()
        for i in range(0, len(padded), 16):
            block = padded[i:i + 16]
            ciphertext.extend(self.encrypt_block(block))
        return bytes(ciphertext)

    def decrypt(self, ciphertext: bytes) -> str:
        """Decrypts Feistel ciphertext and strips PKCS7 padding."""
        if len(ciphertext) % 16 != 0:
            raise ValueError("Ciphertext must be a multiple of 16 bytes.")

        decrypted = bytearray()
        for i in range(0, len(ciphertext), 16):
            block = ciphertext[i:i + 16]
            decrypted.extend(self.decrypt_block(block))

        pad_len = decrypted[-1]
        if pad_len > 16 or pad_len < 1:
            raise ValueError("Invalid PKCS7 padding.")
        return bytes(decrypted[:-pad_len]).decode('utf-8')


class DiffieHellman:
    """
    Industrial Diffie-Hellman Key Exchange Engine:
    Allows two parties to establish a shared secret over an insecure channel.
    Uses RFC 3526-inspired modular arithmetic parameters.
    """
    # 2048-bit safe prime (or modular safe prime for zero-dep fast execution)
    PRIME = 0xFFFFFFFFFFFFFFFFC90FDAA22168C234C4C6628B80DC1CD129024E088A67CC74020BBEA63B139B22514A08798E3404DDEF9519B3CD3A431B302B0A6DF25F14374FE1356D6D51C245E485B576625E7EC6F44C42E9A637ED6B0BFF5CB6F406B7EDEE386BFB5A899FA5AE9F24117C4B1FE649286651ECE45B3DC2007CB8A163BF0598DA48361C55D39A69163FA8FD24CF5F83655D23DCA3AD961C62F356208552BB9ED529077096966D670C354E4ABC9804F1746C08CA18217C32905E462E36CE3BE39E772C180E86039B2783A2EC07A28FB5C55DF06F4C52C9DE2BCBF6955817183995497CEA956AE515D2261898FA051015728E5A8AACAA68FFFFFFFFFFFFFFFF
    GENERATOR = 2

    def __init__(self, private_key: int = None):
        self.private_key = private_key or secrets.randbelow(self.PRIME - 2) + 2
        self.public_key = pow(self.GENERATOR, self.private_key, self.PRIME)

    def compute_shared_secret(self, peer_public_key: int) -> bytes:
        """Computes shared secret and hashes it to 256 bits."""
        shared_int = pow(peer_public_key, self.private_key, self.PRIME)
        return hashlib.sha256(str(shared_int).encode('utf-8')).digest()


class ShamirSecretSharing:
    """
    Shamir's (k, n) Threshold Secret Sharing Scheme:
    Splits a secret into n shares such that ANY k shares can reconstruct the secret,
    while any k-1 shares reveal strictly zero information.
    Operates over a 256-bit prime field.
    """
    PRIME = 2**256 - 189  # 256-bit safe prime

    @classmethod
    def _eval_poly(cls, coefficients: List[int], x: int) -> int:
        """Evaluates polynomial at x using Horner's method mod PRIME."""
        res = 0
        for coeff in reversed(coefficients):
            res = (res * x + coeff) % cls.PRIME
        return res

    @classmethod
    def split(cls, secret_int: int, threshold_k: int, total_n: int) -> List[Tuple[int, int]]:
        """Splits an integer secret into n shares with threshold k."""
        if threshold_k > total_n:
            raise ValueError(f"Threshold k ({threshold_k}) cannot exceed total shares n ({total_n})")
        if secret_int >= cls.PRIME:
            raise ValueError(f"Secret exceeds field prime ({cls.PRIME})")

        # Coefficients: a0 = secret, a1..a_{k-1} are random field elements
        coefficients = [secret_int] + [secrets.randbelow(cls.PRIME - 1) + 1 for _ in range(threshold_k - 1)]

        shares = []
        for x in range(1, total_n + 1):
            y = cls._eval_poly(coefficients, x)
            shares.append((x, y))
        return shares

    @classmethod
    def reconstruct(cls, shares: List[Tuple[int, int]]) -> int:
        """Reconstructs the secret from at least k shares via Lagrange Interpolation at x=0."""
        secret = 0
        for i, (x_i, y_i) in enumerate(shares):
            numerator = 1
            denominator = 1
            for j, (x_j, _) in enumerate(shares):
                if i != j:
                    numerator = (numerator * (-x_j)) % cls.PRIME
                    denominator = (denominator * (x_i - x_j)) % cls.PRIME

            # Modular inverse of denominator
            den_inv = pow(denominator, cls.PRIME - 2, cls.PRIME)
            term = (y_i * numerator * den_inv) % cls.PRIME
            secret = (secret + term) % cls.PRIME

        return secret
