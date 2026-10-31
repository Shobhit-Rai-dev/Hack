from decimal import Decimal, ROUND_HALF_UP
from typing import Any

def round_currency(value: Any) -> Decimal:
    if value is None:
        dec = Decimal("0.00")
    elif isinstance(value, Decimal):
        dec = value
    else:
        dec = Decimal(str(value))
    return dec.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)

def to_decimal(value: Any) -> Decimal:
    if value is None:
        return Decimal("0.00")
    if isinstance(value, Decimal):
        return value
    return Decimal(str(value))