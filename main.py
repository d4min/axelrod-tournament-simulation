"""
Axelrod Tournament Simulation - Main Script

This script runs a complete Axelrod tournament simulation, including:
- Running the tournament with multiple strategies
- Saving results to a database
- Exporting data for PowerBI visualisation

Usage:
    python main.py [--turns TURNS] [--noise NOISE] [--output-dir DIR]
"""

import os
import argparse
import time
from datetime import datetime

from src.strategy import (
    TitForTat,
    AlwaysCooperate,
    AlwaysDefect,
    Random,
    PureRandom,
    Grudger,
    Pavlov
)
from src.tournament import Tournament
from src.database.db_manager import DatabaseManager
from src.visualisation.powerbi_prep import export_for_powerbi

def parse_args():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(description="Run Axelrod Tournament Simulation")
    parser.add_argument("--turns", type=int, default=200,
                      help="Number of turns per match (default: 200)")
    parser.add_argument("--noise", type=float, default=0.02,
                      help="Noise level (probability of error) (default: 0.02)")
    parser.add_argument("--output-dir", type=str, default="powerbi_data",
                      help="Directory for output files (default: powerbi_data)")
    parser.add_argument("--no-self-plays", action="store_true",
                      help="Exclude matches where strategies play against themselves")
    parser.add_argument("--db-path", type=str, default="axelrod_tournament.db",
                      help="Path to the SQLite database file (default: axelrod_tournament.db)")
    return parser.parse_args()

def main():
    """Run the complete Axelrod tournament simulation pipeline."""
    args = parse_args()
    
    # Create output directory if it doesn't exist
    if not os.path.exists(args.output_dir):
        os.makedirs(args.output_dir)
    
    print("\n" + "="*80)
    print("AXELROD TOURNAMENT SIMULATION")
    print("="*80)
    
    # 1. Initialize database
    print("\n[1/4] Initializing database...")
    db_url = f"sqlite:///{args.db_path}"
    db_manager = DatabaseManager(db_url=db_url)
    db_manager.init_db()
    print(f"Database initialized at {args.db_path}")
    
    # 2. Set up and run tournament
    print("\n[2/4] Setting up tournament...")
    strategies = [
        TitForTat(),
        AlwaysCooperate(),
        AlwaysDefect(),
        Random(cooperation_probability=0.7),
        PureRandom(),
        Grudger(),
        Pavlov()
    ]
    
    print(f"Running tournament with {len(strategies)} strategies:")
    for i, strategy in enumerate(strategies):
        print(f"  {i+1}. {strategy.name}")
    
    print(f"\nTournament parameters:")
    print(f"  - Turns per match: {args.turns}")
    print(f"  - Noise level: {args.noise}")
    print(f"  - Self-plays: {not args.no_self_plays}")
    
    start_time = time.time()
    
    tournament = Tournament(
        strategies=strategies,
        turns=args.turns,
        noise=args.noise,
        self_plays=not args.no_self_plays
    )
    
    print("\nRunning tournament (this may take a while)...")
    results = tournament.run()
    
    duration = time.time() - start_time
    print(f"Tournament completed in {duration:.2f} seconds")
    print(f"Total matches: {results['tournament_config']['num_matches']}")
    
    # 3. Save results to database
    print("\n[3/4] Saving results to database...")
    tournament_id = db_manager.save_tournament(results)
    print(f"Tournament saved to database with ID: {tournament_id}")
    
    # Retrieve tournament data in the format needed for export
    tournament_data = db_manager.get_tournament(tournament_id)
    
    # 4. Export data for PowerBI
    print("\n[4/4] Exporting data for PowerBI...")
    files = export_for_powerbi(tournament_data, output_dir=args.output_dir)
    
    print("\nFiles exported for PowerBI:")
    for name, path in files.items():
        print(f"  - {name}: {path}")
    
    # 5. Display results summary
    print("\n" + "="*80)
    print("TOURNAMENT RESULTS SUMMARY")
    print("="*80)
    
    print("\nStrategy Rankings:")
    print("-" * 60)
    print(f"{'Rank':<6}{'Strategy':<20}{'Avg Score':<15}{'Cooperation Rate':<20}{'Wins':<10}")
    print("-" * 60)
    
    for i, player in enumerate(results["players"]):
        print(f"{i+1:<6}{player['name']:<20}{player['avg_score']:<15.2f}"
              f"{player['avg_cooperation_rate']:<20.2f}{player['wins']:<10}")
    
    print("\n" + "="*80)
    print("NEXT STEPS")
    print("="*80)
    print("1. Open PowerBI Desktop")
    print("2. Click 'Get Data' > 'Text/CSV'")
    print(f"3. Navigate to the {args.output_dir} directory")
    print("4. Import each CSV file")
    print("5. Create relationships between datasets")
    print("6. Create visualizations as described in docs/visualization_guide.md")
    
    print("\nDone! Thank you for using the Axelrod Tournament Simulation.")


if __name__ == "__main__":
    main()