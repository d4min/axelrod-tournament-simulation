"""
Match class for the Axelrod tournament simulation.

A match consists of a series of iterated Prisoner's Dilemma games between two players.
"""
import random

from src.game import Game, Action
from src.player import Player

class Match:
    """
    A match between two players in the Prisoner's Dilemma tournament.
    
    A match consists of multiple iterations of the game and tracks the results.
    """

    def __init__(
            self,
            player1,
            player2,
            game=None,
            turns=200,
            noise=0.0,
    ):
        """
        Initialise a new match between two players.

        Args:
            player1: The first player
            player2: The second player
            game: The game to be played (uses default Game if None)
            turns: Number of iterations to play
            noise: Probability of a random action occurring instead of the intended action
        """
        self.player1 = player1
        self.player2 = player2
        self.game = game if game else Game()
        self.turns = turns

        if not 0 <= noise < 1:
            raise ValueError("Noise must be between 0 and 1")
        self.noise = noise
        
        # Track the full history of the match
        self.history = []
        
        # Reset players for a fresh match
        self.player1.reset()
        self.player2.reset()
    
    def play(self):
        """
        Play a match between the two players.

        Returns:
            Dictionary containing the match results
        """
        for _ in range(self.turns):
            # Get moves from both players
            move1 = self.player1.make_move(self.player2.actions)
            move2 = self.player2.make_move(self.player1.actions)
            
            # Apply noise if specified
            if self.noise > 0:
                move1 = self._apply_noise(move1)
                move2 = self._apply_noise(move2)
            
            # Record the moves in each player's history
            self.player1.record_action(move1)
            self.player2.record_action(move2)
            
            # Record the moves in the match history
            self.history.append((move1, move2))
            
            # Score the round and update player scores
            score1, score2 = self.game.score(move1, move2)
            self.player1.record_score(score1)
            self.player2.record_score(score2)
        
        # Return the match results
        return self._compile_results()
    
    def _apply_noise(self, intended_action):
        """
        Apply noise to an action with a specified probability.

        Args:
            intended_action: The action the player intended to take

        Returns:
            Either the intended action or a random action
        """
        if random.random() < self.noise:
            # Flip the action
            return Action.DEFECT if intended_action == Action.COOPERATE else Action.COOPERATE
        return intended_action
    
    def _compile_results(self):
        """
        Compile the results of the match.

        Returns:
            Dictionary containing the results of the match
        """
        # Count cooperation rates
        p1_cooperations = sum(1 for action, _ in self.history if action == Action.COOPERATE)
        p2_cooperations = sum(1 for _, action in self.history if action == Action.COOPERATE)
        
        p1_cooperation_rate = p1_cooperations / len(self.history) if self.history else 0
        p2_cooperation_rate = p2_cooperations / len(self.history) if self.history else 0
        
        # Determine the match outcome
        if self.player1.score > self.player2.score:
            outcome = "win"  # Player 1 wins
        elif self.player1.score < self.player2.score:
            outcome = "loss"  # Player 1 loses
        else:
            outcome = "tie"  # Tie
        
        return {
            "player1": {
                "id": self.player1.player_id,
                "name": self.player1.name,
                "score": self.player1.score,
                "cooperation_rate": p1_cooperation_rate,
            },
            "player2": {
                "id": self.player2.player_id,
                "name": self.player2.name,
                "score": self.player2.score,
                "cooperation_rate": p2_cooperation_rate,
            },
            "turns": self.turns,
            "total_score": self.player1.score + self.player2.score,
            "outcome": outcome,
            "noise": self.noise,
            "payoffs": self.game.get_payoffs(),
        }