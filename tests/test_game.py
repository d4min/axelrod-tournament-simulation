"""
Tests for the Game class.
"""
import pytest
from src.game import Game, Action

def test_game_initialisation():
    """
    Test that a game can be initialised with default parameters.
    """
    game = Game()
    assert game.R == 3.0
    assert game.T == 5.0
    assert game.P == 1.0
    assert game.S == 0.0

def test_game_custom_payoffs():
    """
    Test that a game can be initialised with custom parameters. 
    """
    game = Game(R=4.0, T=6.0, P=2.0, S=1.0)
    assert game.R == 4.0
    assert game.T == 6.0
    assert game.P == 2.0
    assert game.S == 1.0

def test_invalid_payoffs():
    """
    Test that invalid payoffs raise appropriate exceptions.
    """
     # T > R > P > S must be satisfied
    with pytest.raises(ValueError):
        Game(R=5.0, T=3.0, P=1.0, S=0.0)  # T < R
    
    with pytest.raises(ValueError):
        Game(R=3.0, T=5.0, P=4.0, S=0.0)  # P > R
    
    with pytest.raises(ValueError):
        Game(R=3.0, T=5.0, P=1.0, S=2.0)  # S > P
    
    # 2R > T + S must be satisfied
    with pytest.raises(ValueError):
        Game(R=2.0, T=5.0, P=1.0, S=0.0)  # 2*2 = 4 < 5 + 0 = 5

def test_scoring():
    """
    Test that the scoring function returns the correct payoffs.
    """
    game = Game()
    
    # Both cooperate: both get R
    assert game.score(Action.COOPERATE, Action.COOPERATE) == (3.0, 3.0)
    
    # Player 1 cooperates, Player 2 defects: S, T
    assert game.score(Action.COOPERATE, Action.DEFECT) == (0.0, 5.0)
    
    # Player 1 defects, Player 2 cooperates: T, S
    assert game.score(Action.DEFECT, Action.COOPERATE) == (5.0, 0.0)
    
    # Both defect: both get P
    assert game.score(Action.DEFECT, Action.DEFECT) == (1.0, 1.0)

def test_get_payoffs():
    """
    Tests that get_payoffs returns the correct dictionary. 
    """
    game = Game(R=3.5, T=5.5, P=1.5, S=0.5)
    payoffs = game.get_payoffs()
    
    assert payoffs == {'R': 3.5, 'T': 5.5, 'P': 1.5, 'S': 0.5}