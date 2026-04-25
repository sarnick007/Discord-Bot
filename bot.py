import os
from dotenv import load_dotenv

load_dotenv() # Load environment variables from .env file

token = os.getenv('DISCORD_TOKEN') # Get the Discord token from environment variable
import discord
import requests
import json
import time

def get_meme():
  response = requests.get('https://meme-api.com/gimme')
  json_data = json.loads(response.text)
  return json_data['url']

class MyClient(discord.Client):
  async def on_ready(self):
    print('Logged on as {0}!'.format(self.user))

  async def on_message(self, message):
    if message.author == self.user:
      return
    if message.content.startswith('$meme'):
      await message.channel.send(get_meme())
    if message.content.startswith('$saymyname'):
        await message.channel.send('Thank you, my creator Sarnick, for infusing life in me!')
    if message.content.startswith('$time'):
        await message.channel.send(f"It's {time.ctime()}")

intents = discord.Intents.default()
intents.message_content = True

client = MyClient(intents=intents)
client.run(token) # Use the token from environment variables
intents = discord.Intents.default()
intents.message_content = True


