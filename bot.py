# bot.py
import os
import random
import discord

from discord.ext import commands
from dotenv import load_dotenv

load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')
GUILD = os.getenv('DISCORD_GUILD')

bot = commands.Bot(command_prefix='!')

@bot.command(name='test')
async def TestFunction(ctx):
    testing = [
        'Hello there!','Hey!'
    ]

    response = random.choice(testing)
    await ctx.send(response)

bot.run(TOKEN)