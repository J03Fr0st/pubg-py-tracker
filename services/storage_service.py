import asyncio
from typing import List, Optional, Dict, Any
from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase, AsyncIOMotorCollection
from config.settings import settings
from models.player import PlayerModel
from models.processed_match import ProcessedMatchModel
from datetime import datetime
from bson import ObjectId

class StorageService:
    def __init__(self):
        self.client: Optional[AsyncIOMotorClient] = None
        self.db: Optional[AsyncIOMotorDatabase] = None
        self.players_collection: Optional[AsyncIOMotorCollection] = None
        self.processed_matches_collection: Optional[AsyncIOMotorCollection] = None
        
    async def initialize(self):
        """Initialize MongoDB connection and collections"""
        try:
            self.client = AsyncIOMotorClient(settings.MONGODB_URI)
            # Test connection
            await self.client.admin.command('ping')
            print("Successfully connected to MongoDB")
            
            # Get database
            self.db = self.client.get_default_database()
            
            # Get collections (using actual collection names from database)
            self.players_collection = self.db.players
            self.processed_matches_collection = self.db.processedmatches  # Use actual collection name (lowercase)
            
            # Create indexes for performance
            await self._create_indexes()
            
        except Exception as e:
            print(f"Failed to connect to MongoDB: {e}")
            raise
    
    async def _create_indexes(self):
        """Create database indexes for better performance"""
        try:
            # Index on player names for faster lookups
            await self.players_collection.create_index("name", unique=True)
            
            # Index on pubgId for faster lookups (using actual database field name)
            try:
                await self.players_collection.create_index("pubgId", unique=True, sparse=True)
            except Exception:
                # Index might already exist or fail, continue
                pass
            
            # Legacy index for backward compatibility (if any snake_case data exists)
            try:
                await self.players_collection.create_index("pubg_id", unique=True, sparse=True)
            except Exception:
                # Index might already exist or fail, continue
                pass
            
            # Index on match IDs for faster duplicate checking (using snake_case only)
            try:
                await self.processed_matches_collection.create_index("match_id", unique=True, sparse=True)
            except Exception:
                # Index might already exist or fail, continue
                pass
            
            print("Database indexes created successfully")
        except Exception as e:
            print(f"Warning: Failed to create indexes: {e}")
    
    async def close(self):
        """Close MongoDB connection"""
        if self.client:
            self.client.close()
    
    # Player operations
    async def add_player(self, player: PlayerModel) -> bool:
        """Add a new player to monitoring"""
        try:
            # Use upsert to avoid duplicates, query by actual database field names
            await self.players_collection.update_one(
                {
                    "$or": [
                        {"name": player.name},
                        {"pubgId": player.pubgId},  # Use actual database field name
                        {"pubg_id": player.pubgId}  # Fallback for legacy data
                    ]
                },
                {"$set": player.dict(by_alias=True, exclude={"id"})},
                upsert=True
            )
            print(f"Added player {player.name} to monitoring")
            return True
        except Exception as e:
            print(f"Failed to add player {player.name}: {e}")
            return False
    
    async def remove_player(self, player_name: str) -> bool:
        """Remove a player from monitoring"""
        try:
            result = await self.players_collection.delete_one({"name": player_name})
            if result.deleted_count > 0:
                print(f"Removed player {player_name} from monitoring")
                return True
            else:
                print(f"Player {player_name} not found")
                return False
        except Exception as e:
            print(f"Failed to remove player {player_name}: {e}")
            return False
    
    async def get_player_by_name(self, player_name: str) -> Optional[PlayerModel]:
        """Get a player by name"""
        try:
            doc = await self.players_collection.find_one({"name": player_name})
            if doc:
                return PlayerModel(**doc)
            return None
        except Exception as e:
            print(f"Failed to get player {player_name}: {e}")
            return None
    
    async def get_all_players(self) -> List[PlayerModel]:
        """Get all monitored players"""
        try:
            players = []
            async for doc in self.players_collection.find():
                players.append(PlayerModel(**doc))
            return players
        except Exception as e:
            print(f"Failed to get all players: {e}")
            return []
    
    async def update_player(self, player: PlayerModel) -> bool:
        """Update player information"""
        try:
            # Query using actual database field names (prioritize camelCase)
            result = await self.players_collection.replace_one(
                {
                    "$or": [
                        {"pubgId": player.pubgId},  # Use actual database field name
                        {"pubg_id": player.pubgId}  # Fallback for legacy data
                    ]
                },
                player.dict(by_alias=True, exclude={"id"})
            )
            return result.modified_count > 0
        except Exception as e:
            print(f"Failed to update player {player.name}: {e}")
            return False
    
    # Processed match operations
    async def is_match_processed(self, match_id: str) -> bool:
        """Check if a match has already been processed"""
        try:
            # Query using camelCase format
            doc = await self.processed_matches_collection.find_one({"matchId": match_id})
            return doc is not None
        except Exception as e:
            print(f"Failed to check if match {match_id} is processed: {e}")
            return False
    
    async def mark_match_processed(self, match_id: str) -> bool:
        """Mark a match as processed"""
        try:
            if not match_id or match_id.strip() == "":
                print(f"Invalid match_id provided: {match_id}")
                return False
                
            processed_match = ProcessedMatchModel(matchId=match_id)
            # Use upsert with camelCase format
            await self.processed_matches_collection.update_one(
                {"matchId": match_id},
                {"$set": processed_match.dict(by_alias=True, exclude={"id"})},
                upsert=True
            )
            return True
        except Exception as e:
            print(f"Failed to mark match {match_id} as processed: {e}")
            return False
    
    async def get_processed_matches(self, limit: int = 100) -> List[ProcessedMatchModel]:
        """Get recently processed matches"""
        try:
            processed_matches = []
            async for doc in self.processed_matches_collection.find().sort("processedAt", -1).limit(limit):
                processed_matches.append(ProcessedMatchModel(**doc))
            return processed_matches
        except Exception as e:
            print(f"Failed to get processed matches: {e}")
            return []

# Global storage service instance
storage_service = StorageService() 