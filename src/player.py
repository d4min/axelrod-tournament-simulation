"""
Player class for the Axelrod tournament simulation.

A player wraps a strategy and keeps track of history and score.
"""

from .game import Action
from .strategy import Strategy

class Player:
    """
    A player in the Prisoner's Dilemma tournament.
    
    A player encapsulates a strategy and maintains a history of actions and scores.
    """
    def __init__(self, strategy, player_id):
        """
        Initialise a new player with the given strategy.

        Args:
            strategy: The strategy this player will use.
            player_id: Optional unique identifier for this player
        """
        self.strategy = strategy
        self.player_id = player_id if player_id else f"{strategy.name}-{id(self)}"
        self.actions = []
        self.score = 0.0

    def make_move(self, opponent_actions):
        """
        Determine the next move based on the players strategy.

        Args:
            opponent_actions: List of the opponent's previous actions
        
        Returns:
            The action to take in the current round
        """
        action = self.strategy.make_move(self.actions, opponent_actions)
        return action
    
    def record_action(self, action):
        """
        Record an action in this player's history.

        Args:
            action: The action taken by this player
        """
        self.actions.append(action)

    def record_score(self, points):
        """
        Add points to this player's total.

        Args:
            points: The number of points to add        
        """
        self.score += points

    def reset(self):
        """
        Reset the players history and points for a new match.
        """
        self.actions = []
        self.points = 0

    @property
    def name(self):
        """
        Return the name of the player's strategy.
        """
        return self.strategy.name
    
    def __str__(self):
        """
        Return a string representation of the player.
        """
        return f"Player({self.player_id}, {self.strategy.name})"

