# Power BI Integration Guide

This guide explains how to use Power BI with the Axelrod Tournament Simulation project to create visualizations and dashboards.

## Overview

The project includes tools to export tournament data in formats optimized for Power BI. These exported datasets are designed to make it easy to create various visualizations:

- Strategy performance comparisons
- Cooperation rate heatmaps
- Head-to-head analysis
- Tournament statistics

## Exported Datasets

When you run export_for_powerbi(), the following CSV files are created:

1. tournament_{id}.csv: Basic tournament information
1. players_{id}.csv: Player/strategy results and rankings
1. matches_{id}.csv: Individual match results
1. strategy_scores_{id}.csv: Strategy vs. strategy scores in a format optimized for heatmaps
1. strategy_cooperation_{id}.csv: Cooperation rates in a format optimized for heatmaps
1. head_to_head_{id}.csv: Direct comparison data between pairs of strategies

## Step by Step Guide

### 1. Export Tournament Data

```python
from src.tournament import Tournament
from src.strategy import TitForTat, AlwaysDefect, AlwaysCooperate
from src.database.db_manager import DatabaseManager
from src.visualization.powerbi_prep import export_for_powerbi

# Run a tournament
tournament = Tournament(
    strategies=[TitForTat(), AlwaysDefect(), AlwaysCooperate()],
    turns=200
)
results = tournament.run()

# Save to database
db_manager = DatabaseManager()
db_manager.init_db()
tournament_id = db_manager.save_tournament(results)

# Retrieve from database in the format needed for export
tournament_data = db_manager.get_tournament(tournament_id)

# Export data for Power BI
files = export_for_powerbi(tournament_data, output_dir="powerbi_data")
```

### 2. Open PowerBI Desktop

    1. Install [Power BI Desktop](https://www.microsoft.com/en-us/power-platform/products/power-bi/desktop)
    1. Open Power BI Desktop

### 3. Import the Data

    1. Click "Get Data" > "Text/CSV"
    1. Navigate to your exported CSV files and import them one by one
    1. For each dataset, click "Load" to add it to the model

### 4. Create Relationships

Power BI will automatically detect most relationships based on column names, but you may need to manually create some:

    1. Go to "Model" view
    1. Create relationships between:
        - tournament.TournamentID → players.TournamentID
        - tournament.TournamentID → matches.TournamentID
        - tournament.TournamentID → strategy_scores.TournamentID
        - tournament.TournamentID → strategy_cooperation.TournamentID
        - tournament.TournamentID → head_to_head.TournamentID

### 5. Create Visualisations

Here are some recommended visualisations:

#### Strategy Performance Overview

Create a bar chart:

    - Values: players.avg_score
    - Axis: players.strategy_name
    - Sort by: players.avg_score (descending)

#### Cooperation Rate Heatmap

Create a matrix visual:

    - Rows: strategy_cooperation.Strategy
    - Columns: strategy_cooperation.Opponent
    - Values: strategy_cooperation.CooperationRate
    - Format the visual as a heatmap with a color scale

#### Head to Head Comparison

Create a table:

    - Columns: head_to_head.Strategy1, head_to_head.Strategy2, head_to_head.Strategy1Score, head_to_head.Strategy2Score, head_to_head.Advantage
    - Sort by: head_to_head.ScoreDifference (descending)

#### Tournament Stats Card

Create a card visual showing:

    - tournament.NumStrategies
    - tournament.NumMatches
    - tournament.Turns
    - tournament.Noise
