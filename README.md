# PUBG Python Discord Bot

A Discord bot that monitors PUBG players and posts detailed match summaries to Discord channels. This bot replicates the functionality of an existing TypeScript bot with exact message formatting.

## Features

- 🎮 **Automatic Match Monitoring** - Checks for new matches every 60 seconds
- 🎯 **Player Management** - Add/remove players via Discord slash commands
- 📊 **Detailed Match Summaries** - Team performance, individual stats, and kill timelines
- 🔫 **Telemetry Integration** - Real-time kill and knock events with timestamps
- 🌍 **Multi-Platform Support** - Supports Steam, Xbox, PlayStation, and more
- 📱 **Rich Discord Embeds** - Beautiful, color-coded match summaries
- 🔄 **Smart Rate Limiting** - Respects PUBG API rate limits
- 🗄️ **MongoDB Storage** - Persistent player and match tracking

## Discord Message Format

### Main Match Embed
```
🎮 PUBG Match Summary

⏰ 2024/01/15 14:30 (South African timezone)
🗺️ Erangel • Squad TPP

Team Performance
🏆 Placement: #3
👥 Squad Size: 4 players

Combat Summary
⚔️ Total Kills: 12
🔻 Total Knocks: 8
💥 Total Damage: 2,456
```

### Player Embeds (one per squad member)
```
Player: PlayerName

⚔️ Kills: 3 (2 headshots)
🔻 Knocks: 2
💥 Damage: 634 (1 assists)
🎯 Headshot %: 67%
⏰ Survival: 23min
📏 Longest Kill: 156m
👣 Distance: 2.1km
🚑 Revives: 1
🎯 2D Replay

*** KILLS & DBNOs ***
02:15 ⚔️ Killed - PlayerX (M416, 89m)
05:43 🔻 Knocked - PlayerY (Kar98k, 156m)
```

## Prerequisites

- Python 3.8 or higher
- MongoDB (local or cloud)
- Discord Bot Token
- PUBG API Key

## Installation

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd pubg-py-tracker
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Set up environment variables**
   
   Copy `env.example` to `.env` and fill in your credentials:
   ```env
   DISCORD_TOKEN=your_bot_token_here
   DISCORD_CLIENT_ID=your_client_id_here
   DISCORD_CHANNEL_ID=your_channel_id_here
   PUBG_API_KEY=your_pubg_api_key_here
   PUBG_SHARD=steam
   PUBG_MAX_REQUESTS_PER_MINUTE=10
   MONGODB_URI=mongodb://localhost:27017/pubg-tracker
   CHECK_INTERVAL_MS=60000
   MAX_MATCHES_TO_PROCESS=5
   ```

4. **Set up MongoDB**
   
   Install MongoDB locally or use a cloud service like MongoDB Atlas.

## Getting API Keys

### Discord Bot Token

1. Go to [Discord Developer Portal](https://discord.com/developers/applications)
2. Create a new application
3. Go to the "Bot" section
4. Create a bot and copy the token
5. Enable all necessary intents
6. Invite the bot to your server with proper permissions

### PUBG API Key

1. Go to [PUBG Developer Portal](https://developer.pubg.com/)
2. Create an account and generate an API key
3. Use the API key in your environment variables

## Running the Bot

1. **Start the application**
   ```bash
   python main.py
   ```

2. **Verify startup**
   
   You should see output like:
   ```
   Initializing PUBG Tracker services...
   ✓ Environment variables validated
   ✓ Storage service initialized
   ✓ PUBG API service initialized
   Bot logged in as YourBot#1234
   Synced 3 command(s)
   Starting PUBG Discord Bot...
   Bot is ready! Use /add, /remove, and /list commands in Discord.
   ```

## Discord Commands

### `/add playername`
Add a player to monitoring. The bot will start tracking their matches.

**Example:**
```
/add shroud
```

### `/remove playername`
Remove a player from monitoring.

**Example:**
```
/remove shroud
```

### `/list`
List all currently monitored players.

**Example:**
```
/list
```

## Configuration

### Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `DISCORD_TOKEN` | Discord bot token | Required |
| `DISCORD_CLIENT_ID` | Discord application client ID | Required |
| `DISCORD_CHANNEL_ID` | Target channel for match summaries | Required |
| `PUBG_API_KEY` | PUBG API key | Required |
| `PUBG_SHARD` | PUBG platform shard | `steam` |
| `PUBG_MAX_REQUESTS_PER_MINUTE` | API rate limit | `10` |
| `MONGODB_URI` | MongoDB connection string | `mongodb://localhost:27017/pubg-tracker` |
| `CHECK_INTERVAL_MS` | Match check interval in milliseconds | `60000` |
| `MAX_MATCHES_TO_PROCESS` | Max matches to process per check | `5` |

### Supported PUBG Shards

- `steam` - PC Steam
- `xbox` - Xbox
- `psn` - PlayStation
- `kakao` - Kakao (Korea)
- `console` - Console platforms

## Architecture

### Project Structure
```
pubg-py-tracker/
├── main.py                     # Application entry point
├── requirements.txt            # Python dependencies
├── env.example                 # Environment variables template
├── config/
│   └── settings.py            # Configuration management
├── services/
│   ├── discord_bot_service.py # Discord bot and commands
│   ├── pubg_api_service.py    # PUBG API integration
│   ├── match_monitor_service.py # Match monitoring logic
│   └── storage_service.py     # MongoDB operations
├── models/
│   ├── player.py              # Player data model
│   ├── match.py               # Match data model
│   └── processed_match.py     # Processed match tracking
├── utils/
│   ├── rate_limiter.py        # Token bucket rate limiter
│   └── mappings.py            # PUBG data mappings
└── types/
    ├── discord_types.py       # Discord type definitions
    ├── pubg_types.py          # PUBG API type definitions
    └── telemetry_types.py     # Telemetry event types
```

### Key Components

1. **Match Monitor Service** - Periodically checks for new matches
2. **PUBG API Service** - Handles all PUBG API interactions with rate limiting
3. **Discord Bot Service** - Manages Discord commands and embed creation
4. **Storage Service** - MongoDB operations for players and processed matches
5. **Rate Limiter** - Token bucket algorithm for API rate limiting

## Troubleshooting

### Common Issues

1. **Bot not responding to commands**
   - Verify bot has proper permissions in Discord server
   - Check bot token is correct
   - Ensure slash commands are synced

2. **No matches being detected**
   - Verify PUBG API key is valid
   - Check player names are spelled correctly
   - Ensure players have recent matches

3. **Database connection errors**
   - Verify MongoDB is running
   - Check MongoDB URI is correct
   - Ensure database permissions are set

4. **Rate limit errors**
   - Reduce `PUBG_MAX_REQUESTS_PER_MINUTE`
   - Increase `CHECK_INTERVAL_MS`
   - Monitor API usage

### Logs

The bot provides detailed console logging:

```
Found 2 players to monitor
Found 3 recent matches for PlayerName
Processing 1 new matches
Processing match abc123 with players: PlayerName
Found 5 relevant telemetry events
Sent match summary for abc123
Successfully processed match abc123
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Support

For support and questions:

1. Check the troubleshooting section
2. Review the logs for error messages
3. Open an issue on GitHub

## Acknowledgments

- PUBG Corporation for the PUBG API
- Discord.py library developers
- MongoDB team for the database solution