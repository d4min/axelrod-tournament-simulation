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

## Installation 

```bash
git clone https://github.com/d4min/axelrod-tournament.git
cd axelrod-tournament
pip install -r requirements.txt
```

## Usage Example

```python
from src.game import Game
from src.strategy import TitForTat, AlwaysDefect
from src.player import Player
from src.match import Match

# Create players with different strategies
player1 = Player(TitForTat())
player2 = Player(AlwaysDefect())

# Create and run a match
match = Match(player1, player2, turns=100)
results = match.play()

# View results
print(f"Player 1 ({player1.name}) score: {results['player1']['score']}")
print(f"Player 2 ({player2.name}) score: {results['player2']['score']}")
print(f"Outcome: {results['outcome']}")
print(f"Cooperation rates: {results['player1']['cooperation_rate']} vs {results['player2']['cooperation_rate']}")
```

## Testing 

```bash
python -m pytest tests/
```