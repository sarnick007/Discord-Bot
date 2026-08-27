# Deployment Guide

> **⚠️ Vercel cannot host Discord bots.** Vercel is serverless — it kills processes after seconds. Discord bots need a persistent WebSocket connection, which requires a long-running process. Use one of the platforms below instead.

---

## Option 1: Render (Recommended — Free)

Render has a **Background Worker** service type designed for long-running processes like Discord bots.

### Steps:
1. Push your code to GitHub
2. Go to [render.com](https://render.com) and sign in
3. Click **"New +"** → **"Background Worker"**
4. Connect your GitHub repo
5. Render auto-detects `render.yaml` — verify settings:
   - **Runtime**: Python
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `python bot.py`
6. Go to **Environment** tab and add:
   - `DISCORD_TOKEN` = your bot token
7. Click **"Create Background Worker"**
8. Bot stays online 24/7 with auto-restart on failure

**Free tier**: 750 hours/month (enough for one bot)

---

## Option 2: Railway (Free tier available)

Railway supports worker processes and auto-deploys from GitHub.

### Steps:
1. Push code to GitHub
2. Go to [railway.app](https://railway.app) and sign in with GitHub
3. Click **"New Project"** → **"Deploy from GitHub Repo"**
4. Select your bot repo
5. Railway auto-detects Python — it runs `pip install -r requirements.txt` then `python bot.py`
6. Go to **Variables** tab and add:
   - `DISCORD_TOKEN` = your bot token
7. Deploy!

**Free tier**: $5 credit/month (enough for small bots)

---

## Option 3: Fly.io (Free tier)

Fly.io runs your bot in a lightweight micro-VM.

### Steps:
1. Install [Fly CLI](https://fly.io/docs/hands-on/install-flyctl/)
2. Run:
   ```bash
   fly launch
   fly secrets set DISCORD_TOKEN=your_token_here
   fly deploy
   ```

**Free tier**: 3 shared-cpu-1x VMs (256MB RAM each)

---

## Option 4: DigitalOcean Droplet ($4/month)

Most reliable option if you want full control.

### Steps:
1. Create a $4/month Droplet
2. SSH in and install Python:
   ```bash
   apt update && apt install -y python3-pip
   ```
3. Upload files:
   ```bash
   scp -r . root@your_server:/root/discord-bot
   ```
4. Install and run:
   ```bash
   cd /root/discord-bot
   pip3 install -r requirements.txt
   python3 bot.py
   ```
5. Use `tmux` or `systemd` to keep it running

---

## ❌ Why NOT Vercel / Heroku / Cloudflare Workers?

| Platform | Issue |
|----------|-------|
| **Vercel** | Serverless — kills processes after 10s. Cannot maintain WebSocket. |
| **Cloudflare Workers** | Edge runtime — no Python, no persistent connections. |
| **Heroku** | Free tier removed (Nov 2022). Starts at $7/month. |
| **Replit** | Unstable for 24/7 — often sleeps or crashes. |

---

## Quick Comparison

| Platform | Free? | Auto-restart | Persistent process | Difficulty |
|----------|-------|--------------|-------------------|------------|
| **Render** | ✅ 750h/mo | ✅ | ✅ Background Worker | Easy |
| **Railway** | ✅ $5 credit | ✅ | ✅ | Easy |
| **Fly.io** | ✅ 3 VMs | ✅ | ✅ Micro-VM | Medium |
| **DO Droplet** | ❌ $4/mo | ❌ (manual) | ✅ Full VPS | Hard |

---

## Pre-deployment Checklist

- [ ] Set `DISCORD_TOKEN` in the platform's environment variables
- [ ] Enable **Message Content Intent** in [Discord Developer Portal](https://discord.com/developers/applications)
- [ ] Bot has **Send Messages**, **Embed Links**, **Read Message History** permissions
- [ ] Test locally: `python bot.py`
- [ ] Check logs after deploy for "Logged in as..." confirmation

---

## Troubleshooting

**Bot won't come online?**
- Verify `DISCORD_TOKEN` is correct
- Enable "Message Content Intent" in Discord Developer Portal
- Check deploy logs for errors

**Bot goes offline periodically?**
- Some free tiers have memory limits — upgrade if needed
- Check if API calls are timing out (bot.log file)

**Commands not working?**
- Ensure prefix is `$`
- Verify bot permissions in Discord server
- Run `$help` to see available commands
