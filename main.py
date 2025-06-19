import asyncio
import signal
import sys
from config.settings import settings
from services.storage_service import storage_service
from services.pubg_api_service import pubg_api_service
from services.discord_bot_service import bot
from services.match_monitor_service import match_monitor_service

class PubgTrackerApp:
    def __init__(self):
        self.shutdown_event = asyncio.Event()
        
    async def initialize_services(self):
        """Initialize all services"""
        print("Initializing PUBG Tracker services...")
        
        try:
            # Validate environment variables
            settings.validate()
            print("✓ Environment variables validated")
            
            # Initialize storage service
            await storage_service.initialize()
            print("✓ Storage service initialized")
            
            # Initialize PUBG API service
            await pubg_api_service.initialize()
            print("✓ PUBG API service initialized")
            
            print("All services initialized successfully!")
            
        except Exception as e:
            print(f"Failed to initialize services: {e}")
            raise
    
    async def cleanup_services(self):
        """Cleanup all services"""
        print("Cleaning up services...")
        
        try:
            # Stop match monitoring
            match_monitor_service.stop_monitoring()
            
            # Close PUBG API service
            await pubg_api_service.close()
            print("✓ PUBG API service closed")
            
            # Close storage service
            await storage_service.close()
            print("✓ Storage service closed")
            
            # Close Discord bot
            await bot.close()
            print("✓ Discord bot closed")
            
            print("All services cleaned up successfully!")
            
        except Exception as e:
            print(f"Error during cleanup: {e}")
    
    def setup_signal_handlers(self):
        """Setup signal handlers for graceful shutdown"""
        def signal_handler(signum, frame):
            print(f"\nReceived signal {signum}. Initiating graceful shutdown...")
            self.shutdown_event.set()
        
        signal.signal(signal.SIGINT, signal_handler)
        signal.signal(signal.SIGTERM, signal_handler)
    
    async def run_bot_and_monitor(self):
        """Run both the Discord bot and match monitor concurrently"""
        try:
            # Start match monitoring in background
            monitor_task = asyncio.create_task(match_monitor_service.start_monitoring())
            
            # Start Discord bot in background
            bot_task = asyncio.create_task(bot.start(settings.DISCORD_TOKEN))
            
            # Wait for shutdown signal
            await self.shutdown_event.wait()
            
            print("Shutdown signal received, stopping services...")
            
            # Cancel tasks
            monitor_task.cancel()
            bot_task.cancel()
            
            try:
                await monitor_task
            except asyncio.CancelledError:
                pass
            
            try:
                await bot_task
            except asyncio.CancelledError:
                pass
                
        except Exception as e:
            print(f"Error running bot and monitor: {e}")
            raise
    
    async def run(self):
        """Main application entry point"""
        try:
            # Setup signal handlers
            self.setup_signal_handlers()
            
            # Initialize services
            await self.initialize_services()
            
            print("Starting PUBG Discord Bot...")
            print(f"Monitoring interval: {settings.CHECK_INTERVAL_MS / 1000} seconds")
            print(f"Max matches per check: {settings.MAX_MATCHES_TO_PROCESS}")
            print(f"Target Discord channel ID: {settings.DISCORD_CHANNEL_ID}")
            print("Bot is ready! Use /add, /remove, and /list commands in Discord.")
            
            # Run bot and monitor
            await self.run_bot_and_monitor()
            
        except KeyboardInterrupt:
            print("\nKeyboard interrupt received")
        except Exception as e:
            print(f"Application error: {e}")
        finally:
            # Cleanup
            await self.cleanup_services()

async def main():
    """Main function"""
    app = PubgTrackerApp()
    await app.run()

if __name__ == "__main__":
    try:
        # Run the application
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\nApplication stopped by user")
    except Exception as e:
        print(f"Fatal error: {e}")
        sys.exit(1) 