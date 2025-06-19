from typing import Dict, List, Optional, Any
from dataclasses import dataclass

@dataclass
class MatchReference:
    """Match reference from player relationships"""
    type: str
    id: str
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'MatchReference':
        return cls(
            type=data.get('type', ''),
            id=data.get('id', '')
        )

@dataclass
class RelationshipData:
    """Relationship data containing match references"""
    data: List[MatchReference]
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'RelationshipData':
        match_refs = [
            MatchReference.from_dict(match_data) 
            for match_data in data.get('data', [])
        ]
        return cls(data=match_refs)

@dataclass
class PlayerAttributes:
    """Player attributes from PUBG API"""
    name: str
    shard_id: str
    created_at: str
    updated_at: str
    patch_version: str
    title_id: str
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'PlayerAttributes':
        return cls(
            name=data.get('name', ''),
            shard_id=data.get('shardId', ''),
            created_at=data.get('createdAt', ''),
            updated_at=data.get('updatedAt', ''),
            patch_version=data.get('patchVersion', ''),
            title_id=data.get('titleId', '')
        )

@dataclass
class PlayerData:
    """Individual player data from PUBG API"""
    type: str
    id: str
    attributes: PlayerAttributes
    matches: RelationshipData
    links: Optional[Dict[str, str]] = None
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'PlayerData':
        attributes = PlayerAttributes.from_dict(data.get('attributes', {}))
        relationships = data.get('relationships', {})
        matches = RelationshipData.from_dict(relationships.get('matches', {}))
        
        return cls(
            type=data.get('type', ''),
            id=data.get('id', ''),
            attributes=attributes,
            matches=matches,
            links=data.get('links')
        )
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary format used by the rest of the application"""
        match_ids = [match.id for match in self.matches.data]
        return {
            'id': self.id,
            'type': self.type,
            'name': self.attributes.name,
            'shard_id': self.attributes.shard_id,
            'patch_version': self.attributes.patch_version,
            'title_id': self.attributes.title_id,
            'created_at': self.attributes.created_at,
            'updated_at': self.attributes.updated_at,
            'match_ids': match_ids
        }

@dataclass
class PlayersResponse:
    """Root players response from PUBG API"""
    data: List[PlayerData]
    links: Optional[Dict[str, str]] = None
    meta: Optional[Dict[str, Any]] = None
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'PlayersResponse':
        players = [
            PlayerData.from_dict(player_data) 
            for player_data in data.get('data', [])
        ]
        return cls(
            data=players,
            links=data.get('links'),
            meta=data.get('meta')
        )

# Legacy classes for backward compatibility
@dataclass
class PubgMatch:
    id: str
    map_name: str
    game_mode: str
    created_at: str
    duration: int
    custom_match: bool
    shard_id: str
    roster_ids: List[str]
    asset_ids: List[str]

@dataclass
class PubgParticipant:
    id: str
    name: str
    player_id: str
    stats: Dict[str, Any]

@dataclass
class PubgRoster:
    id: str
    rank: int
    team_id: int
    participant_ids: List[str]

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