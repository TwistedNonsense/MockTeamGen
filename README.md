# Mock Team Data Generator

Generate mock data for teams, venues, users, events, and players.  
This tool is useful for seeding demo databases or testing systems that depend on structured sports-style data.

## Features

- **Teams**: Generates mock schools with unique team codes, silly mascots, emails, and websites (based on authentic U.S. city names).
- **Venues**: Assigns each team a venue with consistent U.S. address and phone number formatting.
- **Users**: Creates role-based users (Team Admin, Coach, Assistant Coach, Venue Admin, Event Admin) tied to each team.
- **Events**: Generates events with realistic names, dates, times, and team associations, plus an event–team join table.
- **Players**: Generates lists of players for each of the teams, with random ages using indicated range.
- **GUI**: Simple cross-platform desktop interface (Tkinter) to run any combination of the generators with adjustable options.

The team mascots are intentionally juvenile and silly. To expand the number of possible random teams generated, a probability factor is applied to a pool of colors that may be prepended to the mascots. 

For example, you could end up with a list of teams like this: 
- Arlington Heights Sugar Gliders
- Old Bridge Tumbleweeds
- Sarasota White Chinchillas
- Clearfield Sugar Gliders
- Massapequa Purple Parsnips
- Forest Hills Rutabagas

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
- Configure counts (e.g. number of teams, events, teams per event, players)
- Pick which user roles to include
- Select the option to generate passwords and hash values for those users

The generated CSV files will appear in the chosen folder.

![](https://github.com/TwistedNonsense/MockTeamGen/blob/main/GUI_MockDataGen.png)

### Command Line
Each generator can also be run directly. For ex:
```bash
python generate_mock_teams.py --num-teams 50 --out mock_teams.csv
python generate_mock_venues.py --teams-csv mock_teams.csv --out mock_venues.csv
python generate_mock_users.py --teams-csv mock_teams.csv --out mock_users.csv --roles "Coach,Event Admin"
python generate_mock_events.py --teams-csv mock_teams.csv --venues-csv mock_venues.csv \
    --events-out mock_events.csv --join-out mock_events-teams.csv --num-events 20 --teams-per-event 2
python generate_mock_players.py --teams-csv mock_teams.csv
```

## Output Files
- mock_teams.csv
- mock_venues.csv
- mock_users.csv
- mock_events.csv
- mock_events-teams.csv
- mock_players.csv

Each file contains structured relational data suitable for importing into a database.

## License
This project is licensed under the MIT License.
