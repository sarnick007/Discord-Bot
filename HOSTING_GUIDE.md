# Discord Bot - 24/7 Hosting Guide

## New Features Added ✨

- **10+ New Commands**: Meme, Joke, Magic 8 Ball, Dice Roll, Coin Flip, Avatar, User Info, Help, Ping, Time
- **Beautiful Embeds**: All responses use rich embeds for better UI
- **Rotating Status**: Bot status changes every 5 minutes
- **Error Handling**: Better error messages and exception handling
- **Commands Extension**: Modern discord.py Commands framework

### Available Commands:
```
Fun Commands:
  $meme       - Get a random meme
  $joke       - Get a random joke
  $8ball      - Ask the magic 8 ball
  $roll [max] - Roll a random number (default: 1-100)
  $flip       - Flip a coin

User Commands:
  $avatar [@user]   - Show user's avatar
  $userinfo [@user] - Show user information
  $saymyname        - Special message
  $time             - Show current time

Bot Commands:
  $ping - Check bot latency
  $help - Show all commands
```

---

## 🌐 Hosting Solutions for 24/7 Uptime

### Option 1: **Replit** (Easiest - Free)
1. Go to https://replit.com
2. Create new Python project
3. Upload your bot files
4. Create `.env` file with `DISCORD_TOKEN=your_token_here`
5. Install requirements: `pip install -r requirements.txt`
6. Run the bot: `python bot.py`
7. Keep the web server alive using a free uptime robot service
   - Sign up at https://uptimerobot.com (free)
   - Add HTTP monitor to your Replit URL every 5 minutes

### Option 2: **Railway.app** (Recommended)
1. Go to https://railway.app
2. Create new project → Deploy from GitHub
3. Push your bot code to GitHub
4. Add environment variable: `DISCORD_TOKEN`
5. Railway will keep it running 24/7 for free (limited hours/month initially)

### Option 3: **Render** (Free Tier)
1. Go to https://render.com
2. Create new "Web Service"
3. Connect your GitHub repo
4. Set build command: `pip install -r requirements.txt`
5. Set start command: `python bot.py`
6. Add environment variable: `DISCORD_TOKEN`
7. Deploy!

### Option 4: **DigitalOcean Droplet** (Paid, Most Reliable)
1. Create a $4/month Droplet
2. SSH into your server
3. Install Python: `apt update && apt install python3-pip`
4. Upload files: `scp -r /path/to/bot user@your_server:/home/user/discord-bot`
5. Install dependencies: `pip install -r requirements.txt`
6. Use **systemd** or **screen** to keep bot running
7. Or use **tmux**:
   ```bash
   tmux new-session -d -s discord-bot 'cd /home/user/discord-bot && python3 bot.py'
   ```

### Option 5: **Heroku** (Paid Now, $7+/month)
- Note: Heroku removed free tier in Nov 2022. Costs $7/month minimum.

---

## 🛠️ Local Setup (Development)

1. **Install Python 3.8+**
2. **Create virtual environment:**
   ```bash
   python -m venv venv
   venv\Scripts\activate  # On Windows
   # or
   source venv/bin/activate  # On Mac/Linux
   ```

3. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Create `.env` file:**
   ```
   DISCORD_TOKEN=your_discord_bot_token_here
   ```

5. **Run the bot:**
   ```bash
   python bot.py
   ```

---

## 🔧 Setup Steps

### 1. Create Discord Bot Application
- Go to https://discord.com/developers/applications
- Click "New Application"
- Go to "Bot" section → "Add Bot"
- Copy the token and add to `.env` file
- Enable "Message Content Intent" (Privileged Gateway Intent)

### 2. Invite Bot to Server
- Go to OAuth2 → URL Generator
- Select scopes: `bot`
- Select permissions:
  - Send Messages
  - Read Message History
  - Embed Links
  - Attach Files
- Copy generated URL and open in browser

### 3. Test Locally First
```bash
python bot.py
```
Test all commands in Discord using `$help`

---

## ⚠️ Important Notes

- **Never share your DISCORD_TOKEN** - Keep it secret!
- **Use environment variables** - Never hardcode the token
- **Enable "Message Content Intent"** - Required for command parsing
- **Monitor bot logs** - Check for errors regularly
- **Backup your code** - Use GitHub for version control

---

## 🚀 Quick Deployment Checklist

- [ ] Update `.env` with your Discord token
- [ ] Test bot locally with `python bot.py`
- [ ] Test all commands: `$help`, `$meme`, `$ping`, etc.
- [ ] Choose hosting platform (Replit, Railway, Render)
- [ ] Deploy bot
- [ ] Enable uptime monitoring service
- [ ] Monitor bot performance

---

## 📊 Performance Tips

1. **Add uptime monitoring**: Use UptimeRobot.com (free) to ping your bot every 5 minutes
2. **Set up logging**: Monitor bot health with debug mode
3. **Error notifications**: Add logging to Discord channel for errors
4. **Regular restarts**: Some platforms auto-restart weekly

---

## 🆘 Troubleshooting

**Bot goes offline:**
- Check if your token is valid
- Verify Internet connection
- Check hosting platform status
- Review bot logs for errors

**Commands not working:**
- Ensure "Message Content Intent" is enabled
- Check bot permissions in Discord server
- Verify prefix is correct (`$`)

**API rate limiting:**
- Meme/joke APIs may rate limit - add cooldowns if needed

---

## 📞 Support Resources

- Discord.py Docs: https://discordpy.readthedocs.io/
- Discord Developer Portal: https://discord.com/developers
- Community Help: https://discord.gg/dpy (Discord.py server)

