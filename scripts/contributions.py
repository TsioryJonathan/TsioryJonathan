"""Draw the GitHub contribution calendar as two SVGs (light and dark), without any third-party service.

Usage: gh api graphql -f query=@scripts/calendar.graphql | python3 scripts/contributions.py assets
"""
import json
import sys
from pathlib import Path

CELL, GAP, TOP, PAD = 11, 3, 34, 16

THEMES = {
    "contributions.svg": {
        "bg": "#F6F0E5", "text": "#5A3F2D",
        "levels": ["#E5D9C6", "#EBC7A6", "#D9A073", "#B8673C", "#8F4B25"],
    },
    "contributions-dark.svg": {
        "bg": "#211A13", "text": "#C4B5A4",
        "levels": ["#2E241A", "#5A3F2D", "#8F4B25", "#B8673C", "#F2B38A"],
    },
}


def level_for(count, cutoffs):
    """0 for no contribution, then 1 to 4 by quartile of the busy days.

    GitHub's own levels are relative to the single busiest day, so one huge day flattens the rest of the year.
    """
    if count == 0:
        return 0
    return 1 + sum(count > c for c in cutoffs)


def render(calendar, theme):
    weeks = calendar["weeks"]
    busy = sorted(d["contributionCount"] for w in weeks for d in w["contributionDays"] if d["contributionCount"] > 0)
    cutoffs = [busy[len(busy) * q // 4] for q in (1, 2, 3)] if busy else [0, 0, 0]
    width = PAD * 2 + len(weeks) * (CELL + GAP) - GAP
    height = TOP + 7 * (CELL + GAP) - GAP + PAD
    total = calendar["totalContributions"]
    out = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}" role="img" aria-label="{total} contributions in the last year">',
        f'<rect width="{width}" height="{height}" rx="10" fill="{theme["bg"]}"/>',
        f'<text x="{PAD}" y="22" font-family="-apple-system, Segoe UI, Helvetica, Arial, sans-serif" font-size="12" fill="{theme["text"]}">{total:,} contributions in the last year</text>',
    ]
    for x, week in enumerate(weeks):
        for day in week["contributionDays"]:
            y = day["weekday"]
            level = level_for(day["contributionCount"], cutoffs)
            out.append(
                f'<rect x="{PAD + x * (CELL + GAP)}" y="{TOP + y * (CELL + GAP)}" width="{CELL}" height="{CELL}" rx="2" fill="{theme["levels"][level]}">'
                f'<title>{day["date"]}: {day["contributionCount"]}</title></rect>'
            )
    out.append("</svg>")
    return "\n".join(out) + "\n"


def main():
    target = Path(sys.argv[1])
    calendar = json.load(sys.stdin)["data"]["user"]["contributionsCollection"]["contributionCalendar"]
    target.mkdir(parents=True, exist_ok=True)
    for name, theme in THEMES.items():
        (target / name).write_text(render(calendar, theme))


if __name__ == "__main__":
    main()
