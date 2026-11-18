"""
Ani++ / Haven Scientific Computing & Columnar Data Engine
Industrial-grade Matrix Linear Algebra, Tensor Math, and Columnar DataFrames.
Zero external dependencies. High-precision exact mathematical computation.
Standard Specification & Architecture by Anirudha Puthraya.
Copyright (c) 2026 Haven Language Foundation & Anirudha Puthraya.
"""

import math
import json
import csv
import io
from typing import Any, Callable, Dict, List, Optional, Tuple, Union


class Matrix:
    """
    Industrial Linear Algebra Matrix:
    Supports addition, subtraction, scalar multiplication, matrix multiplication (@),
    transposition, determinants, inverses, and statistical reductions.
    """
    def __init__(self, data: List[List[float]]):
        if not data or not isinstance(data, list) or not isinstance(data[0], list):
            raise ValueError("Matrix must be initialized with a non-empty 2D list.")
        rows = len(data)
        cols = len(data[0])
        if any(len(row) != cols for row in data):
            raise ValueError("All rows in a Matrix must have identical column lengths.")

        self.rows: int = rows
        self.cols: int = cols
        self._data: List[List[float]] = [[float(val) for val in row] for row in data]

    @property
    def shape(self) -> Tuple[int, int]:
        return (self.rows, self.cols)

    def get(self, r: int, c: int) -> float:
        return self._data[r][c]

    def set(self, r: int, c: int, val: float) -> None:
        self._data[r][c] = float(val)

    def to_list(self) -> List[List[float]]:
        return [[val for val in row] for row in self._data]

    @classmethod
    def zeros(cls, rows: int, cols: int) -> "Matrix":
        return cls([[0.0 for _ in range(cols)] for _ in range(rows)])

    @classmethod
    def ones(cls, rows: int, cols: int) -> "Matrix":
        return cls([[1.0 for _ in range(cols)] for _ in range(rows)])

    @classmethod
    def identity(cls, n: int) -> "Matrix":
        mat = cls.zeros(n, n)
        for i in range(n):
            mat.set(i, i, 1.0)
        return mat

    def transpose(self) -> "Matrix":
        t_data = [[self._data[r][c] for r in range(self.rows)] for c in range(self.cols)]
        return Matrix(t_data)

    def trace(self) -> float:
        if self.rows != self.cols:
            raise ValueError("Trace is only defined for square matrices.")
        return sum(self._data[i][i] for i in range(self.rows))

    def __add__(self, other: "Matrix") -> "Matrix":
        if self.shape != other.shape:
            raise ValueError(f"Matrix shape mismatch for addition: {self.shape} vs {other.shape}")
        res = [[self._data[r][c] + other._data[r][c] for c in range(self.cols)] for r in range(self.rows)]
        return Matrix(res)

    def __sub__(self, other: "Matrix") -> "Matrix":
        if self.shape != other.shape:
            raise ValueError(f"Matrix shape mismatch for subtraction: {self.shape} vs {other.shape}")
        res = [[self._data[r][c] - other._data[r][c] for c in range(self.cols)] for r in range(self.rows)]
        return Matrix(res)

    def __mul__(self, scalar: Union[int, float]) -> "Matrix":
        """Scalar multiplication."""
        if not isinstance(scalar, (int, float)):
            raise TypeError("Matrix '*' operator is reserved for scalar multiplication. Use '@' for matrix multiplication.")
        res = [[self._data[r][c] * float(scalar) for c in range(self.cols)] for r in range(self.rows)]
        return Matrix(res)

    def __rmul__(self, scalar: Union[int, float]) -> "Matrix":
        return self.__mul__(scalar)

    def __matmul__(self, other: "Matrix") -> "Matrix":
        """Matrix product A @ B."""
        if not isinstance(other, Matrix):
            raise TypeError("Matmul requires two Matrix instances.")
        if self.cols != other.rows:
            raise ValueError(f"Cannot multiply matrices of shape {self.shape} and {other.shape}.")

        res = [[sum(self._data[r][k] * other._data[k][c] for k in range(self.cols)) for c in range(other.cols)] for r in range(self.rows)]
        return Matrix(res)

    def determinant(self) -> float:
        """Computes determinant using Gaussian elimination with partial pivoting."""
        if self.rows != self.cols:
            raise ValueError("Determinant is only defined for square matrices.")
        n = self.rows
        a = [row[:] for row in self._data]
        det = 1.0

        for i in range(n):
            # Pivot
            pivot = i
            for r in range(i + 1, n):
                if abs(a[r][i]) > abs(a[pivot][i]):
                    pivot = r
            if pivot != i:
                a[i], a[pivot] = a[pivot], a[i]
                det = -det

            if abs(a[i][i]) < 1e-12:
                return 0.0

            det *= a[i][i]
            for r in range(i + 1, n):
                factor = a[r][i] / a[i][i]
                for c in range(i, n):
                    a[r][c] -= factor * a[i][c]

        return det

    def inverse(self) -> "Matrix":
        """Computes matrix inverse via Gauss-Jordan elimination."""
        if self.rows != self.cols:
            raise ValueError("Inverse only defined for square matrices.")
        n = self.rows
        # Augmented matrix [A | I]
        aug = [self._data[r][:] + [1.0 if c == r else 0.0 for c in range(n)] for r in range(n)]

        for i in range(n):
            pivot = i
            for r in range(i + 1, n):
                if abs(aug[r][i]) > abs(aug[pivot][i]):
                    pivot = r
            if pivot != i:
                aug[i], aug[pivot] = aug[pivot], aug[i]

            pivot_val = aug[i][i]
            if abs(pivot_val) < 1e-12:
                raise ValueError("Matrix is singular and cannot be inverted.")

            for c in range(2 * n):
                aug[i][c] /= pivot_val

            for r in range(n):
                if r != i:
                    factor = aug[r][i]
                    for c in range(2 * n):
                        aug[r][c] -= factor * aug[i][c]

        inv_data = [[aug[r][c + n] for c in range(n)] for r in range(n)]
        return Matrix(inv_data)

    def flatten(self) -> List[float]:
        return [val for row in self._data for val in row]

    def sum(self) -> float:
        return sum(self.flatten())

    def mean(self) -> float:
        return self.sum() / (self.rows * self.cols)

    def __repr__(self) -> str:
        rows_str = ", ".join(f"{row}" for row in self._data)
        return f"Matrix({self.rows}x{self.cols}, [{rows_str}])"


class Series:
    """1D Statistical Data Vector."""
    def __init__(self, data: List[Any], name: str = "series"):
        self.name = name
        self.data: List[Any] = list(data)

    def __len__(self) -> int:
        return len(self.data)

    def __getitem__(self, idx: int) -> Any:
        return self.data[idx]

    def to_numeric(self) -> List[float]:
        return [float(x) for x in self.data if x is not None]

    def sum(self) -> float:
        nums = self.to_numeric()
        return sum(nums) if nums else 0.0

    def mean(self) -> float:
        nums = self.to_numeric()
        return sum(nums) / len(nums) if nums else 0.0

    def min(self) -> float:
        nums = self.to_numeric()
        return min(nums) if nums else 0.0

    def max(self) -> float:
        nums = self.to_numeric()
        return max(nums) if nums else 0.0

    def std(self) -> float:
        nums = self.to_numeric()
        if len(nums) < 2:
            return 0.0
        avg = self.mean()
        variance = sum((x - avg) ** 2 for x in nums) / (len(nums) - 1)
        return math.sqrt(variance)

    def __repr__(self) -> str:
        return f"Series({self.name}, count={len(self.data)})"


class DataFrame:
    """
    Industrial Columnar In-Memory DataFrame:
    Zero external dependencies. Blazing fast filtering, projections, and grouping.
    """
    def __init__(self, data: Dict[str, List[Any]]):
        self._columns: List[str] = list(data.keys())
        # Verify length consistency
        lens = [len(v) for v in data.values()]
        if lens and any(l != lens[0] for l in lens):
            raise ValueError("All DataFrame columns must have identical lengths.")
        self._length: int = lens[0] if lens else 0
        self._data: Dict[str, List[Any]] = {k: list(v) for k, v in data.items()}

    @property
    def columns(self) -> List[str]:
        return list(self._columns)

    @property
    def shape(self) -> Tuple[int, int]:
        return (self._length, len(self._columns))

    def __len__(self) -> int:
        return self._length

    def __getitem__(self, col: str) -> Series:
        if col not in self._data:
            raise KeyError(f"Column '{col}' not found in DataFrame.")
        return Series(self._data[col], name=col)

    def column(self, col: str) -> Series:
        """Alias for df[col]."""
        return self[col]

    def head(self, n: int = 5) -> "DataFrame":
        n = min(n, self._length)
        sliced = {k: v[:n] for k, v in self._data.items()}
        return DataFrame(sliced)

    def select(self, *cols: str) -> "DataFrame":
        sub = {c: self._data[c] for c in cols if c in self._data}
        return DataFrame(sub)

    def filter(self, predicate: Callable[[Dict[str, Any]], bool]) -> "DataFrame":
        """Filters rows by lambda predicate: df.filter(lambda row: row['age'] > 30)."""
        matching_indices = []
        for i in range(self._length):
            row = {col: self._data[col][i] for col in self._columns}
            if predicate(row):
                matching_indices.append(i)

        filtered = {col: [self._data[col][idx] for idx in matching_indices] for col in self._columns}
        return DataFrame(filtered)

    def where(self, column_name: str, predicate: Callable[[Any], bool]) -> "DataFrame":
        """Filters rows where df[column_name] satisfies predicate: df.where('status', lambda s: s == 'active')."""
        if column_name not in self._data:
            raise KeyError(f"Column '{column_name}' not found in DataFrame.")
        matching_indices = [
            i for i, val in enumerate(self._data[column_name])
            if predicate(val)
        ]
        filtered = {col: [self._data[col][idx] for idx in matching_indices] for col in self._columns}
        return DataFrame(filtered)

    def to_dicts(self) -> List[Dict[str, Any]]:
        return [{col: self._data[col][i] for col in self._columns} for i in range(self._length)]

    def to_csv(self) -> str:
        out = io.StringIO()
        writer = csv.writer(out)
        writer.writerow(self._columns)
        for i in range(self._length):
            writer.writerow([self._data[c][i] for c in self._columns])
        return out.getvalue()

    @classmethod
    def from_dicts(cls, rows: List[Dict[str, Any]]) -> "DataFrame":
        if not rows:
            return cls({})
        cols = list(rows[0].keys())
        data = {col: [row.get(col) for row in rows] for col in cols}
        return cls(data)

    def summary(self) -> Dict[str, Dict[str, float]]:
        res = {}
        for col in self._columns:
            s = self[col]
            try:
                nums = s.to_numeric()
                if nums:
                    res[col] = {
                        "count": float(len(nums)),
                        "mean": s.mean(),
                        "std": s.std(),
                        "min": s.min(),
                        "max": s.max()
                    }
            except Exception:
                pass
        return res

    def __repr__(self) -> str:
        return f"DataFrame(rows={self._length}, cols={len(self._columns)}, {self._columns})"
