import os
import sys
import asyncio
import signal
import random
import logging
from datetime import datetime, timezone
from dotenv import load_dotenv
import discord
from discord.ext import commands, tasks
import aiohttp

# ──────────────────────────────────────────────
# Logging (resilient to read-only container fs)
# ──────────────────────────────────────────────
_log_handlers: list[logging.Handler] = [logging.StreamHandler()]
try:
    _fh = logging.FileHandler("bot.log")
    _log_handlers.append(_fh)
except OSError:
    # Container / read-only filesystem – skip file logging
    pass

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=_log_handlers,
)
logger = logging.getLogger(__name__)

# ──────────────────────────────────────────────
# Environment
# ──────────────────────────────────────────────
load_dotenv()

token = os.getenv("DISCORD_TOKEN")

if not token:
    logger.critical(
        "DISCORD_TOKEN environment variable not set!\n"
        "  Local:  create .env with DISCORD_TOKEN=your_token_here\n"
        "  Railway/Render: add DISCORD_TOKEN in the Variables / Environment tab"
    )
    sys.exit(1)

# ──────────────────────────────────────────────
# Bot setup
# ──────────────────────────────────────────────
intents = discord.Intents.default()
intents.message_content = True
intents.members = True

bot = commands.Bot(command_prefix="$", intents=intents, help_command=None)

# Shared aiohttp session – avoids creating/leaking connectors
_http_session: aiohttp.ClientSession | None = None


async def get_http_session() -> aiohttp.ClientSession:
    """Lazily create a shared aiohttp session."""
    global _http_session
    if _http_session is None or _http_session.closed:
        _http_session = aiohttp.ClientSession(
            timeout=aiohttp.ClientTimeout(total=10)
        )
    return _http_session


# Status messages for rotating presence
STATUS_MESSAGES = [
    ("playing", "$help for commands"),
    ("watching", "Discord at its finest"),
    ("playing", "with your messages"),
    ("listening", "$help for fun features"),
]

ACTIVITY_TYPE_MAP = {
    "playing": discord.ActivityType.playing,
    "watching": discord.ActivityType.watching,
    "listening": discord.ActivityType.listening,
}


# ══════════════════════════════════════════════
# Non-blocking API helpers (async)
# ══════════════════════════════════════════════
async def fetch_meme() -> str:
    """Fetch a random meme URL.  Returns the image URL or an error string."""
    try:
        session = await get_http_session()
        async with session.get("https://meme-api.com/gimme") as resp:
            if resp.status != 200:
                logger.warning("Meme API returned HTTP %s", resp.status)
                return ""
            data = await resp.json()
            url = data.get("url", "")
            if not url:
                logger.warning("Meme API response missing 'url' key")
            return url
    except asyncio.TimeoutError:
        logger.warning("Meme API request timed out")
        return ""
    except Exception as exc:
        logger.error("Meme API error: %s", exc)
        return ""


async def fetch_joke() -> tuple[str, str]:
    """Fetch a random joke.  Returns (setup, punchline) or ('', error_msg)."""
    try:
        session = await get_http_session()
        async with session.get(
            "https://official-joke-api.appspot.com/random_joke"
        ) as resp:
            if resp.status != 200:
                logger.warning("Joke API returned HTTP %s", resp.status)
                return "", "Could not fetch joke. Try again later!"
            data = await resp.json()
            setup = data.get("setup", "")
            punchline = data.get("punchline", "")
            if not setup or not punchline:
                return "", "Invalid joke data received."
            return setup, punchline
    except asyncio.TimeoutError:
        logger.warning("Joke API request timed out")
        return "", "Request timed out. Try again!"
    except Exception as exc:
        logger.error("Joke API error: %s", exc)
        return "", "Could not fetch joke. Try again later!"


# ══════════════════════════════════════════════
# Events
# ══════════════════════════════════════════════
@bot.event
async def on_ready():
    logger.info("Logged in as %s (ID: %s)", bot.user, bot.user.id)
    if not change_status.is_running():
        change_status.start()
        logger.info("Status rotation task started")


@bot.event
async def on_command_error(ctx: commands.Context, error: commands.CommandError):
    try:
        if isinstance(error, commands.CommandNotFound):
            return  # silently ignore unknown commands to reduce noise

        if isinstance(error, commands.MissingRequiredArgument):
            await ctx.send(f"⚠️ Missing required argument: `{error.param.name}`")
        elif isinstance(error, commands.BadArgument):
            await ctx.send("⚠️ Invalid argument. Check `$help` for usage.")
        elif isinstance(error, commands.CommandOnCooldown):
            await ctx.send(
                f"⏳ Cooldown – try again in **{error.retry_after:.1f}s**."
            )
        elif isinstance(error, commands.MissingPermissions):
            await ctx.send("🔒 You don't have permission to use this command.")
        else:
            # Do NOT expose internal error details to users
            logger.error("Unhandled command error in %s: %s", ctx.command, error)
            await ctx.send("❌ An unexpected error occurred. Please try again later.")
    except discord.Forbidden:
        logger.warning("Cannot send message in %s – missing permissions", ctx.channel)
    except Exception as exc:
        logger.error("Error in error handler: %s", exc)


# ══════════════════════════════════════════════
# Background tasks
# ══════════════════════════════════════════════
@tasks.loop(minutes=5)
async def change_status():
    try:
        kind, text = random.choice(STATUS_MESSAGES)
        activity_type = ACTIVITY_TYPE_MAP.get(kind, discord.ActivityType.playing)
        await bot.change_presence(
            activity=discord.Activity(type=activity_type, name=text)
        )
        logger.debug("Status changed to %s: %s", kind, text)
    except Exception as exc:
        logger.error("Failed to change status: %s", exc)


# ══════════════════════════════════════════════
# Commands
# ══════════════════════════════════════════════
@bot.command(name="ping")
@commands.cooldown(1, 3, commands.BucketType.user)
async def ping(ctx: commands.Context):
    """Show bot latency."""
    latency = round(bot.latency * 1000)
    embed = discord.Embed(
        title="Pong!",
        description=f"Bot latency: **{latency}ms**",
        color=discord.Color.blue(),
    )
    await ctx.send(embed=embed)


@bot.command(name="help")
@commands.cooldown(1, 5, commands.BucketType.user)
async def help_command(ctx: commands.Context):
    """Show all available commands."""
    embed = discord.Embed(
        title="Bot Commands",
        description="Here are all available commands:",
        color=discord.Color.green(),
    )
    embed.add_field(
        name="Fun Commands",
        value=(
            "`$meme` – Get a random meme\n"
            "`$joke` – Get a random joke\n"
            "`$8ball [question]` – Ask the magic 8 ball\n"
            "`$roll [max]` – Roll a random number\n"
            "`$flip` – Flip a coin\n"
            "`$choose <a|b|...>` – Choose between options"
        ),
        inline=False,
    )
    embed.add_field(
        name="User Commands",
        value=(
            "`$avatar [@user]` – Show user's avatar\n"
            "`$userinfo [@user]` – Show user information\n"
            "`$saymyname` – Special message\n"
            "`$time` – Show current time"
        ),
        inline=False,
    )
    embed.add_field(
        name="Bot Commands",
        value=(
            "`$ping` – Check bot latency\n"
            "`$help` – Show this message"
        ),
        inline=False,
    )
    embed.set_footer(text="Prefix: $ | All commands have cooldowns to prevent abuse")
    await ctx.send(embed=embed)
    logger.info("Help command used by %s", ctx.author)


@bot.command(name="meme")
@commands.cooldown(1, 5, commands.BucketType.user)
async def meme(ctx: commands.Context):
    """Get a random meme."""
    async with ctx.typing():
        url = await fetch_meme()
        if not url:
            await ctx.send("😕 Couldn't fetch a meme right now. Try again later!")
            return
        embed = discord.Embed(title="Random Meme", color=discord.Color.random())
        embed.set_image(url=url)
        await ctx.send(embed=embed)
        logger.info("Meme command used by %s", ctx.author)


@bot.command(name="joke")
@commands.cooldown(1, 5, commands.BucketType.user)
async def joke(ctx: commands.Context):
    """Get a random joke."""
    async with ctx.typing():
        setup, punchline = await fetch_joke()
        if not setup:
            # punchline now contains the error message
            await ctx.send(f"😕 {punchline}")
            return
        embed = discord.Embed(
            title="Random Joke",
            description=f"**{setup}**\n\n*{punchline}*",
            color=discord.Color.gold(),
        )
        await ctx.send(embed=embed)
        logger.info("Joke command used by %s", ctx.author)


@bot.command(name="8ball")
@commands.cooldown(1, 3, commands.BucketType.user)
async def eight_ball(ctx: commands.Context, *, question: str | None = None):
    """Ask the magic 8 ball."""
    if not question:
        await ctx.send("Ask a question!  Usage: `$8ball <your question>`")
        return

    responses = [
        "Yes, definitely!",
        "No, absolutely not!",
        "Maybe...",
        "Ask again later.",
        "Don't count on it.",
        "It is certain.",
        "Outlook good.",
        "Very doubtful.",
        "Without a doubt.",
        "My sources say no.",
    ]
    answer = random.choice(responses)
    embed = discord.Embed(
        title="🎱 Magic 8 Ball",
        description=f"**Q:** {question}\n**A:** {answer}",
        color=discord.Color.purple(),
    )
    await ctx.send(embed=embed)
    logger.info("8ball command used by %s", ctx.author)


@bot.command(name="roll")
@commands.cooldown(1, 3, commands.BucketType.user)
async def roll(ctx: commands.Context, max_num: int = 100):
    """Roll a random number (1 to max, default 100)."""
    if max_num < 1:
        await ctx.send("Number must be at least 1!")
        return
    result = random.randint(1, max_num)
    embed = discord.Embed(
        title="🎲 Dice Roll",
        description=f"Rolled: **{result}** (1–{max_num})",
        color=discord.Color.red(),
    )
    await ctx.send(embed=embed)
    logger.info("Roll command used by %s (1-%d)", ctx.author, max_num)


@bot.command(name="flip")
@commands.cooldown(1, 3, commands.BucketType.user)
async def flip(ctx: commands.Context):
    """Flip a coin."""
    result = random.choice(["Heads", "Tails"])
    emoji = "👑" if result == "Heads" else "🪙"
    embed = discord.Embed(
        title="Coin Flip",
        description=f"{emoji} **{result}**",
        color=discord.Color.blue(),
    )
    await ctx.send(embed=embed)
    logger.info("Flip command used by %s", ctx.author)


@bot.command(name="avatar")
@commands.cooldown(1, 5, commands.BucketType.user)
async def avatar(ctx: commands.Context, member: discord.Member | None = None):
    """Show a user's avatar."""
    member = member or ctx.author
    embed = discord.Embed(
        title=f"{member.display_name}'s Avatar", color=discord.Color.blurple()
    )
    embed.set_image(url=member.display_avatar.url)
    embed.set_footer(text=f"Requested by {ctx.author.name}")
    await ctx.send(embed=embed)
    logger.info("Avatar command used by %s for %s", ctx.author, member)


@bot.command(name="userinfo")
@commands.cooldown(1, 5, commands.BucketType.user)
async def userinfo(ctx: commands.Context, member: discord.Member | None = None):
    """Show user information."""
    member = member or ctx.author

    embed = discord.Embed(
        title=f"User Info: {member.display_name}",
        description=f"<@{member.id}>",
        color=discord.Color.blurple(),
    )
    embed.add_field(name="Username", value=member.name, inline=True)
    embed.add_field(name="ID", value=str(member.id), inline=True)
    embed.add_field(
        name="Created",
        value=member.created_at.strftime("%Y-%m-%d"),
        inline=True,
    )
    if member.joined_at:
        embed.add_field(
            name="Joined Server",
            value=member.joined_at.strftime("%Y-%m-%d"),
            inline=True,
        )
    else:
        embed.add_field(name="Joined Server", value="Unknown", inline=True)

    embed.add_field(
        name="Status", value=str(member.status) if member.status else "Unknown", inline=True
    )
    embed.add_field(name="Is Bot", value="Yes" if member.bot else "No", inline=True)
    embed.set_thumbnail(url=member.display_avatar.url)
    await ctx.send(embed=embed)
    logger.info("Userinfo command used by %s for %s", ctx.author, member)


@bot.command(name="saymyname")
@commands.cooldown(1, 5, commands.BucketType.user)
async def saymyname(ctx: commands.Context):
    """Special message."""
    await ctx.send("Thank you, my creator Sarnick, for infusing life in me!")
    logger.info("Saymyname command used by %s", ctx.author)


@bot.command(name="time")
@commands.cooldown(1, 3, commands.BucketType.user)
async def current_time(ctx: commands.Context):
    """Show current UTC time."""
    now = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")
    embed = discord.Embed(
        title="Current Time",
        description=f"`{now}`",
        color=discord.Color.dark_blue(),
    )
    await ctx.send(embed=embed)
    logger.info("Time command used by %s", ctx.author)


@bot.command(name="choose")
@commands.cooldown(1, 3, commands.BucketType.user)
async def choose(ctx: commands.Context, *, choices: str):
    """Choose between options separated by |.  Example: $choose Pizza|Burger|Sushi"""
    if "|" not in choices:
        await ctx.send(
            "Separate options with `|`.\nExample: `$choose Pizza|Burger|Sushi`"
        )
        return

    options = [opt.strip() for opt in choices.split("|") if opt.strip()]

    if len(options) < 2:
        await ctx.send("You need at least 2 non-empty options!")
        return

    pick = random.choice(options)
    embed = discord.Embed(
        title="Choice Maker",
        description=f"I choose: **{pick}**",
        color=discord.Color.green(),
    )
    await ctx.send(embed=embed)
    logger.info("Choose command used by %s", ctx.author)


# ══════════════════════════════════════════════
# Main entry point with graceful shutdown
# ══════════════════════════════════════════════
async def main():
    async with bot:
        try:
            await bot.start(token)
        except discord.LoginFailure:
            logger.critical("Invalid Discord token – check DISCORD_TOKEN")
        except discord.PrivilegedIntentsRequired:
            logger.critical(
                "Required intents not enabled – enable Message Content Intent "
                "in the Discord Developer Portal"
            )
        finally:
            # Clean up aiohttp session
            global _http_session
            if _http_session and not _http_session.closed:
                await _http_session.close()
                logger.info("HTTP session closed")


def _handle_signal(sig, _frame):
    """Handle SIGTERM / SIGINT for graceful shutdown on deployment platforms."""
    logger.info("Received signal %s – shutting down…", sig)
    raise SystemExit(0)


if __name__ == "__main__":
    # Register signal handlers for Railway / Docker / systemd
    for sig in (signal.SIGTERM, signal.SIGINT):
        signal.signal(sig, _handle_signal)

    try:
        logger.info("Starting Discord bot…")
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("Bot stopped by user")
    except SystemExit:
        logger.info("Bot stopped by signal")
    except Exception as exc:
        logger.critical("Unrecoverable error: %s", exc)
        sys.exit(1)
