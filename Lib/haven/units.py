"""
Haven Universal Dimensional Safety Engine (UDE)
Standard: Open Digital Continuity Standard (ODCS) & Physical Computing Spec
Architecture & Specification: Anirudha Puthraya
Copyright (c) 2026 Haven Language Foundation & Anirudha Puthraya.

Provides compile-time and runtime dimensional unit safety for scientific,
financial, aerospace, autonomous robotics, IoT, and high-precision systems.
"""

from typing import Union, Dict, Any, Tuple


class DimensionalSafetyError(TypeError):
    """Raised when an operation violates physical or mathematical dimensional safety."""
    pass


class Dimension:
    """
    Fundamental physical dimension vector:
    [Length (L), Mass (M), Time (T), Current (I), Temperature (Theta), Data (D)]
    """
    def __init__(self, L: int = 0, M: int = 0, T: int = 0, I: int = 0, Theta: int = 0, D: int = 0):
        self.L = L
        self.M = M
        self.T = T
        self.I = I
        self.Theta = Theta
        self.D = D

    def as_tuple(self) -> Tuple[int, int, int, int, int, int]:
        return (self.L, self.M, self.T, self.I, self.Theta, self.D)

    def is_dimensionless(self) -> bool:
        return self.as_tuple() == (0, 0, 0, 0, 0, 0)

    def __eq__(self, other: Any) -> bool:
        if not isinstance(other, Dimension):
            return False
        return self.as_tuple() == other.as_tuple()

    def __mul__(self, other: 'Dimension') -> 'Dimension':
        return Dimension(
            self.L + other.L,
            self.M + other.M,
            self.T + other.T,
            self.I + other.I,
            self.Theta + other.Theta,
            self.D + other.D,
        )

    def __truediv__(self, other: 'Dimension') -> 'Dimension':
        return Dimension(
            self.L - other.L,
            self.M - other.M,
            self.T - other.T,
            self.I - other.I,
            self.Theta - other.Theta,
            self.D - other.D,
        )

    def __repr__(self) -> str:
        parts = []
        names = [("L", self.L), ("M", self.M), ("T", self.T), ("I", self.I), ("Θ", self.Theta), ("D", self.D)]
        for sym, exp in names:
            if exp != 0:
                parts.append(f"{sym}^{exp}" if exp != 1 else sym)
        return "·".join(parts) if parts else "Dimensionless"


# Base Dimensions
DIM_DIMENSIONLESS = Dimension()
DIM_LENGTH = Dimension(L=1)
DIM_MASS = Dimension(M=1)
DIM_TIME = Dimension(T=1)
DIM_DATA = Dimension(D=1)
DIM_TEMPERATURE = Dimension(Theta=1)
DIM_SPEED = Dimension(L=1, T=-1)
DIM_ACCELERATION = Dimension(L=1, T=-2)
DIM_DATA_RATE = Dimension(D=1, T=-1)


class Unit:
    """Represents a specific unit of measure bound to a physical dimension."""
    def __init__(self, name: str, symbol: str, dimension: Dimension, scale: float = 1.0, offset: float = 0.0):
        self.name = name
        self.symbol = symbol
        self.dimension = dimension
        self.scale = scale        # Factor to convert to SI base unit
        self.offset = offset      # Offset for affine units (like Celsius/Fahrenheit)

    def to_base(self, value: float) -> float:
        return (value + self.offset) * self.scale

    def from_base(self, base_val: float) -> float:
        return (base_val / self.scale) - self.offset

    def __repr__(self) -> str:
        return self.symbol


class UnitQuantity:
    """
    A dimensional quantity consisting of a numerical magnitude and a verified unit.
    Prevents conversion errors and illegal dimensional arithmetic.
    """
    def __init__(self, magnitude: Union[int, float], unit: Unit):
        self.magnitude = float(magnitude)
        self.unit = unit

    @property
    def value(self) -> float:
        """Alias for magnitude for intuitive value access."""
        return self.magnitude

    @property
    def dimension(self) -> Dimension:
        return self.unit.dimension

    def to(self, target_unit: Unit) -> 'UnitQuantity':
        """Converts quantity to another compatible unit of the same dimension."""
        if self.dimension != target_unit.dimension:
            raise DimensionalSafetyError(
                f"Cannot convert '{self.unit.name}' ({self.dimension}) to '{target_unit.name}' ({target_unit.dimension}): Incompatible dimensions."
            )
        base_value = self.unit.to_base(self.magnitude)
        converted = target_unit.from_base(base_value)
        return UnitQuantity(converted, target_unit)

    def __add__(self, other: Any) -> 'UnitQuantity':
        if not isinstance(other, UnitQuantity):
            raise DimensionalSafetyError(f"Cannot add scalar number to dimensional quantity '{self}'.")
        if self.dimension != other.dimension:
            raise DimensionalSafetyError(
                f"Dimensional mismatch: Cannot add '{self.unit.symbol}' ({self.dimension}) and '{other.unit.symbol}' ({other.dimension})."
            )
        other_in_self = other.to(self.unit)
        return UnitQuantity(self.magnitude + other_in_self.magnitude, self.unit)

    def __sub__(self, other: Any) -> 'UnitQuantity':
        if not isinstance(other, UnitQuantity):
            raise DimensionalSafetyError(f"Cannot subtract scalar number from dimensional quantity '{self}'.")
        if self.dimension != other.dimension:
            raise DimensionalSafetyError(
                f"Dimensional mismatch: Cannot subtract '{other.unit.symbol}' from '{self.unit.symbol}'."
            )
        other_in_self = other.to(self.unit)
        return UnitQuantity(self.magnitude - other_in_self.magnitude, self.unit)

    def __mul__(self, other: Any) -> Any:
        if isinstance(other, (int, float)):
            return UnitQuantity(self.magnitude * other, self.unit)
        if isinstance(other, UnitQuantity):
            # Compound dimension
            res_dim = self.dimension * other.dimension
            res_scale = self.unit.scale * other.unit.scale
            res_sym = f"{self.unit.symbol}·{other.unit.symbol}"
            new_unit = Unit(name=res_sym, symbol=res_sym, dimension=res_dim, scale=res_scale)
            return UnitQuantity(self.magnitude * other.magnitude, new_unit)
        raise DimensionalSafetyError(f"Unsupported multiplication with type {type(other)}.")

    def __rmul__(self, other: Any) -> 'UnitQuantity':
        return self.__mul__(other)

    def __truediv__(self, other: Any) -> Any:
        if isinstance(other, (int, float)):
            return UnitQuantity(self.magnitude / other, self.unit)
        if isinstance(other, UnitQuantity):
            res_dim = self.dimension / other.dimension
            if res_dim.is_dimensionless():
                # Dimensionless ratio
                base_self = self.unit.to_base(self.magnitude)
                base_other = other.unit.to_base(other.magnitude)
                return base_self / base_other
            
            # Check for standard speed: Length / Time
            if res_dim == DIM_SPEED:
                base_self = self.unit.to_base(self.magnitude)
                base_other = other.unit.to_base(other.magnitude)
                return UnitQuantity(base_self / base_other, meters_per_second)
            
            # Check for data rate: Data / Time
            if res_dim == DIM_DATA_RATE:
                base_self = self.unit.to_base(self.magnitude)
                base_other = other.unit.to_base(other.magnitude)
                return UnitQuantity((base_self / base_other) / (1024 * 1024), megabytes_per_second)

            res_scale = self.unit.scale / other.unit.scale
            res_sym = f"{self.unit.symbol}/{other.unit.symbol}"
            new_unit = Unit(name=res_sym, symbol=res_sym, dimension=res_dim, scale=res_scale)
            return UnitQuantity(self.magnitude / other.magnitude, new_unit)
        raise DimensionalSafetyError(f"Unsupported division with type {type(other)}.")

    def __eq__(self, other: Any) -> bool:
        if not isinstance(other, UnitQuantity):
            return False
        if self.dimension != other.dimension:
            return False
        base_self = round(self.unit.to_base(self.magnitude), 7)
        base_other = round(other.unit.to_base(other.magnitude), 7)
        return base_self == base_other

    def __lt__(self, other: 'UnitQuantity') -> bool:
        if not isinstance(other, UnitQuantity) or self.dimension != other.dimension:
            raise DimensionalSafetyError("Cannot compare quantities with different dimensions.")
        return self.unit.to_base(self.magnitude) < other.unit.to_base(other.magnitude)

    def __le__(self, other: 'UnitQuantity') -> bool:
        return self < other or self == other

    def __gt__(self, other: 'UnitQuantity') -> bool:
        return not (self <= other)

    def __ge__(self, other: 'UnitQuantity') -> bool:
        return not (self < other)

    def __repr__(self) -> str:
        return f"{self.magnitude:g} {self.unit.symbol}"


# Standard Units Registry
# Length
meter = Unit("meter", "m", DIM_LENGTH, 1.0)
kilometer = Unit("kilometer", "km", DIM_LENGTH, 1000.0)
centimeter = Unit("centimeter", "cm", DIM_LENGTH, 0.01)
millimeter = Unit("millimeter", "mm", DIM_LENGTH, 0.001)
mile = Unit("mile", "mi", DIM_LENGTH, 1609.344)
foot = Unit("foot", "ft", DIM_LENGTH, 0.3048)

# Time
second = Unit("second", "s", DIM_TIME, 1.0)
millisecond = Unit("millisecond", "ms", DIM_TIME, 0.001)
minute = Unit("minute", "min", DIM_TIME, 60.0)
hour = Unit("hour", "hr", DIM_TIME, 3600.0)
day = Unit("day", "d", DIM_TIME, 86400.0)

# Mass
kilogram = Unit("kilogram", "kg", DIM_MASS, 1.0)
gram = Unit("gram", "g", DIM_MASS, 0.001)
pound = Unit("pound", "lb", DIM_MASS, 0.453592)
metric_ton = Unit("ton", "t", DIM_MASS, 1000.0)

# Data
byte = Unit("byte", "B", DIM_DATA, 1.0)
kilobyte = Unit("kilobyte", "KB", DIM_DATA, 1024.0)
megabyte = Unit("megabyte", "MB", DIM_DATA, 1024.0 * 1024.0)
gigabyte = Unit("gigabyte", "GB", DIM_DATA, 1024.0 * 1024.0 * 1024.0)
terabyte = Unit("terabyte", "TB", DIM_DATA, 1024.0 ** 4)

# Speed & Rates
meters_per_second = Unit("meters_per_second", "m/s", DIM_SPEED, 1.0)
km_per_hour = Unit("km_per_hour", "km/h", DIM_SPEED, 1.0 / 3.6)
megabytes_per_second = Unit("megabytes_per_second", "MB/s", DIM_DATA_RATE, 1024.0 * 1024.0)

# Temperature
unit_celsius = Unit("celsius", "°C", DIM_TEMPERATURE, 1.0, 273.15)
unit_kelvin = Unit("kelvin", "K", DIM_TEMPERATURE, 1.0)
unit_fahrenheit = Unit("fahrenheit", "°F", DIM_TEMPERATURE, 5.0 / 9.0, 459.67)

# Electrical & Energy
DIM_VOLTAGE = Dimension(L=2, M=1, T=-3, I=-1)
unit_volt = Unit("volt", "V", DIM_VOLTAGE, 1.0)



# Ergonomic Constructors
def meters(val: Union[int, float]) -> UnitQuantity:
    return UnitQuantity(val, meter)

def kilometers(val: Union[int, float]) -> UnitQuantity:
    return UnitQuantity(val, kilometer)

def seconds(val: Union[int, float]) -> UnitQuantity:
    return UnitQuantity(val, second)

def milliseconds(val: Union[int, float]) -> UnitQuantity:
    return UnitQuantity(val, millisecond)

def hours(val: Union[int, float]) -> UnitQuantity:
    return UnitQuantity(val, hour)

def kilograms(val: Union[int, float]) -> UnitQuantity:
    return UnitQuantity(val, kilogram)

def grams(val: Union[int, float]) -> UnitQuantity:
    return UnitQuantity(val, gram)

def megabytes(val: Union[int, float]) -> UnitQuantity:
    return UnitQuantity(val, megabyte)

def gigabytes(val: Union[int, float]) -> UnitQuantity:
    return UnitQuantity(val, gigabyte)

def celsius(val: Union[int, float]) -> UnitQuantity:
    return UnitQuantity(val, unit_celsius)

def volts(val: Union[int, float]) -> UnitQuantity:
    return UnitQuantity(val, unit_volt)



class UnitsNamespace:
    """Namespace for easy access in Haven scripts via `units.meters(100)`."""
    meter = meter
    kilometer = kilometer
    centimeter = centimeter
    millimeter = millimeter
    mile = mile
    foot = foot
    second = second
    millisecond = millisecond
    minute = minute
    hour = hour
    day = day
    kilogram = kilogram
    gram = gram
    byte = byte
    kilobyte = kilobyte
    megabyte = megabyte
    gigabyte = gigabyte
    meters_per_second = meters_per_second
    km_per_hour = km_per_hour
    megabytes_per_second = megabytes_per_second
    celsius_unit = unit_celsius
    volt = unit_volt

    meters = staticmethod(meters)
    kilometers = staticmethod(kilometers)
    seconds = staticmethod(seconds)
    milliseconds = staticmethod(milliseconds)
    hours = staticmethod(hours)
    kilograms = staticmethod(kilograms)
    grams = staticmethod(grams)
    megabytes = staticmethod(megabytes)
    gigabytes = staticmethod(gigabytes)
    celsius = staticmethod(celsius)
    volts = staticmethod(volts)


units = UnitsNamespace()
