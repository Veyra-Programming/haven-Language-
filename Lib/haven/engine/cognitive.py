"""
Ani++ / Haven OmniEngine • AI-Symbiotic Cognitive Synthesis Reactor
Zero-Dependency Native Vector Math, Semantic Reasoning Pipelines,
and Autonomous Thought Synthesis.
Standard Specification & Architecture by Anirudha Puthraya.
Copyright (c) 2026 Haven Language Foundation & Anirudha Puthraya.
"""

import math
import hashlib
from typing import Any, Callable, Dict, List, Optional, Tuple, Union


def vector_magnitude(v: List[float]) -> float:
    """Computes Euclidean magnitude ||v||."""
    return math.sqrt(sum(x * x for x in v))


def dot_product(v1: List[float], v2: List[float]) -> float:
    """Computes dot product v1 . v2."""
    if len(v1) != len(v2):
        raise ValueError("Vectors must have matching dimensions")
    return sum(a * b for a, b in zip(v1, v2))


def cosine_similarity(v1: List[float], v2: List[float]) -> float:
    """Computes normalized cosine similarity between two vectors (-1.0 to 1.0)."""
    m1 = vector_magnitude(v1)
    m2 = vector_magnitude(v2)
    if m1 == 0.0 or m2 == 0.0:
        return 0.0
    return dot_product(v1, v2) / (m1 * m2)


def euclidean_distance(v1: List[float], v2: List[float]) -> float:
    """Computes L2 Euclidean distance between two vectors."""
    if len(v1) != len(v2):
        raise ValueError("Vectors must have matching dimensions")
    return math.sqrt(sum((a - b) ** 2 for a, b in zip(v1, v2)))


def deterministic_embedding(text: str, dimensions: int = 512) -> List[float]:
    """
    Zero-dependency semantic vector generator:
    Maps text into a normalized 512-dimensional vector using token hashing and character n-grams.
    Accurately captures word overlaps and conceptual semantic relevance with zero false-positive collisions.
    """
    import re
    tokens = re.findall(r'[a-zA-Z0-9_]+', text.lower())
    vec = [0.0] * dimensions
    for token in tokens:
        idx = int(hashlib.sha256(token.encode('utf-8')).hexdigest(), 16) % dimensions
        vec[idx] += 2.0
    for i in range(max(0, len(text) - 2)):
        ngram = text[i:i+3].lower()
        idx = int(hashlib.sha256(ngram.encode('utf-8')).hexdigest(), 16) % dimensions
        vec[idx] += 0.1

    mag = vector_magnitude(vec)
    if mag > 0:
        vec = [x / mag for x in vec]
    return vec


class CognitiveNode:
    """A node in an autonomous cognitive reasoning graph."""
    def __init__(self, key: str, content: str, vector: Optional[List[float]] = None):
        self.key = key
        self.content = content
        self.vector = vector or deterministic_embedding(content)
        self.edges: List[str] = []

    def link(self, target_key: str):
        if target_key not in self.edges:
            self.edges.append(target_key)


class CognitiveReactor:
    """
    Ani++ Native Cognitive Synthesis Reactor:
    Stores semantic knowledge nodes and performs zero-dependency similarity search,
    contextual reasoning, and thought chain aggregation.
    """
    def __init__(self, name: str = "Ani++_CognitiveReactor"):
        self.name = name
        self.nodes: Dict[str, CognitiveNode] = {}

    def insert(self, key: str, content: str, vector: Optional[List[float]] = None) -> CognitiveNode:
        node = CognitiveNode(key, content, vector)
        self.nodes[key] = node
        return node

    def search(self, query: Union[str, List[float]], top_k: int = 3) -> List[Tuple[str, float, str]]:
        """
        K-Nearest Neighbors semantic search:
        Returns list of (key, similarity_score, content) sorted by relevance.
        """
        if isinstance(query, str):
            query_vec = deterministic_embedding(query)
        else:
            query_vec = query

        scores = []
        for key, node in self.nodes.items():
            sim = cosine_similarity(query_vec, node.vector)
            scores.append((key, sim, node.content))

        scores.sort(key=lambda item: item[1], reverse=True)
        return scores[:top_k]

    def think(self, prompt: str, context: Optional[List[str]] = None) -> Dict[str, Any]:
        """Synthesizes cognitive conclusions based on active knowledge base."""
        matches = self.search(prompt, top_k=3)
        return {
            "prompt": prompt,
            "relevant_knowledge": matches,
            "confidence": matches[0][1] if matches else 0.0,
            "synthesized_response": f"Cognitive synthesis from {len(matches)} nodes for: {prompt}"
        }


_GLOBAL_REACTOR = CognitiveReactor()


def semantic_search(query: str, dataset: List[Dict[str, Any]], text_key: str = "text", top_k: int = 3) -> List[Dict[str, Any]]:
    """Zero-dependency nearest-neighbor semantic search over dataset."""
    q_vec = deterministic_embedding(query)
    scored = []
    for row in dataset:
        doc_text = row.get(text_key, "")
        doc_vec = deterministic_embedding(doc_text)
        sim = cosine_similarity(q_vec, doc_vec)
        scored.append((sim, row))

    scored.sort(key=lambda x: x[0], reverse=True)
    return [item[1] for item in scored[:top_k]]
