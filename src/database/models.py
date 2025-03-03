"""
Database models for the Axelrod tournament simulation.

This module defines the SQLAlchemy ORM models for storing tournament results.
"""

from datetime import datetime
import json
from sqlalchemy import Column, Integer, String, Float, Boolean, DateTime, ForeignKey, Text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship

Base = declarative_base()

class Tournament(Base):
    """
    Model representing a tournament.
    """
    __tablename__ = "tournaments"
    
    id = Column(Integer, primary_key=True)
    timestamp = Column(DateTime, default=datetime.utcnow)
    turns = Column(Integer, nullable=False)
    noise = Column(Float, nullable=False)
    self_plays = Column(Boolean, nullable=False)
    num_strategies = Column(Integer, nullable=False)
    num_matches = Column(Integer, nullable=False)
    duration = Column(Float)  # Execution time in seconds
    payoff_r = Column(Float, nullable=False)  # Reward payoff
    payoff_t = Column(Float, nullable=False)  # Temptation payoff
    payoff_p = Column(Float, nullable=False)  # Punishment payoff
    payoff_s = Column(Float, nullable=False)  # Sucker payoff
    
    # Relationships
    players = relationship("Player", back_populates="tournament", cascade="all, delete-orphan")
    matches = relationship("Match", back_populates="tournament", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"Tournament(id={self.id}, timestamp={self.timestamp}, strategies={self.num_strategies})"
    
class Player(Base):
    """
    Model representing a player in a tournament.
    """
    __tablename__ = "players"

    id = Column(Integer, primary_key=True)
    tournament_id = Column(Integer, ForeignKey("tournaments.id"))
    strategy_name = Column(String(100), nullable=False)
    avg_score = Column(Float, nullable=False)
    total_score = Column(Float, nullable=False)
    avg_cooperation_rate = Column(Float, nullable=False)
    wins = Column(Integer, nullable=False)
    rank = Column(Integer, nullable=False)
    
    # Relationships
    tournament = relationship("Tournament", back_populates="players")
    player1_matches = relationship("Match", foreign_keys="Match.player1_id", back_populates="player1")
    player2_matches = relationship("Match", foreign_keys="Match.player2_id", back_populates="player2")
    
    def __repr__(self):
        return f"Player(id={self.id}, strategy={self.strategy_name}, rank={self.rank})"
    
class Match(Base):
    """
    Model representing a match between two players.
    """
    __tablename__ = "matches"

    id = Column(Integer, primary_key=True)
    tournament_id = Column(Integer, ForeignKey("tournaments.id"))
    player1_id = Column(Integer, ForeignKey("players.id"))
    player2_id = Column(Integer, ForeignKey("players.id"))
    player1_score = Column(Float, nullable=False)
    player2_score = Column(Float, nullable=False)
    player1_cooperation_rate = Column(Float, nullable=False)
    player2_cooperation_rate = Column(Float, nullable=False)
    outcome = Column(String(10), nullable=False)  # "win", "loss", or "tie"
    turns = Column(Integer, nullable=False)
    history = Column(Text)  # JSON string of match history
    
    # Relationships
    tournament = relationship("Tournament", back_populates="matches")
    player1 = relationship("Player", foreign_keys=[player1_id], back_populates="player1_matches")
    player2 = relationship("Player", foreign_keys=[player2_id], back_populates="player2_matches")
    
    def __repr__(self):
        return f"Match(id={self.id}, p1={self.player1_id}, p2={self.player2_id})"
    
    def get_history(self):
        """Deserialize the history from JSON."""
        if self.history:
            return json.loads(self.history)
        return []
    
    def set_history(self, history_data):
        """Serialize the history to JSON."""
        self.history = json.dumps(history_data)