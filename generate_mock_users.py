#!/usr/bin/env python3
"""
generate_mock_users.py

Generates mock users for each team created by generate_mock_teams.py.

For every team_id in the teams CSV this script creates five users:
  - Team Admin
  - Coach
  - Assistant Coach
  - Venue Admin
  - Event Admin

Output CSV columns:
  user_id, user_full_name, user_email, user_phone, user_team_id, user_role

Defaults align with generate_mock_teams.py:
  - --teams-csv defaults to "mock_teams.csv"
  - user_id starts at 5001 unless overridden

Usage:
  python generate_mock_users.py --teams-csv ./mock_teams.csv --out ./mock_users.csv --seed 123
"""

import argparse
import csv
from dataclasses import dataclass
from pathlib import Path
import random
import re
import sys
from typing import Iterable, List, Set

try:
    from faker import Faker
except ImportError as e:
    sys.exit("Missing dependency: faker. Install with `pip install faker` and retry.")

ROLES = ["Team Admin", "Coach", "Assistant Coach", "Venue Admin", "Event Admin"]

@dataclass
class Args:
    teams_csv: Path
    out: Path
    start_user_id: int
    seed: int | None
    locale: str

def parse_args() -> Args:
    p = argparse.ArgumentParser(description="Generate mock users for teams CSV.")
    p.add_argument("--teams-csv", type=Path, default=Path("mock_teams.csv"),
                   help="Path to teams CSV from generate_mock_teams.py (must include 'team_id').")
    p.add_argument("--out", type=Path, default=Path("mock_users.csv"),
                   help="Output path for users CSV.")
    p.add_argument("--start-user-id", type=int, default=5001,
                   help="Starting user_id. Defaults to 5001.")
    p.add_argument("--seed", type=int, default=None,
                   help="Optional RNG seed for reproducibility.")
    p.add_argument("--locale", type=str, default="en_US",
                   help="Faker locale, e.g. en_US. Defaults to en_US.")
    ns = p.parse_args()
    return Args(
        teams_csv=ns.teams_csv,
        out=ns.out,
        start_user_id=ns.start_user_id,
        seed=ns.seed,
        locale=ns.locale,
    )

def read_team_ids(path: Path) -> List[str]:
    if not path.exists():
        sys.exit(f"Teams CSV not found: {path}")

    with path.open("r", encoding="utf-8", newline="") as f:
        reader = csv.DictReader(f)
        if reader.fieldnames is None:
            sys.exit("Teams CSV has no header row.")
        headers = [h.strip() for h in reader.fieldnames]
        if "team_id" not in headers:
            sys.exit("Required column 'team_id' not found in teams CSV.")
        team_ids: List[str] = []
        for row in reader:
            v = str(row.get("team_id", "")).strip()
            if v:
                team_ids.append(v)
        if not team_ids:
            sys.exit("No team_id values found in teams CSV.")
        return team_ids

def slugify(s: str) -> str:
    return re.sub(r"[^a-z0-9]", "", s.lower())

def ensure_unique(generator_fn, seen: Set[str], max_attempts: int = 1000) -> str:
    for _ in range(max_attempts):
        val = generator_fn()
        if val not in seen:
            seen.add(val)
            return val
    base = generator_fn()
    suffix = 1
    candidate = base
    while candidate in seen:
        candidate = f"{base}{suffix}"
        suffix += 1
    seen.add(candidate)
    return candidate

def build_unique_name(fake: Faker, seen_names: Set[str]) -> str:
    rng = fake.random
    def gen():
        first = fake.first_name()
        last = fake.last_name()
        name = f"{first} {last}"
        if name in seen_names:
            mid = rng.choice("ABCDEFGHIJKLMNOPQRSTUVWXYZ")
            name = f"{first} {mid}. {last}"
        return name
    return ensure_unique(gen, seen_names)

def build_unique_email(fake: Faker, full_name: str, seen_emails: Set[str]) -> str:
    rng = fake.random
    first, *rest = full_name.replace(".", "").split()
    last = rest[-1] if rest else ""
    first_slug = slugify(first)
    last_slug = slugify(last)
    base_local = f"{first_slug}.{last_slug}" if last_slug else first_slug
    domains = [
        "example.com", "example.org", "example.net",
        fake.free_email_domain(),
    ]
    def gen():
        domain = rng.choice(domains)
        suffix = str(rng.randint(10, 9999))
        local = f"{base_local}{suffix}" if base_local else fake.user_name()
        return f"{local}@{domain}"
    return ensure_unique(gen, seen_emails)

def build_unique_phone(fake: Faker, seen_phones: Set[str]) -> str:
    def gen():
        return fake.numerify("(###) ###-####")
    return ensure_unique(gen, seen_phones)

def generate_users(team_ids: Iterable[str], start_user_id: int, fake: Faker) -> List[dict]:
    users: List[dict] = []
    seen_names: Set[str] = set()
    seen_emails: Set[str] = set()
    seen_phones: Set[str] = set()
    uid = start_user_id

    for team_id in team_ids:
        for role in ROLES:
            full_name = build_unique_name(fake, seen_names)
            email = build_unique_email(fake, full_name, seen_emails)
            phone = build_unique_phone(fake, seen_phones)
            users.append({
                "user_id": uid,
                "user_full_name": full_name,
                "user_email": email,
                "user_phone": phone,
                "user_team_id": team_id,
                "user_role": role,
            })
            uid += 1
    return users

def write_users_csv(path: Path, rows: List[dict]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    fields = ["user_id","user_full_name","user_email","user_phone","user_team_id","user_role"]
    with path.open("w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=fields)
        w.writeheader()
        w.writerows(rows)

def main() -> int:
    args = parse_args()
    fake = Faker(args.locale)
    if args.seed is not None:
        fake.seed_instance(args.seed)
    team_ids = read_team_ids(args.teams_csv)
    users = generate_users(team_ids, args.start_user_id, fake)
    write_users_csv(args.out, users)
    print(f"Wrote {len(users)} users to {args.out}")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
