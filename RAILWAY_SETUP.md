# Optional Railway Deployment

The bot code is platform-independent. This file covers only the optional Railway deployment configuration; see [DEPLOY.md](DEPLOY.md) for the platform-neutral instructions.

1. Connect this GitHub repository to a Railway service.
2. Ensure the service starts a worker process rather than expecting an inbound web port.
3. Set the protected environment variable `DISCORD_TOKEN` in Railway's Variables configuration.
4. Deploy the `main` branch and inspect service logs for `Logged in as ...`.
5. In Discord, test `$ping` and `$help`.

The repository's `railway.json` contains the start command and restart policy. Do not place the actual token in `railway.json`, the Dockerfile, source code, or a committed `.env` file.

To rotate a token, regenerate it in the Discord Developer Portal and replace the value in Railway's protected variable configuration.
