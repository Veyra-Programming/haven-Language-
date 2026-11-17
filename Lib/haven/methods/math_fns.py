"""
Haven Standard Library - Mathematical & Statistical Methods
Standard: Open Digital Continuity Standard (ODCS) & Scientific Computing Spec
Architecture & Specification: Anirudha Puthraya
Copyright (c) 2026 Haven Language Foundation & Anirudha Puthraya.
"""

import math
import statistics
from typing import List, Union, Optional, Tuple, Sequence

Number = Union[int, float]


def clamp(val: Number, min_v: Number, max_v: Number) -> Number:
    """Clamps a numerical value between min_v and max_v."""
    return max(min_v, min(max_v, val))


def lerp(a: Number, b: Number, t: float) -> float:
    """Linear interpolation between a and b with factor t [0.0 - 1.0]."""
    return a + (b - a) * t


def sign(x: Number) -> int:
    """Returns -1 if x < 0, 0 if x == 0, and 1 if x > 0."""
    return -1 if x < 0 else (1 if x > 0 else 0)


def abs_val(x: Number) -> Number:
    """Returns absolute value of x."""
    return abs(x)


def sqrt_val(x: Number) -> float:
    """Returns square root of x."""
    return math.sqrt(x)


def cbrt_val(x: Number) -> float:
    """Returns cube root of x."""
    return math.cbrt(x) if hasattr(math, "cbrt") else (x ** (1.0 / 3.0))


def hypot_val(x: Number, y: Number) -> float:
    """Returns Euclidean distance sqrt(x^2 + y^2)."""
    return math.hypot(x, y)


def pow_mod(base: int, exp: int, mod: int) -> int:
    """Computes (base^exp) % mod efficiently."""
    return pow(base, exp, mod)


def gcd_val(a: int, b: int) -> int:
    """Returns greatest common divisor of a and b."""
    return math.gcd(a, b)


def lcm_val(a: int, b: int) -> int:
    """Returns least common multiple of a and b."""
    return math.lcm(a, b) if hasattr(math, "lcm") else abs(a * b) // math.gcd(a, b)


def factorial_val(n: int) -> int:
    """Returns factorial of n."""
    return math.factorial(n)


def comb_val(n: int, k: int) -> int:
    """Returns number of combinations n choose k."""
    return math.comb(n, k)


def perm_val(n: int, k: Optional[int] = None) -> int:
    """Returns number of permutations n permute k."""
    return math.perm(n, k)


def is_prime(n: int) -> bool:
    """Checks whether an integer is prime."""
    if n <= 1:
        return False
    if n <= 3:
        return True
    if n % 2 == 0 or n % 3 == 0:
        return False
    i = 5
    while i * i <= n:
        if n % i == 0 or n % (i + 2) == 0:
            return False
        i += 6
    return True


def prime_factors(n: int) -> List[int]:
    """Returns the list of prime factors of n."""
    factors = []
    d = 2
    temp = n
    while d * d <= temp:
        while temp % d == 0:
            factors.append(d)
            temp //= d
        d += 1
    if temp > 1:
        factors.append(temp)
    return factors


def next_prime(n: int) -> int:
    """Returns the smallest prime strictly greater than n."""
    candidate = n + 1
    while not is_prime(candidate):
        candidate += 1
    return candidate


def fibonacci(n: int) -> int:
    """Returns the n-th Fibonacci number."""
    if n <= 0:
        return 0
    elif n == 1:
        return 1
    a, b = 0, 1
    for _ in range(2, n + 1):
        a, b = b, a + b
    return b


def deg_to_rad(deg: float) -> float:
    """Converts degrees to radians."""
    return math.radians(deg)


def rad_to_deg(rad: float) -> float:
    """Converts radians to degrees."""
    return math.degrees(rad)


def sin_val(x: float) -> float:
    return math.sin(x)


def cos_val(x: float) -> float:
    return math.cos(x)


def tan_val(x: float) -> float:
    return math.tan(x)


def asin_val(x: float) -> float:
    return math.asin(x)


def acos_val(x: float) -> float:
    return math.acos(x)


def atan_val(x: float) -> float:
    return math.atan(x)


def atan2_val(y: float, x: float) -> float:
    return math.atan2(y, x)


def sinh_val(x: float) -> float:
    return math.sinh(x)


def cosh_val(x: float) -> float:
    return math.cosh(x)


def tanh_val(x: float) -> float:
    return math.tanh(x)


def log_val(x: float, base: Optional[float] = None) -> float:
    return math.log(x, base) if base is not None else math.log(x)


def log2_val(x: float) -> float:
    return math.log2(x)


def log10_val(x: float) -> float:
    return math.log10(x)


def exp_val(x: float) -> float:
    return math.exp(x)


def floor_val(x: float) -> int:
    return math.floor(x)


def ceil_val(x: float) -> int:
    return math.ceil(x)


def trunc_val(x: float) -> int:
    return math.trunc(x)


def round_to(val: float, decimals: int = 2) -> float:
    """Rounds a float to specified decimal places."""
    return round(val, decimals)


def is_close(a: float, b: float, rel_tol: float = 1e-09, abs_tol: float = 0.0) -> bool:
    """Determines whether two floating point numbers are close in value."""
    return math.isclose(a, b, rel_tol=rel_tol, abs_tol=abs_tol)


# Statistics
def mean_val(iterable: Sequence[Number]) -> float:
    """Computes arithmetic mean of a collection."""
    return float(statistics.mean(iterable))


def median_val(iterable: Sequence[Number]) -> float:
    """Computes median of a collection."""
    return float(statistics.median(iterable))


def mode_val(iterable: Sequence[Any]) -> Any:
    """Computes single mode of a collection."""
    return statistics.mode(iterable)


def variance_val(iterable: Sequence[Number]) -> float:
    """Computes sample variance."""
    return float(statistics.variance(iterable))


def std_dev_val(iterable: Sequence[Number]) -> float:
    """Computes standard deviation."""
    return float(statistics.stdev(iterable))


def percentile_val(iterable: Sequence[Number], p: float) -> float:
    """Computes p-th percentile (0 <= p <= 100)."""
    sorted_items = sorted(iterable)
    k = (len(sorted_items) - 1) * (p / 100.0)
    f = math.floor(k)
    c = math.ceil(k)
    if f == c:
        return float(sorted_items[int(k)])
    d0 = sorted_items[int(f)] * (c - k)
    d1 = sorted_items[int(c)] * (k - f)
    return float(d0 + d1)


def z_score(val: Number, mean_v: Number, std_v: Number) -> float:
    """Calculates the standard Z-score."""
    if std_v == 0:
        return 0.0
    return (val - mean_v) / std_v


def covariance_val(xs: Sequence[Number], ys: Sequence[Number]) -> float:
    """Calculates covariance between two sequences."""
    return float(statistics.covariance(xs, ys)) if hasattr(statistics, "covariance") else sum((x - statistics.mean(xs)) * (y - statistics.mean(ys)) for x, y in zip(xs, ys)) / (len(xs) - 1)


def correlation_val(xs: Sequence[Number], ys: Sequence[Number]) -> float:
    """Calculates Pearson correlation coefficient between two sequences."""
    return float(statistics.correlation(xs, ys)) if hasattr(statistics, "correlation") else covariance_val(xs, ys) / (statistics.stdev(xs) * statistics.stdev(ys))


def norm_min_max(xs: Sequence[Number]) -> List[float]:
    """Normalizes sequence to [0.0, 1.0] range."""
    min_x = min(xs)
    max_x = max(xs)
    span = max_x - min_x
    if span == 0:
        return [0.0 for _ in xs]
    return [(x - min_x) / span for x in xs]


def sum_val(iterable: Sequence[Number]) -> Number:
    """Computes sum of numbers."""
    return sum(iterable)


def product_val(iterable: Sequence[Number]) -> Number:
    """Computes product of numbers."""
    res = 1
    for x in iterable:
        res *= x
    return res
