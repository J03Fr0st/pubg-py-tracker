#!/usr/bin/env python3
"""
Debug test script for PUBG Discord Bot
Use this to test individual components and debug issues
"""

import asyncio
import sys
from datetime import datetime
from config.settings import settings
from services.storage_service import storage_service
from services.pubg_api_service import pubg_api_service
from models.player import PlayerModel

async def debug_storage_service():
    """Test MongoDB connection and operations"""
    print("🔍 Testing Storage Service...")
    print("-" * 40)
    
    try:
        await storage_service.initialize()
        print("✅ Storage service initialized")
        
        # Test getting all players
        players = await storage_service.get_all_players()
        print(f"✅ Found {len(players)} players in database")
        
        for player in players:
            print(f"  - {player.name} ({player.pubgId})")
            print(f"    Matches: {len(player.matches or [])}")
        
        # Test checking processed matches
        is_processed = await storage_service.is_match_processed("test-match-id")
        print(f"✅ Test match processed check: {is_processed}")
        
        await storage_service.close()
        print("✅ Storage service test completed")
        
    except Exception as e:
        print(f"❌ Storage service test failed: {e}")
        import traceback
        traceback.print_exc()

async def debug_pubg_api():
    """Test PUBG API connection and calls"""
    print("\n🔍 Testing PUBG API Service...")
    print("-" * 40)
    
    try:
        await pubg_api_service.initialize()
        print("✅ PUBG API service initialized")
        
        # Test getting a single player
        test_players = ["J03Fr0st"]  # Known player from your database
        players = await pubg_api_service.get_players_by_names(test_players)
        
        if players:
            player = players[0]
            print(f"✅ Found player: {player['name']}")
            print(f"  - PUBG ID: {player['id']}")
            print(f"  - Shard: {player['shard_id']}")
            print(f"  - Recent matches: {len(player['match_ids'])}")
            
            # Test getting a match if available
            if player['match_ids']:
                match_id = player['match_ids'][0]
                print(f"\n🔍 Testing match retrieval for: {match_id}")
                
                match_result = await pubg_api_service.get_match(match_id)
                if match_result:
                    match_data, included = match_result
                    print(f"✅ Retrieved match: {match_data['map_name']} - {match_data['game_mode']}")
                    print(f"  - Duration: {match_data['duration']} seconds")
                    print(f"  - Included data: {len(included)} items")
                else:
                    print("❌ Failed to retrieve match")
        else:
            print("❌ No players found")
        
        await pubg_api_service.close()
        print("✅ PUBG API test completed")
        
    except Exception as e:
        print(f"❌ PUBG API test failed: {e}")
        import traceback
        traceback.print_exc()

async def debug_match_processing():
    """Test match processing workflow"""
    print("\n🔍 Testing Match Processing Workflow...")
    print("-" * 40)
    
    try:
        # Initialize services
        await storage_service.initialize()
        await pubg_api_service.initialize()
        
        # Get monitored players
        players = await storage_service.get_all_players()
        if not players:
            print("❌ No players to monitor")
            return
        
        print(f"✅ Found {len(players)} monitored players")
        
        # Get recent matches for first player
        first_player = players[0]
        if not first_player.name:
            print("❌ First player has no name")
            return
        player_names = [first_player.name]
        
        api_players = await pubg_api_service.get_players_by_names(player_names)
        if api_players:
            api_player = api_players[0]
            match_ids = api_player['match_ids'][:3]  # Test first 3 matches
            
            print(f"✅ Testing {len(match_ids)} matches for {first_player.name}")
            
            for i, match_id in enumerate(match_ids, 1):
                print(f"\n  📋 Match {i}: {match_id}")
                
                # Check if already processed
                is_processed = await storage_service.is_match_processed(match_id)
                print(f"    Processed: {is_processed}")
                
                # Get match details
                match_result = await pubg_api_service.get_match(match_id)
                if match_result:
                    match_data, included = match_result
                    print(f"    Map: {match_data['map_name']}")
                    print(f"    Mode: {match_data['game_mode']}")
                    print(f"    Created: {match_data['created_at']}")
                else:
                    print("    ❌ Failed to get match details")
        
        await storage_service.close()
        await pubg_api_service.close()
        print("\n✅ Match processing test completed")
        
    except Exception as e:
        print(f"❌ Match processing test failed: {e}")
        import traceback
        traceback.print_exc()

async def debug_environment():
    """Test environment configuration"""
    print("🔍 Testing Environment Configuration...")
    print("-" * 40)
    
    print(f"Discord Token: {'✅ Set' if settings.DISCORD_TOKEN else '❌ Missing'}")
    print(f"Discord Client ID: {'✅ Set' if settings.DISCORD_CLIENT_ID else '❌ Missing'}")
    print(f"Discord Channel ID: {settings.DISCORD_CHANNEL_ID}")
    print(f"PUBG API Key: {'✅ Set' if settings.PUBG_API_KEY else '❌ Missing'}")
    print(f"PUBG API URL: {settings.PUBG_API_URL}")
    print(f"PUBG Shard: {settings.DEFAULT_SHARD}")
    print(f"MongoDB URI: {'✅ Set' if settings.MONGODB_URI else '❌ Missing'}")
    print(f"Check Interval: {settings.CHECK_INTERVAL_MS}ms")
    print(f"Max Matches: {settings.MAX_MATCHES_TO_PROCESS}")

async def debug_discord_bot():
    """Test Discord bot connection"""
    print("\n🔍 Testing Discord Bot Connection...")
    print("-" * 40)
    
    try:
        # Test environment variables
        if not settings.DISCORD_TOKEN:
            print("❌ DISCORD_TOKEN not set")
            return
        if not settings.DISCORD_CLIENT_ID:
            print("❌ DISCORD_CLIENT_ID not set")  
            return
        if not settings.DISCORD_CHANNEL_ID:
            print("❌ DISCORD_CHANNEL_ID not set")
            return
            
        print(f"✅ Token: {'*' * 10 + settings.DISCORD_TOKEN[-10:]}")
        print(f"✅ Client ID: {settings.DISCORD_CLIENT_ID}")
        print(f"✅ Channel ID: {settings.DISCORD_CHANNEL_ID}")
        
        # Test bot connection (short test)
        from discord.ext import commands
        import discord
        
        test_intents = discord.Intents.default()
        test_intents.message_content = True
        test_intents.guilds = True
        
        test_bot = commands.Bot(command_prefix='!', intents=test_intents)
        
        @test_bot.event
        async def on_ready():
            print(f"✅ Bot connected as {test_bot.user}")
            print(f"✅ Connected to {len(test_bot.guilds)} guild(s)")
            
            # Check if target channel exists
            target_channel = test_bot.get_channel(settings.DISCORD_CHANNEL_ID)
            if target_channel and isinstance(target_channel, discord.TextChannel):
                print(f"✅ Found target channel: {target_channel.name}")
            elif target_channel:
                print(f"❌ Channel {settings.DISCORD_CHANNEL_ID} is not a text channel")
            else:
                print(f"❌ Could not find channel with ID {settings.DISCORD_CHANNEL_ID}")
                
            await test_bot.close()
        
        print("🔄 Testing bot connection...")
        try:
            await test_bot.start(settings.DISCORD_TOKEN)
        except discord.LoginFailure:
            print("❌ Invalid bot token")
        except discord.HTTPException as e:
            print(f"❌ HTTP error: {e}")
        except Exception as e:
            print(f"❌ Connection error: {e}")
            
    except Exception as e:
        print(f"❌ Discord bot test failed: {e}")
        import traceback
        traceback.print_exc()

async def main():
    """Main debug function"""
    print("🐛 PUBG Discord Bot Debug Session")
    print("=" * 50)
    print(f"Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    # Test environment
    await debug_environment()
    
    # Test services
    await debug_storage_service()
    await debug_pubg_api()
    await debug_match_processing()
    await debug_discord_bot()
    
    print("\n🎉 Debug session completed!")

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n🛑 Debug session interrupted by user")
    except Exception as e:
        print(f"\n💥 Debug session failed: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1) 