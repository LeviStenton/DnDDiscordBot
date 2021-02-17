#!/usr/bin/python
# cogs/Experience.py
# cogs/RollDice.py
# cogs/Encoutners.py
# cogs/DisplayData.py
# cogs/Main.py

# ---------------------------------------------------------------------------
# IMPORT ALL NECESSARY ASSETS TO RUN THE PROGRAMS

# Operating System
import os
from os.path import splitdrive
# Random
import random
# Math
import math
# Discord
import discord
from discord import reaction
from discord import user
from discord.ext import commands
from discord.ext.commands import has_permissions, CheckFailure
# .env 
from dotenv import load_dotenv
# SQLite
import sqlite3
# Datetime
from datetime import datetime
from datetime import timedelta
# Other scripts
from RollDice import DiceRolling as diceRolling
from Encounters import RandomEncounters as encounter
from Experience import ExperienceSystem as experience
from DisplayData import UserDataCommands as userData
from Main import BotMain as main

# ----------------------------------------------------------------------------
# DECLARE ALL VARIABLES NECESSARY TO RUN THE PROGRAM

# Parse the bot's token, my server, and the file the text to speech reads from
# This file is in the .gitignore and you will need to create your own
load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')

# Initialize the database
conn = sqlite3.connect('databases/levellingDB.db')
c = conn.cursor()
# Write to the prefix file
prefixPath = "prefixes/defaultprefix.txt"
def WriteCommandPrefix(prefix, guild):
    global prefixPath
    prefixPath = f"prefixes/{guild}-prefix.txt"
    commandPrefix = open(prefixPath, "w")
    commandPrefix.write(prefix)
    commandPrefix.close()
# Read from the prefix file
def ReadCommandPrefix():
    commandPrefix = open(prefixPath, "r")
    return commandPrefix.read()
intents = discord.Intents.all()
intents.members = True
intents.reactions = True
# Sets the bot's command prefix to the prefix in prefix.txt
bot = commands.Bot(command_prefix=ReadCommandPrefix(), bot=True, intents=intents, activity = discord.Activity(type = discord.ActivityType.listening, name = f"{ReadCommandPrefix()}help"))  
# Remove the in-built help command to write my own
bot.remove_command("help")
# Cog extensions
cog_extensions = ['Experience', 'RollDice', 'Encounters', 'DisplayData', 'Main']
if __name__ == 'bot':
    for extension in cog_extensions:
        print("Cog Extensions: "+extension)
        bot.load_extension(extension)

# ---------------------------------------------------------------------------
# ON EVENT METHODS

# On ready, get channel ID
async def find_channel():
    mai = main(bot)
    await bot.wait_until_ready()
    channels = bot.get_all_channels()
    for channel in channels:
        if(channel.name == "general"):
            mai.generalChannel = channel.id
        if(channel.name == "level-ups"):
            mai.levelUpChannel = channel.id
    mai.botID = bot.user.id

bot.loop.create_task(find_channel())

# When joining a server for the first time, send a message
@bot.event
async def on_guild_join(guild):
    channels = bot.get_all_channels()
    general = discord.utils.get(channels, name="general")
    generalChannel = general.id
    channel = bot.get_channel(generalChannel)
    await channel.send(f":cowboy: Eyes up Moon Cowboys, I'm connected! Type **{ReadCommandPrefix()}help** to get started.")

# On disconnecting, send a message
@bot.event
async def close():     
    conn.close()  
    for vc in bot.voice_clients: 
        await vc.disconnect()
    
# When a member joins the server, send a welcoming message
@bot.event
async def on_member_join(member):
    dat = userData(bot)
    mai = main(bot)
    print(f"{member.id} joined!")
    memberID = str(member.id)
    author = member.name
    authorAvatar = member.avatar_url
    role = discord.utils.get(member.guild.roles, name='ｄｅｂｒｉｓ 𝓭𝓻𝓲𝓯𝓽𝓮𝓻𝓼')
    channel = bot.get_channel(mai.generalChannel)
    embed = discord.Embed(
        title = f"{dat.cowboyEmote} Eyes up",
        description = "You're a ｍｏｏｎ 𝒸𝑜𝓌𝒷𝑜𝓎 now.",
        colour = dat.embedColour
    )
    embed.set_author(name=author, icon_url=authorAvatar)
    c.execute(f"INSERT or IGNORE INTO userData VALUES(?,0,0,0)", (memberID, ))
    conn.commit()           
    await member.add_roles(role)
    await channel.send(embed=embed)

# Method to do things when a message is sent
@bot.event
async def on_message(message):
    # If messages are sent to the bot through DMs, do not count for anything
    if (isinstance(message.channel, discord.channel.DMChannel)):
        pass
    else:
        exp = experience(bot)
        mai = main(bot)
        # Declaring variables to be used
        generalID = mai.generalChannel
        levelUp = bot.get_channel(mai.levelUpChannel)
        author = message.author
        encounterChance = 0.05
        encounterTypeChance = 0.3
        randFloat = random.random()
        encounterFloat = random.random()
        channelID = message.channel.id
        channel = bot.get_channel(channelID)
        channelHistoryLength = 50

        # Rate limiting the exp users gain from messages
        userMessages = []
        channelMessages = await message.channel.history(limit=channelHistoryLength).flatten()
        for chnlMsg in channelMessages:
            if chnlMsg.author.id == message.author.id:
                userMessages.append(chnlMsg)
        timeDistance = message.created_at - userMessages[1].created_at
        if timeDistance <= timedelta(seconds=exp.rateLimit):
            expBool = False      
        else:
            expBool = True
        exp.MsgExpSystem(message, expBool)  

        # Issueing the levelup message on levelups
        if expBool and message.author.id != mai.botID:
            searchQuery = message.author.id
            c.execute(f'SELECT * FROM userData WHERE userID=?', (searchQuery, ))
            fetchedRow = c.fetchone()
            splitRow = str(fetchedRow).split(", ")
            for idx, item in enumerate(splitRow):
                splitRow[idx] = splitRow[idx].replace('(', '')
                splitRow[idx] = splitRow[idx].replace(')', '')
                splitRow[idx] = splitRow[idx].replace('\'', '')
            messageExp = exp.expPerMsg
            print(splitRow[2])
            userExp = splitRow[2]
            expRemaining = round((math.ceil(float(splitRow[1])) ** 2) / (exp.levellingConstant * exp.levellingConstant) - int(userExp))
            if expRemaining - messageExp <= 0:
                await levelUp.send(embed=exp.LevelUpMsg(int(float(splitRow[1])), author))
                pass
            else:
                pass                          

        # Generating an encounter  
        if(randFloat < encounterChance and channelID == generalID and message.author.id != mai.botID):
            enc = encounter(bot)            
            dat = userData(bot)
            global encounterType
            global encounterID 
            global encounterBool
            if encounterFloat >= encounterTypeChance:
                encounterType = enc.SkillRandomEncounter()
                encounterMsg = await channel.send(embed=encounterType[0])        
                encounterID = encounterMsg.id
                encounterBool = True
                await encounterMsg.add_reaction(dat.rollEmote) 
            elif encounterFloat < encounterTypeChance:
                encounterType = enc.DNDMonRandomEncounter()
                encounterMsg = await channel.send(embed=encounterType[0])        
                encounterID = encounterMsg.id
                encounterBool = True
                await encounterMsg.add_reaction(dat.rollEmote)                 
        await bot.process_commands(message) 

# Method to do things when a reaction is added
@bot.event
async def on_reaction_add(reaction, user):
    rol = diceRolling(bot)
    enc = encounter(bot)            
    dat = userData(bot)
    mai = main(bot)
    general = bot.get_channel(mai.generalChannel)
    levelUp = bot.get_channel(mai.levelUpChannel)
    searchQuery = user.id
    c.execute(f'SELECT * FROM userData WHERE userID=?', (searchQuery, ))
    fetchedRow = c.fetchone()
    splitRow = str(fetchedRow).split(", ")
    for idx, item in enumerate(splitRow):
        splitRow[idx] = splitRow[idx].replace('(', '')
        splitRow[idx] = splitRow[idx].replace(')', '')
        splitRow[idx] = splitRow[idx].replace('\'', '')  
    userMod = 0
    rollNum = 0
    equipment = 0
    try:  
        userMod = int(splitRow[4])
        outcome = rol.QueryRoll("1d20")
        rollNum = int(outcome[2])
        equipment = splitRow[5]
        print("User reacting.")
    except:
        print("No user reacting.")
        pass
    
    # Issueing the levelup message on levelups
    if user.id != mai.botID and rollNum+userMod >= encounterType[2]:  
        exp = experience(bot)      
        encounterExp = int(encounterType[1])
        userExp = int(splitRow[2])
        userLevel = (exp.levellingConstant * math.sqrt(userExp + encounterExp))        
        expRemaining = round((math.ceil(float(splitRow[1])) ** 2) / (exp.levellingConstant * exp.levellingConstant) - userExp)
        if expRemaining - encounterExp <= 0:
            await levelUp.send(embed=exp.LevelUpMsg(int(userLevel), user))
            pass
        else:
            pass

    if reaction.emoji == dat.rollEmote and user.id != mai.botID and reaction.message.id == encounterID:    
        lootChance = random.random()    
        embed = enc.ClearEncounter(reaction, user, rollNum, userMod, equipment)                   
        encClearMsg = await general.send(embed=embed)   
        encClearID = encClearMsg.id          
        if rollNum+userMod >= encounterType[2] and lootChance >= enc.lootDropThresh:
            await encClearMsg.add_reaction(dat.tickEmote)
            await encClearMsg.add_reaction(dat.crossEmote)

    if reaction.emoji == dat.tickEmote and user.id != mai.botID and reaction.message.id == enc.encClearID and user.id == enc.encClearUser:
        c.execute(f"UPDATE userData SET userMod = \"{enc.encClearLoot[1]}\", userEquipment = \"{enc.encClearLoot[0]}\" WHERE userID=?", (searchQuery, ))
        conn.commit()
    elif reaction.emoji == dat.crossEmote and user.id != mai.botID and reaction.message.id == enc.encClearID and user == enc.encClearUser:
        pass

# ---------------------------------------------------------------------------
# COMMAND METHODS

# Sets a new prefix
@bot.command(name='setprefix')
@has_permissions(administrator=True, manage_messages=True, manage_roles=True)
async def set_prefix(ctx, newPrefix):               
    dat = userData(bot)
    acceptablePrefixes = ['!' ,'@' ,'#' ,'$' ,'%' ,'^' ,'&' ,'*' ,'(' ,')' ,'-' ,'=' ,'_' ,'+']
    authorName = ctx.author.name
    authorAvatar = ctx.author.avatar_url
    guild = ctx.guild
    embedMessage = ''
    if newPrefix == ReadCommandPrefix():
        embedMessage = f"The command prefix is already: **{ReadCommandPrefix()}**!"
    else:
        for prefix in acceptablePrefixes:
            if str(newPrefix) == prefix:            
                WriteCommandPrefix(newPrefix, guild)
                bot.command_prefix = ReadCommandPrefix()
                embedMessage = f"You changed the command prefix to: **{ReadCommandPrefix()}**"
                await bot.change_presence(activity = discord.Activity(type = discord.ActivityType.listening, name = f"{ReadCommandPrefix()}help"))
                break
            
            else:
                embedMessage = f"You must use one of the following symbols: **` ~ ! @ # $ % ^ & * ( ) _ + - =**"
    embed = discord.Embed(
        title = f"{dat.prefixEmote} Setting Prefix...",
        description = embedMessage,
        colour = dat.embedColour
    )
    embed.set_author(name=f'{authorName}', icon_url=authorAvatar)
    await ctx.send(embed=embed)

# Loads your guild's prefix
@bot.command(name='loadprefix')
@has_permissions(administrator=True, manage_messages=True, manage_roles=True)
async def load_prefix(ctx):             
    dat = userData(bot)
    guild = ctx.guild
    authorName = ctx.author.name
    authorAvatar = ctx.author.avatar_url
    global prefixPath
    prefixPath = f"prefixes/{guild}-prefix.txt"
    tempPrefix = ReadCommandPrefix()
    WriteCommandPrefix(tempPrefix, guild)
    await bot.change_presence(activity = discord.Activity(type = discord.ActivityType.listening, name = f"{ReadCommandPrefix()}help"))
    embed = discord.Embed(
        title = f"{dat.prefixEmote} Loading Prefix...",
        description = "Prefix loaded!",
        colour = dat.embedColour
    )
    embed.set_author(name=f'{authorName}', icon_url=authorAvatar)
    await ctx.send(embed=embed)



bot.run(TOKEN)

# ---------------------------------------------------------------------------


    

 

    
