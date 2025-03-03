"""
PowerBI integration utilities for the Axelrod tournament simulation.

This module provides functions to prepare and export data specifically for PowerBI.
"""

import os
import pandas as pd
import numpy as np
from datetime import datetime

from src.database.exporters import prepare_powerbi_dataset

def create_strategy_comparison_dataset(tournament_data):
    """
    Create a dataset specifically designed for strategy comparison visualisations.
    
    This function transforms the tournament data into a format optimized for
    creating strategy vs. strategy heatmaps and comparison charts in PowerBI.
    
    Args:
        tournament_data: Dictionary containing tournament data
        
    Returns:
        Dictionary containing DataFrames optimized for strategy comparisons
    """
    # Get basic PowerBI dataset
    datasets = prepare_powerbi_dataset(tournament_data)
    
    # Create a strategy lookup dictionary for efficiency
    strategies = {}
    for player in tournament_data["players"]:
        strategies[player["id"]] = {
            "name": player["strategy_name"],
            "rank": player["rank"],
            "avg_score": player["avg_score"],
            "cooperation_rate": player["avg_cooperation_rate"]
        }
    
    # Create a strategy vs. strategy matrix for heatmap visualisation
    strategy_names = list(set(player["strategy_name"] for player in tournament_data["players"]))
    strategy_names.sort()
    
    # Initialize matrix with NaN
    num_strategies = len(strategy_names)
    score_matrix = np.full((num_strategies, num_strategies), np.nan)
    cooperation_matrix = np.full((num_strategies, num_strategies), np.nan)
    
    # Fill the matrices
    for match in tournament_data["matches"]:
        p1_id = match["player1_id"]
        p2_id = match["player2_id"]
        
        p1_name = strategies[p1_id]["name"]
        p2_name = strategies[p2_id]["name"]
        
        p1_idx = strategy_names.index(p1_name)
        p2_idx = strategy_names.index(p2_name)
        
        # Record player 1's score against player 2
        score_matrix[p1_idx, p2_idx] = match["player1_score"]
        cooperation_matrix[p1_idx, p2_idx] = match["player1_cooperation_rate"]
    
    # Convert matrices to long form for PowerBI
    score_rows = []
    cooperation_rows = []
    
    for i, strategy1 in enumerate(strategy_names):
        for j, strategy2 in enumerate(strategy_names):
            if not np.isnan(score_matrix[i, j]):
                score_rows.append({
                    "Strategy": strategy1,
                    "Opponent": strategy2,
                    "Score": score_matrix[i, j],
                    "TournamentID": tournament_data["id"]
                })
                
                cooperation_rows.append({
                    "Strategy": strategy1,
                    "Opponent": strategy2,
                    "CooperationRate": cooperation_matrix[i, j],
                    "TournamentID": tournament_data["id"]
                })
    
    # Create DataFrames
    strategy_scores_df = pd.DataFrame(score_rows)
    strategy_cooperation_df = pd.DataFrame(cooperation_rows)
    
    # Add head-to-head comparison summary
    head_to_head_rows = []
    for i, strategy1 in enumerate(strategy_names):
        for j, strategy2 in enumerate(strategy_names):
            if i < j:  # Only do pairs once
                # Find matches between these strategies
                pair_matches = []
                for match in tournament_data["matches"]:
                    p1_name = strategies[match["player1_id"]]["name"]
                    p2_name = strategies[match["player2_id"]]["name"]
                    
                    if (p1_name == strategy1 and p2_name == strategy2) or \
                       (p1_name == strategy2 and p2_name == strategy1):
                        pair_matches.append(match)
                
                # If we found matches between these strategies
                if pair_matches:
                    # Calculate statistics
                    total_score1 = sum(
                        match["player1_score"] if strategies[match["player1_id"]]["name"] == strategy1 
                        else match["player2_score"]
                        for match in pair_matches
                    )
                    
                    total_score2 = sum(
                        match["player1_score"] if strategies[match["player1_id"]]["name"] == strategy2 
                        else match["player2_score"]
                        for match in pair_matches
                    )
                    
                    advantage = "Tie"
                    if total_score1 > total_score2:
                        advantage = strategy1
                    elif total_score2 > total_score1:
                        advantage = strategy2
                    
                    head_to_head_rows.append({
                        "Strategy1": strategy1,
                        "Strategy2": strategy2,
                        "Strategy1Score": total_score1,
                        "Strategy2Score": total_score2,
                        "Advantage": advantage,
                        "ScoreDifference": abs(total_score1 - total_score2),
                        "TournamentID": tournament_data["id"]
                    })
    
    head_to_head_df = pd.DataFrame(head_to_head_rows)
    
    # Add to the dataset dictionary
    datasets["strategy_scores"] = strategy_scores_df
    datasets["strategy_cooperation"] = strategy_cooperation_df
    datasets["head_to_head"] = head_to_head_df
    
    return datasets


def export_for_powerbi(tournament_data, output_dir=None):
    """
    Export tournament data in a format optimized for PowerBI.
    
    Args:
        tournament_data: Dictionary containing tournament data
        output_dir: Directory to save files (defaults to current directory)
        
    Returns:
        Dictionary with paths to created files
    """
    if output_dir is None:
        output_dir = "."
        
    os.makedirs(output_dir, exist_ok=True)
    
    tournament_id = tournament_data["id"]
    timestamp = datetime.fromisoformat(tournament_data["timestamp"]).strftime("%Y%m%d_%H%M%S")
    
    # Create the datasets
    datasets = create_strategy_comparison_dataset(tournament_data)
    
    # Export each dataset to CSV
    files = {}
    for name, df in datasets.items():
        file_path = os.path.join(output_dir, f"{name}_{tournament_id}_{timestamp}.csv")
        df.to_csv(file_path, index=False)
        files[name] = file_path
    
    return files


def create_powerbi_template_data(tournament_results):
    """
    Create sample data files that can be used with the PowerBI template.
    
    This function takes tournament results directly from a Tournament object
    and exports them in the format expected by the PowerBI template.
    
    Args:
        tournament_results: Dictionary containing tournament results from Tournament.run()
        
    Returns:
        Dictionary with paths to created files
    """
    # Convert tournament results to database format
    tournament_data = {
        "id": 1,  # Sample ID
        "timestamp": datetime.now().isoformat(),
        "config": tournament_results["tournament_config"],
        "duration": tournament_results["duration"],
        "players": [],
        "matches": tournament_results["matches"]
    }
    
    # Add player data with IDs
    for i, player in enumerate(tournament_results["players"]):
        tournament_data["players"].append({
            "id": i + 1,
            "strategy_name": player["name"],
            "avg_score": player["avg_score"],
            "total_score": player["total_score"],
            "avg_cooperation_rate": player["avg_cooperation_rate"],
            "wins": player["wins"],
            "rank": i + 1
        })
    
    # Add match IDs
    for i, match in enumerate(tournament_data["matches"]):
        match["id"] = i + 1
        
        # Find player IDs based on names
        p1_name = match["player1"]["name"]
        p2_name = match["player2"]["name"]
        
        match["player1_id"] = next(p["id"] for p in tournament_data["players"] if p["strategy_name"] == p1_name)
        match["player2_id"] = next(p["id"] for p in tournament_data["players"] if p["strategy_name"] == p2_name)
    
    # Export for PowerBI
    return export_for_powerbi(tournament_data, "powerbi_template_data")