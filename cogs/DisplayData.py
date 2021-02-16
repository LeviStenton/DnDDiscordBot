# Discord
import discord
from discord.ext import commands
from discord.ext.commands import has_permissions, CheckFailure
from discord.ext.commands.core import command
# SQLite
import sqlite3
# Datetime
from datetime import datetime
# Math
import math
# Other scripts
from cogs.Experience import ExperienceSystem as experience
from cogs.Main import BotMain as main
from bot import ReadCommandPrefix as bRead

class UserDataCommands(commands.Cog):
    # Initialize the database
    conn = sqlite3.connect('databases/levellingDB.db')
    c = conn.cursor()
    # Emotes
    rollEmote = '🎲'
    voiceEmote = ':microphone2:'
    prefixEmote = ':exclamation:'
    levelEmote = '🛡️'
    accountEmote = ':desktop:'
    cowboyEmote = ':cowboy:'
    tickEmote = '✔️'
    crossEmote = '❌'
    equipmentEmote = '⚔️'
    # Embed Colour
    embedColour = discord.Colour.dark_blue()

    def __init__(self, bot):
        self.bot = bot

    # If the command is sent with 'help', send a message showing ways to use the bot
    @commands.command(name='help')
    async def help(self, ctx):
        author = ctx.author.name
        authorAvatar = ctx.author.avatar_url
        embed = discord.Embed(
            title = "Help Commands",
            description = "A list of how to use each command available:",
            colour = self.embedColour
        )
        embed.set_author(name=f'{author}', icon_url=authorAvatar)
        embed.add_field(name=f"{self.rollEmote} Dice rolling:", value=f"To roll, type something like: **{bRead}roll 1d20**\nThe modifiers '+' or '-' may be added: **{bRead}roll 1d20+3**", inline=False)
        embed.add_field(name=f"{self.voiceEmote} Voice Chat:", value=f"To join voice chat, type: **{bRead}join** \nTo leave voice chat, type: **{bRead}leave**", inline=False)
        embed.add_field(name=f"{self.levelEmote} Rank:", value=f"To view your level stats, type: **{bRead}rank**", inline=False)
        embed.add_field(name=f"{self.equipmentEmote} Equipment:", value=f"To view your current equipment, type: **{bRead}equipment**", inline=False)
        embed.add_field(name=f"{self.accountEmote} Account Info:", value=f"To view your account info, type: **{bRead}userinfo**", inline=False)
        embed.add_field(name=f"{self.prefixEmote} Command Prefixes:", value=f"To change the prefix, type: **{bRead}setprefix <prefix>** \nNote: you must be an administrator to do this", inline=False)
        await ctx.send(embed=embed)
        
    # Retrieves member, exp, and level data from levellingDB
    @commands.command(name='rank')
    async def req_rank(self, ctx):
        expSys = experience(self.bot)
        # Open .csv that stores levelling data
        author = ctx.author.name
        authorAvatar = ctx.author.avatar_url
        guild = ctx.guild
        embed = discord.Embed(
            title = f"{self.levelEmote} Your stats for {guild}",
            colour = self.embedColour
        )
        embed.set_thumbnail(url="https://cdn.discordapp.com/attachments/758193066913562656/767867171391930458/ApprovingElite.png")
        embed.set_author(name=f'{author}', icon_url=authorAvatar)  
        searchQuery = ctx.author.id
        self.c.execute(f'SELECT * FROM userData WHERE userID=?', (searchQuery, ))
        fetchedRows = self.c.fetchall()
        for item in fetchedRows:             
            splitRow = str(item).split(", ")        
            for idx, item in enumerate(splitRow):
                splitRow[idx] = splitRow[idx].replace('(', '')
                splitRow[idx] = splitRow[idx].replace(')', '')
                splitRow[idx] = splitRow[idx].replace('\'', '')     
            level = math.floor(float(splitRow[1]))
            exp = splitRow[2]
            expRemaining = round((math.ceil(float(splitRow[1])) ** 2) / (expSys.levellingConstant * expSys.levellingConstant) - int(exp))
            msgsSent = splitRow[3]
            embed.add_field(name="Level:", value=f"{level}", inline=False)
            embed.add_field(name=f"Exp:", value=f"{exp}", inline=False)
            embed.add_field(name=f"Exp Until Next Level:", value=f"{expRemaining}", inline=False)
            embed.add_field(name=f"Messages Sent:", value=f"{msgsSent}", inline=False) 
            pass    
        await ctx.send(embed=embed)

    # Retrieves user account info based on their public profile
    @commands.command(name='userinfo')
    async def req_userinfo(self, ctx):
        authorName = ctx.author.name
        authorAvatar = ctx.author.avatar_url
        currentTime = datetime.now()
        accCreatedAt = str(ctx.author.created_at).split(" ")
        accJoinedAt = str(ctx.author.joined_at).split(" ")
        timeCreated = accCreatedAt[1].split(".")
        timeJoined = accJoinedAt[1].split(".")
        timeSinceAccCreated = str(currentTime - ctx.author.created_at).split(",")
        timeSinceAccJoined = str(currentTime - ctx.author.joined_at).split(",")
        authorNick = ctx.author.nick
        authorID = ctx.author.id
        authorRoles = ""
        for idx, role in enumerate(ctx.author.roles):
            if idx > 0:
                authorRoles = authorRoles+"<@&"+str(role.id)+"> "
            else:
                authorRoles = "No roles!"
        embed = discord.Embed(
            title = f"{self.accountEmote} Your Account Details",
            colour = self.embedColour
        )
        # embed.set_thumbnail(url="https://cdn.discordapp.com/attachments/758193066913562656/767867171391930458/ApprovingElite.png")
        embed.set_author(name=f'{authorName}', icon_url=authorAvatar)  
        embed.add_field(name=f"Current Nickname:", value=f"{authorNick}", inline=True)
        embed.add_field(name=f"Account Name:", value=f"{authorName}", inline=True)
        embed.add_field(name=f"Roles:", value=f"{authorRoles}", inline=False)
        embed.add_field(name=f"Account Created {timeSinceAccCreated[0]} ago", value=f"**{accCreatedAt[0]}** {timeCreated[0]}", inline=True)
        embed.add_field(name=f"Server Joined {timeSinceAccJoined[0]} ago", value=f"**{accJoinedAt[0]}** {timeJoined[0]}", inline=True)    
        embed.set_footer(text=f"UserID: {authorID}")
        await ctx.send(embed=embed)  

    # Display the current equipment and modifier for a user that calls this command
    @commands.command(name='equipment')
    async def ShowEquipment(self, ctx):
        searchQuery = ctx.author.id
        authorName = ctx.author.name
        authorAvatar = ctx.author.avatar_url
        authorMod = ""
        authorEquip = ""
        self.c.execute(f'SELECT * FROM userData WHERE userID=?', (searchQuery, ))
        fetchedRows = self.c.fetchall()
        for item in fetchedRows:             
            splitRow = str(item).split(", ")        
            for idx, item in enumerate(splitRow):
                splitRow[idx] = splitRow[idx].replace('(', '')
                splitRow[idx] = splitRow[idx].replace(')', '')
                splitRow[idx] = splitRow[idx].replace('\'', '')   
            authorMod = splitRow[4]
            authorEquip = splitRow[5]
        embed = discord.Embed(
            title = f"Your Equipment",
            colour = self.embedColour
        )
        embed.set_thumbnail(url="https://cdn.discordapp.com/attachments/758193066913562656/767677300333477888/48cb5349f515f6e59edc2a4de294f439.png")
        embed.set_author(name=f'{authorName}', icon_url=authorAvatar)    
        embed.add_field(name="Item", value=f"{authorEquip}", inline=True)
        embed.add_field(name="Modifier", value=f"{authorMod}", inline=True)
        await ctx.send(embed=embed)

def setup(bot):
    bot.add_cog(UserDataCommands(bot))