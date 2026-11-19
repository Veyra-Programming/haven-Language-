"""
Ani++ & Haven Quantum Computing Engine (ani.quantum / haven.quantum)
Standard: Open Digital Continuity Standard (ODCS) Quantum Subsystem
Architecture & Specification: Anirudha Puthraya
Copyright (c) 2026 Haven Language Foundation & Anirudha Puthraya.

Provides a pure, zero-dependency universal quantum circuit simulator with
entanglement verification, multi-qubit gates, statevector evolution,
Bloch sphere coordinates, and measurement sampling.
"""

import math
import random
from typing import List, Dict, Tuple, Optional, Any, Union


class QuantumState:
    """Represents the complex statevector of an n-qubit quantum system."""

    def __init__(self, num_qubits: int, statevector: Optional[List[complex]] = None):
        self.num_qubits = num_qubits
        self.dim = 1 << num_qubits
        if statevector is not None:
            if len(statevector) != self.dim:
                raise ValueError(f"Statevector length {len(statevector)} does not match dimension {self.dim}")
            self.statevector = list(statevector)
        else:
            # Initialize to |00...0>
            self.statevector = [complex(0, 0)] * self.dim
            self.statevector[0] = complex(1, 0)

    def normalize(self) -> "QuantumState":
        """Normalizes the statevector so the sum of squared amplitudes equals 1."""
        norm_sq = sum(abs(c) ** 2 for c in self.statevector)
        if norm_sq > 0:
            norm = math.sqrt(norm_sq)
            self.statevector = [c / norm for c in self.statevector]
        return self

    def probabilities(self) -> Dict[str, float]:
        """Returns the probability distribution over all computational basis states."""
        res: Dict[str, float] = {}
        fmt = f"0{self.num_qubits}b"
        for i, amp in enumerate(self.statevector):
            prob = abs(amp) ** 2
            if prob > 1e-9:
                bitstring = format(i, fmt)
                res[bitstring] = round(prob, 6)
        return res

    def sample(self, shots: int = 1024, seed: Optional[int] = None) -> Dict[str, int]:
        """Simulates quantum projective measurements over multiple shots."""
        if seed is not None:
            random.seed(seed)
        probs = self.probabilities()
        states = list(probs.keys())
        weights = list(probs.values())
        
        counts: Dict[str, int] = {k: 0 for k in states}
        if not states:
            return counts

        for _ in range(shots):
            r = random.random()
            cum = 0.0
            chosen = states[-1]
            for state, p in zip(states, weights):
                cum += p
                if r <= cum:
                    chosen = state
                    break
            counts[chosen] += 1
        return counts

    def to_ket(self, precision: int = 3) -> str:
        """Returns Dirac bra-ket notation for the statevector (e.g. '0.707|00> + 0.707|11>')."""
        terms = []
        fmt = f"0{self.num_qubits}b"
        for i, amp in enumerate(self.statevector):
            if abs(amp) > 1e-5:
                bitstring = format(i, fmt)
                r = round(amp.real, precision)
                im = round(amp.imag, precision)
                if im == 0:
                    coef = f"{r}"
                elif r == 0:
                    coef = f"{im}j"
                else:
                    sign = "+" if im > 0 else "-"
                    coef = f"({r}{sign}{abs(im)}j)"
                terms.append(f"{coef}|{bitstring}>")
        return " + ".join(terms) if terms else "|0>"

    def bloch_vector(self, qubit: int) -> Tuple[float, float, float]:
        """
        Computes the reduced (x, y, z) Bloch sphere coordinates for a single qubit
        by tracing out all other qubits.
        """
        if qubit < 0 or qubit >= self.num_qubits:
            raise ValueError(f"Qubit index {qubit} out of range [0, {self.num_qubits - 1}]")

        # Reduced density matrix components rho_00, rho_01, rho_10, rho_11
        r00 = 0.0
        r11 = 0.0
        r01 = complex(0, 0)

        for i, amp in enumerate(self.statevector):
            bit = (i >> (self.num_qubits - 1 - qubit)) & 1
            if bit == 0:
                r00 += abs(amp) ** 2
                # Conjugate bit
                paired_i = i | (1 << (self.num_qubits - 1 - qubit))
                r01 += amp * self.statevector[paired_i].conjugate()
            else:
                r11 += abs(amp) ** 2

        # Bloch vector: X = 2*Re(rho_01), Y = 2*Im(rho_01), Z = rho_00 - rho_11
        x = round(2.0 * r01.real, 6)
        y = round(2.0 * r01.imag, 6)
        z = round(r00 - r11, 6)
        return (x, y, z)

    def is_entangled(self, q1: int = 0, q2: int = 1) -> bool:
        """Determines if two qubits exhibit non-separable quantum entanglement."""
        if self.num_qubits < 2:
            return False
        # Calculate purity / reduced Von Neumann entropy proxy via Bloch length
        bx, by, bz = self.bloch_vector(q1)
        length_sq = bx * bx + by * by + bz * bz
        # For a maximally entangled state (like Bell state), individual qubit is completely mixed: length -> 0
        return length_sq < 0.999


class QuantumCircuit:
    """Universal Quantum Circuit simulator supporting 1, 2, and 3 qubit operations."""

    def __init__(self, num_qubits: int):
        if num_qubits < 1 or num_qubits > 16:
            raise ValueError("QuantumCircuit supports between 1 and 16 qubits.")
        self.num_qubits = num_qubits
        self.gates: List[Tuple[str, List[int], List[float]]] = []

    def h(self, qubit: int) -> "QuantumCircuit":
        """Applies Hadamard gate (creates equal superposition)."""
        self._validate_qubit(qubit)
        self.gates.append(("H", [qubit], []))
        return self

    def x(self, qubit: int) -> "QuantumCircuit":
        """Applies Pauli-X (NOT / bit-flip) gate."""
        self._validate_qubit(qubit)
        self.gates.append(("X", [qubit], []))
        return self

    def y(self, qubit: int) -> "QuantumCircuit":
        """Applies Pauli-Y gate."""
        self._validate_qubit(qubit)
        self.gates.append(("Y", [qubit], []))
        return self

    def z(self, qubit: int) -> "QuantumCircuit":
        """Applies Pauli-Z (phase-flip) gate."""
        self._validate_qubit(qubit)
        self.gates.append(("Z", [qubit], []))
        return self

    def s(self, qubit: int) -> "QuantumCircuit":
        """Applies S gate (phase gate, pi/2 rotation around Z)."""
        self._validate_qubit(qubit)
        self.gates.append(("S", [qubit], []))
        return self

    def t(self, qubit: int) -> "QuantumCircuit":
        """Applies T gate (pi/4 rotation around Z)."""
        self._validate_qubit(qubit)
        self.gates.append(("T", [qubit], []))
        return self

    def rx(self, qubit: int, theta: float) -> "QuantumCircuit":
        """Applies rotation around X axis by angle theta."""
        self._validate_qubit(qubit)
        self.gates.append(("RX", [qubit], [float(theta)]))
        return self

    def ry(self, qubit: int, theta: float) -> "QuantumCircuit":
        """Applies rotation around Y axis by angle theta."""
        self._validate_qubit(qubit)
        self.gates.append(("RY", [qubit], [float(theta)]))
        return self

    def rz(self, qubit: int, theta: float) -> "QuantumCircuit":
        """Applies rotation around Z axis by angle theta."""
        self._validate_qubit(qubit)
        self.gates.append(("RZ", [qubit], [float(theta)]))
        return self

    def cnot(self, control: int, target: int) -> "QuantumCircuit":
        """Applies Controlled-NOT (CX) gate between control and target qubits."""
        self._validate_qubit(control)
        self._validate_qubit(target)
        if control == target:
            raise ValueError("Control and target qubits must be distinct.")
        self.gates.append(("CNOT", [control, target], []))
        return self

    def cx(self, control: int, target: int) -> "QuantumCircuit":
        """Alias for cnot."""
        return self.cnot(control, target)

    def cz(self, control: int, target: int) -> "QuantumCircuit":
        """Applies Controlled-Z gate."""
        self._validate_qubit(control)
        self._validate_qubit(target)
        if control == target:
            raise ValueError("Control and target qubits must be distinct.")
        self.gates.append(("CZ", [control, target], []))
        return self

    def swap(self, q1: int, q2: int) -> "QuantumCircuit":
        """Applies SWAP gate between q1 and q2."""
        self._validate_qubit(q1)
        self._validate_qubit(q2)
        if q1 == q2:
            raise ValueError("Qubits to swap must be distinct.")
        self.gates.append(("SWAP", [q1, q2], []))
        return self

    def toffoli(self, c1: int, c2: int, target: int) -> "QuantumCircuit":
        """Applies Toffoli (Controlled-Controlled-NOT) gate."""
        self._validate_qubit(c1)
        self._validate_qubit(c2)
        self._validate_qubit(target)
        if len({c1, c2, target}) != 3:
            raise ValueError("All three qubits in Toffoli must be distinct.")
        self.gates.append(("TOFFOLI", [c1, c2, target], []))
        return self

    def ccx(self, c1: int, c2: int, target: int) -> "QuantumCircuit":
        """Alias for toffoli."""
        return self.toffoli(c1, c2, target)

    def bell_state(self, q0: int = 0, q1: int = 1) -> "QuantumCircuit":
        """Prepares a maximally entangled Bell state (|00> + |11>) / sqrt(2)."""
        return self.h(q0).cnot(q0, q1)

    def ghz_state(self) -> "QuantumCircuit":
        """Prepares a Greenberger-Horne-Zeilinger (GHZ) state across all qubits."""
        self.h(0)
        for i in range(self.num_qubits - 1):
            self.cnot(i, i + 1)
        return self

    def run(self) -> QuantumState:
        """Executes all gates on the initial |0...0> statevector and returns the final QuantumState."""
        state = QuantumState(self.num_qubits)
        inv_sqrt2 = 1.0 / math.sqrt(2.0)

        for gate_name, targets, params in self.gates:
            if gate_name == "H":
                q = targets[0]
                bit_mask = 1 << (self.num_qubits - 1 - q)
                for i in range(1 << self.num_qubits):
                    if (i & bit_mask) == 0:
                        j = i | bit_mask
                        v0 = state.statevector[i]
                        v1 = state.statevector[j]
                        state.statevector[i] = (v0 + v1) * inv_sqrt2
                        state.statevector[j] = (v0 - v1) * inv_sqrt2

            elif gate_name == "X":
                q = targets[0]
                bit_mask = 1 << (self.num_qubits - 1 - q)
                for i in range(1 << self.num_qubits):
                    if (i & bit_mask) == 0:
                        j = i | bit_mask
                        state.statevector[i], state.statevector[j] = state.statevector[j], state.statevector[i]

            elif gate_name == "Y":
                q = targets[0]
                bit_mask = 1 << (self.num_qubits - 1 - q)
                for i in range(1 << self.num_qubits):
                    if (i & bit_mask) == 0:
                        j = i | bit_mask
                        v0 = state.statevector[i]
                        v1 = state.statevector[j]
                        state.statevector[i] = -1j * v1
                        state.statevector[j] = 1j * v0

            elif gate_name == "Z":
                q = targets[0]
                bit_mask = 1 << (self.num_qubits - 1 - q)
                for i in range(1 << self.num_qubits):
                    if (i & bit_mask) != 0:
                        state.statevector[i] = -state.statevector[i]

            elif gate_name == "S":
                q = targets[0]
                bit_mask = 1 << (self.num_qubits - 1 - q)
                for i in range(1 << self.num_qubits):
                    if (i & bit_mask) != 0:
                        state.statevector[i] = state.statevector[i] * 1j

            elif gate_name == "T":
                q = targets[0]
                bit_mask = 1 << (self.num_qubits - 1 - q)
                phase = complex(math.cos(math.pi / 4), math.sin(math.pi / 4))
                for i in range(1 << self.num_qubits):
                    if (i & bit_mask) != 0:
                        state.statevector[i] = state.statevector[i] * phase

            elif gate_name == "RX":
                q = targets[0]
                theta = params[0]
                cos_h = math.cos(theta / 2.0)
                sin_h = math.sin(theta / 2.0)
                bit_mask = 1 << (self.num_qubits - 1 - q)
                for i in range(1 << self.num_qubits):
                    if (i & bit_mask) == 0:
                        j = i | bit_mask
                        v0 = state.statevector[i]
                        v1 = state.statevector[j]
                        state.statevector[i] = cos_h * v0 - 1j * sin_h * v1
                        state.statevector[j] = -1j * sin_h * v0 + cos_h * v1

            elif gate_name == "RY":
                q = targets[0]
                theta = params[0]
                cos_h = math.cos(theta / 2.0)
                sin_h = math.sin(theta / 2.0)
                bit_mask = 1 << (self.num_qubits - 1 - q)
                for i in range(1 << self.num_qubits):
                    if (i & bit_mask) == 0:
                        j = i | bit_mask
                        v0 = state.statevector[i]
                        v1 = state.statevector[j]
                        state.statevector[i] = cos_h * v0 - sin_h * v1
                        state.statevector[j] = sin_h * v0 + cos_h * v1

            elif gate_name == "RZ":
                q = targets[0]
                theta = params[0]
                p0 = complex(math.cos(-theta / 2.0), math.sin(-theta / 2.0))
                p1 = complex(math.cos(theta / 2.0), math.sin(theta / 2.0))
                bit_mask = 1 << (self.num_qubits - 1 - q)
                for i in range(1 << self.num_qubits):
                    if (i & bit_mask) == 0:
                        state.statevector[i] *= p0
                    else:
                        state.statevector[i] *= p1

            elif gate_name == "CNOT":
                ctrl, tgt = targets[0], targets[1]
                ctrl_mask = 1 << (self.num_qubits - 1 - ctrl)
                tgt_mask = 1 << (self.num_qubits - 1 - tgt)
                for i in range(1 << self.num_qubits):
                    if (i & ctrl_mask) != 0 and (i & tgt_mask) == 0:
                        j = i | tgt_mask
                        state.statevector[i], state.statevector[j] = state.statevector[j], state.statevector[i]

            elif gate_name == "CZ":
                ctrl, tgt = targets[0], targets[1]
                ctrl_mask = 1 << (self.num_qubits - 1 - ctrl)
                tgt_mask = 1 << (self.num_qubits - 1 - tgt)
                combined = ctrl_mask | tgt_mask
                for i in range(1 << self.num_qubits):
                    if (i & combined) == combined:
                        state.statevector[i] = -state.statevector[i]

            elif gate_name == "SWAP":
                q1, q2 = targets[0], targets[1]
                m1 = 1 << (self.num_qubits - 1 - q1)
                m2 = 1 << (self.num_qubits - 1 - q2)
                for i in range(1 << self.num_qubits):
                    b1 = (i & m1) != 0
                    b2 = (i & m2) != 0
                    if b1 and not b2:
                        j = (i ^ m1) | m2
                        state.statevector[i], state.statevector[j] = state.statevector[j], state.statevector[i]

            elif gate_name == "TOFFOLI":
                c1, c2, tgt = targets[0], targets[1], targets[2]
                c1_mask = 1 << (self.num_qubits - 1 - c1)
                c2_mask = 1 << (self.num_qubits - 1 - c2)
                tgt_mask = 1 << (self.num_qubits - 1 - tgt)
                ctrls = c1_mask | c2_mask
                for i in range(1 << self.num_qubits):
                    if (i & ctrls) == ctrls and (i & tgt_mask) == 0:
                        j = i | tgt_mask
                        state.statevector[i], state.statevector[j] = state.statevector[j], state.statevector[i]

        return state.normalize()

    def _validate_qubit(self, qubit: int):
        if qubit < 0 or qubit >= self.num_qubits:
            raise ValueError(f"Qubit index {qubit} must be in [0, {self.num_qubits - 1}]")

    def __repr__(self) -> str:
        return f"<QuantumCircuit ({self.num_qubits} qubits, {len(self.gates)} gates)>"


# Convenience functional factory
def circuit(num_qubits: int) -> QuantumCircuit:
    """Creates a new QuantumCircuit with the specified number of qubits."""
    return QuantumCircuit(num_qubits)
