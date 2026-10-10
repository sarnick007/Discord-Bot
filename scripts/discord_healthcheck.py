"""Manually verify that a configured bot token can open a Discord Gateway session.

This is a short login/connectivity check, not a replacement for monitoring the
long-running production process. It intentionally requests no privileged intents.
"""
import asyncio
import os

import discord


class HealthCheckClient(discord.Client):
    def __init__(self) -> None:
        super().__init__(intents=discord.Intents.none())

    async def on_ready(self) -> None:
        user = self.user
        if user is not None:
            print(f"Discord Gateway login succeeded for {user} (ID: {user.id}).")
        await self.close()


async def main() -> None:
    token = os.getenv("DISCORD_TOKEN", "").strip()
    if not token:
        raise SystemExit(
            "DISCORD_TOKEN is not configured. Add it as a GitHub Actions repository "
            "secret before running this manual check. The secret value is never printed."
        )

    client = HealthCheckClient()
    try:
        await asyncio.wait_for(client.start(token), timeout=30)
    except discord.LoginFailure:
        raise SystemExit(
            "Discord rejected DISCORD_TOKEN. Regenerate the bot token in the Discord "
            "Developer Portal and update the stored secret."
        )
    except asyncio.TimeoutError:
        await client.close()
        raise SystemExit(
            "Timed out waiting for Discord Gateway READY. Check network access and "
            "Discord service status, then retry."
        )
    finally:
        if not client.is_closed():
            await client.close()


if __name__ == "__main__":
    asyncio.run(main())
