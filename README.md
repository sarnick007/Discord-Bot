# Discord Bot

A cross-platform Discord entertainment bot built with Python and `discord.py`. It runs as a persistent process on Windows, macOS, Linux, Docker, virtual machines, and worker-style hosting services.

## Features

- `$help` — list commands
- `$ping` — report Discord gateway latency
- `$meme [subreddit]` — fetch a random image meme from Reddit (e.g. `$meme ProgrammerHumor`); falls back to meme-api.com
- `$joke` — fetch a random joke
- `$8ball <question>` — ask the magic 8-ball
- `$roll [max]` — roll from 1 to the supplied maximum (100 by default)
- `$flip` — flip a coin
- `$choose option1|option2|option3` — choose an option
- `$avatar [@user]` — show a user's avatar
- `$userinfo [@user]` — show basic user information
- `$time` — display UTC time
- `$saymyname` — creator easter egg
- Rotating activity and per-user command cooldowns

## Requirements

- Python **3.12** is the recommended runtime. The source uses Python 3.10+ syntax.
- A Discord application and bot token.
- Network access to Discord's Gateway and the public meme/joke APIs. Meme fetching tries Reddit's public listing first and falls back to meme-api.com; either service can rate-limit or become unavailable.

## Run locally

### Windows (PowerShell)

```powershell
py -3.12 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
Copy-Item .env.example .env
# Edit .env and set DISCORD_TOKEN to your bot token.
python bot.py
```

### macOS / Linux

```bash
python3.12 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
cp .env.example .env
# Edit .env and set DISCORD_TOKEN to your bot token.
python bot.py
```

You can also set `DISCORD_TOKEN` directly in the process environment instead of using a `.env` file. Environment variables are the recommended way to configure hosted deployments.

## Discord Developer Portal setup

1. Open the [Discord Developer Portal](https://discord.com/developers/applications) and choose the bot application.
2. Under **Bot → Privileged Gateway Intents**, enable **Message Content Intent**. This bot uses prefix commands (the `$` prefix), so Discord must allow message content.
3. Keep **Server Members Intent** and **Presence Intent** disabled unless you deliberately need them. They are disabled by default in code. To opt in, set `ENABLE_MEMBERS_INTENT=true` or `ENABLE_PRESENCE_INTENT=true` and enable the matching intent in the Developer Portal.
4. Invite the bot with the `bot` OAuth2 scope and, at minimum, **View Channels**, **Send Messages**, **Embed Links**, and **Read Message History** in the channels where it should respond.

## Configuration

| Variable | Required | Default | Purpose |
|---|---|---|---|
| `DISCORD_TOKEN` | Yes | — | Bot token, stored as a secret/environment variable |
| `LOG_LEVEL` | No | `INFO` | Python logging level, e.g. `DEBUG`, `INFO`, `WARNING` |
| `LOG_FILE` | No | Unset | Optional log-file path. Console logging is used by default for container compatibility. |
| `ENABLE_MEMBERS_INTENT` | No | `false` | Opt in to privileged Server Members Intent |
| `ENABLE_PRESENCE_INTENT` | No | `false` | Opt in to privileged Presence Intent |

Never commit a real `.env`, publish a token, put it in code, or add it to logs. If a token is exposed, regenerate it immediately in the Developer Portal.

## Run with Docker

The Docker image runs as an unprivileged user and writes logs to standard output.

```bash
docker build -t discord-bot .
docker run --rm -e DISCORD_TOKEN="YOUR_TOKEN" discord-bot
```

For repeat use, set the environment variable through your deployment platform's secret manager rather than typing it into a shared shell or storing it in a Dockerfile. The bot does not need an inbound HTTP port: it maintains an outbound persistent connection to Discord.

## Hosting on different platforms

The application code does not depend on Railway, Render, or another provider. Use any host that can run a **long-lived Python process** and permit outbound WebSocket/HTTPS connections.

- **Docker-capable hosts / VPS:** build the included `Dockerfile`, or install Python and run `python bot.py`.
- **Worker/background-process platforms:** set the build command to `python -m pip install -r requirements.txt`, the start command to `python bot.py`, and configure `DISCORD_TOKEN` as a secret.
- **PaaS/buildpack platforms:** `.python-version` and `runtime.txt` provide Python version hints; `Procfile`, `railway.json`, and `render.yaml` are optional provider-specific deployment helpers.
- **Serverless/function-only runtimes** that terminate background processes are not appropriate for a bot that must maintain a persistent Discord Gateway connection.

See [DEPLOY.md](DEPLOY.md) for a provider-neutral deployment checklist.

## Test

The offline tests do not log in to Discord and do not need a token:

```bash
python -m pip install -r requirements.txt
python -m unittest -v test_bot
python -m compileall -q bot.py test_bot.py
```

GitHub Actions runs those checks on pushes and pull requests across Python 3.12, 3.13, and 3.14. Passing CI proves that the code imports, command registration/configuration checks pass, and dependencies install; it does **not** prove that a deployed bot token is valid or that the bot is online in Discord.

### Manual live Discord connection check

The **Discord live connection check** workflow under GitHub Actions can verify that the configured token can authenticate and reach Discord's Gateway. To use it:

1. In repository **Settings → Secrets and variables → Actions**, create a secret named `DISCORD_TOKEN` (the value remains hidden).
2. Open **Actions → Discord live connection check → Run workflow**.
3. A successful run confirms that this secret is valid and a short-lived connection can be established. A failure prints a safe diagnostic without printing the token.

This is a separate, temporary login check—not proof that the production deployment process is currently running. To verify the deployed instance, check the hosting service's logs for `Logged in as ...` and test `$ping` in Discord.

## Troubleshooting

- **Bot exits before connecting:** verify `DISCORD_TOKEN` is configured as an environment variable. Do not paste the token into an issue or chat.
- **Privileged intent error:** enable Message Content Intent both in code and in the Developer Portal. Enable additional intents only when you explicitly opted in.
- **Bot is online but ignores commands:** check Message Content Intent, the `$` prefix, channel permissions, and the host logs.
- **Meme/joke commands fail:** they rely on Reddit's public listing and third-party public APIs, which can rate-limit or change. The meme command currently serves direct image posts only, skips posts flagged NSFW, and skips video/link posts. Instagram, TikTok, and X are not scraped because reliable access generally requires their official APIs and credentials.
- **AiOps reporting workflow fails:** this is a separate scheduled GitHub Actions integration and is not a health check for the Discord bot. See its step logs for the exact OIDC/API failure.

## Project files

- `bot.py` — bot, entertainment commands, and Reddit/meme API helpers
- `requirements.txt` — Python dependencies
- `test_bot.py` — offline configuration and command smoke tests
- `Dockerfile` — portable container runtime
- `.env.example` — safe local configuration template
- `.github/workflows/python-ci.yml` — code checks
- `.github/workflows/report-to-aiops-enabler.yml` — optional AiOps reporting integration

Created by Sarnick Patra.
