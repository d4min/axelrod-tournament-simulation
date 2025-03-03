"""
Tests for the Database module.
"""

import os
import tempfile
import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from src.strategy import TitForTat, AlwaysDefect
from src.tournament import Tournament
from src.database.db_manager import DatabaseManager
from src.database.models import Base, Tournament as DbTournament, Player as DbPlayer, Match as DbMatch

@pytest.fixture
def db_manager():
    """Create a temporary database for testing."""
    # Use in-memory SQLite database for tests
    db_manager = DatabaseManager(db_url="sqlite:///:memory:")
    db_manager.init_db()
    yield db_manager
    db_manager.close_sessions()


@pytest.fixture
def tournament_results():
    """Run a simple tournament and return the results."""
    strategies = [TitForTat(), AlwaysDefect()]
    tournament = Tournament(strategies=strategies, turns=10)
    return tournament.run()

def test_db_initialisation():
    """
    Test database initialisation.
    """
    # Check that we can get a session
    session = db_manager.get_session()
    
    # Verify the tables exist by querying them
    tournaments = session.query(DbTournament).all()
    players = session.query(DbPlayer).all()
    matches = session.query(DbMatch).all()
    
    # Should be empty but not error
    assert len(tournaments) == 0
    assert len(players) == 0
    assert len(matches) == 0
    
    session.close()

def test_save_tournament(db_manager, tournament_results):
    """Test saving tournament results to the database."""
    # Save tournament results
    tournament_id = db_manager.save_tournament(tournament_results)
    
    # Verify tournament was saved with an ID
    assert tournament_id is not None
    assert isinstance(tournament_id, int)
    
    # Check that tournament exists in DB
    session = db_manager.get_session()
    tournament = session.query(DbTournament).filter_by(id=tournament_id).first()
    
    assert tournament is not None
    assert tournament.turns == tournament_results["tournament_config"]["turns"]
    assert tournament.noise == tournament_results["tournament_config"]["noise"]
    
    # Verify players were saved
    players = session.query(DbPlayer).filter_by(tournament_id=tournament_id).all()
    assert len(players) == len(tournament_results["players"])
    
    # Verify matches were saved
    matches = session.query(DbMatch).filter_by(tournament_id=tournament_id).all()
    assert len(matches) == len(tournament_results["matches"])
    
    session.close()


def test_get_tournament(db_manager, tournament_results):
    """Test retrieving tournament results from the database."""
    # Save tournament results
    tournament_id = db_manager.save_tournament(tournament_results)
    
    # Retrieve tournament data
    retrieved_data = db_manager.get_tournament(tournament_id)
    
    # Verify basic tournament properties
    assert retrieved_data["id"] == tournament_id
    assert retrieved_data["config"]["turns"] == tournament_results["tournament_config"]["turns"]
    assert retrieved_data["config"]["noise"] == tournament_results["tournament_config"]["noise"]
    
    # Verify players were retrieved
    assert len(retrieved_data["players"]) == len(tournament_results["players"])
    
    # Verify matches were retrieved
    assert len(retrieved_data["matches"]) == len(tournament_results["matches"])


def test_get_nonexistent_tournament(db_manager):
    """Test retrieving a tournament that doesn't exist."""
    with pytest.raises(ValueError):
        db_manager.get_tournament(999)  # ID that doesn't exist


def test_get_all_tournaments(db_manager, tournament_results):
    """Test retrieving all tournaments."""
    # Initially should be empty
    tournaments = db_manager.get_all_tournaments()
    assert len(tournaments) == 0
    
    # Save a tournament
    tournament_id = db_manager.save_tournament(tournament_results)
    
    # Now should have one tournament
    tournaments = db_manager.get_all_tournaments()
    assert len(tournaments) == 1
    assert tournaments[0]["id"] == tournament_id
    
    # Save another tournament
    tournament_id2 = db_manager.save_tournament(tournament_results)
    
    # Now should have two tournaments
    tournaments = db_manager.get_all_tournaments()
    assert len(tournaments) == 2
    assert {t["id"] for t in tournaments} == {tournament_id, tournament_id2}


def test_delete_tournament(db_manager, tournament_results):
    """Test deleting a tournament."""
    # Save a tournament
    tournament_id = db_manager.save_tournament(tournament_results)
    
    # Verify it exists
    session = db_manager.get_session()
    tournament = session.query(DbTournament).filter_by(id=tournament_id).first()
    assert tournament is not None
    
    # Delete the tournament
    result = db_manager.delete_tournament(tournament_id)
    assert result is True
    
    # Verify it's gone
    tournament = session.query(DbTournament).filter_by(id=tournament_id).first()
    assert tournament is None
    
    # Verify players are also gone (cascade delete)
    players = session.query(DbPlayer).filter_by(tournament_id=tournament_id).all()
    assert len(players) == 0
    
    # Verify matches are also gone (cascade delete)
    matches = session.query(DbMatch).filter_by(tournament_id=tournament_id).all()
    assert len(matches) == 0
    
    session.close()


def test_delete_nonexistent_tournament(db_manager):
    """Test deleting a tournament that doesn't exist."""
    result = db_manager.delete_tournament(999)  # ID that doesn't exist
    assert result is False