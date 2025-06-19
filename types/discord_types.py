from typing import Dict, List, Optional, Any
from dataclasses import dataclass

@dataclass
class DiscordEmbed:
    title: str
    description: str
    color: int
    timestamp: Optional[str] = None
    footer: Optional[str] = None

@dataclass
class PlayerStats:
    player_name: str
    kills: int
    headshot_kills: int
    knocks: int
    damage: int
    assists: int
    headshot_percentage: float
    survival_time: int
    longest_kill: float
    distance_traveled: float
    revives: int
    
@dataclass
class MatchSummary:
    match_id: str
    map_name: str
    game_mode: str
    match_date: str
    placement: int
    squad_size: int
    total_kills: int
    total_knocks: int
    total_damage: int
    players: List[PlayerStats]
    
@dataclass
class KillEvent:
    timestamp: str
    event_type: str  # 'kill' or 'knock'
    killer: str
    victim: str
    weapon: str
    distance: float
    
@dataclass
class PlayerTimeline:
    player_name: str
    events: List[KillEvent] 