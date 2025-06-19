import asyncio
from typing import List, Dict, Any, Set, Optional
from datetime import datetime
from config.settings import settings
from services.storage_service import storage_service
from services.pubg_api_service import pubg_api_service
from services.discord_bot_service import bot
from models.match import Match

class MatchMonitorService:
    def __init__(self):
        self.is_running = False
        self.check_interval = settings.CHECK_INTERVAL_MS / 1000  # Convert to seconds
        self.max_matches_to_process = settings.MAX_MATCHES_TO_PROCESS
        
    async def start_monitoring(self):
        """Start the match monitoring loop"""
        self.is_running = True
        print("Starting match monitoring...")
        
        while self.is_running:
            try:
                await self._check_for_new_matches()
                await asyncio.sleep(self.check_interval)
            except Exception as e:
                print(f"Error in monitoring loop: {e}")
                await asyncio.sleep(self.check_interval)
    
    def stop_monitoring(self):
        """Stop the match monitoring loop"""
        self.is_running = False
        print("Stopping match monitoring...")
    
    async def _check_for_new_matches(self):
        """Check for new matches for all monitored players"""
        try:
            print("🔍 Checking for new matches...")
            
            # Get all monitored players
            players = await storage_service.get_all_players()
            if not players:
                print("❌ No players to monitor - use /add command to add players")
                return

            player_names = [p.name for p in players if p.name]
            print(f"✅ Found {len(players)} players to monitor: {', '.join(player_names)}")
            
            # Get recent matches for all players
            all_match_ids = await self._get_recent_matches_for_players(players)
            if not all_match_ids:
                print("❌ No recent matches found for any monitored players")
                return
            
            total_matches = sum(len(matches) for matches in all_match_ids.values())
            print(f"✅ Found {total_matches} total recent matches across all players")
            
            # Group matches by ID and collect monitored players in each match
            match_groups = await self._group_matches_by_id(all_match_ids, players)
            print(f"✅ Grouped into {len(match_groups)} unique matches")
            
            # Filter out already processed matches
            new_matches = await self._filter_unprocessed_matches(match_groups)
            if not new_matches:
                print("ℹ️  No new matches to process (all matches already processed)")
                return
            
            print(f"✅ Found {len(new_matches)} new matches to process")
            
            # Sort matches chronologically (oldest first)
            sorted_matches = self._sort_matches_chronologically(new_matches)
            
            # Process matches (limit to max_matches_to_process)
            matches_to_process = sorted_matches[:self.max_matches_to_process]
            print(f"🚀 Processing {len(matches_to_process)} new matches...")
            
            for match_info in matches_to_process:
                await self._process_match(match_info)
                
        except Exception as e:
            print(f"❌ Error checking for new matches: {e}")
            import traceback
            traceback.print_exc()
    
    async def _get_recent_matches_for_players(self, players) -> Dict[str, List[str]]:
        """Get recent match IDs for all players"""
        player_matches = {}
        
        # Group players for batch API requests (PUBG API supports multiple players)
        player_names = [player.name for player in players if player.name]
        
        try:
            # Get player data with recent matches
            pubg_players = await pubg_api_service.get_players_by_names(player_names)
            
            for pubg_player in pubg_players:
                # Limit to recent matches
                recent_match_ids = pubg_player['match_ids'][:self.max_matches_to_process]
                player_matches[pubg_player['name']] = recent_match_ids
                print(f"Found {len(recent_match_ids)} recent matches for {pubg_player['name']}")
                
        except Exception as e:
            print(f"Error getting recent matches: {e}")
        
        return player_matches
    
    async def _group_matches_by_id(self, player_matches: Dict[str, List[str]], players) -> Dict[str, List[str]]:
        """Group matches by match ID, collecting all monitored players in each match"""
        match_groups = {}
        
        for player_name, match_ids in player_matches.items():
            for match_id in match_ids:
                if match_id not in match_groups:
                    match_groups[match_id] = []
                match_groups[match_id].append(player_name)
        
        return match_groups
    
    async def _filter_unprocessed_matches(self, match_groups: Dict[str, List[str]]) -> Dict[str, List[str]]:
        """Filter out matches that have already been processed"""
        new_matches = {}
        
        for match_id, player_names in match_groups.items():
            if not await storage_service.is_match_processed(match_id):
                new_matches[match_id] = player_names
        
        return new_matches
    
    def _sort_matches_chronologically(self, match_groups: Dict[str, List[str]]) -> List[Dict[str, Any]]:
        """Sort matches by timestamp (this requires fetching match data)"""
        # For now, return in order found. In a real implementation, we'd need to
        # fetch basic match data to get timestamps for sorting
        return [{"match_id": match_id, "players": players} for match_id, players in match_groups.items()]
    
    async def _process_match(self, match_info: Dict[str, Any]):
        """Process a single match"""
        match_id = match_info["match_id"]
        monitored_players = match_info["players"]
        
        try:
            print(f"Processing match {match_id} with players: {', '.join(monitored_players)}")
            
            # Get match details
            match_result = await pubg_api_service.get_match(match_id)
            if not match_result:
                print(f"Could not fetch match details for {match_id}")
                return
            
            pubg_match, included_data = match_result
            
            # Create match object
            match = Match.from_pubg_api(pubg_match, included_data)
            
            # Get monitored player IDs for roster lookup
            players = await storage_service.get_all_players()
            monitored_player_ids = []
            monitored_player_name_to_id = {}
            
            for player in players:
                if player.name and player.name in monitored_players:
                    monitored_player_ids.append(player.pubgId)
                    monitored_player_name_to_id[player.name] = player.pubgId
            
            # Get squad members (all players in the roster containing monitored players)
            squad_members = match.get_squad_members(monitored_player_ids)
            if not squad_members:
                print(f"Could not find squad members for monitored players in match {match_id}")
                return
            
            # Get telemetry events
            telemetry_events = []
            if match.telemetry_url:
                telemetry_data = await pubg_api_service.get_telemetry(match.telemetry_url)
                if telemetry_data:
                    # Properly format the timestamp for telemetry processing
                    if match.created_at.tzinfo is not None:
                        # Already has timezone info, use as is
                        match_timestamp = match.created_at.isoformat()
                    else:
                        # No timezone info, add Z for UTC
                        match_timestamp = match.created_at.isoformat() + "Z"
                    
                    telemetry_events = pubg_api_service.process_telemetry_events(
                        telemetry_data,
                        monitored_players,
                        match_timestamp
                    )
                    print(f"Found {len(telemetry_events)} relevant telemetry events")
                else:
                    print(f"Could not fetch telemetry for match {match_id}")
            else:
                print(f"No telemetry URL available for match {match_id}")
            
            # Send Discord embed
            print(f"📤 Sending Discord message for match {match_id}")
            await bot.send_match_summary(
                match.to_dict(),
                squad_members,
                telemetry_events
            )
            print(f"✅ Discord message sent for match {match_id}")
            
            # Mark match as processed
            await storage_service.mark_match_processed(match_id)
            print(f"Successfully processed match {match_id}")
            
        except Exception as e:
            print(f"❌ Error processing match {match_id}: {e}")
            import traceback
            traceback.print_exc()

# Global monitor service instance
match_monitor_service = MatchMonitorService() 