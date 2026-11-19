"""
Ani++ & Haven Deep Learning, Autograd & AI Engine (ani.ai / haven.ai)
Standard: Open Digital Continuity Standard (ODCS) Cognitive Logic Spec
Architecture & Specification: Anirudha Puthraya
Copyright (c) 2026 Haven Language Foundation & Anirudha Puthraya.

Provides a pure, zero-dependency Autograd Neural Network framework,
loss functions, Adam optimizer, BPE Subword Tokenizer, and K-Means Clustering.
"""

import math
import random
from typing import List, Set, Tuple, Dict, Optional, Union, Callable, Any


class Value:
    """Scalar Autograd Value supporting reverse-mode automatic differentiation."""

    def __init__(self, data: float, _children: Tuple["Value", ...] = (), _op: str = "", label: str = ""):
        self.data = float(data)
        self.grad = 0.0
        self._backward: Callable[[], None] = lambda: None
        self._prev = set(_children)
        self._op = _op
        self.label = label

    def __add__(self, other: Union["Value", float, int]) -> "Value":
        other = other if isinstance(other, Value) else Value(other)
        out = Value(self.data + other.data, (self, other), "+")

        def _backward():
            self.grad += out.grad
            other.grad += out.grad
        out._backward = _backward
        return out

    def __radd__(self, other: Union[float, int]) -> "Value":
        return self + other

    def __sub__(self, other: Union["Value", float, int]) -> "Value":
        return self + (-other)

    def __rsub__(self, other: Union[float, int]) -> "Value":
        return Value(other) - self

    def __mul__(self, other: Union["Value", float, int]) -> "Value":
        other = other if isinstance(other, Value) else Value(other)
        out = Value(self.data * other.data, (self, other), "*")

        def _backward():
            self.grad += other.data * out.grad
            other.grad += self.data * out.grad
        out._backward = _backward
        return out

    def __rmul__(self, other: Union[float, int]) -> "Value":
        return self * other

    def __truediv__(self, other: Union["Value", float, int]) -> "Value":
        other = other if isinstance(other, Value) else Value(other)
        return self * (other ** -1)

    def __rtruediv__(self, other: Union[float, int]) -> "Value":
        return Value(other) / self

    def __neg__(self) -> "Value":
        return self * -1.0

    def __pow__(self, other: Union[int, float]) -> "Value":
        if not isinstance(other, (int, float)):
            raise TypeError("Power exponent must be int or float.")
        out = Value(self.data ** other, (self,), f"**{other}")

        def _backward():
            self.grad += (other * (self.data ** (other - 1))) * out.grad
        out._backward = _backward
        return out

    def relu(self) -> "Value":
        """Rectified Linear Unit activation: max(0, x)."""
        out = Value(self.data if self.data > 0 else 0.0, (self,), "ReLU")

        def _backward():
            self.grad += (1.0 if out.data > 0 else 0.0) * out.grad
        out._backward = _backward
        return out

    def sigmoid(self) -> "Value":
        """Sigmoid activation: 1 / (1 + exp(-x))."""
        sig = 1.0 / (1.0 + math.exp(-max(-500.0, min(500.0, self.data))))
        out = Value(sig, (self,), "Sigmoid")

        def _backward():
            self.grad += (sig * (1.0 - sig)) * out.grad
        out._backward = _backward
        return out

    def tanh(self) -> "Value":
        """Hyperbolic tangent activation."""
        t = math.tanh(max(-500.0, min(500.0, self.data)))
        out = Value(t, (self,), "Tanh")

        def _backward():
            self.grad += (1.0 - t ** 2) * out.grad
        out._backward = _backward
        return out

    def backward(self):
        """Topological reverse-mode automatic differentiation DAG traversal."""
        topo: List[Value] = []
        visited: Set[Value] = set()

        def build_topo(v: Value):
            if v not in visited:
                visited.add(v)
                for child in v._prev:
                    build_topo(child)
                topo.append(v)

        build_topo(self)
        self.grad = 1.0
        for node in reversed(topo):
            node._backward()

    def __repr__(self) -> str:
        return f"Value(data={self.data:.4f}, grad={self.grad:.4f})"


class Neuron:
    """A single artificial neuron with weights and bias."""

    def __init__(self, nin: int, nonlin: str = "relu"):
        # Xavier/He initialization
        scale = math.sqrt(2.0 / nin)
        self.w = [Value(random.gauss(0.0, scale)) for _ in range(nin)]
        self.b = Value(0.0)
        self.nonlin = nonlin

    def __call__(self, x: List[Union[Value, float]]) -> Value:
        act = sum((wi * xi for wi, xi in zip(self.w, x)), self.b)
        if self.nonlin == "relu":
            return act.relu()
        elif self.nonlin == "sigmoid":
            return act.sigmoid()
        elif self.nonlin == "tanh":
            return act.tanh()
        return act

    def parameters(self) -> List[Value]:
        return self.w + [self.b]


class Layer:
    """A fully connected neural network layer."""

    def __init__(self, nin: int, nout: int, nonlin: str = "relu"):
        self.neurons = [Neuron(nin, nonlin=nonlin) for _ in range(nout)]

    def __call__(self, x: List[Union[Value, float]]) -> List[Value]:
        return [n(x) for n in self.neurons]

    def parameters(self) -> List[Value]:
        return [p for n in self.neurons for p in n.parameters()]


class MLP:
    """Multi-Layer Perceptron neural network architecture."""

    def __init__(self, nin: int, nouts: List[int], activations: Optional[List[str]] = None):
        sz = [nin] + nouts
        if activations is None:
            activations = ["relu"] * (len(nouts) - 1) + ["linear"]
        self.layers = [
            Layer(sz[i], sz[i + 1], nonlin=activations[i])
            for i in range(len(nouts))
        ]

    def __call__(self, x: List[Union[Value, float]]) -> Union[Value, List[Value]]:
        out = x
        for layer in self.layers:
            out = layer(out)
        return out[0] if len(out) == 1 else out

    def parameters(self) -> List[Value]:
        return [p for layer in self.layers for p in layer.parameters()]

    def zero_grad(self):
        for p in self.parameters():
            p.grad = 0.0


class Adam:
    """Adam Adaptive Moment Estimation optimizer."""

    def __init__(self, parameters: List[Value], lr: float = 0.01, beta1: float = 0.9, beta2: float = 0.999, eps: float = 1e-8):
        self.params = parameters
        self.lr = lr
        self.beta1 = beta1
        self.beta2 = beta2
        self.eps = eps
        self.m = [0.0] * len(parameters)
        self.v = [0.0] * len(parameters)
        self.t = 0

    def step(self):
        self.t += 1
        for i, p in enumerate(self.params):
            g = p.grad
            self.m[i] = self.beta1 * self.m[i] + (1.0 - self.beta1) * g
            self.v[i] = self.beta2 * self.v[i] + (1.0 - self.beta2) * (g * g)
            m_hat = self.m[i] / (1.0 - (self.beta1 ** self.t))
            v_hat = self.v[i] / (1.0 - (self.beta2 ** self.t))
            p.data -= self.lr * m_hat / (math.sqrt(v_hat) + self.eps)


def mse_loss(preds: List[Value], targets: List[float]) -> Value:
    """Mean Squared Error Loss."""
    return sum([(p - t) ** 2 for p, t in zip(preds, targets)]) * (1.0 / len(preds))


class BpeTokenizer:
    """Byte-Pair Encoding (BPE) subword tokenizer for NLP and LLM systems."""

    def __init__(self):
        self.merges: List[Tuple[str, str]] = []
        self.vocab: Dict[str, int] = {}
        self.inv_vocab: Dict[int, str] = {}

    def train(self, text: str, max_merges: int = 50):
        words = text.strip().split()
        splits = {w: [c for c in w] + ["</w>"] for w in set(words)}
        freqs = {w: words.count(w) for w in splits}

        for _ in range(max_merges):
            pairs: Dict[Tuple[str, str], int] = {}
            for w, split in splits.items():
                count = freqs[w]
                for i in range(len(split) - 1):
                    p = (split[i], split[i + 1])
                    pairs[p] = pairs.get(p, 0) + count
            if not pairs:
                break
            best_pair = max(pairs, key=lambda k: pairs[k])
            self.merges.append(best_pair)
            p1, p2 = best_pair
            new_splits = {}
            for w, split in splits.items():
                new_split = []
                i = 0
                while i < len(split):
                    if i < len(split) - 1 and split[i] == p1 and split[i + 1] == p2:
                        new_split.append(p1 + p2)
                        i += 2
                    else:
                        new_split.append(split[i])
                        i += 1
                new_splits[w] = new_split
            splits = new_splits

        # Build vocabulary
        vocab_set = {"<PAD>", "<UNK>", "</w>"}
        for split in splits.values():
            vocab_set.update(split)
        self.vocab = {tok: idx for idx, tok in enumerate(sorted(vocab_set))}
        self.inv_vocab = {idx: tok for tok, idx in self.vocab.items()}

    def encode(self, text: str) -> List[int]:
        tokens = []
        for word in text.strip().split():
            chars = [c for c in word] + ["</w>"]
            for p1, p2 in self.merges:
                new_chars = []
                i = 0
                while i < len(chars):
                    if i < len(chars) - 1 and chars[i] == p1 and chars[i + 1] == p2:
                        new_chars.append(p1 + p2)
                        i += 2
                    else:
                        new_chars.append(chars[i])
                        i += 1
                chars = new_chars
            unk_idx = self.vocab.get("<UNK>", 1)
            tokens.extend([self.vocab.get(tok, unk_idx) for tok in chars])
        return tokens

    def decode(self, token_ids: List[int]) -> str:
        words = []
        curr = ""
        for tid in token_ids:
            tok = self.inv_vocab.get(tid, "")
            if tok == "</w>":
                words.append(curr)
                curr = ""
            elif tok.endswith("</w>"):
                curr += tok[:-4]
                words.append(curr)
                curr = ""
            else:
                curr += tok
        if curr:
            words.append(curr)
        return " ".join(words)


class KMeans:
    """Zero-dependency K-Means clustering engine."""

    def __init__(self, k: int = 3, max_iters: int = 100):
        self.k = k
        self.max_iters = max_iters
        self.centroids: List[List[float]] = []

    def fit(self, data: List[List[float]], seed: Optional[int] = None) -> "KMeans":
        if seed is not None:
            random.seed(seed)
        if not data or len(data) < self.k:
            raise ValueError(f"Data points ({len(data)}) must be >= k ({self.k})")

        # Pick random initial centroids
        self.centroids = [list(pt) for pt in random.sample(data, self.k)]
        dim = len(data[0])

        for _ in range(self.max_iters):
            clusters: List[List[List[float]]] = [[] for _ in range(self.k)]
            for pt in data:
                best_idx = 0
                min_dist = float("inf")
                for c_idx, c in enumerate(self.centroids):
                    d = sum((a - b) ** 2 for a, b in zip(pt, c))
                    if d < min_dist:
                        min_dist = d
                        best_idx = c_idx
                clusters[best_idx].append(pt)

            new_centroids = []
            for c_idx, cluster in enumerate(clusters):
                if cluster:
                    mean_pt = [sum(pt[d] for pt in cluster) / len(cluster) for d in range(dim)]
                    new_centroids.append(mean_pt)
                else:
                    new_centroids.append(self.centroids[c_idx])

            if new_centroids == self.centroids:
                break
            self.centroids = new_centroids
        return self

    def predict(self, points: List[List[float]]) -> List[int]:
        labels = []
        for pt in points:
            best_idx = 0
            min_dist = float("inf")
            for c_idx, c in enumerate(self.centroids):
                d = sum((a - b) ** 2 for a, b in zip(pt, c))
                if d < min_dist:
                    min_dist = d
                    best_idx = c_idx
            labels.append(best_idx)
        return labels
