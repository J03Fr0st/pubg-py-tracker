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
        self.title_id = "bluehole-pubg"
        self.matches: List[str] = []
    
    def to_dict(self) -> dict:
        """Convert to dictionary for MongoDB storage"""
        return {
            "pubg_id": self.pubg_id,
            "name": self.name,
            "shard_id": self.shard_id,
            "created_at": self.created_at.isoformat() + "Z",
            "updated_at": self.updated_at.isoformat() + "Z",
            "patch_version": self.patch_version,
            "title_id": self.title_id,
            "matches": self.matches
        }
    
    @classmethod
    def from_dict(cls, data: dict) -> 'Player':
        """Create Player from MongoDB document, handling both camelCase and snake_case"""
        # Handle both camelCase and snake_case field names for backward compatibility
        pubg_id = data.get("pubg_id") or data.get("pubgId")
        name = data.get("name")
        shard_id = data.get("shard_id") or data.get("shardId", "steam")
        
        if not pubg_id:
            raise ValueError("Player document must have pubg_id or pubgId field")
        if not name:
            raise ValueError("Player document must have name field")
        
        player = cls(
            pubg_id=pubg_id,
            name=name,
            shard_id=shard_id
        )
        
        # Handle patch_version / patchVersion
        player.patch_version = data.get("patch_version") or data.get("patchVersion", "")
        
        # Handle title_id / titleId
        player.title_id = data.get("title_id") or data.get("titleId", "bluehole-pubg")
        
        # Handle matches array
        player.matches = data.get("matches", [])
        
        # Parse datetime strings - handle both formats
        created_at_str = data.get("created_at") or data.get("createdAt")
        if created_at_str:
            try:
                if isinstance(created_at_str, str):
                    player.created_at = datetime.fromisoformat(created_at_str.replace("Z", "+00:00"))
                elif hasattr(created_at_str, 'replace'):
                    # Handle MongoDB datetime objects
                    player.created_at = created_at_str.replace(tzinfo=None)
            except Exception as e:
                print(f"Warning: Could not parse created_at date: {e}")
                player.created_at = datetime.utcnow()
        
        updated_at_str = data.get("updated_at") or data.get("updatedAt")
        if updated_at_str:
            try:
                if isinstance(updated_at_str, str):
                    player.updated_at = datetime.fromisoformat(updated_at_str.replace("Z", "+00:00"))
                elif hasattr(updated_at_str, 'replace'):
                    # Handle MongoDB datetime objects
                    player.updated_at = updated_at_str.replace(tzinfo=None)
            except Exception as e:
                print(f"Warning: Could not parse updated_at date: {e}")
                player.updated_at = datetime.utcnow()
            
        return player
    
    def update_from_api(self, api_data: dict) -> None:
        """Update player data from PUBG API response"""
        attributes = api_data.get("attributes", {})
        self.patch_version = attributes.get("patchVersion", "")
        self.title_id = attributes.get("titleId", "bluehole-pubg")
        self.updated_at = datetime.utcnow()
        
        # Update created_at and updated_at from API if available
        if "createdAt" in attributes:
            try:
                self.created_at = datetime.fromisoformat(attributes["createdAt"].replace("Z", "+00:00"))
            except:
                pass  # Keep existing value on parse error
                
        if "updatedAt" in attributes:
            try:
                self.updated_at = datetime.fromisoformat(attributes["updatedAt"].replace("Z", "+00:00"))
            except:
                pass  # Keep existing value on parse error 