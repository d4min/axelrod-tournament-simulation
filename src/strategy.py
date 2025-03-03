"""
Implementation of various strategies for the iterated Prisoner's Dilemma.

This module contains both classic strategies from Axelrod's original tournaments
and additional strategies developed later in the literature.
"""

import random
from abc import ABC, abstractmethod

from .game import Action

class Strategy(ABC):
    """
    Abstract base class for all strategies in the Prisoner's Dilemma tournament.

    A strategy decides what action to take based on the history of the game. 
    """

    def __init__(self, name = None):
        """
        Initialise a new strategy.

        Args:
            name: Optional custom name for the strategy
        """
        self.name = name if name else self.__class__.__name__
    
    @abstractmethod
    def make_move(self, my_history, opponent_history):
        """
        Determine the next move based on game history.

        Args:
            my_history: List of this strategy's previous actions.
            opponent_history: List of opposing strategy's previous actions. 

        Returns:
            The action to take in the current round
        """
        pass

    def __str__(self) -> str:
        """Return the name of the strategy."""
        return self.name
    
class TitForTat(Strategy):
    """
    The famous Tit-for-Tat strategy: cooperate on the first move, then copy
    the opponent's previous move.
    
    This strategy won Axelrod's original tournaments and exemplifies the 
    properties of being nice, retaliatory, forgiving, and clear.
    """
    def make_move(self, my_history, opponent_history):
        """
        Cooperate on the first move, then copy the opponent's last move.
        """
        if not opponent_history:
            return Action.COOPERATE
        return opponent_history[-1]
    
class AlwaysCooperate(Strategy):
    """
    A strategy that always cooperates regardless of the opponent's actions.
    
    This is a "nice" strategy but can be exploited by defectors.
    """
    def make_move(self, my_history, opponent_history):
        """
        Always return the cooperation action.
        """
        return Action.COOPERATE
    
class AlwaysDefect(Strategy):
    """
    A strategy that always defects regardless of the opponent's actions.
    
    This strategy maximizes exploitation of cooperative opponents but performs
    poorly against retaliatory strategies in iterated games.
    """
    def make_move(self, my_history, opponent_history):
        """
        Always return the defect action.
        """
        return Action.DEFECT
    
class Grudger(Strategy):
    """
    Cooperates until the opponent defects, then defects forever.
    
    Also known as "Grim Trigger" in the literature.
    """
    def make_move(self, my_history, opponent_history):
        """
        Cooperate until the opponent defects, then defect forever.
        """
        if not opponent_history:
            return Action.COOPERATE

        if Action.DEFECT in opponent_history:
            return Action.DEFECT
        
        return Action.COOPERATE
    
class Random(Strategy):
    """
    A strategy that makes completely random decisions without any bias.
    
    Each move has exactly a 50% chance of being cooperation or defection,
    regardless of the game history.
    """
    def make_move(self, my_history, opponent_history):
        """
        Return a purely random action with equal probability.
        """
        return random.choice([Action.COOPERATE, Action.DEFECT])
            
