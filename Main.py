# Discord
import discord
from discord.ext import commands

class BotMain(commands.Cog):
    # Global channel variables
    generalChannel = 0
    levelUpChannel = 0
    # Global ID variables
    botID = 715110532532797490 

    def __init__(self, bot):
        self.bot = bot

def setup(bot):
    bot.add_cog(BotMain(bot))