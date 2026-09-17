from datetime import datetime


def now_str():
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")


def format_timestamp(ts, fmt="%d %b %Y, %I:%M %p"):
    """Accepts a datetime, a string, or None and returns a friendly display string."""
    if ts is None:
        return "-"
    if isinstance(ts, str):
        try:
            ts = datetime.strptime(ts, "%Y-%m-%d %H:%M:%S")
        except ValueError:
            return ts
    return ts.strftime(fmt)
