# Deployment Guide

This bot is a persistent Python worker that maintains an outbound connection to Discord. It does not need an inbound HTTP port or a particular hosting provider.

## 1. Configure the Discord application

1. Create/open the application at https://discord.com/developers/applications.
2. Under **Bot → Privileged Gateway Intents**, enable **Message Content Intent** because the bot uses the `$` prefix.
3. Keep **Server Members Intent** and **Presence Intent** disabled unless needed. They are opt-in in code via `ENABLE_MEMBERS_INTENT=true` and `ENABLE_PRESENCE_INTENT=true`.
4. Invite it with the `bot` OAuth2 scope and permissions such as View Channels, Send Messages, Embed Links, and Read Message History.
5. Store the bot token securely as the environment variable `DISCORD_TOKEN`.

Never commit the actual token to GitHub or include it in logs.

## 2. Generic deployment requirements

Choose a host that supports all of the following:

- A long-running Python process (not a short-lived request/function runtime).
- Outbound connectivity to Discord's Gateway over WebSocket and HTTPS.
- Secure environment variables/secrets.
- Process restart/recovery after failure.

Recommended runtime: Python 3.12. The repository includes `.python-version`, `runtime.txt`, and a Dockerfile as deployment aids.

## 3. Run directly on a machine or virtual machine

Install Python 3.12 and then:

```bash
python -m venv .venv
# macOS/Linux:
source .venv/bin/activate
# Windows PowerShell:
# .\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
python -m unittest -v test_bot
python bot.py
```

Set `DISCORD_TOKEN` through the machine's environment or a local `.env` file. For a server, use a supervisor such as systemd, Docker restart policies, or the platform's worker supervisor rather than relying on an interactive terminal.

## 4. Run with Docker

```bash
docker build -t discord-bot .
docker run --rm -e DISCORD_TOKEN="YOUR_TOKEN" discord-bot
```

For production, inject the value through the host's secret manager. Do not bake credentials into the image or Dockerfile.

## 5. Managed worker platforms

On a managed worker/background-process service, configure:

- **Build command:** `python -m pip install -r requirements.txt`
- **Start command:** `python -u bot.py`
- **Secret/environment variable:** `DISCORD_TOKEN`
- **Optional variables:** `LOG_LEVEL`, `LOG_FILE`, `ENABLE_MEMBERS_INTENT`, `ENABLE_PRESENCE_INTENT`

The repository includes optional `render.yaml`, `railway.json`, and `Procfile` examples. They are deployment conveniences only; the bot code does not import or depend on those providers.

## 6. Verify a deployment

Look for a startup log similar to `Logged in as ...`. Then, in a channel where the bot has permissions, test:

- `$ping` — should reply with latency.
- `$help` — should list commands.
- `$choose Pizza|Burger|Sushi` — should choose one option.

If startup fails, inspect the host logs without sharing token values. A successful GitHub Actions CI run checks the code and dependencies, but does not verify the live token or gateway connection.

## Troubleshooting

- **Missing token:** set `DISCORD_TOKEN` in the runtime environment.
- **Invalid token:** regenerate it in the Discord Developer Portal and update the host's secret.
- **Privileged intent error:** enable Message Content Intent in both the portal and code configuration. Only enable other privileged intents when needed.
- **Commands ignored:** confirm the `$` prefix, Message Content Intent, and channel permissions.
- **Bot exits when a terminal closes:** use a managed worker, container restart policy, or process supervisor.
- **Meme/joke API errors:** those commands rely on external public APIs and can fail independently of the Discord connection.
- **AiOps workflow errors:** the scheduled reporting workflow is separate from the Discord runtime, and its status does not indicate whether the bot is online.
