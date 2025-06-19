#!/usr/bin/env python3
"""
Debug individual service components
Use this with the debugger to step through specific service methods
"""

import asyncio
import sys
from config.settings import settings
from services.storage_service import storage_service
from services.pubg_api_service import pubg_api_service
from services.match_monitor_service import match_monitor_service

async def debug_single_match():
    """Debug processing a single match in detail"""
    print("🔍 Debug Single Match Processing")
    print("-" * 40)
    
    # Initialize services
    await storage_service.initialize()
    await pubg_api_service.initialize()
    
    # Get a test player
    players = await storage_service.get_all_players()
    if not players:
        print("❌ No players found")
        return
    
    test_player = players[0]
    print(f"🎮 Testing with player: {test_player.name}")
    
    # Get recent matches
    api_players = await pubg_api_service.get_players_by_names([test_player.name])
    if not api_players:
        print("❌ Failed to get player from API")
        return
    
    api_player = api_players[0]
    if not api_player['match_ids']:
        print("❌ No matches found")
        return
    
    # Get first unprocessed match
    test_match_id = None
    for match_id in api_player['match_ids']:
        is_processed = await storage_service.is_match_processed(match_id)
        if not is_processed:
            test_match_id = match_id
            break
    
    if not test_match_id:
        test_match_id = api_player['match_ids'][0]  # Use first match even if processed
    
    print(f"📋 Testing match: {test_match_id}")
    
    # Set breakpoint here for debugging
    breakpoint()  # This will pause execution when debugging
    
    # Get match details
    match_result = await pubg_api_service.get_match(test_match_id)
    if not match_result:
        print("❌ Failed to get match details")
        return
    
    match_data, included = match_result
    print(f"✅ Match retrieved: {match_data['map_name']} - {match_data['game_mode']}")
    
    # Test telemetry if available
    telemetry_url = None
    for item in included:
        if item.get('type') == 'asset' and 'telemetry' in item.get('attributes', {}).get('URL', ''):
            telemetry_url = item['attributes']['URL']
            break
    
    if telemetry_url:
        print(f"🔗 Testing telemetry: {telemetry_url[:50]}...")
        telemetry_data = await pubg_api_service.get_telemetry(telemetry_url)
        if telemetry_data:
            print(f"✅ Telemetry loaded: {len(telemetry_data)} events")
            
            # Process telemetry events
            events = pubg_api_service.process_telemetry_events(
                telemetry_data,
                [test_player.name],
                match_data['created_at']
            )
            print(f"✅ Processed events: {len(events)}")
        else:
            print("❌ Failed to load telemetry")
    
    await storage_service.close()
    await pubg_api_service.close()

async def debug_database_operations():
    """Debug database operations step by step"""
    print("🔍 Debug Database Operations")
    print("-" * 40)
    
    # Set breakpoint here for debugging
    breakpoint()
    
    await storage_service.initialize()
    
    # Test player operations
    players = await storage_service.get_all_players()
    print(f"Found {len(players)} players")
    
    if players:
        first_player = players[0]
        print(f"First player: {first_player.name}")
        
        # Test getting player by name
        found_player = await storage_service.get_player_by_name(first_player.name)
        print(f"Found by name: {found_player.name if found_player else 'None'}")
    
    # Test processed matches
    test_match_id = "test-debug-match-123"
    is_processed = await storage_service.is_match_processed(test_match_id)
    print(f"Test match processed: {is_processed}")
    
    # Mark as processed
    success = await storage_service.mark_match_processed(test_match_id)
    print(f"Mark processed success: {success}")
    
    # Check again
    is_processed = await storage_service.is_match_processed(test_match_id)
    print(f"Test match processed after marking: {is_processed}")
    
    await storage_service.close()

async def debug_api_requests():
    """Debug API requests step by step"""
    print("🔍 Debug API Requests")
    print("-" * 40)
    
    # Set breakpoint here for debugging
    breakpoint()
    
    await pubg_api_service.initialize()
    
    # Test player lookup
    test_names = ["J03Fr0st"]
    players = await pubg_api_service.get_players_by_names(test_names)
    
    if players:
        player = players[0]
        print(f"Player found: {player['name']}")
        print(f"Match IDs count: {len(player['match_ids'])}")
        
        if player['match_ids']:
            # Test match retrieval
            match_id = player['match_ids'][0]
            match_result = await pubg_api_service.get_match(match_id)
            
            if match_result:
                match_data, included = match_result
                print(f"Match data: {match_data['map_name']}")
                print(f"Included items: {len(included)}")
    
    await pubg_api_service.close()

async def main():
    """Main debug entry point"""
    print("🐛 Service Debug Mode")
    print("=" * 30)
    
    if len(sys.argv) > 1:
        mode = sys.argv[1]
    else:
        print("Available debug modes:")
        print("  python debug_service.py match    - Debug single match processing")
        print("  python debug_service.py db       - Debug database operations")
        print("  python debug_service.py api      - Debug API requests")
        print()
        mode = input("Enter debug mode (match/db/api): ").strip().lower()
    
    if mode == "match":
        await debug_single_match()
    elif mode == "db":
        await debug_database_operations()
    elif mode == "api":
        await debug_api_requests()
    else:
        print("❌ Invalid mode. Use: match, db, or api")
        sys.exit(1)

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n🛑 Debug interrupted")
    except Exception as e:
        print(f"\n💥 Debug failed: {e}")
        import traceback
        traceback.print_exc() 