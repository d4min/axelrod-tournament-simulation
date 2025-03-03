"""
Tests for the strategy implementations.
"""
import pytest
from src.game import Action
from src.strategy import (
    TitForTat, 
    AlwaysCooperate, 
    AlwaysDefect, 
    Random, 
    Grudger,
)

def test_tit_for_tat():
    """
    Test that TitForTat behaves as expected.
    """    
    strategy = TitForTat()

    # Should cooperate on first move
    assert strategy.make_move([], []) == Action.COOPERATE
    
    # Should copy opponent's last move
    assert strategy.make_move([Action.COOPERATE], [Action.COOPERATE]) == Action.COOPERATE
    assert strategy.make_move([Action.COOPERATE], [Action.DEFECT]) == Action.DEFECT
    
    # Should still copy with longer history
    assert strategy.make_move(
        [Action.COOPERATE, Action.DEFECT, Action.COOPERATE],
        [Action.COOPERATE, Action.COOPERATE, Action.DEFECT]
    ) == Action.DEFECT

def test_always_cooperate():
    """Test that AlwaysCooperate behaves as expected."""
    strategy = AlwaysCooperate()
    
    # Should cooperate on first move
    assert strategy.make_move([], []) == Action.COOPERATE
    
    # Should cooperate regardless of opponent's move
    assert strategy.make_move([Action.COOPERATE], [Action.COOPERATE]) == Action.COOPERATE
    assert strategy.make_move([Action.COOPERATE], [Action.DEFECT]) == Action.COOPERATE
    
    # Should cooperate with longer history
    assert strategy.make_move(
        [Action.COOPERATE, Action.COOPERATE, Action.COOPERATE],
        [Action.COOPERATE, Action.DEFECT, Action.DEFECT]
    ) == Action.COOPERATE


def test_always_defect():
    """Test that AlwaysDefect behaves as expected."""
    strategy = AlwaysDefect()
    
    # Should defect on first move
    assert strategy.make_move([], []) == Action.DEFECT
    
    # Should defect regardless of opponent's move
    assert strategy.make_move([Action.DEFECT], [Action.COOPERATE]) == Action.DEFECT
    assert strategy.make_move([Action.DEFECT], [Action.DEFECT]) == Action.DEFECT
    
    # Should defect with longer history
    assert strategy.make_move(
        [Action.DEFECT, Action.DEFECT, Action.DEFECT],
        [Action.COOPERATE, Action.COOPERATE, Action.COOPERATE]
    ) == Action.DEFECT


def test_grudger():
    """Test that Grudger behaves as expected."""
    strategy = Grudger()
    
    # Should cooperate on first move
    assert strategy.make_move([], []) == Action.COOPERATE
    
    # Should cooperate if opponent has always cooperated
    assert strategy.make_move([Action.COOPERATE], [Action.COOPERATE]) == Action.COOPERATE
    assert strategy.make_move(
        [Action.COOPERATE, Action.COOPERATE],
        [Action.COOPERATE, Action.COOPERATE]
    ) == Action.COOPERATE
    
    # Should defect forever after opponent defects once
    assert strategy.make_move([Action.COOPERATE], [Action.DEFECT]) == Action.DEFECT
    
    # Should still defect even if opponent returns to cooperation
    assert strategy.make_move(
        [Action.COOPERATE, Action.DEFECT],
        [Action.DEFECT, Action.COOPERATE]
    ) == Action.DEFECT

def test_random():
    """
    Test the Random strategy.
    
    Since this strategy is truly random, we can only verify that it returns
    a valid action and doesn't raise exceptions.
    """
    strategy = Random()
    
    # Test with empty history
    action = strategy.make_move([], [])
    assert action in [Action.COOPERATE, Action.DEFECT]
    
    # Test with some history
    action = strategy.make_move(
        [Action.COOPERATE, Action.DEFECT],
        [Action.DEFECT, Action.COOPERATE]
    )
    assert action in [Action.COOPERATE, Action.DEFECT]
