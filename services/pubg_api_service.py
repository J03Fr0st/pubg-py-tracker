import asyncio
import aiohttp
import gzip
import json
from typing import List, Optional, Dict, Any, Tuple
from config.settings import settings
from utils.rate_limiter import RateLimiter
from utils.mappings import DAMAGE_CAUSER_NAME
from datetime import datetime, timezone
from pubg_types.pubg_types import PlayersResponse
from pubg_types.telemetry_types import LogPlayerKillV2, LogPlayerMakeGroggy, ProcessedTelemetryEvent

class PubgApiService:
    def __init__(self):
        # Clean up base URL - remove any trailing /shards if present
        base_url = settings.PUBG_API_URL.rstrip('/')
        if base_url.endswith('/shards'):
            base_url = base_url[:-7]  # Remove '/shards'
        
        self.base_url = base_url
        self.api_key = settings.PUBG_API_KEY
        self.shard = settings.PUBG_SHARD
        self.rate_limiter = RateLimiter(settings.PUBG_MAX_REQUESTS_PER_MINUTE)
        self.session: Optional[aiohttp.ClientSession] = None
        
        print(f"PUBG API initialized with base URL: {self.base_url}")
        
    async def initialize(self):
        """Initialize the HTTP session"""
        timeout = aiohttp.ClientTimeout(total=30)
        self.session = aiohttp.ClientSession(
            timeout=timeout,
            headers={
                'Authorization': f'Bearer {self.api_key}',
                'Accept': 'application/vnd.api+json',
                'Accept-Encoding': 'gzip'
            }
        )
        print("✓ PUBG API service initialized")
    
    async def close(self):
        """Close the HTTP session"""
        if self.session:
            await self.session.close()
    
    async def _make_request(self, url: str, retries: int = 3) -> Optional[Dict[str, Any]]:
        """Make an HTTP request with rate limiting and retries"""
        if not self.session:
            print("HTTP session not initialized")
            return None
            
        for attempt in range(retries):
            try:
                # Wait for rate limiter
                await self.rate_limiter.try_acquire()
                
                async with self.session.get(url) as response:
                    if response.status == 200:
                        data = await response.json()
                        return data
                    elif response.status == 429:
                        # Rate limited, wait and retry
                        retry_after = int(response.headers.get('Retry-After', '60'))
                        print(f"Rate limited. Waiting {retry_after} seconds...")
                        await asyncio.sleep(retry_after)
                        continue
                    elif response.status == 404:
                        print(f"Not found: {url}")
                        return None
                    else:
                        print(f"API request failed with status {response.status}: {url}")
                        if attempt < retries - 1:
                            await asyncio.sleep(2 ** attempt)  # Exponential backoff
                            continue
                        return None
                        
            except asyncio.TimeoutError:
                print(f"Request timeout (attempt {attempt + 1}): {url}")
                if attempt < retries - 1:
                    await asyncio.sleep(2 ** attempt)
                    continue
                return None
            except Exception as e:
                print(f"Request error (attempt {attempt + 1}): {e}")
                if attempt < retries - 1:
                    await asyncio.sleep(2 ** attempt)
                    continue
                return None
        
        return None
    
    async def get_players_by_names(self, player_names: List[str]) -> List[Dict[str, Any]]:
        """Get player data by names"""
        if not player_names:
            return []
        
        # API can handle multiple players in one request
        names_param = ','.join(player_names)
        url = f"{self.base_url}/shards/{self.shard}/players"
        
        params = {'filter[playerNames]': names_param}
        full_url = f"{url}?{'&'.join([f'{k}={v}' for k, v in params.items()])}"
        
        data = await self._make_request(full_url)
        if not data:
            return []
        
        try:
            # Use the new PlayersResponse class to parse the response
            players_response = PlayersResponse.from_dict(data)
            
            # Convert to the dictionary format expected by the rest of the application
            players = []
            for player_data in players_response.data:
                if player_data.type == 'player':
                    players.append(player_data.to_dict())
            
            return players
            
        except Exception as e:
            print(f"Error parsing players response with new types: {e}")
            # Fallback to the old parsing method
            players = []
            
            for player_data in data.get('data', []):
                if player_data.get('type') == 'player':
                    # Create player object manually
                    attributes = player_data.get('attributes', {})
                    relationships = player_data.get('relationships', {})
                    matches = relationships.get('matches', {})
                    match_data = matches.get('data', [])
                    match_ids = [match.get('id', '') for match in match_data]
                    
                    player = {
                        'id': player_data.get('id', ''),
                        'type': player_data.get('type', ''),
                        'name': attributes.get('name', ''),
                        'shard_id': attributes.get('shardId', ''),
                        'patch_version': attributes.get('patchVersion', ''),
                        'title_id': attributes.get('titleId', ''),
                        'created_at': attributes.get('createdAt', ''),
                        'updated_at': attributes.get('updatedAt', ''),
                        'match_ids': match_ids
                    }
                    players.append(player)
            
            return players
    
    async def get_match(self, match_id: str) -> Optional[Tuple[Dict[str, Any], List[Dict[str, Any]]]]:
        """Get match details including all included data"""
        url = f"{self.base_url}/shards/{self.shard}/matches/{match_id}"
        
        data = await self._make_request(url)
        if not data:
            return None
        
        match_data = data.get('data')
        included = data.get('included', [])
        
        if not match_data:
            return None
        
        if match_data.get('type') != 'match':
            return None
        
        # Create match object manually
        attributes = match_data.get('attributes', {})
        relationships = match_data.get('relationships', {})
        
        # Rosters
        rosters = relationships.get('rosters', {})
        roster_data = rosters.get('data', [])
        roster_ids = [roster.get('id', '') for roster in roster_data]
        
        # Assets (for telemetry)
        assets = relationships.get('assets', {})
        asset_data = assets.get('data', [])
        asset_ids = [asset.get('id', '') for asset in asset_data]
        
        match = {
            'id': match_data.get('id', ''),
            'type': match_data.get('type', ''),
            'map_name': attributes.get('mapName', ''),
            'game_mode': attributes.get('gameMode', ''),
            'created_at': attributes.get('createdAt', ''),
            'duration': attributes.get('duration', 0),
            'custom_match': attributes.get('isCustomMatch', False),
            'shard_id': attributes.get('shardId', ''),
            'roster_ids': roster_ids,
            'asset_ids': asset_ids
        }
        
        return match, included
    
    async def get_telemetry(self, telemetry_url: str) -> Optional[List[Dict[str, Any]]]:
        """Fetch and parse telemetry data"""
        if not telemetry_url:
            return None
        
        try:
            # Telemetry doesn't require API key, but may or may not be gzip compressed
            async with aiohttp.ClientSession() as session:
                async with session.get(telemetry_url) as response:
                    if response.status == 200:
                        raw_data = await response.read()
                        
                        # Try to parse as JSON directly first (uncompressed)
                        try:
                            telemetry_data = json.loads(raw_data.decode('utf-8'))
                            return telemetry_data
                        except (json.JSONDecodeError, UnicodeDecodeError):
                            # If that fails, try gzip decompression
                            try:
                                decompressed_data = gzip.decompress(raw_data)
                                telemetry_data = json.loads(decompressed_data.decode('utf-8'))
                                return telemetry_data
                            except (gzip.BadGzipFile, json.JSONDecodeError, UnicodeDecodeError) as e:
                                print(f"Failed to parse telemetry data: {e}")
                                return None
                    else:
                        print(f"Failed to fetch telemetry: HTTP {response.status}")
                        return None
        except Exception as e:
            print(f"Error fetching telemetry: {e}")
            return None
    
    def process_telemetry_events(
        self, 
        telemetry_data: List[Dict[str, Any]], 
        monitored_player_names: List[str],
        match_start_time: str
    ) -> List[Dict[str, Any]]:
        """Process telemetry data to extract kill and knock events"""
        if not telemetry_data:
            return []
        
        events = []
        
        # Convert match start time to datetime for calculations
        try:
            match_start = datetime.fromisoformat(match_start_time.replace('Z', '+00:00'))
        except:
            match_start = datetime.now(timezone.utc)
        
        for event_data in telemetry_data:
            event_type = event_data.get('_T', '')
            
            try:
                # Process kill events using new structured types
                if event_type == 'LogPlayerKillV2':
                    kill_event = LogPlayerKillV2.from_dict(event_data)
                    processed_event = self._process_kill_event_v2(kill_event, monitored_player_names, match_start)
                    if processed_event:
                        events.append(processed_event.to_dict())
                
                # Process knock events using new structured types
                elif event_type == 'LogPlayerMakeGroggy':
                    knock_event = LogPlayerMakeGroggy.from_dict(event_data)
                    processed_event = self._process_knock_event_v2(knock_event, monitored_player_names, match_start)
                    if processed_event:
                        events.append(processed_event.to_dict())
                        
            except Exception as e:
                print(f"Error processing telemetry event {event_type}: {e}")
                # Fallback to old processing method
                if event_type == 'LogPlayerKillV2':
                    event = self._process_kill_event(event_data, monitored_player_names, match_start)
                    if event:
                        events.append(event)
                elif event_type == 'LogPlayerMakeGroggy':
                    event = self._process_knock_event(event_data, monitored_player_names, match_start)
                    if event:
                        events.append(event)
        
        # Sort events by timestamp
        events.sort(key=lambda x: x['timestamp'])
        return events
    
    def _process_kill_event(
        self, 
        event_data: Dict[str, Any], 
        monitored_player_names: List[str],
        match_start: datetime
    ) -> Optional[Dict[str, Any]]:
        """Process a kill event from telemetry"""
        try:
            killer = event_data.get('killer', {})
            victim = event_data.get('victim', {})
            finisher = event_data.get('finisher', {})
            
            killer_name = killer.get('name', '')
            victim_name = victim.get('name', '')
            finisher_name = finisher.get('name', '') if finisher else ''
            
            # Only include events involving monitored players
            is_monitored = (
                killer_name in monitored_player_names or 
                victim_name in monitored_player_names or
                finisher_name in monitored_player_names
            )
            
            if not is_monitored:
                return None
            
            # Get event timestamp and calculate match time
            event_timestamp = event_data.get('_D', '')
            try:
                event_time = datetime.fromisoformat(event_timestamp.replace('Z', '+00:00'))
                match_elapsed = event_time - match_start
                match_time_seconds = int(match_elapsed.total_seconds())
                match_time_str = f"{match_time_seconds // 60:02d}:{match_time_seconds % 60:02d}"
            except:
                match_time_str = "00:00"
            
            # Process weapon name
            damage_causer = event_data.get('damageCauserName', '')
            weapon = DAMAGE_CAUSER_NAME.get(damage_causer, damage_causer)
            
            # Use finisher if available, otherwise killer
            actor_name = finisher_name if finisher_name else killer_name
            
            distance = event_data.get('distance', 0) / 100  # Convert to meters
            
            return {
                'timestamp': event_timestamp,
                'match_time': match_time_str,
                'event_type': 'kill',
                'actor': actor_name,
                'target': victim_name,
                'weapon': weapon,
                'distance': distance,
                'is_monitored_player': actor_name in monitored_player_names
            }
            
        except Exception as e:
            print(f"Error processing kill event: {e}")
            return None
    
    def _process_knock_event(
        self, 
        event_data: Dict[str, Any], 
        monitored_player_names: List[str],
        match_start: datetime
    ) -> Optional[Dict[str, Any]]:
        """Process a knock event from telemetry"""
        try:
            attacker = event_data.get('attacker', {})
            victim = event_data.get('victim', {})
            
            attacker_name = attacker.get('name', '')
            victim_name = victim.get('name', '')
            
            # Only include events involving monitored players
            is_monitored = (
                attacker_name in monitored_player_names or 
                victim_name in monitored_player_names
            )
            
            if not is_monitored:
                return None
            
            # Get event timestamp and calculate match time
            event_timestamp = event_data.get('_D', '')
            try:
                event_time = datetime.fromisoformat(event_timestamp.replace('Z', '+00:00'))
                match_elapsed = event_time - match_start
                match_time_seconds = int(match_elapsed.total_seconds())
                match_time_str = f"{match_time_seconds // 60:02d}:{match_time_seconds % 60:02d}"
            except:
                match_time_str = "00:00"
            
            # Process weapon name
            damage_causer = event_data.get('damageCauserName', '')
            weapon = DAMAGE_CAUSER_NAME.get(damage_causer, damage_causer)
            
            distance = event_data.get('distance', 0) / 100  # Convert to meters
            
            return {
                'timestamp': event_timestamp,
                'match_time': match_time_str,
                'event_type': 'knock',
                'actor': attacker_name,
                'target': victim_name,
                'weapon': weapon,
                'distance': distance,
                'is_monitored_player': attacker_name in monitored_player_names
            }
            
        except Exception as e:
            print(f"Error processing knock event: {e}")
            return None
    
    def _process_kill_event_v2(
        self, 
        event: LogPlayerKillV2, 
        monitored_player_names: List[str],
        match_start: datetime
    ) -> Optional[ProcessedTelemetryEvent]:
        """Process a LogPlayerKillV2 event using structured types"""
        try:
            # Determine the actor (prefer finisher, then killer)
            actor_name = ""
            if event.finisher:
                actor_name = event.finisher.name
            elif event.killer:
                actor_name = event.killer.name
            
            victim_name = event.victim.name
            
            # Only include events involving monitored players
            is_monitored = (
                actor_name in monitored_player_names or 
                victim_name in monitored_player_names
            )
            
            if not is_monitored:
                return None
            
            # Calculate match time
            try:
                event_time = datetime.fromisoformat(event.timestamp.replace('Z', '+00:00'))
                match_elapsed = event_time - match_start
                match_time_seconds = int(match_elapsed.total_seconds())
                match_time_str = f"{match_time_seconds // 60:02d}:{match_time_seconds % 60:02d}"
            except:
                match_time_str = "00:00"
            
            # Get weapon name from damage info
            weapon = "Unknown"
            if event.finish_damage_info:
                weapon = DAMAGE_CAUSER_NAME.get(event.finish_damage_info.damage_causer_name, event.finish_damage_info.damage_causer_name)
            elif event.killer_damage_info:
                weapon = DAMAGE_CAUSER_NAME.get(event.killer_damage_info.damage_causer_name, event.killer_damage_info.damage_causer_name)
            
            return ProcessedTelemetryEvent.from_kill_event(event, match_time_str, monitored_player_names, weapon)
            
        except Exception as e:
            print(f"Error processing LogPlayerKillV2: {e}")
            return None
    
    def _process_knock_event_v2(
        self, 
        event: LogPlayerMakeGroggy, 
        monitored_player_names: List[str],
        match_start: datetime
    ) -> Optional[ProcessedTelemetryEvent]:
        """Process a LogPlayerMakeGroggy event using structured types"""
        try:
            attacker_name = event.attacker.name
            victim_name = event.victim.name
            
            # Only include events involving monitored players
            is_monitored = (
                attacker_name in monitored_player_names or 
                victim_name in monitored_player_names
            )
            
            if not is_monitored:
                return None
            
            # Calculate match time
            try:
                event_time = datetime.fromisoformat(event.timestamp.replace('Z', '+00:00'))
                match_elapsed = event_time - match_start
                match_time_seconds = int(match_elapsed.total_seconds())
                match_time_str = f"{match_time_seconds // 60:02d}:{match_time_seconds % 60:02d}"
            except:
                match_time_str = "00:00"
            
            # Process weapon name
            weapon = DAMAGE_CAUSER_NAME.get(event.damage_causer_name, event.damage_causer_name)
            
            return ProcessedTelemetryEvent.from_knock_event(event, match_time_str, monitored_player_names, weapon)
            
        except Exception as e:
            print(f"Error processing LogPlayerMakeGroggy: {e}")
            return None

# Global API service instance
pubg_api_service = PubgApiService() 