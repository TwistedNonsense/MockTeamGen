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
