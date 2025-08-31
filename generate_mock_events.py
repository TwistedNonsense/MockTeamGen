#!/usr/bin/env python3
"""
generate_mock_events.py

Outputs:
  - mock_events.csv with columns:
      event_id,event_name,event_date,event_venue_id,event_start_time
  - mock_events-teams.csv with columns:
      event_id,team_id

Prompts:
  - Number of events (default 20)
  - Teams per event (default 2)

CLI:
  --teams-csv mock_teams.csv
  --venues-csv mock_venues.csv
  --events-out mock_events.csv
  --join-out mock_events-teams.csv
  --start-event-id 9001
  --num-events N
  --teams-per-event K
  --seed 123
  --locale en_US
"""

import argparse
import csv
from dataclasses import dataclass
from datetime import date, timedelta
from pathlib import Path
import random
import sys
from typing import List

try:
    from faker import Faker
except ImportError:
    sys.exit("Missing dependency: faker. Install with `pip install faker` and retry.")

DEFAULT_EVENTS_OUT = "mock_events.csv"
DEFAULT_JOIN_OUT = "mock_events-teams.csv"
DEFAULT_TEAMS_CSV = "mock_teams.csv"
DEFAULT_VENUES_CSV = "mock_venues.csv"

@dataclass
class Args:
    teams_csv: Path
    venues_csv: Path
    events_out: Path
    join_out: Path
    start_event_id: int
    num_events: int | None
    teams_per_event: int | None
    seed: int | None
    locale: str

def parse_args() -> Args:
    p = argparse.ArgumentParser(description="Generate mock events and event-team join rows.")
    p.add_argument("--teams-csv", type=Path, default=Path(DEFAULT_TEAMS_CSV))
    p.add_argument("--venues-csv", type=Path, default=Path(DEFAULT_VENUES_CSV))
    p.add_argument("--events-out", type=Path, default=Path(DEFAULT_EVENTS_OUT))
    p.add_argument("--join-out", type=Path, default=Path(DEFAULT_JOIN_OUT))
    p.add_argument("--start-event-id", type=int, default=9001)
    p.add_argument("--num-events", type=int)
    p.add_argument("--teams-per-event", type=int)
    p.add_argument("--seed", type=int, default=None)
    p.add_argument("--locale", type=str, default="en_US")
    ns = p.parse_args()
    return Args(
        teams_csv=ns.teams_csv,
        venues_csv=ns.venues_csv,
        events_out=ns.events_out,
        join_out=ns.join_out,
        start_event_id=ns.start_event_id,
        num_events=ns.num_events,
        teams_per_event=ns.teams_per_event,
        seed=ns.seed,
        locale=ns.locale,
    )

def prompt_int(question: str, default_value: int) -> int:
    try:
        raw = input(f"{question} [{default_value}]: ").strip()
    except EOFError:
        return default_value
    if not raw:
        return default_value
    try:
        return int(raw)
    except ValueError:
        print(f"Invalid integer. Using default {default_value}.")
        return default_value

def read_ids_from_csv(path: Path, col: str) -> List[str]:
    if not path.exists():
        sys.exit(f"Required CSV not found: {path}")
    with path.open("r", encoding="utf-8", newline="") as f:
        reader = csv.DictReader(f)
        if reader.fieldnames is None:
            sys.exit(f"{path} has no header row.")
        headers = [h.strip() for h in reader.fieldnames]
        if col not in headers:
            sys.exit(f"Required column '{col}' not found in {path}. Headers: {headers}")
        ids: List[str] = []
        for row in reader:
            v = str(row.get(col, "")).strip()
            if v:
                ids.append(v)
        if not ids:
            sys.exit(f"No '{col}' values found in {path}.")
        return ids

def read_ids_optional(path: Path, col: str) -> List[str]:
    if not path.exists():
        return []
    with path.open("r", encoding="utf-8", newline="") as f:
        reader = csv.DictReader(f)
        if not reader.fieldnames or col not in reader.fieldnames:
            return []
        return [str(row.get(col, "")).strip() for row in reader if str(row.get(col, "")).strip()]

def pick_event_name(fake: Faker, rng: random.Random) -> str:
    suffix = rng.choice([
        "Challenge","Classic","Championship","Cup","Derby","Finals","Invitational","Invite","Open","Series","Showcase"
    ])
    return f"{fake.city()} {suffix}"

def pick_event_date(rng: random.Random) -> str:
    start = date.today()
    d = start + timedelta(days=rng.randint(0, 180))
    return d.isoformat()

def pick_start_time(rng: random.Random) -> str:
    hour = rng.randint(8, 20)
    minute = rng.choice([0, 15, 30, 45])
    return f"{hour:02d}:{minute:02d}"

def generate(events_count: int, teams_per_event: int, team_ids: List[str], venue_ids: List[str],
             start_event_id: int, fake: Faker, rng: random.Random):
    if teams_per_event < 1:
        sys.exit("teams_per_event must be >= 1.")
    if teams_per_event > len(team_ids):
        sys.exit(f"teams_per_event ({teams_per_event}) exceeds available teams ({len(team_ids)}).")

    events_rows: List[dict] = []
    join_rows: List[dict] = []

    for i in range(events_count):
        eid = start_event_id + i
        events_rows.append({
            "event_id": eid,
            "event_name": pick_event_name(fake, rng),
            "event_date": pick_event_date(rng),
            "event_venue_id": (rng.choice(venue_ids) if venue_ids else ""),
            "event_start_time": pick_start_time(rng),
        })
        for tid in rng.sample(team_ids, k=teams_per_event):
            join_rows.append({"event_id": eid, "team_id": tid})
    return events_rows, join_rows

def write_csv(path: Path, rows: List[dict], fieldnames: List[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=fieldnames)
        w.writeheader()
        w.writerows(rows)

def main() -> int:
    args = parse_args()
    fake = Faker(args.locale)
    rng = random.Random(args.seed)

    events_count = args.num_events if args.num_events is not None else prompt_int("How many events to generate?", 20)
    teams_per_event = args.teams_per_event if args.teams_per_event is not None else prompt_int("How many teams per event?", 2)

    team_ids = read_ids_from_csv(args.teams_csv, "team_id")
    venue_ids = read_ids_optional(args.venues_csv, "venue_id")

    events_rows, join_rows = generate(events_count, teams_per_event, team_ids, venue_ids,
                                      args.start_event_id, fake, rng)

    write_csv(args.events_out, events_rows, ["event_id","event_name","event_date","event_venue_id","event_start_time"])
    write_csv(args.join_out, join_rows, ["event_id","team_id"])

    print(f"Wrote {len(events_rows)} events to {args.events_out}")
    print(f"Wrote {len(join_rows)} event-team rows to {args.join_out}")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
