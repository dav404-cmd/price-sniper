from datetime import datetime, timedelta
import re

def normalize_scraped_date(raw_date: str) -> str:
    raw_date = raw_date.strip()

    # Case 1: Relative times like "20h ago", "2d ago", "3w ago", "5m ago"
    match = re.match(r"(\d+)([hdwm])\s*ago", raw_date, re.IGNORECASE)
    if match:
        amount = int(match.group(1))
        unit = match.group(2).lower()
        now = datetime.now()

        if unit == "h":
            dt = now - timedelta(hours=amount)
        elif unit == "d":
            dt = now - timedelta(days=amount)
        elif unit == "w":
            dt = now - timedelta(weeks=amount)
        elif unit == "m":  # months (approx as 30 days)
            dt = now - timedelta(days=30 * amount)

        return dt.strftime("%Y-%m-%d %H:%M")

    # Case 2: "Yesterday 01:12 PM"
    if raw_date.lower().startswith("yesterday"):
        time_part = raw_date.split(" ", 1)[1]  # take "01:12 PM"
        dt = datetime.strptime(time_part, "%I:%M %p")
        yesterday = datetime.now() - timedelta(days=1)
        dt = yesterday.replace(hour=dt.hour, minute=dt.minute)
        return dt.strftime("%Y-%m-%d %H:%M")

    # Case 2.5: "Today 01:30 AM"
    if raw_date.lower().startswith("today"):
        time_part = raw_date.split(" ", 1)[1]  # take "01:30 AM"
        dt = datetime.strptime(time_part, "%I:%M %p")
        today = datetime.now()
        dt = today.replace(hour=dt.hour, minute=dt.minute)
        return dt.strftime("%Y-%m-%d %H:%M")

    # Case 3: Full date like "Jun 16, 2025 08:09 AM"
    try:
        dt = datetime.strptime(raw_date, "%b %d, %Y %I:%M %p")
        return dt.strftime("%Y-%m-%d %H:%M")
    except ValueError:
        pass

    # Case 4: Already in datetime format like "2025-08-22 01:11:40.842025"
    try:
        dt = datetime.fromisoformat(raw_date)
        return dt.strftime("%Y-%m-%d %H:%M")
    except ValueError:
        pass

    raise ValueError(f"Unsupported date format: {raw_date}")

def time_ago(ts):
    now = datetime.now()
    delta = now - ts

    days = delta.days
    seconds = delta.seconds

    if days < 1:
        if seconds < 60:
            return f"{seconds}s ago"
        elif seconds < 3600:
            return f"{seconds // 60}m ago"
        else:
            return f"{seconds // 3600}h ago"
    elif days < 7:
        return f"{days}d ago"
    elif days < 30:
        return f"{days // 7}w ago"
    elif days < 365:
        return f"{days // 30}mo ago"
    else:
        return f"{days // 365}y ago"




# --- tests ---
if __name__ == "__main__":
    print(2 * "-","normalize",2 * "-")
    print(normalize_scraped_date("20h ago"))
    print(normalize_scraped_date("2w ago"))
    print(normalize_scraped_date("Yesterday 01:12 PM"))
    print(normalize_scraped_date("Jun 16, 2025 08:09 AM"))
    print(normalize_scraped_date("2025-08-22 01:11:40.842025"))
    print(2 * "-", "time_ago", 2 * "-")
    print(time_ago(datetime(2025, 8, 21, 13, 12)))