"""
Tests for the player class
"""
import pytest
from src.game import Action
from src.strategy import TitForTat, AlwaysCooperate
from src.player import Player

def test_player_initialisation():
    """
    Test that a player can be initialised properly.
    """
    strategy = TitForTat()
    player = Player(strategy)

    assert player.strategy == strategy
    assert player.name == "TitForTat"
    assert player.actions == []
    assert player.score == 0.0
    assert player.player_id.startswith("TitForTat-")

def test_player_custom_id():
    """Test that a player can be initialised with a custom ID."""
    strategy = TitForTat()
    player = Player(strategy, player_id="Player1")
    
    assert player.player_id == "Player1"

def test_make_move():
    """Test that make_move correctly delegates to the strategy."""
    strategy = TitForTat()
    player = Player(strategy)
    
    # First move with empty histories
    action = player.make_move([])
    assert action == Action.COOPERATE
    
    # Move after opponent defected
    action = player.make_move([Action.DEFECT])
    assert action == Action.DEFECT
    
    # Notice that the player doesn't automatically record its own actions,
    # this must be done separately with record_action

def test_record_action():
    """Test that record_action correctly updates the player's history."""
    player = Player(TitForTat())
    
    assert player.actions == []
    
    player.record_action(Action.COOPERATE)
    assert player.actions == [Action.COOPERATE]
    
    player.record_action(Action.DEFECT)
    assert player.actions == [Action.COOPERATE, Action.DEFECT]

def test_record_score():
    """Test that record_score correctly updates the player's score."""
    player = Player(TitForTat())
    
    assert player.score == 0.0
    
    player.record_score(3.0)
    assert player.score == 3.0
    
    player.record_score(5.0)
    assert player.score == 8.0


def test_reset():
    """Test that reset correctly clears the player's history and score."""
    player = Player(TitForTat())
    
    player.record_action(Action.COOPERATE)
    player.record_action(Action.DEFECT)
    player.record_score(8.0)
    
    assert player.actions == [Action.COOPERATE, Action.DEFECT]
    assert player.score == 8.0
    
    player.reset()
    
    assert player.actions == []
    assert player.score == 0.0


def test_str_representation():
    """Test the string representation of a player."""
    player = Player(TitForTat(), player_id="Player1")
    
    assert str(player) == "Player(Player1, TitForTat)"