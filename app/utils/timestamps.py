from datetime import datetime
import pytz

def parse_iso861_to_utc(iso_string: str) -> tuple[str, str]:
    """
        Parse ISO 86061 string to UTC datetime
    """
    dt = datetime.fromisoformat(iso_string.replace("Z", "+00:00"))
    utc_dt = dt.astimezone(pytz.UTC)
    return utc_dt.isoformat(), iso_string


def normalize_to_utc_iso(iso_string: str) -> str:
    dt = datetime.fromisoformat(iso_string.replace("Z", "+00:00"))
    return dt.astimezone(pytz.UTC).isoformat()