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

@bot.command(name='roll')
async def roll(ctx, number_of_dice: int, number_of_sides: int):
    dice = []
    totalDice = 0
    
    for i in number_of_dice:
        dice.insert(str(random.choice(range(1, number_of_sides + 1))))
        totalDice += dice[i]
    
    await ctx.send('Dice: '+dice+' Total: '+totalDice)

bot.run(TOKEN)