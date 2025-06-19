#!/usr/bin/env python3
"""
Utility script to clear processed matches for testing
This will allow the bot to re-process recent matches
"""

import asyncio
from services.storage_service import storage_service

async def clear_processed_matches():
    """Clear all processed matches so they can be re-processed"""
    try:
        await storage_service.initialize()
        print("Connected to database...")
        
        # Get count before clearing
        collection = storage_service.processed_matches_collection
        if collection is None:
            print("❌ Processed matches collection not initialized")
            return
        count_before = await collection.count_documents({})
        print(f"Found {count_before} processed matches")
        
        if count_before == 0:
            print("No processed matches to clear")
            return
        
        # Ask for confirmation
        response = input(f"Clear all {count_before} processed matches? This will allow re-processing recent matches. (y/N): ")
        
        if response.lower() != 'y':
            print("Operation cancelled")
            return
        
        # Clear all processed matches
        result = await collection.delete_many({})
        print(f"✅ Cleared {result.deleted_count} processed matches")
        print("The bot will now re-process recent matches on its next check")
        
        await storage_service.close()
        
    except Exception as e:
        print(f"❌ Error clearing processed matches: {e}")
        import traceback
        traceback.print_exc()

async def clear_recent_matches(count: int = 5):
    """Clear only the most recent processed matches"""
    try:
        await storage_service.initialize()
        print("Connected to database...")
        
        # Get the most recent processed matches
        collection = storage_service.processed_matches_collection
        if collection is None:
            print("❌ Processed matches collection not initialized")
            return
        recent_matches = await collection.find().sort("processedAt", -1).limit(count).to_list(length=count)
        
        if not recent_matches:
            print("No recent processed matches found")
            return
        
        print(f"Found {len(recent_matches)} recent processed matches:")
        for match in recent_matches:
            print(f"  - {match['matchId']} (processed at {match['processedAt']})")
        
        response = input(f"Clear these {len(recent_matches)} recent matches? (y/N): ")
        
        if response.lower() != 'y':
            print("Operation cancelled")
            return
        
        # Delete the recent matches
        match_ids = [match['matchId'] for match in recent_matches]
        result = await collection.delete_many({"matchId": {"$in": match_ids}})
        print(f"✅ Cleared {result.deleted_count} recent processed matches")
        print("The bot will re-process these matches on its next check")
        
        await storage_service.close()
        
    except Exception as e:
        print(f"❌ Error clearing recent matches: {e}")
        import traceback
        traceback.print_exc()

async def main():
    """Main function with options"""
    print("🧹 PUBG Match Processor Cleaner")
    print("=" * 40)
    print("This utility helps clear processed matches for testing")
    print()
    print("Options:")
    print("1. Clear recent 1 matches (recommended for testing)")
    print("2. Exit")
    
    choice = input("\nSelect option (1/2): ")
    
    if choice == '1':
        await clear_recent_matches(1)
    elif choice == '2':
        print("Goodbye!")
    else:
        print("Invalid choice")

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n🛑 Operation cancelled by user")
    except Exception as e:
        print(f"\n💥 Operation failed: {e}") 