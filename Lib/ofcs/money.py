"""
Open Financial Continuity Standard (OFCS) - High-Precision Monetary Engine
Standard Specification & Architecture by Anirudha Puthraya.
Copyright (c) 2026 Haven Language Foundation & Anirudha Puthraya.

Guarantees:
  1. Exact Decimal Representation (Zero Floating-Point Drift: 0.1 + 0.2 == 0.3)
  2. ISO-4217 Currency Safety (Illegal currency mixing prevented)
  3. Immutable Monetary Value Objects
"""

from decimal import Decimal, ROUND_HALF_EVEN, InvalidOperation
from typing import Any, Dict, Optional, Union


class CurrencyMismatchError(TypeError):
    """Raised when attempting mathematical operations on different currencies without exchange rate."""
    pass


class Currency:
    """Represents an ISO-4217 currency or digital sovereign asset."""
    def __init__(self, code: str, symbol: str = "", precision: int = 2):
        self.code = code.upper()
        self.symbol = symbol or self.code
        self.precision = precision

    def __repr__(self) -> str:
        return f"Currency({self.code})"

    def __eq__(self, other: Any) -> bool:
        if isinstance(other, Currency):
            return self.code == other.code
        if isinstance(other, str):
            return self.code == other.upper()
        return False

    def __hash__(self) -> int:
        return hash(self.code)


# Standard Currencies
USD = Currency("USD", "$", 2)
EUR = Currency("EUR", "€", 2)
GBP = Currency("GBP", "£", 2)
INR = Currency("INR", "₹", 2)
JPY = Currency("JPY", "¥", 0)
BTC = Currency("BTC", "₿", 8)
HVN = Currency("HVN", "✦", 6) # Native Haven Continuity Gas Token

_CURRENCIES: Dict[str, Currency] = {
    "USD": USD, "EUR": EUR, "GBP": GBP, "INR": INR,
    "JPY": JPY, "BTC": BTC, "HVN": HVN
}


def get_currency(code_or_obj: Union[str, Currency]) -> Currency:
    if isinstance(code_or_obj, Currency):
        return code_or_obj
    code = str(code_or_obj).upper()
    return _CURRENCIES.get(code, Currency(code, code, 2))


class Money:
    """
    OFCS Exact Monetary Value:
    Immutable, high-precision value backed by Python's Decimal engine.
    Ensures zero floating-point accumulation error across millions of transactions.
    """
    def __init__(self, amount: Union[Decimal, float, int, str], currency: Union[str, Currency] = USD):
        if isinstance(amount, float):
            # Convert float safely via string representation to avoid immediate drift
            self._amount = Decimal(str(amount))
        elif isinstance(amount, Decimal):
            self._amount = amount
        else:
            self._amount = Decimal(str(amount))

        self._currency = get_currency(currency)
        # Quantize to currency precision
        quantizer = Decimal("10") ** -self._currency.precision
        self._amount = self._amount.quantize(quantizer, rounding=ROUND_HALF_EVEN)

    @property
    def amount(self) -> Decimal:
        return self._amount

    @property
    def currency(self) -> Currency:
        return self._currency

    def to_dict(self) -> Dict[str, Any]:
        return {
            "amount": str(self._amount),
            "currency": self._currency.code
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Money":
        return cls(amount=data["amount"], currency=data["currency"])

    def _check_currency(self, other: "Money"):
        if not isinstance(other, Money):
            raise TypeError(f"Cannot operate between Money and '{type(other).__name__}'")
        if self._currency != other._currency:
            raise CurrencyMismatchError(
                f"Cannot operate between {self._currency.code} and {other._currency.code} without ExchangeRate"
            )

    def __add__(self, other: "Money") -> "Money":
        self._check_currency(other)
        return Money(self._amount + other._amount, self._currency)

    def __sub__(self, other: "Money") -> "Money":
        self._check_currency(other)
        return Money(self._amount - other._amount, self._currency)

    def __mul__(self, factor: Union[Decimal, int, float]) -> "Money":
        if isinstance(factor, (int, Decimal)):
            mult = Decimal(factor)
        else:
            mult = Decimal(str(factor))
        return Money(self._amount * mult, self._currency)

    def __truediv__(self, divisor: Union[Decimal, int, float]) -> "Money":
        if isinstance(divisor, (int, Decimal)):
            div = Decimal(divisor)
        else:
            div = Decimal(str(divisor))
        return Money(self._amount / div, self._currency)

    def __neg__(self) -> "Money":
        return Money(-self._amount, self._currency)

    def __abs__(self) -> "Money":
        return Money(abs(self._amount), self._currency)

    def __eq__(self, other: Any) -> bool:
        if not isinstance(other, Money):
            return False
        return self._currency == other._currency and self._amount == other._amount

    def __lt__(self, other: "Money") -> bool:
        self._check_currency(other)
        return self._amount < other._amount

    def __le__(self, other: "Money") -> bool:
        self._check_currency(other)
        return self._amount <= other._amount

    def __gt__(self, other: "Money") -> bool:
        self._check_currency(other)
        return self._amount > other._amount

    def __ge__(self, other: "Money") -> bool:
        self._check_currency(other)
        return self._amount >= other._amount

    def is_zero(self) -> bool:
        return self._amount == Decimal(0)

    def is_positive(self) -> bool:
        return self._amount > Decimal(0)

    def is_negative(self) -> bool:
        return self._amount < Decimal(0)

    def __repr__(self) -> str:
        return f"{self._currency.symbol}{self._amount:.{self._currency.precision}f} {self._currency.code}"

    def __str__(self) -> str:
        return f"{self._currency.symbol}{self._amount:.{self._currency.precision}f}"


class ExchangeRate:
    """Immutable rate for converting between two sovereign currencies."""
    def __init__(self, from_currency: Union[str, Currency], to_currency: Union[str, Currency], rate: Union[Decimal, float, str]):
        self.from_currency = get_currency(from_currency)
        self.to_currency = get_currency(to_currency)
        self.rate = Decimal(str(rate))

    def convert(self, money: Money) -> Money:
        if money.currency != self.from_currency:
            raise CurrencyMismatchError(
                f"ExchangeRate expects {self.from_currency.code}, got {money.currency.code}"
            )
        converted_amount = money.amount * self.rate
        return Money(converted_amount, self.to_currency)

    def __repr__(self) -> str:
        return f"ExchangeRate(1 {self.from_currency.code} = {self.rate} {self.to_currency.code})"
