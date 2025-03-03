"""
Tournament class for the Axelrod tournament simulation.

A tournament manages matches between multiple strategies and aggregates results.
"""

import itertools
import time

from src.game import Game
from src.player import Player
from src.strategy import Strategy
from src.match import Match

class Tournament:
    """
    A tournament in the Prisoner's Dilemma simulation.

    A tournament runs matches between all pairs of strategies and compiles
    the results to determine overall performance.
    """

    def __init__(
            self,
            strategies=None,
            game=None,
            turns=200,
            noise=0.0,
            self_plays=True,
    ):
        """
        Initialise a new tournament.

        Args:
            strategies: List of strategies to include in the tournament
            game: The game to be played (uses default Game if None)
            turns: Number of iterations per match
            noise: Probability of a random action occurring
            self_plays: Whether to include matches where a strategy plays against itself
        """
        self.strategies = strategies if strategies else []
        self.game = game if game else Game()
        self.turns = turns
        self.noise = noise
        self.self_plays = self_plays
        
        # Will store results after the tournament is run
        self.results = None
        self.rankings = None

    def add_strategy(self, strategy):
        """
        Add a strategy to the tournament.

        Args:
            strategy: The strategy to add 
        """
        self.strategies.append(strategy)

    def run(self):
        """
        Run the tournament by playing matches between all pairs of strategies. 

        Returns:
            Dictionary containing the tournament results
        """
        if not self.strategies:
            raise ValueError("No strategies in tournament")
            
        start_time = time.time()
        
        # Create players for each strategy
        players = [Player(strategy) for strategy in self.strategies]
        
        # Track all match results
        match_results = []
        
        # Track accumulated scores and cooperation rates
        total_scores = {player.player_id: 0.0 for player in players}
        cooperation_rates = {player.player_id: [] for player in players}
        win_counts = {player.player_id: 0 for player in players}
        
        # Generate all pairs of players to compete
        player_pairs = list(itertools.product(players, players))
        if not self.self_plays:
            player_pairs = [(p1, p2) for p1, p2 in player_pairs if p1.player_id != p2.player_id]
        
        # Run matches for all pairs
        for player1, player2 in player_pairs:
            match = Match(
                player1=player1,
                player2=player2,
                game=self.game,
                turns=self.turns,
                noise=self.noise
            )
            
            result = match.play()
            match_results.append(result)
            
            # Update scores
            total_scores[player1.player_id] += result["player1"]["score"]
            total_scores[player2.player_id] += result["player2"]["score"]
            
            # Update cooperation rates
            cooperation_rates[player1.player_id].append(result["player1"]["cooperation_rate"])
            cooperation_rates[player2.player_id].append(result["player2"]["cooperation_rate"])
            
            # Update win counts
            if result["outcome"] == "win":
                win_counts[player1.player_id] += 1
            elif result["outcome"] == "loss":
                win_counts[player2.player_id] += 1
        
        # Calculate average scores and cooperation rates
        num_matches = len(player_pairs) / len(players) if self.self_plays else len(player_pairs) / (len(players) - 1)
        
        avg_scores = {player_id: score / num_matches for player_id, score in total_scores.items()}
        avg_cooperation = {
            player_id: sum(rates) / len(rates) if rates else 0.0
            for player_id, rates in cooperation_rates.items()
        }
        
        # Create player summary data
        player_data = []
        for player in players:
            player_data.append({
                "id": player.player_id,
                "name": player.name,
                "avg_score": avg_scores[player.player_id],
                "total_score": total_scores[player.player_id],
                "avg_cooperation_rate": avg_cooperation[player.player_id],
                "wins": win_counts[player.player_id]
            })
            
        # Sort player data by average score (descending) to get rankings
        player_data.sort(key=lambda x: x["avg_score"], reverse=True)
        
        # Calculate total tournament duration
        duration = time.time() - start_time
        
        # Compile full tournament results
        self.results = {
            "players": player_data,
            "matches": match_results,
            "tournament_config": {
                "turns": self.turns,
                "noise": self.noise,
                "self_plays": self.self_plays,
                "num_strategies": len(self.strategies),
                "num_matches": len(match_results),
                "payoffs": self.game.get_payoffs(),
            },
            "duration": duration
        }
        
        # Store rankings separately for convenience
        self.rankings = player_data
        
        return self.results
    
    def get_strategy_match_results(self, strategy_name):
        """
        Get all match results involving the specified strategy.

        Args:
            strategy_name: Name of the strategy to filter by

        Return:
            List of match results involving the the specified strategy
        """
        if not self.results:
            raise ValueError("Tournament has not been run yet")
            
        return [
            match for match in self.results["matches"]
            if match["player1"]["name"] == strategy_name or match["player2"]["name"] == strategy_name
        ]
    
    def get_strategy_ranking(self, strategy_name):
        """
        Get the ranking of a specified strategy.

        Args:
            strategy_name: Name of the strategy to filter by

        Returns:
            Rank of the specified strategy (1-Indexed)
        """
        if not self.rankings:
            raise ValueError("Tournament has not been run yet")
            
        for i, player in enumerate(self.rankings):
            if player["name"] == strategy_name:
                return i + 1
            
        raise ValueError(f"Strategy '{strategy_name}' not found in tournament")
    
    def get_head_to_head_results(self, strategy1_name, strategy2_name):
        """
        Get results of direct matches between two strategies.

        Args:
            strategy1_name: Name of the first strategy.
            strategy2_name: Name of the second strategy.

        Returns:
            Dictionary containing head-to-head match results 
        """
        if not self.results:
            raise ValueError("Tournament has not been run yet")
            
        # Find matches between these strategies
        matches = []
        for match in self.results["matches"]:
            p1_name = match["player1"]["name"]
            p2_name = match["player2"]["name"]
            
            if ((p1_name == strategy1_name and p2_name == strategy2_name) or
                (p1_name == strategy2_name and p2_name == strategy1_name)):
                matches.append(match)
                
        if not matches:
            raise ValueError(f"No matches found between '{strategy1_name}' and '{strategy2_name}'")
            
        return matches