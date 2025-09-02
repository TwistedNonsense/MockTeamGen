# Mock Team Data Generator

Generate realistic mock data for teams, venues, users, and events.  
This tool is useful for seeding demo databases or testing systems that depend on structured sports-style data.

## Features

- **Teams**: Generates mock schools with unique team codes, mascots, emails, and websites (based on authentic U.S. city names).
- **Venues**: Assigns each team a venue with consistent U.S. address and phone number formatting.
- **Users**: Creates role-based users (Team Admin, Coach, Assistant Coach, Venue Admin, Event Admin) tied to each team.
- **Events**: Generates events with realistic names, dates, times, and team associations, plus an event–team join table.
- **GUI**: Simple cross-platform desktop interface (Tkinter) to run any combination of the generators with adjustable options.

## Requirements

- Python 3.10+
- Dependencies:
  - `geonamescache`
  - `faker`
  - `tkinter`

Install all requirements:

```bash
pip install -r requirements.txt
```

## Usage

### GUI
Run the graphical user interface:
```bash
python generator.py
```

From the GUI you can: 
- Choose an output folder
- Select which data sets to generate
- Configure counts (e.g. number of teams, events, teams per event)
- Pick which user roles to include

The generated CSV files will appear in the chosen folder.

### Command Line
Each generator can also be run directly:
```bash
python generate_mock_teams.py --num-teams 50 --out mock_teams.csv
python generate_mock_venues.py --teams-csv mock_teams.csv --out mock_venues.csv
python generate_mock_users.py --teams-csv mock_teams.csv --out mock_users.csv --roles "Coach,Event Admin"
python generate_mock_events.py --teams-csv mock_teams.csv --venues-csv mock_venues.csv \
    --events-out mock_events.csv --join-out mock_events-teams.csv --num-events 20 --teams-per-event 2
```

## Output Files
- mock_teams.csv
- mock_venues.csv
- mock_users.csv
- mock_events.csv
- mock_events-teams.csv

Each file contains structured relational data suitable for importing into a database.

## License
This project is licensed under the MIT License.
