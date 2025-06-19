import discord
from discord.ext import commands
from typing import List, Dict, Any, Optional
import pytz
from datetime import datetime
from config.settings import settings
from services.storage_service import storage_service
from services.pubg_api_service import pubg_api_service
from models.player import Player
from utils.mappings import MAP_NAMES, GAME_MODES, generate_match_color
# from pubg_types.telemetry_types import ProcessedTelemetryEvent

class DiscordBotService(commands.Bot):
    def __init__(self):
        intents = discord.Intents.default()
        intents.message_content = True
        
        super().__init__(
            command_prefix='/',
            intents=intents,
            case_insensitive=True
        )
        
        self.channel_id = settings.DISCORD_CHANNEL_ID
        self.target_channel: Optional[discord.TextChannel] = None
        
    async def setup_hook(self):
        """Setup hook called when bot is ready"""
        print(f"Bot logged in as {self.user}")
        
        # Get all channels
        channels = await self.fetch_channels()
        for channel in channels:
            print(f"Channel: {channel.name} - {channel.id}")
        
        # Get target channel
        self.target_channel = self.get_channel(self.channel_id)
        if not self.target_channel:
            print(f"Warning: Could not find channel with ID {self.channel_id}")
        
        # Sync slash commands
        try:
            synced = await self.tree.sync()
            print(f"Synced {len(synced)} command(s)")
        except Exception as e:
            print(f"Failed to sync commands: {e}")
    
    async def send_match_summary(
        self, 
        match_data: Dict[str, Any], 
        squad_members: List[Dict[str, Any]],
        telemetry_events: List[Dict[str, Any]]
    ):
        """Send match summary to Discord channel"""
        if not self.target_channel:
            print("No target channel configured")
            return
        
        try:
            # Create main match embed
            main_embed = self._create_match_embed(match_data, squad_members)
            
            # Create player embeds
            player_embeds = []
            for player in squad_members:
                player_embed = self._create_player_embed(
                    player, 
                    match_data["match_id"], 
                    telemetry_events
                )
                player_embeds.append(player_embed)
            
            # Send embeds (Discord has a limit of 10 embeds per message)
            all_embeds = [main_embed] + player_embeds
            
            # Split into chunks if needed
            embed_chunks = [all_embeds[i:i+10] for i in range(0, len(all_embeds), 10)]
            
            for chunk in embed_chunks:
                await self.target_channel.send(embeds=chunk)
                
            print(f"Sent match summary for {match_data['match_id']}")
            
        except Exception as e:
            print(f"Failed to send match summary: {e}")
    
    def _create_match_embed(self, match_data: Dict[str, Any], squad_members: List[Dict[str, Any]]) -> discord.Embed:
        """Create the main match summary embed"""
        # Convert timestamp to South African timezone
        sa_tz = pytz.timezone('Africa/Johannesburg')
        try:
            utc_time = datetime.fromisoformat(match_data["created_at"].replace('Z', '+00:00'))
            sa_time = utc_time.astimezone(sa_tz)
            formatted_time = sa_time.strftime("%Y/%m/%d %H:%M")
        except:
            formatted_time = "Unknown"
        
        # Get map and game mode display names
        map_display = MAP_NAMES.get(match_data["map_name"], match_data["map_name"])
        mode_display = GAME_MODES.get(match_data["game_mode"], match_data["game_mode"])
        
        # Calculate team stats
        placement = squad_members[0].get("stats", {}).get("win_place", 0) if squad_members else 0
        placement_text = f"#{placement}" if placement > 0 else "N/A"
        squad_size = len(squad_members)
        
        total_kills = sum(member.get("stats", {}).get("kills", 0) for member in squad_members)
        total_knocks = sum(member.get("stats", {}).get("dbnos", 0) for member in squad_members)
        total_damage = sum(member.get("stats", {}).get("damage_dealt", 0) for member in squad_members)
        
        # Create description
        description = f"""⏰ **{formatted_time}**
🗺️ **{map_display}** • {mode_display}

**Team Performance**
🏆 Placement: **{placement_text}**
👥 Squad Size: **{squad_size} players**

**Combat Summary**
⚔️ Total Kills: **{total_kills}**
🔻 Total Knocks: **{total_knocks}**
💥 Total Damage: **{round(total_damage)}**"""
        
        # Generate color based on match ID
        color = generate_match_color(match_data["match_id"])
        
        embed = discord.Embed(
            title="🎮 PUBG Match Summary",
            description=description,
            color=color,
            timestamp=datetime.fromisoformat(match_data["created_at"].replace('Z', '+00:00'))
        )
        
        embed.set_footer(text=f"PUBG Match Tracker - {match_data['match_id']}")
        
        return embed
    
    def _create_player_embed(
        self, 
        player_data: Dict[str, Any], 
        match_id: str,
        telemetry_events: List[Dict[str, Any]]
    ) -> discord.Embed:
        """Create a player-specific embed"""
        stats = player_data.get("stats", {})
        player_name = player_data.get("name", "Unknown")
        
        # Basic stats
        kills = stats.get("kills", 0)
        headshot_kills = stats.get("headshot_kills", 0)
        knocks = stats.get("dbnos", 0)
        damage = round(stats.get("damage_dealt", 0))
        assists = stats.get("assists", 0)
        revives = stats.get("revives", 0)
        longest_kill = round(stats.get("longest_kill", 0))
        time_survived = round(stats.get("time_survived", 0) / 60)  # Convert to minutes
        walk_distance = round(stats.get("walk_distance", 0) / 1000, 1)  # Convert to km
        
        # Calculate headshot percentage
        if kills > 0:
            headshot_percentage = round((headshot_kills / kills) * 100)
        else:
            headshot_percentage = 0
        
        # Build description
        description = f"""⚔️ Kills: {kills} ({headshot_kills} headshots)
🔻 Knocks: {knocks}
💥 Damage: {damage} ({assists} assists)
🎯 Headshot %: {headshot_percentage}%
⏰ Survival: {time_survived}min
📏 Longest Kill: {longest_kill}m
👣 Distance: {walk_distance}km"""
        
        # Add revives if > 0
        if revives > 0:
            description += f"\n🚑 Revives: {revives}"
        
        # Add 2D Replay link
        description += f"\n🎯 [2D Replay](https://pubg.sh/{player_name}/steam/{match_id})"
        
        # Add telemetry events
        player_events = [
            event for event in telemetry_events 
            if event['actor'] == player_name or event['target'] == player_name
        ]
        
        if player_events:
            description += "\n*** KILLS & DBNOs ***"
            for event in player_events:
                if event['actor'] == player_name:  # Player performed the action
                    if event['event_type'] == 'kill':
                        icon = "⚔️ Killed"
                    else:
                        icon = "🔻 Knocked"
                    
                    target_link = f"[{event['target']}](https://pubg.op.gg/user/{event['target']})"
                    description += f"\n`{event['match_time']}` {icon} - {target_link} ({event['weapon']}, {round(event['distance'])}m)"
        
        embed = discord.Embed(
            title=f"Player: {player_name}",
            description=description,
            color=0x2f3136  # Dark gray
        )
        
        return embed
    
    async def send_error_embed(self, interaction: discord.Interaction, title: str, description: str):
        """Send an error embed"""
        embed = discord.Embed(
            title=title,
            description=description,
            color=0xff0000  # Red
        )
        
        try:
            await interaction.response.send_message(embed=embed, ephemeral=True)
        except:
            await interaction.followup.send(embed=embed, ephemeral=True)
    
    async def send_success_embed(self, interaction: discord.Interaction, title: str, description: str):
        """Send a success embed"""
        embed = discord.Embed(
            title=title,
            description=description,
            color=0x00ff00  # Green
        )
        
        try:
            await interaction.response.send_message(embed=embed, ephemeral=True)
        except:
            await interaction.followup.send(embed=embed, ephemeral=True)

# Create bot instance
bot = DiscordBotService()

# Slash commands
@bot.tree.command(name="add", description="Add a player to PUBG monitoring")
async def add_player(interaction: discord.Interaction, playername: str):
    """Add a player to monitoring"""
    try:
        # Check if player already exists
        existing_player = await storage_service.get_player_by_name(playername)
        if existing_player:
            await bot.send_error_embed(
                interaction, 
                "Player Already Monitored", 
                f"Player {playername} is already being monitored."
            )
            return
        
        # Fetch player data from PUBG API
        players = await pubg_api_service.get_players_by_names([playername])
        if not players:
            await bot.send_error_embed(
                interaction,
                "Player Not Found",
                f"Could not find player {playername} on PUBG servers."
            )
            return
        
        pubg_player = players[0]
        
        # Create and save player
        player = Player(pubg_player['id'], pubg_player['name'], pubg_player['shard_id'])
        player.update_from_api({"attributes": {
            "patchVersion": pubg_player['patch_version'],
            "titleId": pubg_player['title_id'],
            "createdAt": pubg_player['created_at'],
            "updatedAt": pubg_player['updated_at']
        }})
        
        success = await storage_service.add_player(player)
        if success:
            await bot.send_success_embed(
                interaction,
                "Player Added",
                f"Successfully added {playername} to monitoring."
            )
        else:
            await bot.send_error_embed(
                interaction,
                "Database Error",
                f"Failed to add player {playername} to database."
            )
    
    except Exception as e:
        print(f"Error in add_player command: {e}")
        await bot.send_error_embed(
            interaction,
            "Error",
            "An error occurred while adding the player."
        )

@bot.tree.command(name="remove", description="Remove a player from PUBG monitoring")
async def remove_player(interaction: discord.Interaction, playername: str):
    """Remove a player from monitoring"""
    try:
        success = await storage_service.remove_player(playername)
        if success:
            await bot.send_success_embed(
                interaction,
                "Player Removed",
                f"Successfully removed {playername} from monitoring."
            )
        else:
            await bot.send_error_embed(
                interaction,
                "Player Not Found",
                f"Player {playername} is not being monitored."
            )
    
    except Exception as e:
        print(f"Error in remove_player command: {e}")
        await bot.send_error_embed(
            interaction,
            "Error",
            "An error occurred while removing the player."
        )

@bot.tree.command(name="list", description="List all monitored PUBG players")
async def list_players(interaction: discord.Interaction):
    """List all monitored players"""
    try:
        players = await storage_service.get_all_players()
        
        if not players:
            await bot.send_error_embed(
                interaction,
                "No Players",
                "No players are currently being monitored."
            )
            return
        
        player_names = [player.name for player in players]
        description = "**Monitored Players:**\n" + "\n".join([f"• {name}" for name in player_names])
        
        embed = discord.Embed(
            title="PUBG Player Monitoring",
            description=description,
            color=0x0099ff  # Blue
        )
        
        await interaction.response.send_message(embed=embed, ephemeral=True)
    
    except Exception as e:
        print(f"Error in list_players command: {e}")
        await bot.send_error_embed(
            interaction,
            "Error",
            "An error occurred while fetching the player list."
        ) 