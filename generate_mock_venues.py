#!/usr/bin/env python3
import argparse, csv, re, sys
from pathlib import Path
try:
    from faker import Faker
except ImportError:
    sys.exit("Missing dependency: Faker. Install with `pip install Faker` and retry.")

def clean_school_street(fake):
    s = f"{fake.building_number()} {fake.street_name()}"
    s = s.replace("\n", " ")
    s = re.sub(r"\b(?:Apt|Apartment|Suite|Ste|Unit|#)\b.*$", "", s, flags=re.I)
    return s.strip(" ,")

def read_teams(path: Path):
    if not path.exists():
        sys.exit(f"Teams CSV not found: {path}")
    with path.open("r", encoding="utf-8", newline="") as f:
        rdr = csv.DictReader(f)
        if not rdr.fieldnames or "team_id" not in rdr.fieldnames or "team_school" not in rdr.fieldnames:
            sys.exit("Teams CSV must contain 'team_id' and 'team_school'.")
        return [{"team_id": r["team_id"], "team_school": r["team_school"]} for r in rdr if r.get("team_id")]

def main():
    p = argparse.ArgumentParser(description="Generate venues for teams CSV.")
    p.add_argument("--teams-csv", type=Path, default=Path("mock_teams.csv"))
    p.add_argument("--out", type=Path, default=Path("mock_venues.csv"))
    p.add_argument("--start-id", type=int, default=3001)
    args = p.parse_args()

    teams = read_teams(args.teams_csv)
    fake = Faker("en_US")
    rows = []
    for i, t in enumerate(teams):
        vid = args.start_id + i
        city = t["team_school"]
        rows.append({
            "venue_id": vid,
            "venue_name": f"{city} High School",
            "venue_street": clean_school_street(fake),
            "venue_city": city,
            "venue_state": fake.state_abbr(),
            "venue_zip": fake.zipcode(),
            "venue_phone": fake.numerify("(###) ###-####"),
            "venue_team_id": t["team_id"],
        })
    fields = ["venue_id","venue_name","venue_street","venue_city","venue_state","venue_zip","venue_phone","venue_team_id"]
    with args.out.open("w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=fields)
        w.writeheader(); w.writerows(rows)
    print(f"Wrote {len(rows)} venues to {args.out}")

if __name__ == "__main__":
    main()
