from datetime import datetime
from typing import Optional, List

class Player:
    def __init__(self, pubg_id: str, name: str, shard_id: str = "steam"):
        self.pubg_id = pubg_id
        self.name = name
        self.shard_id = shard_id
        self.created_at = datetime.utcnow()
        self.updated_at = datetime.utcnow()
        self.patch_version = ""
        self.title_id = "pubg"
        self.matches: List[str] = []
    
    def to_dict(self) -> dict:
        """Convert to dictionary for MongoDB storage using camelCase to match existing database"""
        return {
            "pubgId": self.pubg_id,
            "name": self.name,
            "shardId": self.shard_id,
            "createdAt": self.created_at,
            "updatedAt": self.updated_at,
            "patchVersion": self.patch_version,
            "titleId": self.title_id,
            "matches": self.matches
        }
    
    @classmethod
    def from_dict(cls, data: dict) -> 'Player':
        """Create Player from MongoDB document, handling the actual camelCase structure"""
        # Get fields using the actual database field names (camelCase)
        pubg_id = data.get("pubgId") or data.get("pubg_id")  # Prioritize camelCase
        name = data.get("name")
        shard_id = data.get("shardId") or data.get("shard_id", "steam")
        
        if not pubg_id:
            raise ValueError("Player document must have pubgId field")
        if not name:
            raise ValueError("Player document must have name field")
        
        player = cls(
            pubg_id=pubg_id,
            name=name,
            shard_id=shard_id
        )
        
        # Handle patchVersion (prioritize camelCase)
        player.patch_version = data.get("patchVersion") or data.get("patch_version", "")
        
        # Handle titleId (prioritize camelCase)
        player.title_id = data.get("titleId") or data.get("title_id", "pubg")
        
        # Handle matches array
        player.matches = data.get("matches", [])
        
        # Parse datetime objects - MongoDB returns datetime objects, not strings
        created_at = data.get("createdAt") or data.get("created_at")
        if created_at:
            try:
                if isinstance(created_at, datetime):
                    # MongoDB datetime object - remove timezone info for consistency
                    player.created_at = created_at.replace(tzinfo=None)
                elif isinstance(created_at, str):
                    # String format - parse it
                    player.created_at = datetime.fromisoformat(created_at.replace("Z", "+00:00")).replace(tzinfo=None)
                else:
                    player.created_at = datetime.utcnow()
            except Exception as e:
                print(f"Warning: Could not parse createdAt date: {e}")
                player.created_at = datetime.utcnow()
        
        updated_at = data.get("updatedAt") or data.get("updated_at")
        if updated_at:
            try:
                if isinstance(updated_at, datetime):
                    # MongoDB datetime object - remove timezone info for consistency
                    player.updated_at = updated_at.replace(tzinfo=None)
                elif isinstance(updated_at, str):
                    # String format - parse it
                    player.updated_at = datetime.fromisoformat(updated_at.replace("Z", "+00:00")).replace(tzinfo=None)
                else:
                    player.updated_at = datetime.utcnow()
            except Exception as e:
                print(f"Warning: Could not parse updatedAt date: {e}")
                player.updated_at = datetime.utcnow()
            
        return player
    
    def update_from_api(self, api_data: dict) -> None:
        """Update player data from PUBG API response"""
        attributes = api_data.get("attributes", {})
        self.patch_version = attributes.get("patchVersion", "")
        self.title_id = attributes.get("titleId", "pubg")
        self.updated_at = datetime.utcnow()
        
        # Update created_at and updated_at from API if available
        if "createdAt" in attributes:
            try:
                self.created_at = datetime.fromisoformat(attributes["createdAt"].replace("Z", "+00:00")).replace(tzinfo=None)
            except:
                pass  # Keep existing value on parse error
                
        if "updatedAt" in attributes:
            try:
                self.updated_at = datetime.fromisoformat(attributes["updatedAt"].replace("Z", "+00:00")).replace(tzinfo=None)
            except:
                pass  # Keep existing value on parse error 