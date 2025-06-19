from typing import Dict, List, Optional, Any
from dataclasses import dataclass

@dataclass
class Location:
    """Player location coordinates"""
    x: float
    y: float
    z: float
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Location':
        return cls(
            x=data.get('x', 0.0),
            y=data.get('y', 0.0),
            z=data.get('z', 0.0)
        )

@dataclass
class Character:
    """Player character information"""
    name: str
    team_id: int
    health: float
    location: Location
    ranking: int
    account_id: str
    is_in_blue_zone: Optional[bool] = None
    is_in_red_zone: Optional[bool] = None
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Character':
        location_data = data.get('location', {})
        location = Location.from_dict(location_data)
        
        return cls(
            name=data.get('name', ''),
            team_id=data.get('teamId', 0),
            health=data.get('health', 0.0),
            location=location,
            ranking=data.get('ranking', 0),
            account_id=data.get('accountId', ''),
            is_in_blue_zone=data.get('isInBlueZone'),
            is_in_red_zone=data.get('isInRedZone')
        )

@dataclass
class GameResult:
    """Victim's game result information"""
    rank: int
    game_result: str
    team_id: int
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'GameResult':
        return cls(
            rank=data.get('rank', 0),
            game_result=data.get('gameResult', ''),
            team_id=data.get('teamId', 0)
        )

@dataclass
class DamageInfo:
    """Damage information details"""
    damage_causer_name: str
    damage_reason: str
    damage_type_category: str
    distance: Optional[float] = None
    is_through_penetrable_wall: Optional[bool] = None
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'DamageInfo':
        return cls(
            damage_causer_name=data.get('damageCauserName', ''),
            damage_reason=data.get('damageReason', ''),
            damage_type_category=data.get('damageTypeCategory', ''),
            distance=data.get('distance'),
            is_through_penetrable_wall=data.get('isThroughPenetrableWall')
        )

@dataclass
class LogPlayerKillV2:
    """Player kill event from telemetry"""
    timestamp: str  # _D
    event_type: str  # _T
    attack_id: int
    victim_game_result: GameResult
    victim: Character
    dbno_id: Optional[int] = None
    victim_weapon: Optional[str] = None
    victim_weapon_additional_info: Optional[List[str]] = None
    dbno_maker: Optional[Character] = None
    dbno_damage_info: Optional[DamageInfo] = None
    finisher: Optional[Character] = None
    finish_damage_info: Optional[DamageInfo] = None
    killer: Optional[Character] = None
    killer_damage_info: Optional[DamageInfo] = None
    assists_account_id: Optional[List[str]] = None
    team_killers_account_id: Optional[List[str]] = None
    is_suicide: Optional[bool] = None
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'LogPlayerKillV2':
        # Parse required fields
        victim_game_result = GameResult.from_dict(data.get('victimGameResult', {}))
        victim = Character.from_dict(data.get('victim', {}))
        
        # Parse optional Character fields
        dbno_maker = None
        if 'dBNOMaker' in data and data['dBNOMaker']:
            dbno_maker = Character.from_dict(data['dBNOMaker'])
            
        finisher = None
        if 'finisher' in data and data['finisher']:
            finisher = Character.from_dict(data['finisher'])
            
        killer = None
        if 'killer' in data and data['killer']:
            killer = Character.from_dict(data['killer'])
        
        # Parse optional DamageInfo fields
        dbno_damage_info = None
        if 'dBNODamageInfo' in data and data['dBNODamageInfo']:
            dbno_damage_info = DamageInfo.from_dict(data['dBNODamageInfo'])
            
        finish_damage_info = None
        if 'finishDamageInfo' in data and data['finishDamageInfo']:
            finish_damage_info = DamageInfo.from_dict(data['finishDamageInfo'])
            
        killer_damage_info = None
        if 'killerDamageInfo' in data and data['killerDamageInfo']:
            killer_damage_info = DamageInfo.from_dict(data['killerDamageInfo'])
        
        return cls(
            timestamp=data.get('_D', ''),
            event_type=data.get('_T', ''),
            attack_id=data.get('attackId', 0),
            victim_game_result=victim_game_result,
            victim=victim,
            dbno_id=data.get('dBNOId'),
            victim_weapon=data.get('victimWeapon'),
            victim_weapon_additional_info=data.get('victimWeaponAdditionalInfo'),
            dbno_maker=dbno_maker,
            dbno_damage_info=dbno_damage_info,
            finisher=finisher,
            finish_damage_info=finish_damage_info,
            killer=killer,
            killer_damage_info=killer_damage_info,
            assists_account_id=data.get('assists_AccountId'),
            team_killers_account_id=data.get('teamKillers_AccountId'),
            is_suicide=data.get('isSuicide')
        )

@dataclass
class LogPlayerMakeGroggy:
    """Player knock event from telemetry"""
    timestamp: str  # _D
    event_type: str  # _T
    attack_id: int
    attacker: Character
    victim: Character
    damage_reason: str
    damage_type_category: str
    damage_causer_name: str
    damage_causer_additional_info: List[str]
    victim_weapon: str
    victim_weapon_additional_info: List[str]
    distance: float
    is_attacker_in_vehicle: bool
    dbno_id: int
    is_through_penetrable_wall: bool
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'LogPlayerMakeGroggy':
        attacker = Character.from_dict(data.get('attacker', {}))
        victim = Character.from_dict(data.get('victim', {}))
        
        return cls(
            timestamp=data.get('_D', ''),
            event_type=data.get('_T', ''),
            attack_id=data.get('attackId', 0),
            attacker=attacker,
            victim=victim,
            damage_reason=data.get('damageReason', ''),
            damage_type_category=data.get('damageTypeCategory', ''),
            damage_causer_name=data.get('damageCauserName', ''),
            damage_causer_additional_info=data.get('damageCauserAdditionalInfo', []),
            victim_weapon=data.get('VictimWeapon', ''),
            victim_weapon_additional_info=data.get('VictimWeaponAdditionalInfo', []),
            distance=data.get('distance', 0.0),
            is_attacker_in_vehicle=data.get('isAttackerInVehicle', False),
            dbno_id=data.get('dBNOId', 0),
            is_through_penetrable_wall=data.get('isThroughPenetrableWall', False)
        )

# Legacy classes for backward compatibility
@dataclass
class ProcessedTelemetryEvent:
    """Processed telemetry event for Discord display"""
    timestamp: str
    match_time: str  # MM:SS format
    event_type: str  # 'kill' or 'knock'
    actor: str  # killer/attacker name
    target: str  # victim name
    weapon: str  # processed weapon name
    distance: float
    is_monitored_player: bool
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for compatibility with existing code"""
        return {
            'timestamp': self.timestamp,
            'match_time': self.match_time,
            'event_type': self.event_type,
            'actor': self.actor,
            'target': self.target,
            'weapon': self.weapon,
            'distance': self.distance,
            'is_monitored_player': self.is_monitored_player
        }

    @classmethod
    def from_kill_event(cls, event: LogPlayerKillV2, match_time: str, monitored_players: List[str], weapon_name: str) -> 'ProcessedTelemetryEvent':
        """Create from LogPlayerKillV2"""
        # Determine actor (prefer finisher, then killer)
        actor = ""
        if event.finisher:
            actor = event.finisher.name
        elif event.killer:
            actor = event.killer.name
        
        # Get distance from appropriate damage info
        distance = 0.0
        if event.finish_damage_info and event.finish_damage_info.distance:
            distance = event.finish_damage_info.distance / 100  # Convert to meters
        elif event.killer_damage_info and event.killer_damage_info.distance:
            distance = event.killer_damage_info.distance / 100  # Convert to meters
        
        return cls(
            timestamp=event.timestamp,
            match_time=match_time,
            event_type='kill',
            actor=actor,
            target=event.victim.name,
            weapon=weapon_name,
            distance=distance,
            is_monitored_player=actor in monitored_players
        )
    
    @classmethod
    def from_knock_event(cls, event: LogPlayerMakeGroggy, match_time: str, monitored_players: List[str], weapon_name: str) -> 'ProcessedTelemetryEvent':
        """Create from LogPlayerMakeGroggy"""
        distance = event.distance / 100 if event.distance else 0.0  # Convert to meters
        
        return cls(
            timestamp=event.timestamp,
            match_time=match_time,
            event_type='knock',
            actor=event.attacker.name,
            target=event.victim.name,
            weapon=weapon_name,
            distance=distance,
            is_monitored_player=event.attacker.name in monitored_players
        ) 