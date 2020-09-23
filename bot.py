# bot.py
import os

import discord
from dotenv import load_dotenv

load_dotenv()
TOKEN = os.getenv('NzE1MTEwNTMyNTMyNzk3NDkw.Xs4clQ.-y1_oKhnQTPYYB8NHyVobtBo8Kk')

client = discord.Client()

@client.event
async def on_ready():
    print(f'{client.user} has connected to Discord!')

client.run(TOKEN)