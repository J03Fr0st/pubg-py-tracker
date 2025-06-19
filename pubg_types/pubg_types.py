from typing import Dict, List, Optional, Any
from datetime import datetime

class PubgApiResponse:
    def __init__(self, data: Dict[str, Any]):
        self.data = data.get('data', [])
        self.included = data.get('included', [])
        self.links = data.get('links', {})
        self.meta = data.get('meta', {})

class PubgPlayer:
    def __init__(self, data: Dict[str, Any]):
        self.id = data.get('id', '')
        self.type = data.get('type', '')
        attributes = data.get('attributes', {})
        self.name = attributes.get('name', '')
        self.shard_id = attributes.get('shardId', '')
        self.patch_version = attributes.get('patchVersion', '')
        self.title_id = attributes.get('titleId', '')
        self.created_at = attributes.get('createdAt', '')
        self.updated_at = attributes.get('updatedAt', '')
        
        # Parse match relationships
        relationships = data.get('relationships', {})
        matches = relationships.get('matches', {})
        match_data = matches.get('data', [])
        self.match_ids = [match.get('id', '') for match in match_data]

class PubgMatch:
    def __init__(self, data: Dict[str, Any]):
        self.id = data.get('id', '')
        self.type = data.get('type', '')
        attributes = data.get('attributes', {})
        self.map_name = attributes.get('mapName', '')
        self.game_mode = attributes.get('gameMode', '')
        self.created_at = attributes.get('createdAt', '')
        self.duration = attributes.get('duration', 0)
        self.custom_match = attributes.get('isCustomMatch', False)
        self.shard_id = attributes.get('shardId', '')
        
        # Parse relationships
        relationships = data.get('relationships', {})
        
        # Rosters
        rosters = relationships.get('rosters', {})
        roster_data = rosters.get('data', [])
        self.roster_ids = [roster.get('id', '') for roster in roster_data]
        
        # Assets (for telemetry)
        assets = relationships.get('assets', {})
        asset_data = assets.get('data', [])
        self.asset_ids = [asset.get('id', '') for asset in asset_data]

class PubgParticipant:
    def __init__(self, data: Dict[str, Any]):
        self.id = data.get('id', '')
        self.type = data.get('type', '')
        attributes = data.get('attributes', {})
        self.actor = attributes.get('actor', '')
        self.shard_id = attributes.get('shardId', '')
        
        # Stats
        stats = attributes.get('stats', {})
        self.assists = stats.get('assists', 0)
        self.boosts = stats.get('boosts', 0)
        self.damage_dealt = stats.get('damageDealt', 0)
        self.dbnos = stats.get('DBNOs', 0)
        self.headshot_kills = stats.get('headshotKills', 0)
        self.heals = stats.get('heals', 0)
        self.kill_place = stats.get('killPlace', 0)
        self.kill_streaks = stats.get('killStreaks', 0)
        self.kills = stats.get('kills', 0)
        self.longest_kill = stats.get('longestKill', 0)
        self.name = stats.get('name', '')
        self.player_id = stats.get('playerId', '')
        self.revives = stats.get('revives', 0)
        self.ride_distance = stats.get('rideDistance', 0)
        self.road_kills = stats.get('roadKills', 0)
        self.swim_distance = stats.get('swimDistance', 0)
        self.team_kills = stats.get('teamKills', 0)
        self.time_survived = stats.get('timeSurvived', 0)
        self.vehicle_destroys = stats.get('vehicleDestroys', 0)
        self.walk_distance = stats.get('walkDistance', 0)
        self.weapons_acquired = stats.get('weaponsAcquired', 0)
        self.win_place = stats.get('winPlace', 0)

class PubgRoster:
    def __init__(self, data: Dict[str, Any]):
        self.id = data.get('id', '')
        self.type = data.get('type', '')
        attributes = data.get('attributes', {})
        self.shard_id = attributes.get('shardId', '')
        
        # Stats
        stats = attributes.get('stats', {})
        self.rank = stats.get('rank', 0)
        self.team_id = stats.get('teamId', 0)
        
        # Parse participant relationships
        relationships = data.get('relationships', {})
        participants = relationships.get('participants', {})
        participant_data = participants.get('data', [])
        self.participant_ids = [participant.get('id', '') for participant in participant_data]

class PubgAsset:
    def __init__(self, data: Dict[str, Any]):
        self.id = data.get('id', '')
        self.type = data.get('type', '')
        attributes = data.get('attributes', {})
        self.url = attributes.get('URL', '')
        self.created_at = attributes.get('createdAt', '')
        self.description = attributes.get('description', '')
        self.name = attributes.get('name', '')

class TelemetryEvent:
    def __init__(self, data: Dict[str, Any]):
        self.timestamp = data.get('_D', '')
        self.event_type = data.get('_T', '')
        self.data = data

class KillEvent(TelemetryEvent):
    def __init__(self, data: Dict[str, Any]):
        super().__init__(data)
        self.killer = data.get('killer', {})
        self.victim = data.get('victim', {}) 
        self.damage_type_category = data.get('damageTypeCategory', '')
        self.damage_causer_name = data.get('damageCauserName', '')
        self.distance = data.get('distance', 0)
        self.finisher = data.get('finisher', {})

class KnockEvent(TelemetryEvent):
    def __init__(self, data: Dict[str, Any]):
        super().__init__(data)
        self.attacker = data.get('attacker', {})
        self.victim = data.get('victim', {})
        self.damage_type_category = data.get('damageTypeCategory', '')
        self.damage_causer_name = data.get('damageCauserName', '')
        self.distance = data.get('distance', 0) 