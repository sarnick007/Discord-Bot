import os
import asyncio
import random
import logging
from datetime import datetime
from dotenv import load_dotenv
import discord
from discord.ext import commands, tasks
import requests

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('bot.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Load from .env file if it exists (local development)
load_dotenv()

# Get token from environment (Railway) or .env (local)
token = os.getenv('DISCORD_TOKEN')

# Validate token exists
if not token:
    print("ERROR: DISCORD_TOKEN environment variable not set!")
    print("\nFor local development:")
    print("  Create .env file with: DISCORD_TOKEN=your_token_here")
    print("\nFor Railway deployment:")
    print("  1. Go to Railway dashboard")
    print("  2. Click your project")
    print("  3. Go to 'Variables' tab")
    print("  4. Add: DISCORD_TOKEN = your_token_here")
    exit(1)

# Bot setup with intents
intents = discord.Intents.default()
intents.message_content = True
intents.members = True

bot = commands.Bot(command_prefix='$', intents=intents, help_command=None)

# Status messages for rotating presence
status_messages = [
    "$help for commands",
    "Discord at its finest",
    "with your messages",
    "👾 for fun features"
]

# ============ API Functions ============
def get_meme():
    """Fetch a random meme from API"""
    try:
        response = requests.get('https://meme-api.com/gimme', timeout=5)
        response.raise_for_status()
        json_data = response.json()
        return json_data.get('url', 'Could not fetch meme')
    except requests.Timeout:
        logger.warning("Meme API request timed out")
        return 'Request timed out. Try again!'
    except requests.RequestException as e:
        logger.error(f"Meme API error: {e}")
        return 'Failed to fetch meme. Try again later!'
    except ValueError as e:
        logger.error(f"Meme API JSON decode error: {e}")
        return 'Invalid response from API.'

def get_joke():
    """Fetch a random joke from API"""
    try:
        response = requests.get('https://official-joke-api.appspot.com/random_joke', timeout=5)
        response.raise_for_status()
        joke_data = response.json()
        return f"{joke_data['setup']}\n{joke_data['punchline']}"
    except requests.Timeout:
        logger.warning("Joke API request timed out")
        return "Request timed out. Try again!"
    except requests.RequestException as e:
        logger.error(f"Joke API error: {e}")
        return "Could not fetch joke. Try again later!"
    except (ValueError, KeyError) as e:
        logger.error(f"Joke API parsing error: {e}")
        return "Invalid response from API."

# ============ Events ============
@bot.event
async def on_ready():
    """Called when bot is ready"""
    logger.info(f'Successfully logged on as {bot.user} (ID: {bot.user.id})')
    if not change_status.is_running():
        change_status.start()
        logger.info('Status rotation task started')
    
@bot.event
async def on_command_error(ctx, error):
    """Handle command errors"""
    try:
        if isinstance(error, commands.CommandNotFound):
            await ctx.send("Command not found! Type `$help` for available commands.")
        elif isinstance(error, commands.MissingRequiredArgument):
            await ctx.send(f"Missing argument: {error.param.name}")
        elif isinstance(error, commands.CommandOnCooldown):
            await ctx.send(f"Command is on cooldown. Try again in {error.retry_after:.1f} seconds.")
        elif isinstance(error, commands.MissingPermissions):
            await ctx.send("You don't have permission to use this command.")
        else:
            logger.error(f"Unhandled command error: {error}")
            await ctx.send(f"An error occurred: {str(error)[:100]}")
    except discord.Forbidden:
        logger.warning(f"Cannot send message in {ctx.channel} - missing permissions")
    except Exception as e:
        logger.error(f"Error in error handler: {e}")

# ============ Background Tasks ============
@tasks.loop(minutes=5)
async def change_status():
    """Rotate bot status every 5 minutes"""
    try:
        status = random.choice(status_messages)
        await bot.change_presence(
            activity=discord.Activity(
                type=discord.ActivityType.playing,
                name=status
            )
        )
        logger.debug(f"Status changed to: {status}")
    except Exception as e:
        logger.error(f"Failed to change status: {e}")

# ============ Commands ============
@bot.command(name='ping')
@commands.cooldown(1, 3, commands.BucketType.user)
async def ping(ctx):
    """Show bot latency"""
    latency = round(bot.latency * 1000)
    embed = discord.Embed(
        title="Pong!",
        description=f"Bot latency: **{latency}ms**",
        color=discord.Color.blue()
    )
    await ctx.send(embed=embed)

@bot.command(name='help')
@commands.cooldown(1, 5, commands.BucketType.user)
async def help_command(ctx):
    """Show all available commands"""
    embed = discord.Embed(
        title="Bot Commands",
        description="Here are all available commands:",
        color=discord.Color.green()
    )
    embed.add_field(name="Fun Commands", value=
        "`$meme` - Get a random meme\n"
        "`$joke` - Get a random joke\n"
        "`$8ball [question]` - Ask the magic 8 ball\n"
        "`$roll [max]` - Roll a random number\n"
        "`$flip` - Flip a coin\n"
        "`$choose <option1|option2|...>` - Choose between options", inline=False)
    embed.add_field(name="User Commands", value=
        "`$avatar [@user]` - Show user's avatar\n"
        "`$userinfo [@user]` - Show user information\n"
        "`$saymyname` - Special message\n"
        "`$time` - Show current time", inline=False)
    embed.add_field(name="Bot Commands", value=
        "`$ping` - Check bot latency\n"
        "`$help` - Show this message", inline=False)
    embed.set_footer(text="Prefix: $ | All commands have cooldowns to prevent abuse")
    await ctx.send(embed=embed)
    logger.info(f"Help command used by {ctx.author}")

@bot.command(name='meme')
@commands.cooldown(1, 5, commands.BucketType.user)
async def meme(ctx):
    """Get a random meme"""
    async with ctx.typing():
        meme_url = get_meme()
        embed = discord.Embed(title="Random Meme", color=discord.Color.random())
        embed.set_image(url=meme_url)
        await ctx.send(embed=embed)
        logger.info(f"Meme command used by {ctx.author}")

@bot.command(name='joke')
@commands.cooldown(1, 5, commands.BucketType.user)
async def joke(ctx):
    """Get a random joke"""
    async with ctx.typing():
        joke_text = get_joke()
        embed = discord.Embed(title="Random Joke", description=joke_text, color=discord.Color.gold())
        await ctx.send(embed=embed)
        logger.info(f"Joke command used by {ctx.author}")

@bot.command(name='8ball')
@commands.cooldown(1, 3, commands.BucketType.user)
async def eight_ball(ctx, *, question=None):
    """Ask the magic 8 ball"""
    if not question:
        await ctx.send("Please ask a question! Usage: `$8ball [your question]`")
        return
    
    responses = [
        "Yes, definitely!",
        "No, absolutely not!",
        "Maybe...",
        "Ask again later",
        "Don't count on it",
        "It is certain",
        "Outlook good",
        "Very doubtful"
    ]
    answer = random.choice(responses)
    embed = discord.Embed(
        title="Magic 8 Ball",
        description=f"**Q:** {question}\n**A:** {answer}",
        color=discord.Color.purple()
    )
    await ctx.send(embed=embed)
    logger.info(f"8ball command used by {ctx.author}")

@bot.command(name='roll')
@commands.cooldown(1, 3, commands.BucketType.user)
async def roll(ctx, max_num: int = 100):
    """Roll a random number"""
    if max_num < 1:
        await ctx.send("Number must be at least 1!")
        return
    
    result = random.randint(1, max_num)
    embed = discord.Embed(
        title="Dice Roll",
        description=f"Rolled: **{result}** (1-{max_num})",
        color=discord.Color.red()
    )
    await ctx.send(embed=embed)
    logger.info(f"Roll command used by {ctx.author} (1-{max_num})")

@bot.command(name='flip')
@commands.cooldown(1, 3, commands.BucketType.user)
async def flip(ctx):
    """Flip a coin"""
    result = random.choice(['Heads', 'Tails'])
    emoji = '👑' if result == 'Heads' else '🪙'
    embed = discord.Embed(
        title="Coin Flip",
        description=f"{emoji} **{result}**",
        color=discord.Color.blue()
    )
    await ctx.send(embed=embed)
    logger.info(f"Flip command used by {ctx.author}")

@bot.command(name='avatar')
@commands.cooldown(1, 5, commands.BucketType.user)
async def avatar(ctx, member: discord.Member = None):
    """Show user's avatar"""
    member = member or ctx.author
    embed = discord.Embed(title=f"{member.name}'s Avatar", color=discord.Color.blurple())
    embed.set_image(url=member.display_avatar.url)
    embed.set_footer(text=f"Requested by {ctx.author.name}")
    await ctx.send(embed=embed)
    logger.info(f"Avatar command used by {ctx.author} for {member}")

@bot.command(name='userinfo')
@commands.cooldown(1, 5, commands.BucketType.user)
async def userinfo(ctx, member: discord.Member = None):
    """Show user information"""
    member = member or ctx.author
    embed = discord.Embed(
        title=f"User Info: {member.name}",
        description=f"<@{member.id}>",
        color=discord.Color.blurple()
    )
    embed.add_field(name="Username", value=member.name, inline=True)
    embed.add_field(name="ID", value=member.id, inline=True)
    embed.add_field(name="Created", value=member.created_at.strftime("%Y-%m-%d"), inline=True)
    embed.add_field(name="Joined Server", value=member.joined_at.strftime("%Y-%m-%d"), inline=True)
    embed.add_field(name="Status", value=str(member.status), inline=True)
    embed.add_field(name="Is Bot", value="Yes" if member.bot else "No", inline=True)
    embed.set_thumbnail(url=member.display_avatar.url)
    await ctx.send(embed=embed)
    logger.info(f"Userinfo command used by {ctx.author} for {member}")

@bot.command(name='saymyname')
@commands.cooldown(1, 5, commands.BucketType.user)
async def saymyname(ctx):
    """Special message"""
    await ctx.send('Thank you, my creator Sarnick, for infusing life in me!')
    logger.info(f"Saymyname command used by {ctx.author}")

@bot.command(name='time')
@commands.cooldown(1, 3, commands.BucketType.user)
async def current_time(ctx):
    """Show current time"""
    current = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    embed = discord.Embed(
        title="Current Time",
        description=f"`{current}`",
        color=discord.Color.dark_blue()
    )
    await ctx.send(embed=embed)
    logger.info(f"Time command used by {ctx.author}")

@bot.command(name='choose')
@commands.cooldown(1, 3, commands.BucketType.user)
async def choose(ctx, *, choices):
    """Choose between multiple options (use | to separate)"""
    if '|' not in choices:
        await ctx.send("Please provide multiple options separated by `|`\nExample: `$choose option1|option2|option3`")
        return
    
    options = [option.strip() for option in choices.split('|')]
    options = [opt for opt in options if opt]  # Remove empty options
    
    if len(options) < 2:
        await ctx.send("You need at least 2 options!")
        return
    
    choice = random.choice(options)
    embed = discord.Embed(
        title="Choice Maker",
        description=f"I choose: **{choice}**",
        color=discord.Color.green()
    )
    await ctx.send(embed=embed)
    logger.info(f"Choose command used by {ctx.author}")

async def main():
    """Main function with error handling"""
    async with bot:
        try:
            await bot.start(token)
        except discord.LoginFailure:
            logger.critical("Invalid Discord token provided")
        except discord.PrivilegedIntentsRequired:
            logger.critical("Required intents not enabled in Discord Developer Portal")
        except Exception as e:
            logger.critical(f"Critical error during bot startup: {e}")

if __name__ == "__main__":
    try:
        logger.info("Starting Discord bot...")
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("Bot stopped by user (KeyboardInterrupt)")
    except Exception as e:
        logger.critical(f"Unrecoverable error: {e}")


