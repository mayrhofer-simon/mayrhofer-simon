"""
fetch_contributions.py — scrapes public GitHub contribution calendar
Writes data/contributions.json (no token required).

Usage:
    python scripts/fetch_contributions.py
"""

import json
import re
from datetime import date, timedelta
from pathlib import Path

import requests
from bs4 import BeautifulSoup

USERNAME = "mayrhofer-simon"
URL      = f"https://github.com/users/{USERNAME}/contributions"
OUT      = Path("data/contributions.json")


def fetch() -> list[dict]:
    headers = {"X-Requested-With": "XMLHttpRequest"}
    r = requests.get(URL, headers=headers, timeout=15)
    r.raise_for_status()
    soup = BeautifulSoup(r.text, "html.parser")

    # Build a map from cell id → tooltip text
    # GitHub renders: <tool-tip for="contribution-day-component-X-Y">N contributions on ...</tool-tip>
    tooltip_map: dict[str, str] = {}
    for tip in soup.find_all("tool-tip"):
        cell_id = tip.get("for", "")
        if cell_id:
            tooltip_map[cell_id] = tip.get_text(strip=True)

    days = []
    for td in soup.find_all("td", attrs={"data-date": True}):
        d     = td["data-date"]
        level = int(td.get("data-level", 0))
        tip   = tooltip_map.get(td.get("id", ""), "")
        count_match = re.match(r"(\d+)", tip)
        count = int(count_match.group(1)) if count_match else 0
        days.append({"date": d, "level": level, "count": count})

    return days


def derive_stats(days: list[dict]) -> dict:
    total        = sum(d["count"] for d in days)
    streak       = 0
    max_streak   = 0
    cur_streak   = 0
    best_day     = max(days, key=lambda d: d["count"]) if days else {}

    today = date.today()
    day_map = {d["date"]: d["count"] for d in days}

    # current streak (backwards from today)
    check = today
    while True:
        key = check.strftime("%Y-%m-%d")
        if day_map.get(key, 0) > 0:
            cur_streak += 1
            check -= timedelta(days=1)
        else:
            break

    # longest streak
    run = 0
    for d in sorted(days, key=lambda x: x["date"]):
        if d["count"] > 0:
            run += 1
            max_streak = max(max_streak, run)
        else:
            run = 0

    return {
        "total":          total,
        "current_streak": cur_streak,
        "longest_streak": max_streak,
        "best_day":       best_day,
    }


def main() -> None:
    days  = fetch()
    stats = derive_stats(days)
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps({"days": days, "stats": stats}, indent=2))
    print(f"Saved {len(days)} days → {OUT}")
    print(f"  total: {stats['total']}  streak: {stats['current_streak']}  best: {stats['best_day']}")


if __name__ == "__main__":
    main()
