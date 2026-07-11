#!/usr/bin/env python3
"""
fetch_contributions.py

Scrapes the public contribution graph for GH_PROFILE_USER (no auth/token
needed) from https://github.com/users/<user>/contributions and writes
data/contributions.json. This needs real network access -- run it locally
or let the GitHub Actions workflow run it (Actions runners have network).
"""
import os
import json
from datetime import datetime
import requests
from bs4 import BeautifulSoup

USER = os.environ.get("GH_PROFILE_USER")
if not USER:
    raise SystemExit("set GH_PROFILE_USER env var to your GitHub username")

URL = f"https://github.com/users/{USER}/contributions"
OUT = "data/contributions.json"


def fetch():
    r = requests.get(URL, headers={"User-Agent": "Mozilla/5.0"}, timeout=20)
    r.raise_for_status()
    soup = BeautifulSoup(r.text, "html.parser")

    days = []
    for td in soup.select("td.ContributionCalendar-day"):
        date = td.get("data-date")
        level = td.get("data-level")
        if date is None:
            continue
        days.append({"date": date, "level": int(level) if level is not None else 0})

    # GitHub has changed this markup before (td -> rect); fall back if needed
    if not days:
        for rect in soup.select("rect.ContributionCalendar-day"):
            date = rect.get("data-date")
            level = rect.get("data-level")
            if date:
                days.append({"date": date, "level": int(level) if level is not None else 0})

    days.sort(key=lambda d: d["date"])
    return days


def streaks(days):
    longest = 0
    run = 0
    for d in days:
        if d["level"] > 0:
            run += 1
            longest = max(longest, run)
        else:
            run = 0
    current = 0
    for d in reversed(days):
        if d["level"] > 0:
            current += 1
        else:
            break
    return current, longest


def main():
    days = fetch()
    if not days:
        raise SystemExit("no contribution data parsed -- GitHub markup may have changed")
    current, longest = streaks(days)
    total_active = sum(1 for d in days if d["level"] > 0)
    payload = {
        "user": USER,
        "generated_at": datetime.utcnow().isoformat() + "Z",
        "current_streak": current,
        "longest_streak": longest,
        "active_days": total_active,
        "days": days,
    }
    os.makedirs("data", exist_ok=True)
    with open(OUT, "w") as f:
        json.dump(payload, f, indent=2)
    print(f"wrote {OUT}  ({len(days)} days, current streak {current}, longest {longest})")


if __name__ == "__main__":
    main()
