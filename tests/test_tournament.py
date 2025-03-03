"""
Tests for the Tournament class
"""

import pytest
from src.game import Game
from src.strategy import TitForTat, AlwaysCooperate, AlwaysDefect
from src.tournament import Tournament

def test_tournament_initialisation():
    """
    Test that a tournament can be initialised with default parameters.
    """
    tournament = Tournament()
    
    assert tournament.strategies == []
    assert isinstance(tournament.game, Game)
    assert tournament.turns == 200
    assert tournament.noise == 0.0
    assert tournament.self_plays is True
    assert tournament.results is None
    assert tournament.rankings is None

def test_tournament_custom_parameters():
    """
    Test that a tournament can be initialised with default parameters.
    """
    strategies = [TitForTat(), AlwaysCooperate()]
    game = Game(R=4.0, T=6.0, P=2.0, S=1.0)
    
    tournament = Tournament(
        strategies=strategies,
        game=game,
        turns=100,
        noise=0.1,
        self_plays=False
    )
    
    assert tournament.strategies == strategies
    assert tournament.game == game
    assert tournament.turns == 100
    assert tournament.noise == 0.1
    assert tournament.self_plays is False

def test_add_strategy():
    """
    Test that strategies can be added to the tournament.
    """
    tournament = Tournament()
    
    assert len(tournament.strategies) == 0
    
    tournament.add_strategy(TitForTat())
    assert len(tournament.strategies) == 1
    
    tournament.add_strategy(AlwaysCooperate())
    assert len(tournament.strategies) == 2

def test_run_tournament_empty():
    """
    Test that running the tournament with no strategies raises an error.
    """
    tournament = Tournament()
    
    with pytest.raises(ValueError):
        tournament.run()

def test_run_tournament_basic():
    """Test that a simple tournament runs and produces expected results."""
    # Use small number of turns for faster tests
    tournament = Tournament(
        strategies=[TitForTat(), AlwaysCooperate(), AlwaysDefect()],
        turns=10
    )
    
    results = tournament.run()
    
    # Check that we have the expected number of matches
    # With 3 strategies and self-plays, we should have 9 matches
    assert len(results["matches"]) == 9
    
    # Check that we have results for each player
    assert len(results["players"]) == 3
    
    # Check that rankings are available
    assert tournament.rankings is not None
    assert len(tournament.rankings) == 3
    
    # Check tournament configuration
    assert results["tournament_config"]["turns"] == 10
    assert results["tournament_config"]["noise"] == 0.0
    assert results["tournament_config"]["self_plays"] is True
    assert results["tournament_config"]["num_strategies"] == 3
    assert results["tournament_config"]["num_matches"] == 9


def test_run_tournament_without_self_plays():
    """Test tournament with self_plays=False."""
    tournament = Tournament(
        strategies=[TitForTat(), AlwaysCooperate(), AlwaysDefect()],
        turns=10,
        self_plays=False
    )
    
    results = tournament.run()
    
    # With 3 strategies and no self-plays, we should have 6 matches
    assert len(results["matches"]) == 6


def test_get_strategy_match_results():
    """Test getting all matches for a specific strategy."""
    tournament = Tournament(
        strategies=[TitForTat(), AlwaysCooperate(), AlwaysDefect()],
        turns=5
    )
    
    tournament.run()
    
    # Get TitForTat matches
    tft_matches = tournament.get_strategy_match_results("TitForTat")
    
    # TitForTat should be in 3 matches (vs itself, vs AlwaysCooperate, vs AlwaysDefect)
    assert len(tft_matches) == 3
    
    # Check all matches involve TitForTat
    for match in tft_matches:
        assert match["player1"]["name"] == "TitForTat" or match["player2"]["name"] == "TitForTat"


def test_get_strategy_ranking():
    """Test getting the ranking of a specific strategy."""
    tournament = Tournament(
        strategies=[TitForTat(), AlwaysCooperate(), AlwaysDefect()],
        turns=10
    )
    
    tournament.run()
    
    # Get rankings for each strategy
    tft_rank = tournament.get_strategy_ranking("TitForTat")
    ac_rank = tournament.get_strategy_ranking("AlwaysCooperate")
    ad_rank = tournament.get_strategy_ranking("AlwaysDefect")
    
    # Ensure we got valid rankings
    assert 1 <= tft_rank <= 3
    assert 1 <= ac_rank <= 3
    assert 1 <= ad_rank <= 3
    
    # Verify they're all different (no ties in this simple case)
    assert len({tft_rank, ac_rank, ad_rank}) == 3


def test_get_head_to_head_results():
    """Test getting head-to-head results between two strategies."""
    tournament = Tournament(
        strategies=[TitForTat(), AlwaysDefect()],
        turns=5
    )
    
    tournament.run()
    
    # Get head-to-head results
    results = tournament.get_head_to_head_results("TitForTat", "AlwaysDefect")
    
    # Should be 2 matches (TFT vs AD and AD vs TFT)
    assert len(results) == 2
    
    # Verify both matches involve the two strategies
    for match in results:
        assert (match["player1"]["name"] == "TitForTat" and match["player2"]["name"] == "AlwaysDefect") or \
               (match["player1"]["name"] == "AlwaysDefect" and match["player2"]["name"] == "TitForTat")


def test_invalid_operations_before_run():
    """Test that operations requiring results raise errors if called before run()."""
    tournament = Tournament(strategies=[TitForTat(), AlwaysDefect()])
    
    with pytest.raises(ValueError):
        tournament.get_strategy_match_results("TitForTat")
    
    with pytest.raises(ValueError):
        tournament.get_strategy_ranking("TitForTat")
    
    with pytest.raises(ValueError):
        tournament.get_head_to_head_results("TitForTat", "AlwaysDefect")

