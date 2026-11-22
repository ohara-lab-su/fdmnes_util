"""Element numbers and symbols used in FDMNES structure records."""

from importlib.resources import files


SYMBOLS_BY_NUMBER = {}
for row in files("fdmnes_util").joinpath("atomic_symbols.list").read_text(
    encoding="utf-8"
).splitlines():
    number, symbol = row.split()[:2]
    SYMBOLS_BY_NUMBER[int(number)] = symbol

NUMBERS_BY_SYMBOL = {symbol: number for number, symbol in SYMBOLS_BY_NUMBER.items()}
