# Discord Bot

A feature-rich Discord bot built with Python featuring memes, jokes, games, and more!

**Original Project**: My custom meme bot created in 2023  
**Current Version**: Completely rewritten with 11 commands and modern features

---

## Features

### Entertainment Commands
- **$meme** - Get random memes from the internet
- **$joke** - Get random jokes
- **$8ball** - Ask the magic 8 ball
- **$roll** - Roll a random number
- **$flip** - Flip a coin
- **$choose** - Choose between options

### User Commands
- **$avatar** - Show any user's avatar
- **$userinfo** - Display user information
- **$time** - Show current UTC time
- **$saymyname** - Easter egg message

### Bot Utilities
- **$help** - Display all available commands
- **$ping** - Check bot latency
- **Rotating Status** - Bot status changes every 5 minutes
- **Beautiful Embeds** - All responses use rich Discord embeds
- **Error Handling** - Graceful error messages

---

## Quick Start

### Prerequisites
- Python 3.8 or higher
- Discord bot token (from https://discord.com/developers)

### Installation

1. **Clone/Download the repository**

2. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

3. **Create `.env` file:**
   ```env
   DISCORD_TOKEN=your_discord_bot_token_here
   ```

4. **Run the bot:**
   ```bash
   python bot.py
   ```

---

## 📖 Commands

| Command | Description |
|---------|-------------|
| `$meme` | Random meme 🎉 |
| `$joke` | Random joke 😂 |
| `$8ball [question]` | Magic 8 ball 🎱 |
| `$roll [max]` | Roll a number (1-100 default) 🎲 |
| `$flip` | Flip a coin 🪙 |
| `$choose <a\|b\|...>` | Choose between options ✅ |
| `$avatar [@user]` | Show avatar 👤 |
| `$userinfo [@user]` | User information 📊 |
| `$time` | Current time (UTC) ⏰ |
| `$ping` | Bot latency 🏓 |
| `$help` | All commands 📖 |
| `$saymyname` | Easter egg 🙏 |

---

## 🚀 24/7 Hosting

> **⚠️ Vercel/Cloudflare Workers cannot host Discord bots.** Use platforms that support long-running processes.

**Recommended (Free):**
- [Render](https://render.com) — Background Worker, 750h/month free
- [Railway](https://railway.app) — $5 credit/month free

**Other options:**
- [Fly.io](https://fly.io) — 3 free micro-VMs
- [DigitalOcean](https://www.digitalocean.com) — $4/month Droplet

See [DEPLOY.md](DEPLOY.md) for detailed deployment instructions.

---

## Project Structure

```
Discord Bot/
├── bot.py              # Main bot file
├── requirements.txt    # Python dependencies
├── render.yaml         # Render deployment config
├── Dockerfile          # Container deployment config
├── .env               # Environment variables (create this)
├── README.md          # This file
└── DEPLOY.md          # Deployment guide
```

---

## Configuration

### Discord Bot Setup
1. Visit https://discord.com/developers/applications
2. Create new application
3. Go to "Bot" → "Add Bot"
4. Copy token to `.env` file
5. Enable "Message Content Intent" (required)
6. Invite bot using OAuth2 URL Generator

### Required Permissions
- Send Messages
- Embed Links
- Read Message History

---

## Technologies Used

- **discord.py** - Python Discord API wrapper
- **aiohttp** - Async HTTP client (non-blocking API calls)
- **python-dotenv** - Environment variable management

---

## Security

- ✅ Token stored in `.env` (never committed)
- ✅ Non-blocking async API calls
- ✅ Graceful error handling
- ✅ Command cooldowns prevent abuse
- ✅ Structured logging (file + console)
- ✅ Graceful shutdown on SIGTERM

---

## Troubleshooting

**Bot won't start?**
- Verify Discord token is correct
- Check all dependencies are installed: `pip install -r requirements.txt`
- Enable "Message Content Intent" in Discord Developer Portal

**Commands not working?**
- Check command prefix is `$`
- Verify bot has permission to send messages
- Use `$help` to see all available commands

**Bot goes offline?**
- Check your hosting platform's logs
- Verify `DISCORD_TOKEN` is set correctly
- Ensure your hosting plan supports long-running processes

---

## License

Free to use and modify

---

## Creator

Created by Sarnick

---

## Contributing

Feel free to fork and add your own features!

---

## Support

Need help? Check the [DEPLOY.md](DEPLOY.md) for detailed setup instructions.
