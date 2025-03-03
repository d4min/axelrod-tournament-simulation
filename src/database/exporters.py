"""
Data exporters for the Axelrod tournament simulation.

This module provides functions for exporting tournament data to various formats
for analysis in tools like PowerBI.
"""

import os
import csv
import json
import pandas as pd
from datetime import datetime

def export_tournament_to_csv(tournament_data, output_dir=None):
    """
    Export tournament data to CSV files.
    
    Creates three CSV files:
    - tournament_info_{id}.csv: General tournament information
    - players_{id}.csv: Player rankings and stats
    - matches_{id}.csv: Match results
    
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
    
    # File paths
    tournament_file = os.path.join(output_dir, f"tournament_info_{tournament_id}_{timestamp}.csv")
    players_file = os.path.join(output_dir, f"players_{tournament_id}_{timestamp}.csv")
    matches_file = os.path.join(output_dir, f"matches_{tournament_id}_{timestamp}.csv")

    with open(tournament_file, "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["Parameter", "Value"])
        writer.writerow(["Tournament ID", tournament_id])
        writer.writerow(["Timestamp", tournament_data["timestamp"]])
        writer.writerow(["Turns", tournament_data["config"]["turns"]])
        writer.writerow(["Noise", tournament_data["config"]["noise"]])
        writer.writerow(["Self Plays", tournament_data["config"]["self_plays"]])
        writer.writerow(["Number of Strategies", tournament_data["config"]["num_strategies"]])
        writer.writerow(["Number of Matches", tournament_data["config"]["num_matches"]])
        writer.writerow(["Duration (seconds)", tournament_data["duration"]])
        writer.writerow(["Payoff R", tournament_data["config"]["payoffs"]["R"]])
        writer.writerow(["Payoff T", tournament_data["config"]["payoffs"]["T"]])
        writer.writerow(["Payoff P", tournament_data["config"]["payoffs"]["P"]])
        writer.writerow(["Payoff S", tournament_data["config"]["payoffs"]["S"]])
    
    # Export players data
    with open(players_file, "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow([
            "Player ID", "Strategy Name", "Average Score", "Total Score",
            "Average Cooperation Rate", "Wins", "Rank"
        ])
        
        for player in tournament_data["players"]:
            writer.writerow([
                player["id"],
                player["strategy_name"],
                player["avg_score"],
                player["total_score"],
                player["avg_cooperation_rate"],
                player["wins"],
                player["rank"]
            ])
    
    # Export matches data
    with open(matches_file, "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow([
            "Match ID", "Player 1 ID", "Player 2 ID", "Player 1 Score",
            "Player 2 Score", "Player 1 Cooperation Rate", "Player 2 Cooperation Rate",
            "Outcome", "Turns"
        ])
        
        for match in tournament_data["matches"]:
            writer.writerow([
                match["id"],
                match["player1_id"],
                match["player2_id"],
                match["player1_score"],
                match["player2_score"],
                match["player1_cooperation_rate"],
                match["player2_cooperation_rate"],
                match["outcome"],
                match["turns"]
            ])
    
    return {
        "tournament_file": tournament_file,
        "players_file": players_file,
        "matches_file": matches_file
    }

def export_tournament_to_json(tournament_data, output_dir=None):
    """
    Export tournament data to a JSON file.
    
    Args:
        tournament_data: Dictionary containing tournament data
        output_dir: Directory to save file (defaults to current directory)
        
    Returns:
        Path to created file
    """
    if output_dir is None:
        output_dir = "."
        
    os.makedirs(output_dir, exist_ok=True)
    
    tournament_id = tournament_data["id"]
    timestamp = datetime.fromisoformat(tournament_data["timestamp"]).strftime("%Y%m%d_%H%M%S")
    
    # File path
    json_file = os.path.join(output_dir, f"tournament_{tournament_id}_{timestamp}.json")
    
    # Export to JSON
    with open(json_file, "w") as f:
        json.dump(tournament_data, f, indent=2)
    
    return json_file

def export_tournament_to_excel(tournament_data, output_dir=None):
    """
    Export tournament data to an Excel file with multiple sheets.
    
    Args:
        tournament_data: Dictionary containing tournament data
        output_dir: Directory to save file (defaults to current directory)
        
    Returns:
        Path to created file
    """
    if output_dir is None:
        output_dir = "."
        
    os.makedirs(output_dir, exist_ok=True)
    
    tournament_id = tournament_data["id"]
    timestamp = datetime.fromisoformat(tournament_data["timestamp"]).strftime("%Y%m%d_%H%M%S")
    
    # File path
    excel_file = os.path.join(output_dir, f"tournament_{tournament_id}_{timestamp}.xlsx")
    
    # Create Excel writer
    with pd.ExcelWriter(excel_file) as writer:
        # Tournament info sheet
        info_data = {
            "Parameter": [
                "Tournament ID", "Timestamp", "Turns", "Noise", "Self Plays",
                "Number of Strategies", "Number of Matches", "Duration (seconds)",
                "Payoff R", "Payoff T", "Payoff P", "Payoff S"
            ],
            "Value": [
                tournament_id,
                tournament_data["timestamp"],
                tournament_data["config"]["turns"],
                tournament_data["config"]["noise"],
                tournament_data["config"]["self_plays"],
                tournament_data["config"]["num_strategies"],
                tournament_data["config"]["num_matches"],
                tournament_data["duration"],
                tournament_data["config"]["payoffs"]["R"],
                tournament_data["config"]["payoffs"]["T"],
                tournament_data["config"]["payoffs"]["P"],
                tournament_data["config"]["payoffs"]["S"]
            ]
        }
        info_df = pd.DataFrame(info_data)
        info_df.to_excel(writer, sheet_name="Tournament Info", index=False)
        
        # Players sheet
        players_df = pd.DataFrame(tournament_data["players"])
        players_df.to_excel(writer, sheet_name="Players", index=False)
        
        # Matches sheet
        matches_df = pd.DataFrame(tournament_data["matches"])
        matches_df.to_excel(writer, sheet_name="Matches", index=False)
    
    return excel_file

def prepare_powerbi_dataset(tournament_data, include_history=False):
    """
    Prepare a dataset optimized for PowerBI import.
    
    Creates multiple DataFrames that can be loaded into PowerBI.
    
    Args:
        tournament_data: Dictionary containing tournament data
        include_history: Whether to include detailed match history
        
    Returns:
        Dictionary of DataFrames ready for PowerBI
    """
    # Tournament table
    tournament = {
        "TournamentID": [tournament_data["id"]],
        "Timestamp": [tournament_data["timestamp"]],
        "Turns": [tournament_data["config"]["turns"]],
        "Noise": [tournament_data["config"]["noise"]],
        "SelfPlays": [tournament_data["config"]["self_plays"]],
        "NumStrategies": [tournament_data["config"]["num_strategies"]],
        "NumMatches": [tournament_data["config"]["num_matches"]],
        "Duration": [tournament_data["duration"]],
        "PayoffR": [tournament_data["config"]["payoffs"]["R"]],
        "PayoffT": [tournament_data["config"]["payoffs"]["T"]],
        "PayoffP": [tournament_data["config"]["payoffs"]["P"]],
        "PayoffS": [tournament_data["config"]["payoffs"]["S"]]
    }
    tournament_df = pd.DataFrame(tournament)
    
    # Players table
    players_df = pd.DataFrame(tournament_data["players"])
    players_df["TournamentID"] = tournament_data["id"]
    
    # Matches table
    matches_df = pd.DataFrame(tournament_data["matches"])
    matches_df["TournamentID"] = tournament_data["id"]
    
    # Optional: Match history table
    history_df = None
    if include_history:
        history_rows = []
        for match in tournament_data["matches"]:
            if "history" in match:
                match_id = match["id"]
                for turn, (p1_action, p2_action) in enumerate(match["history"]):
                    history_rows.append({
                        "MatchID": match_id,
                        "Turn": turn + 1,
                        "Player1Action": p1_action,
                        "Player2Action": p2_action
                    })
        
        if history_rows:
            history_df = pd.DataFrame(history_rows)
    
    result = {
        "tournament": tournament_df,
        "players": players_df,
        "matches": matches_df
    }
    
    if history_df is not None:
        result["history"] = history_df
    
    return result