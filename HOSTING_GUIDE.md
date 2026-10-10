# Hosting Guide

The project is designed to run on any host capable of maintaining a long-lived Python process and outbound Discord Gateway connections. It is not tied to a particular cloud provider.

For the canonical deployment, environment-variable, Docker, and troubleshooting steps, see [DEPLOY.md](DEPLOY.md).

## Basic launch

```bash
python -m pip install -r requirements.txt
python -m unittest -v test_bot
python bot.py
```

Set `DISCORD_TOKEN` as a protected environment variable. For local development, copy `.env.example` to `.env` and add the token there. Never commit the real `.env` file or paste the token into logs/issues.

## Hosting checklist

- Use a long-running worker or Docker/VPS process.
- Configure `DISCORD_TOKEN` securely.
- Enable Message Content Intent in the Discord Developer Portal.
- Give the bot the required channel permissions.
- Check provider logs for `Logged in as ...`.
- Test `$ping` and `$help` inside Discord.

Provider-specific files such as `render.yaml`, `railway.json`, and `Procfile` are optional deployment helpers. The Python application itself does not require either provider.
