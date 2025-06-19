from typing import Dict, List, Optional, Any
from dataclasses import dataclass

@dataclass
class TelemetryPlayer:
    name: str
    account_id: str
    team_id: int
    
@dataclass
class TelemetryLocation:
    x: float
    y: float
    z: float

@dataclass
class TelemetryKillEvent:
    timestamp: str
    killer: TelemetryPlayer
    victim: TelemetryPlayer
    damage_causer_name: str
    damage_type_category: str
    distance: float
    finisher: Optional[TelemetryPlayer] = None
    
@dataclass
class TelemetryKnockEvent:
    timestamp: str
    attacker: TelemetryPlayer
    victim: TelemetryPlayer
    damage_causer_name: str
    damage_type_category: str
    distance: float

@dataclass
class ProcessedTelemetryEvent:
    timestamp: str
    match_time: str  # MM:SS format
    event_type: str  # 'kill' or 'knock'
    actor: str  # killer/attacker name
    target: str  # victim name
    weapon: str  # processed weapon name
    distance: float
    is_monitored_player: bool 