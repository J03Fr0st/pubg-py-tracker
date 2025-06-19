from datetime import datetime
from typing import Optional

class Player:
    def __init__(self, pubg_id: str, name: str, shard_id: str = "steam"):
        self.pubg_id = pubg_id
        self.name = name
        self.shard_id = shard_id
        self.created_at = datetime.utcnow()
        self.updated_at = datetime.utcnow()
        self.patch_version = ""
        self.title_id = "bluehole-pubg"
    
    def to_dict(self) -> dict:
        return {
            "pubg_id": self.pubg_id,
            "name": self.name,
            "shard_id": self.shard_id,
            "created_at": self.created_at.isoformat() + "Z",
            "updated_at": self.updated_at.isoformat() + "Z",
            "patch_version": self.patch_version,
            "title_id": self.title_id
        }
    
    @classmethod
    def from_dict(cls, data: dict) -> 'Player':
        player = cls(
            pubg_id=data["pubg_id"],
            name=data["name"],
            shard_id=data.get("shard_id", "steam")
        )
        player.patch_version = data.get("patch_version", "")
        player.title_id = data.get("title_id", "bluehole-pubg")
        
        # Parse datetime strings
        if "created_at" in data:
            player.created_at = datetime.fromisoformat(data["created_at"].replace("Z", "+00:00"))
        if "updated_at" in data:
            player.updated_at = datetime.fromisoformat(data["updated_at"].replace("Z", "+00:00"))
            
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