import os
import sys
import asyncio
import signal
import random
import logging
import html
import re
from urllib.parse import urlparse
from datetime import datetime, timezone
from dotenv import load_dotenv
import discord
from discord.ext import commands, tasks
import aiohttp

# Load local development settings before configuring logging; hosted environment
# variables take precedence because python-dotenv does not override by default.
load_dotenv()

# ──────────────────────────────────────────────
# Logging: console by default, optional file for local/VPS deployments
# ──────────────────────────────────────────────
_log_handlers: list[logging.Handler] = [logging.StreamHandler(sys.stdout)]
_log_file = os.getenv("LOG_FILE")
_log_file_error: OSError | None = None
if _log_file:
    try:
        _log_handlers.append(logging.FileHandler(_log_file, encoding="utf-8"))
    except OSError as exc:
        _log_file_error = exc

_log_level_name = os.getenv("LOG_LEVEL", "INFO").upper()
_log_level = getattr(logging, _log_level_name, logging.INFO)
logging.basicConfig(
    level=_log_level,
    format="%(asctime)s - %(levelname)s - %(name)s - %(message)s",
    handlers=_log_handlers,
)
logger = logging.getLogger(__name__)
if _log_file_error:
    logger.warning("Could not open LOG_FILE=%r; using console logging only: %s", _log_file, _log_file_error)

# ──────────────────────────────────────────────
# Environment
# ──────────────────────────────────────────────
def get_discord_token() -> str:
    """Return the configured bot token, or fail with platform-neutral guidance."""
    token = os.getenv("DISCORD_TOKEN", "").strip()
    if not token:
        raise RuntimeError(
            "DISCORD_TOKEN is not configured. Set it as an environment variable "
            "or add it to a local .env file. Never commit the real token."
        )
    return token

# ──────────────────────────────────────────────
# Bot setup
# ──────────────────────────────────────────────
intents = discord.Intents.default()
# Prefix commands read message content, so enable this in code and in the
# Discord Developer Portal. Other privileged intents are opt-in only.
intents.message_content = True
intents.members = os.getenv("ENABLE_MEMBERS_INTENT", "false").strip().lower() == "true"
intents.presences = os.getenv("ENABLE_PRESENCE_INTENT", "false").strip().lower() == "true"

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
# Keep the default feed focused on general-audience communities. A requested
# subreddit can also be supplied to the meme command; posts marked NSFW are skipped.
DEFAULT_MEME_SUBREDDITS = (
    "memes",
    "ProgrammerHumor",
    "wholesomememes",
    "me_irl",
    "PrequelMemes",
)
SUBREDDIT_PATTERN = re.compile(r"^[A-Za-z0-9_]{2,21}$")
IMAGE_EXTENSIONS = {".jpg", ".jpeg", ".png", ".gif", ".webp"}


def _is_direct_image_url(url: str) -> bool:
    """Return True for HTTPS URLs with a common direct-image extension."""
    try:
        parsed = urlparse(url)
        return (
            parsed.scheme == "https"
            and bool(parsed.netloc)
            and parsed.path.lower().endswith(tuple(IMAGE_EXTENSIONS))
        )
    except (TypeError, ValueError):
        return False


def _reddit_image_url(post: dict) -> str:
    """Get a direct image URL from a Reddit post, ignoring video/link posts."""
    direct_url = post.get("url_overridden_by_dest") or post.get("url") or ""
    if _is_direct_image_url(direct_url):
        return direct_url

    # Reddit preview URLs may include HTML-escaped query parameters.
    images = post.get("preview", {}).get("images", [])
    if images:
        source_url = html.unescape(images[0].get("source", {}).get("url", ""))
        if _is_direct_image_url(source_url):
            return source_url
    return ""


async def _fetch_reddit_meme(session: aiohttp.ClientSession, subreddit: str | None) -> dict | None:
    """Fetch a random image post from Reddit's public listing JSON."""
    feed = subreddit or "+".join(DEFAULT_MEME_SUBREDDITS)
    url = f"https://www.reddit.com/r/{feed}/hot.json"
    headers = {"User-Agent": "ShrekDiscordBot/1.0 (meme command)"}
    async with session.get(
        url,
        params={"limit": "50", "raw_json": "1"},
        headers=headers,
    ) as resp:
        if resp.status != 200:
            logger.warning("Reddit listing returned HTTP %s for r/%s", resp.status, feed)
            return None
        data = await resp.json(content_type=None)

    children = data.get("data", {}).get("children", [])
    candidates = []
    for child in children:
        post = child.get("data", {})
        if post.get("over_18") or post.get("is_video") or post.get("stickied"):
            continue
        image_url = _reddit_image_url(post)
        if not image_url:
            continue
        candidates.append({
            "title": post.get("title") or "Reddit meme",
            "url": image_url,
            "post_url": "https://www.reddit.com" + post.get("permalink", ""),
            "subreddit": post.get("subreddit") or feed,
            "source": "Reddit",
        })
    return random.choice(candidates) if candidates else None


async def _fetch_meme_api(session: aiohttp.ClientSession, subreddit: str | None) -> dict | None:
    """Fallback to meme-api.com if Reddit's listing is unavailable."""
    endpoint = "https://meme-api.com/gimme"
    if subreddit:
        endpoint += f"/{subreddit}"
    async with session.get(endpoint) as resp:
        if resp.status != 200:
            logger.warning("Meme API returned HTTP %s", resp.status)
            return None
        data = await resp.json(content_type=None)

    image_url = data.get("url", "")
    if data.get("nsfw") or not _is_direct_image_url(image_url):
        logger.warning("Meme API returned NSFW content or a non-direct image")
        return None
    return {
        "title": data.get("title") or "Random meme",
        "url": image_url,
        "post_url": data.get("postLink") or image_url,
        "subreddit": data.get("subreddit") or subreddit or "memes",
        "source": "meme-api.com",
    }


async def fetch_meme(subreddit: str | None = None) -> dict | None:
    """Fetch a general-audience meme from Reddit, with a public API fallback.

    Returns title, direct image URL, post URL, subreddit and source; None if
    no suitable image is available. This skips video posts and NSFW items.
    """
    normalized_subreddit = None
    if subreddit:
        normalized_subreddit = subreddit.removeprefix("r/").strip()
        if not SUBREDDIT_PATTERN.fullmatch(normalized_subreddit):
            logger.warning("Rejected invalid subreddit argument")
            return None

    try:
        session = await get_http_session()
        try:
            result = await _fetch_reddit_meme(session, normalized_subreddit)
            if result:
                return result
        except (aiohttp.ClientError, asyncio.TimeoutError, ValueError) as exc:
            logger.warning("Reddit fetch failed: %s", exc)

        try:
            result = await _fetch_meme_api(session, normalized_subreddit)
            if result:
                return result
        except (aiohttp.ClientError, asyncio.TimeoutError, ValueError) as exc:
            logger.warning("Meme API fallback failed: %s", exc)
    except Exception as exc:
        logger.error("Meme service error: %s", exc)
    return None


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
            "`$meme [subreddit]` – Get a random Reddit meme\n"
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
async def meme(ctx: commands.Context, subreddit: str | None = None):
    """Get a random general-audience Reddit meme, optionally from one subreddit."""
    async with ctx.typing():
        result = await fetch_meme(subreddit)
        if not result:
            await ctx.send(
                "😕 Couldn't find a suitable image meme right now. "
                "Try the meme command again later."
            )
            return
        title = str(result["title"])[:256]
        embed = discord.Embed(
            title=title or "Random Meme",
            url=result.get("post_url") or result["url"],
            color=discord.Color.random(),
        )
        embed.set_image(url=result["url"])
        embed.set_footer(
            text=f"Source: {result.get('source', 'Reddit')} • r/{result.get('subreddit', 'memes')}"
        )
        await ctx.send(embed=embed)
        logger.info("Meme command used by %s (source=%s)", ctx.author, result.get("source"))


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

    status_value = (
        str(member.status)
        if intents.presences
        else "Not enabled (set ENABLE_PRESENCE_INTENT=true to opt in)"
    )
    embed.add_field(name="Status", value=status_value, inline=True)
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
    try:
        token = get_discord_token()
    except RuntimeError as exc:
        logger.critical("%s", exc)
        raise SystemExit(1)

    async with bot:
        try:
            await bot.start(token)
        except discord.LoginFailure:
            logger.critical("Invalid Discord token – check DISCORD_TOKEN")
            raise SystemExit(1)
        except discord.PrivilegedIntentsRequired:
            logger.critical(
                "A required privileged intent is disabled. This prefix-command bot "
                "requires Message Content Intent to be enabled both in bot.py and in "
                "the Discord Developer Portal. Only enable Server Members or Presence "
                "Intent if you explicitly set ENABLE_MEMBERS_INTENT=true or "
                "ENABLE_PRESENCE_INTENT=true."
            )
            raise SystemExit(1)
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
    except SystemExit as exc:
        if exc.code not in (None, 0):
            sys.exit(exc.code)
        logger.info("Bot stopped by signal")
    except Exception as exc:
        logger.critical("Unrecoverable error: %s", exc)
        sys.exit(1)
