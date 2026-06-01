from app.data.providers.dukascopy.symbol_mapper import (
    DUKASCOPY_SYMBOLS,
)

for symbol, instrument in (
    DUKASCOPY_SYMBOLS.items()
):
    print(
        symbol,
        "->",
        instrument,
    )
