"""
Database manager for the Axelrod tournament simulation.

This module handles database connections and operations.
"""

import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, scoped_session
from sqlalchemy.ext.declarative import declarative_base

from src.database.models import Base, Tournament, Player, Match

class DatabaseManager:
    """
    Manages database connections and operations for storing tournament results.
    """

    def __init__(self, db_url=None):
        """
        Initialise a new Database Manager.

        Args:
            db_url: Database connection URL. If None, uses SQLite in-memory database.
        """
        # Default to SQLite in-memory database if no URL provided
        self.db_url = db_url or 'sqlite:///axelrod_tournament.db'
        
        # Create engine and session factory
        self.engine = create_engine(self.db_url)
        self.session_factory = sessionmaker(bind=self.engine)
        self.Session = scoped_session(self.session_factory)

    def init_db(self):
        """
        Initialise the database schema.
        """
        Base.metadata.create_all(self.engine)

    def drop_db(self):
        """
        Drop all database tables.

        WARNING: This will delete all data.
        """
        Base.metadata.drop_all(self.engine)

    def get_session(self):
        """
        Get a new database session.
        
        Returns:
            A SQLAlchemy session object
        """
        return self.Session()
        
    def close_sessions(self):
        """Close all sessions."""
        self.Session.remove()
        
    def save_tournament(self, tournament_results):
        """
        Save tournament results to the database.
        
        Args:
            tournament_results: Dictionary containing tournament results
            
        Returns:
            The database ID of the created tournament
        """
        session = self.get_session()
        
        try:
            # Create Tournament record
            config = tournament_results["tournament_config"]
            payoffs = config["payoffs"]
            
            db_tournament = Tournament(
                turns=config["turns"],
                noise=config["noise"],
                self_plays=config["self_plays"],
                num_strategies=config["num_strategies"],
                num_matches=config["num_matches"],
                duration=tournament_results["duration"],
                payoff_r=payoffs["R"],
                payoff_t=payoffs["T"],
                payoff_p=payoffs["P"],
                payoff_s=payoffs["S"]
            )
            
            session.add(db_tournament)
            session.flush()  # Flush to get tournament ID
            
            # Create Player records
            players_map = {}  # Map player name to DB player object
            
            for i, player_data in enumerate(tournament_results["players"]):
                db_player = Player(
                    tournament_id=db_tournament.id,
                    strategy_name=player_data["name"],
                    avg_score=player_data["avg_score"],
                    total_score=player_data["total_score"],
                    avg_cooperation_rate=player_data["avg_cooperation_rate"],
                    wins=player_data["wins"],
                    rank=i + 1  # Rank is 1-indexed
                )
                
                session.add(db_player)
                session.flush()  # Flush to get player ID
                
                players_map[player_data["id"]] = db_player
            
            # Create Match records
            for match_data in tournament_results["matches"]:
                player1_id = match_data["player1"]["id"]
                player2_id = match_data["player2"]["id"]
                
                db_match = Match(
                    tournament_id=db_tournament.id,
                    player1_id=players_map[player1_id].id,
                    player2_id=players_map[player2_id].id,
                    player1_score=match_data["player1"]["score"],
                    player2_score=match_data["player2"]["score"],
                    player1_cooperation_rate=match_data["player1"]["cooperation_rate"],
                    player2_cooperation_rate=match_data["player2"]["cooperation_rate"],
                    outcome=match_data["outcome"],
                    turns=match_data["turns"]
                )
                
                # Optional: Save match history if available
                if "history" in match_data:
                    db_match.set_history(match_data["history"])
                
                session.add(db_match)
            
            # Commit all changes
            session.commit()
            return db_tournament.id
            
        except Exception as e:
            session.rollback()
            raise e
            
        finally:
            session.close()
            
    def get_tournament(self, tournament_id):
        """
        Retrieve a tournament by ID.
        
        Args:
            tournament_id: ID of the tournament to retrieve
            
        Returns:
            Dictionary containing tournament data
        """
        session = self.get_session()
        
        try:
            tournament = session.query(Tournament).filter_by(id=tournament_id).first()
            
            if not tournament:
                raise ValueError(f"Tournament with ID {tournament_id} not found")
                
            # Build tournament data dictionary
            result = {
                "id": tournament.id,
                "timestamp": tournament.timestamp.isoformat(),
                "config": {
                    "turns": tournament.turns,
                    "noise": tournament.noise,
                    "self_plays": tournament.self_plays,
                    "num_strategies": tournament.num_strategies,
                    "num_matches": tournament.num_matches,
                    "payoffs": {
                        "R": tournament.payoff_r,
                        "T": tournament.payoff_t,
                        "P": tournament.payoff_p,
                        "S": tournament.payoff_s
                    }
                },
                "duration": tournament.duration,
                "players": [],
                "matches": []
            }
            
            # Get players
            players = session.query(Player).filter_by(tournament_id=tournament_id).all()
            for player in players:
                result["players"].append({
                    "id": player.id,
                    "strategy_name": player.strategy_name,
                    "avg_score": player.avg_score,
                    "total_score": player.total_score,
                    "avg_cooperation_rate": player.avg_cooperation_rate,
                    "wins": player.wins,
                    "rank": player.rank
                })
                
            # Get matches
            matches = session.query(Match).filter_by(tournament_id=tournament_id).all()
            for match in matches:
                match_data = {
                    "id": match.id,
                    "player1_id": match.player1_id,
                    "player2_id": match.player2_id,
                    "player1_score": match.player1_score,
                    "player2_score": match.player2_score,
                    "player1_cooperation_rate": match.player1_cooperation_rate,
                    "player2_cooperation_rate": match.player2_cooperation_rate,
                    "outcome": match.outcome,
                    "turns": match.turns
                }
                
                # Include history if available
                if match.history:
                    match_data["history"] = match.get_history()
                    
                result["matches"].append(match_data)
                
            return result
            
        finally:
            session.close()
            
    def get_all_tournaments(self):
        """
        Retrieve basic info for all tournaments.
        
        Returns:
            List of dictionaries containing basic tournament info
        """
        session = self.get_session()
        
        try:
            tournaments = session.query(Tournament).order_by(Tournament.timestamp.desc()).all()
            
            result = []
            for tournament in tournaments:
                result.append({
                    "id": tournament.id,
                    "timestamp": tournament.timestamp.isoformat(),
                    "num_strategies": tournament.num_strategies,
                    "num_matches": tournament.num_matches,
                    "turns": tournament.turns,
                    "noise": tournament.noise
                })
                
            return result
            
        finally:
            session.close()
            
    def delete_tournament(self, tournament_id):
        """
        Delete a tournament and all related data.
        
        Args:
            tournament_id: ID of the tournament to delete
            
        Returns:
            True if successful, False if tournament not found
        """
        session = self.get_session()
        
        try:
            tournament = session.query(Tournament).filter_by(id=tournament_id).first()
            
            if not tournament:
                return False
                
            session.delete(tournament)
            session.commit()
            return True
            
        except Exception as e:
            session.rollback()
            raise e
            
        finally:
            session.close()