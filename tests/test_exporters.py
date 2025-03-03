"""
Tests for the data exporter functionality.
"""

import os
import tempfile
import json
import pytest
import pandas as pd

from src.strategy import TitForTat, AlwaysDefect
from src.tournament import Tournament
from src.database.exporters import (
    export_tournament_to_csv,
    export_tournament_to_json,
    export_tournament_to_excel,
    prepare_powerbi_dataset
)
from src.database.db_manager import DatabaseManager


@pytest.fixture
def tournament_data():
    """Run a tournament and prepare data in the format returned by get_tournament."""
    # Run a simple tournament
    strategies = [TitForTat(), AlwaysDefect()]
    tournament = Tournament(strategies=strategies, turns=5)
    results = tournament.run()
    
    # Convert to the format returned by get_tournament
    payoffs = results["tournament_config"]["payoffs"]
    config = {
        "turns": results["tournament_config"]["turns"],
        "noise": results["tournament_config"]["noise"],
        "self_plays": results["tournament_config"]["self_plays"],
        "num_strategies": results["tournament_config"]["num_strategies"],
        "num_matches": results["tournament_config"]["num_matches"],
        "payoffs": payoffs
    }
    
    # Add IDs and timestamp for database format compatibility
    tournament_data = {
        "id": 1,
        "timestamp": "2023-01-01T12:00:00",
        "config": config,
        "duration": results["duration"],
        "players": [],
        "matches": []
    }
    
    # Add player data with IDs
    for i, player in enumerate(results["players"]):
        tournament_data["players"].append({
            "id": i + 1,
            "strategy_name": player["name"],
            "avg_score": player["avg_score"],
            "total_score": player["total_score"],
            "avg_cooperation_rate": player["avg_cooperation_rate"],
            "wins": player["wins"],
            "rank": i + 1
        })
    
    # Add match data with IDs
    for i, match in enumerate(results["matches"]):
        # Find player IDs based on original player IDs
        p1_id = next(p["id"] for p in tournament_data["players"] 
                    if p["strategy_name"] == match["player1"]["name"])
        p2_id = next(p["id"] for p in tournament_data["players"]
                    if p["strategy_name"] == match["player2"]["name"])
                    
        tournament_data["matches"].append({
            "id": i + 1,
            "player1_id": p1_id,
            "player2_id": p2_id,
            "player1_score": match["player1"]["score"],
            "player2_score": match["player2"]["score"],
            "player1_cooperation_rate": match["player1"]["cooperation_rate"],
            "player2_cooperation_rate": match["player2"]["cooperation_rate"],
            "outcome": match["outcome"],
            "turns": match["turns"]
        })
    
    return tournament_data


def test_export_to_csv(tournament_data):
    """Test exporting tournament data to CSV files."""
    with tempfile.TemporaryDirectory() as tmpdir:
        # Export to CSV
        files = export_tournament_to_csv(tournament_data, output_dir=tmpdir)
        
        # Verify files were created
        assert os.path.exists(files["tournament_file"])
        assert os.path.exists(files["players_file"])
        assert os.path.exists(files["matches_file"])
        
        # Check content of files
        # Tournament info
        with open(files["tournament_file"], 'r') as f:
            content = f.read()
            assert "Tournament ID,1" in content.replace(" ", "")
            assert f"Turns,{tournament_data['config']['turns']}" in content.replace(" ", "")
        
        # Players
        with open(files["players_file"], 'r') as f:
            content = f.read()
            for player in tournament_data["players"]:
                assert str(player["id"]) in content
                assert player["strategy_name"] in content
        
        # Matches
        with open(files["matches_file"], 'r') as f:
            content = f.read()
            for match in tournament_data["matches"]:
                assert str(match["id"]) in content
                assert str(match["player1_id"]) in content
                assert str(match["player2_id"]) in content


def test_export_to_json(tournament_data):
    """Test exporting tournament data to JSON file."""
    with tempfile.TemporaryDirectory() as tmpdir:
        # Export to JSON
        json_file = export_tournament_to_json(tournament_data, output_dir=tmpdir)
        
        # Verify file was created
        assert os.path.exists(json_file)
        
        # Check content of file
        with open(json_file, 'r') as f:
            loaded_data = json.load(f)
            
            # Verify tournament info
            assert loaded_data["id"] == tournament_data["id"]
            assert loaded_data["timestamp"] == tournament_data["timestamp"]
            assert loaded_data["config"]["turns"] == tournament_data["config"]["turns"]
            
            # Verify players
            assert len(loaded_data["players"]) == len(tournament_data["players"])
            
            # Verify matches
            assert len(loaded_data["matches"]) == len(tournament_data["matches"])


def test_export_to_excel(tournament_data):
    """Test exporting tournament data to Excel file."""
    with tempfile.TemporaryDirectory() as tmpdir:
        # Export to Excel
        excel_file = export_tournament_to_excel(tournament_data, output_dir=tmpdir)
        
        # Verify file was created
        assert os.path.exists(excel_file)
        
        # Check content of file - read all sheets
        with pd.ExcelFile(excel_file) as xls:
            # Verify sheet names
            assert "Tournament Info" in xls.sheet_names
            assert "Players" in xls.sheet_names
            assert "Matches" in xls.sheet_names
            
            # Check content of Players sheet
            players_df = pd.read_excel(xls, "Players")
            assert len(players_df) == len(tournament_data["players"])
            
            # Check content of Matches sheet
            matches_df = pd.read_excel(xls, "Matches")
            assert len(matches_df) == len(tournament_data["matches"])


def test_prepare_powerbi_dataset(tournament_data):
    """Test preparing a dataset for PowerBI."""
    # Prepare dataset
    datasets = prepare_powerbi_dataset(tournament_data)
    
    # Verify datasets are pandas DataFrames
    assert isinstance(datasets["tournament"], pd.DataFrame)
    assert isinstance(datasets["players"], pd.DataFrame)
    assert isinstance(datasets["matches"], pd.DataFrame)
    
    # Check content
    assert len(datasets["tournament"]) == 1
    assert datasets["tournament"]["TournamentID"].iloc[0] == tournament_data["id"]
    
    assert len(datasets["players"]) == len(tournament_data["players"])
    assert len(datasets["matches"]) == len(tournament_data["matches"])


def test_prepare_powerbi_dataset_with_history(tournament_data):
    """Test preparing a dataset for PowerBI with history included."""
    # Add some history data to a match
    tournament_data["matches"][0]["history"] = [
        ["C", "C"],
        ["C", "D"],
        ["D", "D"]
    ]
    
    # Prepare dataset with history
    datasets = prepare_powerbi_dataset(tournament_data, include_history=True)
    
    # Verify history dataset exists
    assert "history" in datasets
    assert isinstance(datasets["history"], pd.DataFrame)
    
    # Check content
    assert len(datasets["history"]) == 3  # 3 turns of history
    assert "Turn" in datasets["history"].columns
    assert "MatchID" in datasets["history"].columns
    assert "Player1Action" in datasets["history"].columns
    assert "Player2Action" in datasets["history"].columns