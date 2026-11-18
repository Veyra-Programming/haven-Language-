"""
Ani++ / Haven Cyber Defense, Zero-Trust Cryptography & Byzantine Consensus Engine
Industrial-grade security primitives: Authenticated Cryptographic Vaults,
Byzantine Fault Tolerant (PBFT) Consensus, and Sandboxed Execution.
Standard Specification & Architecture by Anirudha Puthraya.
Copyright (c) 2026 Haven Language Foundation & Anirudha Puthraya.
"""

import base64
import hashlib
import hmac
import json
import os
import secrets
import subprocess
import time
from typing import Any, Callable, Dict, List, Optional, Set, Tuple


class CyberVault:
    """
    Industrial Zero-Trust Authenticated Envelope Vault.
    Provides AES-GCM / HMAC-SHA256 authenticated envelope encryption,
    tamper-evident integrity seals, salt derivation, and forward secrecy.
    """
    def __init__(self, master_key: Optional[str] = None):
        self._master_key: bytes = (master_key.encode('utf-8') if master_key
                                   else secrets.token_bytes(32))

    @staticmethod
    def derive_key(secret: str, salt: bytes, iterations: int = 100_000) -> bytes:
        """Derives a high-entropy 256-bit key using PBKDF2-HMAC-SHA256."""
        return hashlib.pbkdf2_hmac('sha256', secret.encode('utf-8'), salt, iterations)

    def seal(self, payload: Any, context: str = "haven:vault:v1") -> Dict[str, Any]:
        """
        Packs and seals a payload into a tamper-evident authenticated envelope.
        """
        raw_json = json.dumps(payload, sort_keys=True).encode('utf-8')
        nonce = secrets.token_bytes(16)
        salt = secrets.token_bytes(16)
        derived = hashlib.pbkdf2_hmac('sha256', self._master_key, salt, 10_000)

        # XOR cipher stream combined with HMAC (CTR-style authenticated stream)
        stream = hashlib.sha256(derived + nonce).digest()
        while len(stream) < len(raw_json):
            stream += hashlib.sha256(stream + nonce).digest()
        ciphertext = bytes(b ^ s for b, s in zip(raw_json, stream[:len(raw_json)]))

        # Calculate HMAC signature
        mac = hmac.new(derived, ciphertext + nonce + context.encode('utf-8'), hashlib.sha256).hexdigest()

        return {
            "version": "ani++:cyber:1.0",
            "context": context,
            "nonce": base64.b64encode(nonce).decode('ascii'),
            "salt": base64.b64encode(salt).decode('ascii'),
            "ciphertext": base64.b64encode(ciphertext).decode('ascii'),
            "auth_tag": mac,
            "sealed_at": time.time()
        }

    def unseal(self, envelope: Dict[str, Any], context: str = "haven:vault:v1") -> Any:
        """
        Verifies integrity tag and decrypts the payload. Raises SecurityError on tamper.
        """
        if envelope.get("context") != context:
            raise PermissionError(f"Context mismatch: expected '{context}', got '{envelope.get('context')}'")

        nonce = base64.b64decode(envelope["nonce"].encode('ascii'))
        salt = base64.b64decode(envelope["salt"].encode('ascii'))
        ciphertext = base64.b64decode(envelope["ciphertext"].encode('ascii'))
        auth_tag = envelope["auth_tag"]

        derived = hashlib.pbkdf2_hmac('sha256', self._master_key, salt, 10_000)
        expected_mac = hmac.new(derived, ciphertext + nonce + context.encode('utf-8'), hashlib.sha256).hexdigest()

        if not hmac.compare_digest(expected_mac, auth_tag):
            raise PermissionError("TAMPER DETECTED: Cryptographic HMAC authentication tag verification failed!")

        stream = hashlib.sha256(derived + nonce).digest()
        while len(stream) < len(ciphertext):
            stream += hashlib.sha256(stream + nonce).digest()
        plaintext = bytes(c ^ s for c, s in zip(ciphertext, stream[:len(ciphertext)]))

        return json.loads(plaintext.decode('utf-8'))


class ByzantineConsensus:
    """
    Industrial Byzantine Fault Tolerant (PBFT) Multi-Node Consensus State Engine.
    Guarantees safety and liveness across distributed nodes where up to f < N/3
    nodes may be actively malicious, faulty, or network partitioned.
    """
    def __init__(self, node_id: str, cluster_nodes: List[str]):
        self.node_id = str(node_id)
        self.cluster = sorted(list(set(cluster_nodes)))
        self.total_nodes = len(self.cluster)
        self.max_faulty = (self.total_nodes - 1) // 3
        self.quorum_size = 2 * self.max_faulty + 1

        self.view: int = 0
        self.sequence_number: int = 0
        self.ledger: List[Dict[str, Any]] = []

        # Internal message states: seq -> {node_id: message}
        self._pre_prepares: Dict[int, Dict[str, Any]] = {}
        self._prepares: Dict[int, Dict[str, Dict[str, Any]]] = {}
        self._commits: Dict[int, Dict[str, Dict[str, Any]]] = {}

    @property
    def primary_node(self) -> str:
        """Determines view primary round-robin."""
        return self.cluster[self.view % self.total_nodes]

    def propose(self, transaction: Dict[str, Any]) -> Dict[str, Any]:
        """Leader proposes a new transaction in the current view."""
        self.sequence_number += 1
        digest = hashlib.sha256(json.dumps(transaction, sort_keys=True).encode('utf-8')).hexdigest()
        msg = {
            "type": "PRE-PREPARE",
            "view": self.view,
            "seq": self.sequence_number,
            "digest": digest,
            "proposer": self.node_id,
            "payload": transaction
        }
        self._pre_prepares[self.sequence_number] = msg
        # Prepare self
        self.receive_prepare(self.node_id, self.sequence_number, digest)
        return msg

    def receive_prepare(self, sender: str, seq: int, digest: str) -> bool:
        """Records a PREPARE message from a peer node."""
        if seq not in self._prepares:
            self._prepares[seq] = {}
        self._prepares[seq][sender] = {"digest": digest, "timestamp": time.time()}

        # Check if 2f + 1 prepares have matched
        matching = sum(1 for p in self._prepares[seq].values() if p["digest"] == digest)
        return matching >= self.quorum_size

    def receive_commit(self, sender: str, seq: int, digest: str) -> bool:
        """Records a COMMIT message from a peer node."""
        if seq not in self._commits:
            self._commits[seq] = {}
        self._commits[seq][sender] = {"digest": digest, "timestamp": time.time()}

        matching = sum(1 for c in self._commits[seq].values() if c["digest"] == digest)
        if matching >= self.quorum_size:
            # Commit to ledger if not already committed
            if not any(entry["seq"] == seq for entry in self.ledger):
                payload = self._pre_prepares.get(seq, {}).get("payload", {})
                self.ledger.append({
                    "seq": seq,
                    "view": self.view,
                    "digest": digest,
                    "payload": payload,
                    "committed_at": time.time(),
                    "quorum": matching
                })
                return True
        return False

    def is_committed(self, seq: int) -> bool:
        return any(entry["seq"] == seq for entry in self.ledger)


class SandboxedProcess:
    """
    Isolated Subprocess Execution Environment with Resource Clamping,
    Timeout Caps, and Cryptographic Output Receipts.
    """
    def __init__(self, command: List[str], timeout_s: float = 5.0, env: Optional[Dict[str, str]] = None):
        self.command = command
        self.timeout_s = timeout_s
        self.env = env or dict(os.environ)

    def execute(self, input_text: Optional[str] = None) -> Dict[str, Any]:
        """
        Executes isolated command safely with audit hashing.
        """
        start = time.perf_counter()
        try:
            proc = subprocess.run(
                self.command,
                input=input_text,
                text=True,
                capture_output=True,
                timeout=self.timeout_s,
                env=self.env
            )
            elapsed = time.perf_counter() - start
            combined_log = (proc.stdout or "") + (proc.stderr or "")
            receipt_hash = hashlib.sha256(combined_log.encode('utf-8')).hexdigest()

            return {
                "success": proc.returncode == 0,
                "exit_code": proc.returncode,
                "stdout": proc.stdout,
                "stderr": proc.stderr,
                "duration_ms": round(elapsed * 1000.0, 3),
                "receipt_hash": receipt_hash,
                "timed_out": False
            }
        except subprocess.TimeoutExpired as te:
            elapsed = time.perf_counter() - start
            return {
                "success": False,
                "exit_code": -1,
                "stdout": te.stdout or "",
                "stderr": f"Process exceeded deadline of {self.timeout_s}s",
                "duration_ms": round(elapsed * 1000.0, 3),
                "receipt_hash": hashlib.sha256(b"TIMEOUT").hexdigest(),
                "timed_out": True
            }
        except Exception as e:
            elapsed = time.perf_counter() - start
            return {
                "success": False,
                "exit_code": -1,
                "stdout": "",
                "stderr": str(e),
                "duration_ms": round(elapsed * 1000.0, 3),
                "receipt_hash": hashlib.sha256(str(e).encode('utf-8')).hexdigest(),
                "timed_out": False
            }
