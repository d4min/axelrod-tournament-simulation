"""
Tests for the Match class
"""

import pytest
from src.game import Game, Action
from src.player import Player
from src.strategy import AlwaysCooperate, AlwaysDefect, TitForTat
from src.match import Match

def test_match_initialisation():
    """
    Test that a match can be initialised with default parameters.
    """
    player1 = Player(AlwaysCooperate())
    player2 = Player(AlwaysDefect())
    
    match = Match(player1, player2)
    
    assert match.player1 == player1
    assert match.player2 == player2
    assert isinstance(match.game, Game)
    assert match.turns == 200
    assert match.noise == 0.0
    assert match.history == []

def test_match_custom_parameters():
    """
    Test that a match can be initialised with custom parameters.
    """
    player1 = Player(AlwaysCooperate())
    player2 = Player(AlwaysDefect())
    game = Game(R=4.0, T=6.0, P=2.0, S=1.0)
    
    match = Match(player1, player2, game=game, turns=100, noise=0.1)
    
    assert match.player1 == player1
    assert match.player2 == player2
    assert match.game == game
    assert match.turns == 100
    assert match.noise == 0.1

def test_invalid_noise():
    """
    Test that match initialisation fails with invalid noise value.
    """
    player1 = Player(AlwaysCooperate())
    player2 = Player(AlwaysDefect())
    
    with pytest.raises(ValueError):
        Match(player1, player2, noise=1.5)

def test_player_reset_on_match_initialisation():
    """
    Test that a players history and points are reset when a match is initialised.
    """
    player1 = Player(AlwaysCooperate())
    player2 = Player(AlwaysDefect())
    
    # Add some history and score to the players
    player1.record_action(Action.COOPERATE)
    player1.record_score(3.0)
    player2.record_action(Action.DEFECT)
    player2.record_score(5.0)
    
    # Initialize a match
    match = Match(player1, player2)
    
    # Players should be reset
    assert player1.actions == []
    assert player1.score == 0.0
    assert player2.actions == []
    assert player2.score == 0.0

def test_play_always_cooperate_vs_always_defect():
    """Test a match between AlwaysCooperate and AlwaysDefect."""
    player1 = Player(AlwaysCooperate())
    player2 = Player(AlwaysDefect())
    match = Match(player1, player2, turns=10)
    
    results = match.play()
    
    # Check player actions
    assert all(action == Action.COOPERATE for action in player1.actions)
    assert all(action == Action.DEFECT for action in player2.actions)
    
    # Check match history
    assert len(match.history) == 10
    assert all(p1_action == Action.COOPERATE for p1_action, _ in match.history)
    assert all(p2_action == Action.DEFECT for _, p2_action in match.history)
    
    # Check scores
    assert player1.score == 0.0  # Sucker's payoff (S=0) * 10 turns
    assert player2.score == 50.0  # Temptation payoff (T=5) * 10 turns
    
    # Check results dict
    assert results["player1"]["cooperation_rate"] == 1.0
    assert results["player2"]["cooperation_rate"] == 0.0
    assert results["outcome"] == "loss"  # Player 1 loses
    assert results["turns"] == 10
    assert results["total_score"] == 50.0


def test_play_tit_for_tat_vs_always_defect():
    """Test a match between TitForTat and AlwaysDefect."""
    player1 = Player(TitForTat())
    player2 = Player(AlwaysDefect())
    match = Match(player1, player2, turns=10)
    
    results = match.play()
    
    # TitForTat should cooperate on first move, then defect
    assert player1.actions[0] == Action.COOPERATE
    assert all(action == Action.DEFECT for action in player1.actions[1:])
    
    # AlwaysDefect should always defect
    assert all(action == Action.DEFECT for action in player2.actions)
    
    # Check scores - first round: (0,5), remaining rounds: (1,1) each
    assert player1.score == 0 + 9 * 1  # S=0 for first round, P=1 for the rest
    assert player2.score == 5 + 9 * 1  # T=5 for first round, P=1 for the rest
    
    # Check results dict
    assert results["player1"]["cooperation_rate"] == 0.1  # 1 out of 10 moves
    assert results["player2"]["cooperation_rate"] == 0.0
    assert results["outcome"] == "loss"  # Player 1 loses


def test_play_with_noise():
    """
    Test that noise properly affects player moves.
    
    This is a probabilistic test, so we use a high noise value and
    multiple turns to have a high probability of seeing at least one
    move affected by noise.
    """
    player1 = Player(AlwaysCooperate())
    player2 = Player(AlwaysCooperate())
    # High noise to almost guarantee some flipped moves
    match = Match(player1, player2, turns=50, noise=0.3)
    
    match.play()
    
    # With noise=0.3 and 50 turns per player, it's extremely unlikely
    # that no moves will be flipped to defection
    # Check if there are any defections in either player's history
    has_noise_effect = (
        any(action == Action.DEFECT for action in player1.actions) or
        any(action == Action.DEFECT for action in player2.actions)
    )
    
    assert has_noise_effect, "Noise did not affect any moves, which is highly unlikely"


def test_compile_results():
    """Test the _compile_results method for correct result structure."""
    player1 = Player(AlwaysCooperate(), player_id="P1")
    player2 = Player(AlwaysDefect(), player_id="P2")
    match = Match(player1, player2, turns=5)
    
    # Manually set up history and scores to test result compilation
    match.history = [
        (Action.COOPERATE, Action.DEFECT),
        (Action.COOPERATE, Action.DEFECT),
        (Action.COOPERATE, Action.DEFECT),
        (Action.COOPERATE, Action.DEFECT),
        (Action.COOPERATE, Action.DEFECT)
    ]
    player1.score = 0.0  # S=0 * 5
    player2.score = 25.0  # T=5 * 5
    
    results = match._compile_results()
    
    # Check results structure
    assert results["player1"]["id"] == "P1"
    assert results["player1"]["name"] == "AlwaysCooperate"
    assert results["player1"]["score"] == 0.0
    assert results["player1"]["cooperation_rate"] == 1.0
    
    assert results["player2"]["id"] == "P2"
    assert results["player2"]["name"] == "AlwaysDefect"
    assert results["player2"]["score"] == 25.0
    assert results["player2"]["cooperation_rate"] == 0.0
    
    assert results["turns"] == 5
    assert results["total_score"] == 25.0
    assert results["outcome"] == "loss"
    assert results["noise"] == 0.0
    assert "payoffs" in results
