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

## Installation 

```bash
git clone https://github.com/d4min/axelrod-tournament.git
cd axelrod-tournament
pip install -r requirements.txt
```