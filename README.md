# Discord Bot

A feature-rich Discord bot built with python featuring memes, jokes, games, and more!

**Original Project**: My custom meme bot created in 2023  
**Current Version**: Completely rewritten with 10+ commands and modern features

---

## Features

### Entertainment Commands
- **$meme** - Get random memes from the internet
- **$joke** - Get random jokes
- **$8ball** - Ask the magic 8 ball
- **$roll** - Roll a random number
- **$flip** - Flip a coin

### User Commands
- **$avatar** - Show any user's avatar
- **$userinfo** - Display user information
- **$time** - Show current time
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
| `$avatar [@user]` | Show avatar 👤 |
| `$userinfo [@user]` | User information 📊 |
| `$time` | Current time ⏰ |
| `$ping` | Bot latency 🏓 |
| `$help` | All commands 📖 |
| `$saymyname` | Easter egg 🙏 |

---

## 24/7 Hosting

To keep your bot online 24/7, see [HOSTING_GUIDE.md](HOSTING_GUIDE.md) for options:
- **Replit** (Free, easiest)
- **Railway.app** (Free tier available)
- **Render** (Free tier available)
- **DigitalOcean** (Paid, most reliable)

---

## Project Structure

```
Discord Bot/
├── bot.py              # Main bot file
├── requirements.txt    # Python dependencies
├── .env               # Environment variables (create this)
├── README.md          # This file
└── HOSTING_GUIDE.md   # 24/7 hosting setup guide
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
- **requests** - HTTP library for API calls
- **python-dotenv** - Environment variable management

---

## Security

- ✅ Token stored in `.env` (never commit to git)
- ✅ Error handling for API failures
- ✅ Command validation
- ✅ Graceful shutdown

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
- Read [HOSTING_GUIDE.md](HOSTING_GUIDE.md) for 24/7 solutions
- Set up uptime monitoring

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

Need help? Check the [HOSTING_GUIDE.md](HOSTING_GUIDE.md) for detailed setup instructions.

---

