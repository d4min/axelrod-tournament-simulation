# Axelrod Tournament Simulation 

This project implements a simulation of the famous iterated Prisoner's Dilemma tournaments conducted by Professor Robert Axelrod in the late 1970s and early 1980s.

## About Axelrod's Work

Robert Axelrod, a political scientist, conducted groundbreaking research on cooperation through computer tournaments of the iterated Prisoner's Dilemma. In these tournaments, various strategies competed against each other over multiple rounds of the Prisoner's Dilemma game.

## Key Findings from Axelrod's Research:

1. Success of Simple Strategies: The remarkably simple TIT FOR TAT strategy (cooperate on the first move, then do whatever your opponent did in the previous round) emerged as the winner in Axelrod's tournaments.

1. Properties of Successful Strategies:

    - Nice: Successful strategies tend to start with cooperation
    - Retaliatory: They respond to defection with defection
    - Forgiving: They return to cooperation after the opponent returns to cooperative behavior
    - Clear: The best strategies were simple and understandable to opponents

1. Evolution of Cooperation: Axelrod showed that cooperation can emerge naturally even in a world of egoists without central authority, particularly when interactions are repeated.

## Project Goals

This project aims to:

- Implement the Prisoner's Dilemma game using object-oriented principles
- Recreate the various strategies from Axelrod's original tournaments
- Simulate tournaments to verify Axelrod's findings
- Store results in a database for further analysis
- Create visualizations using PowerBI

## Project Implementation

The project consists of the following components:

- Game Class: Represents the Prisoner's Dilemma game with configurable payoffs (R, T, P, S)

- Strategy Classes: A collection of strategies including:

    - TitForTat: Cooperates on first move, then copies opponent's last move
    - AlwaysCooperate: Always cooperates
    - AlwaysDefect: Always defects
    - Random: Makes completely random decisions (50/50)
    - Grudger: Cooperates until opponent defects, then always defects

- Player Class: Wraps a strategy and tracks history and score throughout a match

- Match Class: Manages a series of games between two players with:
    - Configurable number of turns
    - Optional noise simulation
    - Detailed results analysis and statistics

- Tournament Class: Organises matches between multiple strategies
    - Round-Robin tournament structure
    - Comprehensive results aggregation
    - Detailed rankings and statistics

- Database Integration: Stores tournament results for persistence and analysis
    - SQLAlchemy ORM models
    - CRUD operations for tournament data
    - Exporters for various formats (CSV, JSON, Excel)

- Power BI Integration
    - Optimised datasets for specific visualisation types
    - Strategy comparison matrices
    - Cooperation rate analysis
    - Head-to-head performance metrics
    
## Installation 

```bash
git clone https://github.com/d4min/axelrod-tournament.git
cd axelrod-tournament
pip install -r requirements.txt
```

## Usage Example

### Running a Basic Tournament

```python
from src.game import Game
from src.strategy import TitForTat, AlwaysDefect, AlwaysCooperate
from src.tournament import Tournament

# Create a tournament with various strategies
tournament = Tournament([
    TitForTat(),
    AlwaysDefect(),
    AlwaysCooperate()
])

# Run the tournament
results = tournament.run()

# Display results
print("\nTournament Rankings:")
for i, player in enumerate(results["players"]):
    print(f"{i+1}. {player['name']} - Score: {player['avg_score']:.2f}")
```

### Saving Results to a Database

```python
from src.database.db_manager import DatabaseManager

# Initialize database
db_manager = DatabaseManager()
db_manager.init_db()

# Save tournament results
tournament_id = db_manager.save_tournament(results)

# Retrieve tournament data
tournament_data = db_manager.get_tournament(tournament_id)
```

### Exporting for PowerBI

```python
from src.visualization.powerbi_prep import export_for_powerbi

# Export tournament data for PowerBI
files = export_for_powerbi(tournament_data, output_dir="powerbi_data")
```

## Testing 

```bash
python -m pytest tests/
```