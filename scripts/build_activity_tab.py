"""Draw the last 28 UTC days of public GitHub events as six guitar strings."""

import argparse
from datetime import date, datetime, timedelta, timezone
from html import escape
import json
import math
import os
from pathlib import Path
import re
from urllib.request import Request, urlopen
from xml.etree import ElementTree

ROWS = [("e", "pushes"), ("B", "pull requests"), ("G", "reviews"),
        ("D", "issues / comments"), ("A", "repos / branches"), ("E", "other")]
EVENT_ROWS = {"PushEvent": 0, "PullRequestEvent": 1, "PullRequestReviewEvent": 2,
              "PullRequestReviewCommentEvent": 2, "IssuesEvent": 3,
              "IssueCommentEvent": 3, "CreateEvent": 4, "DeleteEvent": 4}
PALETTES = {
    "light": {"bg": "#ffffff", "text": "#59636e", "line": "#d8dee4", "accent": "#28664e", "today": "#f1f6f3"},
    "dark": {"bg": "#0d1117", "text": "#9da7b3", "line": "#30363d", "accent": "#8cc9ab", "today": "#14221c"},
}


def event_day(event):
    return datetime.fromisoformat(event["created_at"].replace("Z", "+00:00")).astimezone(timezone.utc).date()


def fetch_events(user, start):
    events = []
    headers = {"Accept": "application/vnd.github+json", "User-Agent": "roger-profile-activity",
               "X-GitHub-Api-Version": "2026-03-10"}
    if os.environ.get("GITHUB_TOKEN"):
        headers["Authorization"] = "Bearer " + os.environ["GITHUB_TOKEN"]
    for page in range(1, 4):
        url = f"https://api.github.com/users/{user}/events/public?per_page=100&page={page}"
        with urlopen(Request(url, headers=headers), timeout=30) as response:
            batch = json.load(response)
        if not isinstance(batch, list):
            raise ValueError("The public-events response is not an event list.")
        events.extend(batch)
        if len(batch) < 100 or any(event_day(event) < start for event in batch):
            break
    return events


def build_snapshot(events, user, today):
    start = today - timedelta(days=27)
    counts = [[0] * 28 for _ in ROWS]
    seen = set()
    for event in events:
        if event.get("public") is not True or event.get("actor", {}).get("login", "").lower() != user.lower():
            continue
        identifier = event["id"]
        if identifier in seen:
            continue
        seen.add(identifier)
        day = event_day(event)
        if start <= day <= today:
            counts[EVENT_ROWS.get(event["type"], 5)][(day - start).days] += 1
    limited = len(events) >= 300 and min(map(event_day, events)) >= start
    return {"user": user, "start": start.isoformat(), "end": today.isoformat(),
            "timezone": "UTC", "source": f"https://api.github.com/users/{user}/events/public",
            "limited_to_available_events": limited, "total_events": sum(map(sum, counts)),
            "rows": [{"string": string, "label": label, "days": days, "total": sum(days)}
                     for (string, label), days in zip(ROWS, counts)]}


def draw_svg(snapshot, theme, mobile=False):
    c = PALETTES[theme]
    total = snapshot["total_events"]
    title = f"{snapshot['user']}: {total} public GitHub events over 28 UTC days"
    description = f"{snapshot['start']} through {snapshot['end']} UTC. "
    description += "; ".join(f"{row['label']}: {row['total']}" for row in snapshot["rows"])
    description += ". Each dot groups one day; dot size grows with the event count."
    if snapshot["limited_to_available_events"]:
        description += " The public feed's 300-event limit was reached."
    width, height = (360, 190) if mobile else (720, 174)
    svg = [f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}" role="img" aria-labelledby="title desc">',
           f'<title id="title">{escape(title)}</title>', f'<desc id="desc">{escape(description)}</desc>',
           '<style>.today{animation:breath 4s ease-in-out infinite}@keyframes breath{50%{opacity:.55}}@media(prefers-reduced-motion:reduce){.today{animation:none}}</style>',
           f'<rect width="{width}" height="{height}" fill="{c["bg"]}"/>']
    left, right, top, spacing = (28 if mobile else 144), width - 16, 28, 20
    step = (right - left) / 27
    svg.append(f'<rect x="{right - step / 2:.2f}" y="16" width="{step:.2f}" height="124" rx="3" fill="{c["today"]}"/>')
    for day in [6, 13, 20]:
        x = left + (day + .5) * step
        svg.append(f'<path d="M{x:.2f} 16v124" stroke="{c["line"]}" stroke-dasharray="2 5"/>')
    for index, row in enumerate(snapshot["rows"]):
        y = top + index * spacing
        svg.append(f'<text x="2" y="{y + 4}" fill="{c["accent"]}" font-family="ui-monospace,Consolas,monospace" font-size="{16 if mobile else 14}">{row["string"]}</text>')
        if not mobile:
            svg.append(f'<text x="23" y="{y + 4}" fill="{c["text"]}" font-family="-apple-system,BlinkMacSystemFont,Segoe UI,Arial,sans-serif" font-size="12">{escape(row["label"])}</text>')
        svg.append(f'<path d="M{left} {y}H{right}" stroke="{c["line"]}" stroke-width="{.65 + index * .17:.2f}"/>')
        for day, count in enumerate(row["days"]):
            if count:
                x = left + day * step
                radius = min(4.5 if mobile else 6.5, 2.5 + math.sqrt(count))
                current = ' class="today"' if day == 27 else ""
                label = f"{date.fromisoformat(snapshot['start']) + timedelta(days=day)}: {count} {row['label']} events"
                svg.append(f'<circle cx="{x:.2f}" cy="{y}" r="{radius:.2f}" fill="{c["accent"]}"{current}><title>{escape(label)}</title></circle>')
    start, end = date.fromisoformat(snapshot["start"]), date.fromisoformat(snapshot["end"])
    footer = f"{start:%b %d} — {end:%b %d} · {total} events" if mobile else f"{start:%b %d} — {end:%b %d, %Y} · {total} public events"
    if not mobile and snapshot["limited_to_available_events"]:
        footer += " · feed limit reached"
    elif not mobile and not total:
        footer += " · quiet four weeks"
    svg.append(f'<text x="{left}" y="163" fill="{c["text"]}" font-family="-apple-system,BlinkMacSystemFont,Segoe UI,Arial,sans-serif" font-size="12">{escape(footer)}</text>')
    if mobile:
        note = "Public feed limit reached · UTC" if snapshot["limited_to_available_events"] else "Quiet four weeks · UTC" if not total else "Public GitHub events · UTC"
        svg.append(f'<text x="{left}" y="183" fill="{c["text"]}" font-family="-apple-system,BlinkMacSystemFont,Segoe UI,Arial,sans-serif" font-size="12">{note}</text>')
    svg.append('</svg>')
    text = "\n".join(svg) + "\n"
    ElementTree.fromstring(text)
    return text


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--user", default="rogerrrmalcolm")
    parser.add_argument("--out", type=Path, default=Path("dist"))
    parser.add_argument("--today", type=date.fromisoformat, default=datetime.now(timezone.utc).date())
    parser.add_argument("--events-file", type=Path, help="Use a saved public event list for an offline run.")
    args = parser.parse_args()
    if not re.fullmatch(r"[A-Za-z0-9](?:[A-Za-z0-9-]{0,37}[A-Za-z0-9])?", args.user):
        parser.error("Invalid GitHub username.")
    events = json.loads(args.events_file.read_text(encoding="utf-8")) if args.events_file else fetch_events(args.user, args.today - timedelta(days=27))
    snapshot = build_snapshot(events, args.user, args.today)
    images = {theme + ("-mobile" if mobile else ""): draw_svg(snapshot, theme, mobile)
              for theme in PALETTES for mobile in [False, True]}
    args.out.mkdir(parents=True, exist_ok=True)
    for theme, svg in images.items():
        (args.out / f"activity-tab-{theme}.svg").write_text(svg, encoding="utf-8")
    (args.out / "activity.json").write_text(json.dumps(snapshot, indent=2) + "\n", encoding="utf-8")
    print(f"Generated four activity tabs: {snapshot['total_events']} public events, {snapshot['start']} to {snapshot['end']} UTC.")


if __name__ == "__main__":
    main()
