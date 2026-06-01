from datetime import datetime
from datetime import UTC

def to_milliseconds(
    date_string: str,
) -> int:

    dt = datetime.strptime(
        date_string,
        "%Y-%m-%d",
    )

    dt = dt.replace(
        tzinfo=UTC,
    )

    return int(
        dt.timestamp() * 1000
    )
