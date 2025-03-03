"""
Implementation of the Prisoner's Dilemma game as used in Axelrod's tournaments.

The Prisoner's Dilemma is a fundamental game in game theory where two players
must choose to either cooperate or defect. The payoffs are structured such that:
- If both cooperate, both receive a moderate reward (R)
- If both defect, both receive a punishment (P)
- If one cooperates and one defects, the defector gets a temptation payoff (T)
  and the cooperator gets a sucker payoff (S)

The payoffs must satisfy: T > R > P > S and 2R > T + S
"""

from enum import Enum 

class Action(Enum):
    """
    Possible actions in the Prisoner's Dilemma game.
    """
    COOPERATE = 'C'
    DEFECT = 'D'

class Game:
    """
    Represents the Prisoner's Dilemma game with configurable payoffs.

    Attributes:
        R (float): Reward payoff (both cooperate)
        T (float): Temptation payoff (defect while opponent cooperates)
        P (float): Punishment payoff (both defect)
        S (float): Sucker payoff (cooperate while opponent defects)
    """

    def __init__(
            self,
            R = 3.0,
            T = 5.0,
            P = 1.0,
            S = 0.0,
    ):
        """
        Initialise a new Prisoner's Dilemma game with the given payoffs.

        Args:
            R: Reward payoff (both cooperate)
            T: Temptation payoff (defect while opponent cooperates)
            P: Punishment payoff (both defect)
            S: Sucker payoff (cooperate while opponent defects)
        """
        # Validate that payoffs satisfy Prisoner's Dilemma conditions
        if not (T > R > P > S):
            raise ValueError("Payoffs must satisfy T > R > P > S")
        if not (2 * R > T + S):
            raise ValueError("Payoffs must satisfy 2R > T + S")
            
        self.R = R
        self.T = T
        self.P = P
        self.S = S

        # Precompute the payoff matrix for performance
        self._payoff_matrix = {
            (Action.COOPERATE, Action.COOPERATE): (R, R),
            (Action.COOPERATE, Action.DEFECT): (S, T),
            (Action.DEFECT, Action.COOPERATE): (T, S),
            (Action.DEFECT, Action.DEFECT): (P, P)
        }

    def score(self, action1, action2):
        """
        Calculate the scores for a single round of the game. 

        Args:
            action1: The action taken by the first player
            action2: The action taken by the second player

        Returns:
            A tuple containing the scores for player 1 and player 2
        """
        return self._payoff_matrix[(action1, action2)]
    
    def get_payoffs(self):
        """
        Return the current payoff values as a dictionary.
        """
        return {
            'R': self.R,
            'T': self.T,
            'P': self.P,
            'S': self.S
        }