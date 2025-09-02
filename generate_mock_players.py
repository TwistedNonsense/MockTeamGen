#!/usr/bin/env python3
"""
generate_mock_players.py

Generate mock players linked to existing teams.

Output CSV: mock_players.csv with columns:
- player_id
- player_name
- player_age
- player_team_id

Requirements:
- faker

Example:
    python generate_mock_players.py \
        --teams-csv mock_teams.csv \
        --players-per-team 20 \
        --age-min 18 --age-max 22 \
        --start-id 7001 \
        --out mock_players.csv \
        --seed 42
"""
from __future__ import annotations

import argparse
import csv
import random
import sys
from pathlib import Path
from typing import List, Tuple

try:
    from faker import Faker
except Exception as e:
    print("Faker is required. Install with: pip install faker", file=sys.stderr)
    raise


def read_team_ids(teams_csv: Path) -> List[int]:
    if not teams_csv.exists():
        raise FileNotFoundError(f"Teams CSV not found: {teams_csv}")
    team_ids: List[int] = []
    with teams_csv.open(newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        # Accept common header variants
        header_lower = {h.lower(): h for h in reader.fieldnames or []}
        team_id_key = header_lower.get("team_id")
        if not team_id_key:
            raise KeyError("Expected 'team_id' column in teams CSV.")
        for row in reader:
            raw = row.get(team_id_key, "").strip()
            if raw == "":
                continue
            try:
                team_ids.append(int(raw))
            except ValueError:
                raise ValueError(f"Invalid team_id value: {raw!r}")
    if not team_ids:
        raise ValueError("No team_id values found in teams CSV.")
    return team_ids


def generate_unique_names(fake: Faker, count: int) -> List[str]:
    names = set()
    attempts = 0
    # cap to avoid infinite loops if count is too large
    cap = max(5000, count * 3)
    while len(names) < count and attempts < cap:
        # American-sounding names via en_US locale
        name = fake.name()
        names.add(name)
        attempts += 1
    if len(names) < count:
        # Fill remainder  using indexed variants
        base_list = list(names) or [fake.first_name() + " " + fake.last_name()]
        i = 0
        while len(names) < count:
            names.add(f"{base_list[i % len(base_list)]} {i//len(base_list)+2}")
            i += 1
    return list(names)


def generate_players(
    team_ids: List[int],
    players_per_team: int,
    age_min: int,
    age_max: int,
    start_id: int,
    seed: int | None = None,
) -> List[Tuple[int, str, int, int]]:
    if age_min > age_max:
        raise ValueError("age-min cannot be greater than age-max")
    if players_per_team < 0:
        raise ValueError("players-per-team must be >= 0")
    if players_per_team == 0:
        return []

    fake = Faker("en_US")
    if seed is not None:
        random.seed(seed)
        Faker.seed(seed)

    total_players = players_per_team * len(team_ids)

    # Pre-generate unique names
    names = generate_unique_names(fake, total_players)
    random.shuffle(names)

    rows: List[Tuple[int, str, int, int]] = []
    pid = start_id
    name_idx = 0

    for tid in team_ids:
        for _ in range(players_per_team):
            age = random.randint(age_min, age_max)
            rows.append((pid, names[name_idx], age, tid))
            pid += 1
            name_idx += 1

    return rows


def write_players_csv(out_csv: Path, rows: List[Tuple[int, str, int, int]]) -> None:
    out_csv.parent.mkdir(parents=True, exist_ok=True)
    with out_csv.open("w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["player_id", "player_name", "player_age", "player_team_id"])
        writer.writerows(rows)


def parse_args(argv: List[str]) -> argparse.Namespace:
    p = argparse.ArgumentParser(description="Generate mock players linked to teams.")
    p.add_argument("--teams-csv", default="mock_teams.csv", type=Path,
                   help="Path to teams CSV to use for player_team_id values (default: mock_teams.csv).")
    p.add_argument("--players-per-team", default=20, type=int,
                   help="Number of players per team (default: 20).")
    p.add_argument("--age-min", default=16, type=int,
                   help="Minimum player age (default: 16).")
    p.add_argument("--age-max", default=22, type=int,
                   help="Maximum player age (default: 22).")
    p.add_argument("--start-id", default=7001, type=int,
                   help="Starting player_id (default: 7001).")
    p.add_argument("--out", default="mock_players.csv", type=Path,
                   help="Output CSV path (default: mock_players.csv).")
    p.add_argument("--seed", default=None, type=int,
                   help="Optional RNG seed for reproducibility.")
    return p.parse_args(argv)


def main(argv: List[str] | None = None) -> int:
    ns = parse_args(argv or sys.argv[1:])
    team_ids = read_team_ids(ns.teams_csv)
    rows = generate_players(
        team_ids=team_ids,
        players_per_team=ns.players_per_team,
        age_min=ns.age_min,
        age_max=ns.age_max,
        start_id=ns.start_id,
        seed=ns.seed,
    )
    write_players_csv(ns.out, rows)
    print(f"✔ Generated {len(rows)} players -> {ns.out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
