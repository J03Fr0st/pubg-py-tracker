from datetime import datetime
from typing import List, Dict, Any, Optional

class Match:
    def __init__(self, match_id: str):
        self.match_id = match_id
        self.map_name = ""
        self.game_mode = ""
        self.created_at = datetime.utcnow()
        self.duration = 0
        self.custom_match = False
        self.shard_id = "steam"
        self.participants: List[Dict[str, Any]] = []
        self.rosters: List[Dict[str, Any]] = []
        self.telemetry_url = ""
        
    @classmethod
    def from_pubg_api(cls, pubg_match: Dict[str, Any], included_data: List[Dict[str, Any]]) -> 'Match':
        """Create Match from PUBG API response data"""
        match = cls(pubg_match['id'])
        match.map_name = pubg_match['map_name']
        match.game_mode = pubg_match['game_mode']
        match.duration = pubg_match['duration']
        match.custom_match = pubg_match['custom_match']
        match.shard_id = pubg_match['shard_id']
        
        # Parse created_at timestamp
        try:
            match.created_at = datetime.fromisoformat(pubg_match['created_at'].replace("Z", "+00:00"))
        except:
            match.created_at = datetime.utcnow()
        
        # Process included data to extract participants, rosters, and assets
        participants_by_id = {}
        rosters_by_id = {}
        
        for item in included_data:
            item_type = item.get("type", "")
            item_id = item.get("id", "")
            
            if item_type == "participant":
                # Create participant object manually without import
                participant_data = {
                    "id": item.get("id", ""),
                    "name": item.get("attributes", {}).get("stats", {}).get("name", ""),
                    "player_id": item.get("attributes", {}).get("stats", {}).get("playerId", ""),
                    "stats": item.get("attributes", {}).get("stats", {})
                }
                participants_by_id[item_id] = participant_data
                
            elif item_type == "roster":
                # Create roster object manually without import
                roster_data = {
                    "id": item.get("id", ""),
                    "rank": item.get("attributes", {}).get("stats", {}).get("rank", 0),
                    "team_id": item.get("attributes", {}).get("stats", {}).get("teamId", 0),
                    "participant_ids": [p.get("id", "") for p in item.get("relationships", {}).get("participants", {}).get("data", [])]
                }
                rosters_by_id[item_id] = roster_data
                
            elif item_type == "asset":
                # Check if this is telemetry asset
                attributes = item.get("attributes", {})
                if attributes.get("name", "") == "telemetry":
                    match.telemetry_url = attributes.get("URL", "")
        
        # Build rosters with their participants
        for roster_id in pubg_match['roster_ids']:
            if roster_id in rosters_by_id:
                roster = rosters_by_id[roster_id]
                roster_data = {
                    "id": roster["id"],
                    "rank": roster["rank"],
                    "team_id": roster["team_id"],
                    "participants": []
                }
                
                # Add participants to this roster
                for participant_id in roster["participant_ids"]:
                    if participant_id in participants_by_id:
                        participant = participants_by_id[participant_id]
                        participant_data = {
                            "id": participant["id"],
                            "name": participant["name"],
                            "player_id": participant["player_id"],
                            "stats": {
                                "assists": participant["stats"].get("assists", 0),
                                "boosts": participant["stats"].get("boosts", 0),
                                "damage_dealt": participant["stats"].get("damageDealt", 0),
                                "dbnos": participant["stats"].get("DBNOs", 0),
                                "headshot_kills": participant["stats"].get("headshotKills", 0),
                                "heals": participant["stats"].get("heals", 0),
                                "kill_place": participant["stats"].get("killPlace", 0),
                                "kills": participant["stats"].get("kills", 0),
                                "longest_kill": participant["stats"].get("longestKill", 0),
                                "revives": participant["stats"].get("revives", 0),
                                "ride_distance": participant["stats"].get("rideDistance", 0),
                                "swim_distance": participant["stats"].get("swimDistance", 0),
                                "time_survived": participant["stats"].get("timeSurvived", 0),
                                "walk_distance": participant["stats"].get("walkDistance", 0),
                                "win_place": participant["stats"].get("winPlace", 0)
                            }
                        }
                        roster_data["participants"].append(participant_data)
                        match.participants.append(participant_data)
                
                match.rosters.append(roster_data)
        
        return match
    
    def to_dict(self) -> Dict[str, Any]:
        # Format timestamp properly
        if self.created_at.tzinfo is not None:
            # Already has timezone info, use as is
            created_at_str = self.created_at.isoformat()
        else:
            # No timezone info, add Z for UTC
            created_at_str = self.created_at.isoformat() + "Z"
        
        return {
            "match_id": self.match_id,
            "map_name": self.map_name,
            "game_mode": self.game_mode,
            "created_at": created_at_str,
            "duration": self.duration,
            "custom_match": self.custom_match,
            "shard_id": self.shard_id,
            "participants": self.participants,
            "rosters": self.rosters,
            "telemetry_url": self.telemetry_url
        }
    
    def get_monitored_players_roster(self, monitored_player_ids: List[str]) -> Optional[Dict[str, Any]]:
        """Find the roster containing any of the monitored players"""
        for roster in self.rosters:
            for participant in roster["participants"]:
                if participant["player_id"] in monitored_player_ids:
                    return roster
        return None
    
    def get_squad_members(self, monitored_player_ids: List[str]) -> List[Dict[str, Any]]:
        """Get all squad members from the roster containing monitored players"""
        roster = self.get_monitored_players_roster(monitored_player_ids)
        if roster:
            return roster["participants"]
        return [] 