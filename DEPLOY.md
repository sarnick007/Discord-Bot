# Quick Deployment Instructions

## For Railway.app (Recommended - Free)

1. Push your code to GitHub
2. Go to https://railway.app
3. Sign in with GitHub
4. Create new project → Deploy from GitHub repo
5. Select this repository
6. Add environment variable:
   - Key: `DISCORD_TOKEN`
   - Value: Your Discord bot token
7. Railway will auto-deploy and keep running!

---

## For Render.com

1. Push your code to GitHub
2. Go to https://render.com
3. Create new "Web Service"
4. Connect GitHub account and select this repo
5. Fill in settings:
   - **Name**: discord-bot (or any name)
   - **Runtime**: Python 3
   - **Build command**: `pip install -r requirements.txt`
   - **Start command**: `python bot.py`
6. Add environment variable:
   - Key: `DISCORD_TOKEN`
   - Value: Your Discord bot token
7. Click "Create Web Service" and deploy!

---

## For Replit (Easiest)

1. Go to https://replit.com
2. Create new Python project
3. Upload bot.py, requirements.txt, .env files
4. Create .env with: `DISCORD_TOKEN=your_token_here`
5. Click "Run" to start
6. To keep alive, use: https://uptimerobot.com
   - Create monitor for your Replit URL
   - Set interval to 5 minutes

---

## Recommended: Use GitHub + Railway

This is the easiest and most reliable:

1. Create GitHub account if you don't have one
2. Create new repository
3. Push your bot files:
   ```bash
   git add .
   git commit -m "Initial Discord bot commit"
   git push origin main
   ```
4. Go to Railway.app
5. Connect your GitHub
6. Select your bot repo
7. Add DISCORD_TOKEN environment variable
8. Done! Your bot is now 24/7 online

---

**The key is having your code on GitHub - that's what makes deployment super easy!**
