import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class Settings:
    # Discord configuration
    DISCORD_TOKEN = os.getenv('DISCORD_TOKEN')
    DISCORD_CLIENT_ID = os.getenv('DISCORD_CLIENT_ID')
    DISCORD_CHANNEL_ID = int(os.getenv('DISCORD_CHANNEL_ID', '0'))
    
    # PUBG API configuration
    PUBG_API_KEY = os.getenv('PUBG_API_KEY')
    PUBG_API_URL = os.getenv('PUBG_API_URL', 'https://api.pubg.com')
    PUBG_SHARD = os.getenv('PUBG_SHARD', 'steam')
    PUBG_MAX_REQUESTS_PER_MINUTE = int(os.getenv('PUBG_MAX_REQUESTS_PER_MINUTE', '10'))
    
    # MongoDB configuration
    MONGODB_URI = os.getenv('MONGODB_URI', 'mongodb://localhost:27017/pubg-tracker')
    
    # Application configuration
    CHECK_INTERVAL_MS = int(os.getenv('CHECK_INTERVAL_MS', '60000'))
    MAX_MATCHES_TO_PROCESS = int(os.getenv('MAX_MATCHES_TO_PROCESS', '5'))
    
    # Validation
    @classmethod
    def validate(cls):
        """Validate that all required environment variables are set"""
        required_vars = [
            ('DISCORD_TOKEN', cls.DISCORD_TOKEN),
            ('DISCORD_CLIENT_ID', cls.DISCORD_CLIENT_ID),
            ('DISCORD_CHANNEL_ID', cls.DISCORD_CHANNEL_ID),
            ('PUBG_API_KEY', cls.PUBG_API_KEY),
        ]
        
        missing_vars = []
        for var_name, var_value in required_vars:
            if not var_value or (isinstance(var_value, int) and var_value == 0):
                missing_vars.append(var_name)
        
        if missing_vars:
            raise ValueError(f"Missing required environment variables: {', '.join(missing_vars)}")
        
        return True

# Create settings instance
settings = Settings() 