"""Illustrative maturity payment, assuming full payment by the issuer.

Python 3.11+, standard library only. No market data or product valuation.
Run: python3 participation_payoff.py 1000 100 120 0.8
Output: 1160.00 (currency units, including principal)
"""

import argparse
import re
from fractions import Fraction


def _number(name: str, value: str) -> Fraction:
    """Accept ordinary decimal strings with up to six decimal places."""
    if not isinstance(value, str) or not re.fullmatch(
        r"[0-9]{1,10}(?:\.[0-9]{1,6})?", value
    ):
        raise ValueError(f"{name}: use a nonnegative decimal string, up to 6 decimals")
    number = Fraction(value)
    if number > 1_000_000_000:
        raise ValueError(f"{name}: must not exceed 1000000000")
    return number


def maturity_payment(
    principal: str, initial: str, final: str, participation: str
) -> str:
    """Return the assumed gross payment, rounded half up to 2 decimals.

    N * (1 + p * max(final / initial - 1, 0)).
    All inputs are decimal strings, not binary floating-point numbers.
    N and initial must be positive; final >= 0; 0 <= p <= 1.
    Fraction keeps the arithmetic exact until the final currency rounding.
    The 1 billion / 6 decimal limits are teaching-tool input limits,
    not restrictions that apply to structured products in general.
    """
    n = _number("principal", principal)
    s0 = _number("initial", initial)
    st = _number("final", final)
    p = _number("participation", participation)
    if n <= 0 or s0 <= 0:
        raise ValueError("principal and initial must be positive")
    if p > 1:
        raise ValueError("participation must be between 0 and 1")

    level_return = st / s0 - 1
    payment = n * (1 + p * max(level_return, 0))
    # All payments are positive. Add half a cent, then floor to whole cents.
    rounded = payment * 100 + Fraction(1, 2)
    cents = rounded.numerator // rounded.denominator
    return f"{cents // 100}.{cents % 100:02d}"


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    for name in ("principal", "initial", "final", "participation"):
        parser.add_argument(name)
    args = parser.parse_args()
    try:
        print(maturity_payment(args.principal, args.initial, args.final, args.participation))
    except ValueError as error:
        parser.error(str(error))


if __name__ == "__main__":
    main()
