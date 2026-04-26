# Quick Railway Deployment (5 minutes)

## Step 1: Initialize Git Repository Locally

```bash
cd "C:\Users\patra\Programming\Discord Bot"
git init
git add .
git commit -m "Initial Discord bot commit"
git branch -M main
```

## Step 2: Create GitHub Repository

1. Go to: https://github.com/new
2. Repository name: `discord-bot` (or any name)
3. Choose: **Public** (for free Railway deployment)
4. Click **Create repository**

## Step 3: Add Remote & Push to GitHub

After creating the repo, GitHub will show you commands. Run:

```bash
git remote add origin https://github.com/YOUR_USERNAME/discord-bot.git
git push -u origin main
```

Replace `YOUR_USERNAME` with your actual GitHub username.

## Step 4: Connect to Railway

1. Go to: https://railway.app
2. Sign in with GitHub (click "Start with GitHub")
3. Click **"Create a new project"**
4. Select **"Deploy from GitHub repo"**
5. Select your `discord-bot` repository
6. Railway will auto-detect it's a Python project

## Step 5: Add Environment Variables

In Railway dashboard:
1. Go to **Variables** tab
2. Click **"New Variable"**
3. Add:
   - **Key**: `DISCORD_TOKEN`
   - **Value**: (paste your Discord bot token)
4. Click **Add**

## Step 6: Deploy!

1. Click **"Deploy"** button
2. Wait 2-3 minutes for deployment
3. Watch the logs for success message
4. Your bot will be online 24/7!

## Step 7: Verify It's Working

In Discord:
- Type `$ping` - should respond with latency
- Type `$help` - should show all commands

---

## That's It! 🎉

Your bot is now hosted on Railway and running 24/7 for free!

**Railway Benefits:**
- ✅ Free tier (enough for small bots)
- ✅ 24/7 uptime
- ✅ Auto-restart if crashes
- ✅ Easy GitHub integration
- ✅ Environment variables support
- ✅ Monitor logs in real-time
- ✅ Easy rollback if issues

---

## Troubleshooting

**Bot not online?**
1. Check logs in Railway dashboard
2. Verify `DISCORD_TOKEN` is correct
3. Check Discord Developer Portal - "Message Content Intent" enabled?

**Want to update code?**
1. Make changes locally
2. `git add .` → `git commit -m "update"` → `git push`
3. Railway auto-deploys!

**Need more resources?**
1. Railway free tier includes enough for typical bot usage
2. Upgrade to paid if needed later

