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
   PUBG_API_URL=https://api.pubg.com
   DEFAULT_SHARD=steam
   MONGODB_URI=mongodb://localhost:27017/pubg-tracker
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
| `PUBG_API_URL` | PUBG API base URL | `https://api.pubg.com` |
| `DEFAULT_SHARD` | PUBG platform shard | `steam` |
| `MONGODB_URI` | MongoDB connection string | `mongodb://localhost:27017/pubg-tracker` |

### Application Configuration (Hardcoded)

The following settings are now hardcoded for simplicity:

- **Rate Limit**: 10 requests per minute
- **Check Interval**: 60 seconds
- **Max Matches**: 5 matches per check

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

## Development & CI/CD

### Development Setup

1. **Install development dependencies**
   ```bash
   pip install -r requirements-dev.txt
   ```

2. **Set up pre-commit hooks**
   ```bash
   pre-commit install
   ```

3. **Run code quality checks**
   ```bash
   # Format code
   black .
   isort .
   
   # Lint code
   flake8 .
   
   # Security scan
   bandit -r .
   
   # Check dependencies
   safety check
   ```

### GitHub Actions Pipeline

The project includes a comprehensive CI/CD pipeline that runs on every push and pull request:

#### 🧪 **Test Stage**
- **Multi-Python Testing**: Tests against Python 3.10, 3.11, and 3.12
- **Code Quality**: Black formatting, isort import sorting, flake8 linting
- **Security Scanning**: Bandit security analysis, Safety dependency checks
- **Import Testing**: Validates all modules can be imported correctly
- **Configuration Testing**: Ensures settings validation works properly

#### 🏷️ **Auto-Tagging Stage**
- **Automatic Versioning**: Creates version tags on every push to main
- **Smart Version Bumping**: Supports semantic versioning based on commit messages
- **Controlled Releases**: Option to skip tagging with `[skip-tag]`
- **Release Generation**: Automatically creates GitHub releases with assets

#### 🐳 **Docker Stage**
- **Multi-Architecture Builds**: Supports AMD64 and ARM64 architectures
- **Container Security**: Trivy vulnerability scanning
- **Smart Caching**: Uses GitHub Actions cache for faster builds
- **Automated Publishing**: Pushes to Docker Hub on successful builds

#### 🚀 **Release Stage**
- **Automated Releases**: Creates deployment packages on GitHub releases
- **Semantic Versioning**: Supports versioned Docker tags
- **Release Assets**: Generates compressed deployment archives

### Pipeline Configuration

The pipeline is configured in `.github/workflows/docker-publish.yml` and includes:

```yaml
# Triggers
on:
  push:
    branches: [ main, develop ]
  pull_request:
    branches: [ main ]
  release:
    types: [ published ]
```

### Docker Images

Docker images are automatically built and published to Docker Hub:

- **Latest**: `your-dockerhub-username/pubg-tracker-bot:latest` (from main branch)
- **Develop**: `your-dockerhub-username/pubg-tracker-bot:develop` (from develop branch)  
- **Versioned**: `your-dockerhub-username/pubg-tracker-bot:v1.0.0` (from auto-tags)

**Running with Docker:**
```bash
# Pull and run latest version
docker run -d --name pubg-tracker --env-file .env your-dockerhub-username/pubg-tracker-bot:latest

# Or run specific version
docker run -d --name pubg-tracker --env-file .env your-dockerhub-username/pubg-tracker-bot:v1.0.1
```

### Development Workflow

1. **Create Feature Branch**
   ```bash
   git checkout -b feature/your-feature
   ```

2. **Make Changes**
   - Code changes follow Black formatting
   - Import sorting with isort
   - Linting passes flake8 checks

3. **Pre-commit Checks**
   ```bash
   pre-commit run --all-files
   ```

4. **Push and Create PR**
   - CI pipeline runs automatically
   - Checks must pass before merge

5. **Deployment**
   - Merge to `main` triggers production build
   - **Auto-tagging**: New version tag created automatically
   - **Automatic Release**: GitHub release generated with assets
   - Docker image automatically published and tagged

### Auto-Tagging System

The project includes an intelligent auto-tagging system that creates version tags on every push to `main`:

- **Default Behavior**: Patch version increment (v1.0.0 → v1.0.1)
- **Minor Release**: Include `[minor]` or `feat:` in commit message (v1.0.0 → v1.1.0)
- **Major Release**: Include `[major]` or `BREAKING CHANGE` in commit message (v1.0.0 → v2.0.0)
- **Skip Tagging**: Include `[skip-tag]` in commit message to skip automatic tagging

**Examples:**
```bash
git commit -m "Fix Discord message formatting"           # → v1.0.1 (patch)
git commit -m "feat: Add new player statistics command"  # → v1.1.0 (minor)
git commit -m "BREAKING CHANGE: Redesign API structure"  # → v2.0.0 (major)
git commit -m "Update documentation [skip-tag]"          # → No tag created
```

For detailed information, see [AUTO_TAGGING.md](AUTO_TAGGING.md).

### Secrets Configuration

For the CI/CD pipeline to work, configure these GitHub repository secrets:

| Secret | Description | Required For |
|--------|-------------|--------------|
| `DOCKERHUB_USERNAME` | Docker Hub username | Docker image publishing |
| `DOCKERHUB_TOKEN` | Docker Hub access token | Docker image publishing |

**To add secrets:**
1. Go to your GitHub repository → Settings → Secrets and variables → Actions
2. Click "New repository secret"
3. Add each secret with the exact names above

**Docker Hub Token Setup:**
1. Log in to [Docker Hub](https://hub.docker.com)
2. Go to Account Settings → Security → Access Tokens
3. Create a new access token with "Read, Write, Delete" permissions
4. Use this token as `DOCKERHUB_TOKEN` (not your password)

### Quality Standards

The project maintains high code quality through:

- **100% Import Coverage**: All modules must import without errors
- **Security First**: Regular dependency and code security scans
- **Consistent Formatting**: Automated code formatting with Black
- **Type Hints**: Gradual typing with mypy support
- **Documentation**: Comprehensive inline and API documentation

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
   - The bot uses a hardcoded rate limit of 10 requests per minute
   - The check interval is hardcoded to 60 seconds
   - Monitor API usage through logs

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