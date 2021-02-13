#!/usr/bin/python

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
# Speech Recognition
import speech_recognition as sr
# Regex
import re
from re import I
# .env 
from dotenv import load_dotenv
# SQLite
import sqlite3
# Datetime
from datetime import datetime
from datetime import timedelta


# ----------------------------------------------------------------------------
# DECLARE ALL VARIABLES NECESSARY TO RUN THE PROGRAM

# Parse the bot's token, my server, and the file the text to speech reads from
# This file is in the .gitignore and you will need to create your own
load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')
#GUILD = os.getenv('DISCORD_GUILD')

# Initialize the database
conn = sqlite3.connect('databases/levellingDB.db')
c = conn.cursor()
# Initialize the voice recognizer
r = sr.Recognizer()
# Emotes
rollEmote = '🎲'
voiceEmote = ':microphone2:'
prefixEmote = ':exclamation:'
levelEmote = ':crossed_swords:'
accountEmote = ':desktop:'
cowboyEmote = ':cowboy:'
# Embed Colour
embedColour = discord.Colour.dark_blue()
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
bot = commands.Bot(command_prefix=ReadCommandPrefix(), intents=intents)  
# Remove the in-built help command to write my own
bot.remove_command("help")
# Global variables for Encounters
encounterID = ""
encounterBool = False
encounterType = []
levellingConstant = 0.1
expPerMsg = 1
# Global channel variables
generalChannel = 0
levelUpChannel = 0
# Global ID variables
botID = 0

# ---------------------------------------------------------------------------
# ON EVENT METHODS

# When joining a server for the first time, send a message
@bot.event
async def on_guild_join(guild):
    channels = bot.get_all_channels()
    global generalChannel
    general = discord.utils.get(channels, name="general")
    generalChannel = general.id
    channel = bot.get_channel(generalChannel)
    await channel.send(f":cowboy: Eyes up Moon Cowboys, I'm connected! Type **{ReadCommandPrefix()}help** to get started.")

# On ready, set the custom status
@bot.event
async def on_ready():
    channels = bot.get_all_channels()
    global botID
    global generalChannel
    global levelUpChannel
    botID = bot.user.id
    general = discord.utils.get(channels, name="general")
    generalChannel = general.id
    levelUps = discord.utils.get(channels, name="level-ups")
    levelUpChannel = levelUps.id
    await bot.change_presence(activity = discord.Activity(type = discord.ActivityType.listening, name = f"{ReadCommandPrefix()}help"))

# On disconnecting, send a message
@bot.event
async def close():     
    conn.close()  
    for vc in bot.voice_clients: 
        await vc.disconnect()
    
# When a member joins the server, send a welcoming message
@bot.event
async def on_member_join(member):
    global generalChannel
    print(f"{member.id} joined!")
    memberID = str(member.id)
    author = member.name
    authorAvatar = member.avatar_url
    role = discord.utils.get(member.guild.roles, name='ｄｅｂｒｉｓ 𝓭𝓻𝓲𝓯𝓽𝓮𝓻𝓼')
    channel = bot.get_channel(generalChannel)
    embed = discord.Embed(
        title = f"{cowboyEmote} Eyes up",
        description = "You're a ｍｏｏｎ 𝒸𝑜𝓌𝒷𝑜𝓎 now.",
        colour = embedColour
    )
    embed.set_author(name=author, icon_url=authorAvatar)
    c.execute(f"INSERT or IGNORE INTO userData VALUES(?,0,0,0)", (memberID, ))
    conn.commit()           
    await member.add_roles(role)
    await channel.send(embed=embed)

# Method to do things when a message is sent
@bot.event
async def on_message(message):
    if (isinstance(message.channel, discord.channel.DMChannel)):
        pass
    else:
        # Declaring variables to be used
        generalID = generalChannel
        levelUp = bot.get_channel(levelUpChannel)
        global botID
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
        if timeDistance <= timedelta(seconds=3):
            expBool = False      
        else:
            expBool = True
        MsgExpSystem(message, expBool)  

        # Issueing the levelup message on levelups
        # Returning 0 exp and 0 remaining when levels up are meant to happen for some reason
        if expBool and message.author.id != botID:
            searchQuery = message.author.id
            c.execute(f'SELECT * FROM userData WHERE userID=?', (searchQuery, ))
            fetchedRow = c.fetchone()
            print(fetchedRow)
            splitRow = str(fetchedRow).split(", ")
            print(len(splitRow))
            for idx, item in enumerate(splitRow):
                print("Row: "+splitRow[idx])
                splitRow[idx] = splitRow[idx].replace('(', '')
                splitRow[idx] = splitRow[idx].replace(')', '')
                splitRow[idx] = splitRow[idx].replace('\'', '')
            messageExp = expPerMsg
            userExp = splitRow[2]
            expRemaining = round((math.ceil(float(splitRow[1])) ** 2) / (levellingConstant * levellingConstant) - int(userExp))
            print("Message EXP: "+str(messageExp))
            print("Current Remaining EXP: "+str(expRemaining))
            if expRemaining - messageExp <= 0:
                print("LEVEL UP!")
                await levelUp.send(embed=LevelUpMsg(int(float(splitRow[1])), author))
                pass
            else:
                pass
            print("-----------------------------------------------------------")
                          

        # Generating an encounter  
        if(randFloat < encounterChance and channelID == generalID and message.author.id != botID):
            global encounterType
            global encounterID 
            global encounterBool
            if encounterFloat >= encounterTypeChance:
                encounterType = SkillRandomEncounter()
                encounterMsg = await channel.send(embed=encounterType[0])        
                encounterID = str(encounterMsg.id)
                encounterBool = True
                await encounterMsg.add_reaction(rollEmote) 
            elif encounterFloat < encounterTypeChance:
                encounterType = DNDMonRandomEncounter()
                encounterMsg = await channel.send(embed=encounterType[0])        
                encounterID = str(encounterMsg.id)
                encounterBool = True
                await encounterMsg.add_reaction(rollEmote)                 
        await bot.process_commands(message) 

# Method to do things when a reaction is added
@bot.event
async def on_reaction_add(reaction, user):
    general = bot.get_channel(generalChannel)
    if reaction.emoji == rollEmote and user.id != botID:
        embed = ClearEncounter(reaction, user)
        await general.send(embed=embed)

# ---------------------------------------------------------------------------
# COMMAND METHODS

# If the command is sent with 'help', send a message showing ways to use the bot
@bot.command(name='help')
async def help(ctx):
    author = ctx.author.name
    authorAvatar = ctx.author.avatar_url
    embed = discord.Embed(
        title = "Help Commands",
        description = "A list of how to use each command available:",
        colour = embedColour
    )
    embed.set_author(name=f'{author}', icon_url=authorAvatar)
    embed.add_field(name=f"{rollEmote} Dice rolling:", value=f"To roll, type something like: **{ReadCommandPrefix()}roll 1d20**\nThe modifiers '+' or '-' may be added: **{ReadCommandPrefix()}roll 1d20+3**", inline=False)
    embed.add_field(name=f"{voiceEmote} Voice Chat:", value=f"To join voice chat, type: **{ReadCommandPrefix()}join** \nTo leave voice chat, type: **{ReadCommandPrefix()}leave**", inline=False)
    embed.add_field(name=f"{levelEmote} Rank:", value=f"To view your level stats, type: **{ReadCommandPrefix()}rank**", inline=False)
    embed.add_field(name=f"{accountEmote} Account Info:", value=f"To view your account info, type: **{ReadCommandPrefix()}userinfo**", inline=False)
    embed.add_field(name=f"{prefixEmote} Command Prefixes:", value=f"To change the prefix, type: **{ReadCommandPrefix()}setprefix <prefix>** \nNote: you must be an administrator to do this", inline=False)
    await ctx.send(embed=embed)

# Sets a new prefix
@bot.command(name='setprefix')
@has_permissions(administrator=True, manage_messages=True, manage_roles=True)
async def set_prefix(ctx, newPrefix):    
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
        title = f"{prefixEmote} Setting Prefix...",
        description = embedMessage,
        colour = embedColour
    )
    embed.set_author(name=f'{authorName}', icon_url=authorAvatar)
    await ctx.send(embed=embed)

# Loads your guild's prefix
@bot.command(name='loadprefix')
@has_permissions(administrator=True, manage_messages=True, manage_roles=True)
async def load_prefix(ctx):    
    guild = ctx.guild
    authorName = ctx.author.name
    authorAvatar = ctx.author.avatar_url
    global prefixPath
    prefixPath = f"prefixes/{guild}-prefix.txt"
    tempPrefix = ReadCommandPrefix()
    print(tempPrefix)
    WriteCommandPrefix(tempPrefix, guild)
    await bot.change_presence(activity = discord.Activity(type = discord.ActivityType.listening, name = f"{ReadCommandPrefix()}help"))
    embed = discord.Embed(
        title = f"{prefixEmote} Loading Prefix...",
        description = "Prefix loaded!",
        colour = embedColour
    )
    embed.set_author(name=f'{authorName}', icon_url=authorAvatar)
    await ctx.send(embed=embed)

# If the command is sent with 'join', join the voice channel that the author is in
@bot.command(name='join')
async def join_voice(ctx):
    author = ctx.author.name
    authorAvatar = ctx.author.avatar_url
    embedMessage = '' 
    connected = None
    channel = None
    try:
        connected = ctx.author.voice
        channel = ctx.author.voice.channel        
    except:
        embedMessage = f"You need to join a voice channel first!"
    try:
        if connected:           
            await channel.connect()          
            for client in bot.voice_clients:
                if client.channel == channel:
                    embedMessage = f"I've connected to **{str(channel)}**!"                    
    except:
        embedMessage = f"I\'m already connected to **{str(channel)}**."
    joinEmbed = discord.Embed(
        title = f"{voiceEmote} Connecting...",
        description = embedMessage,
        colour = embedColour
    )
    joinEmbed.set_author(name=f'{author}', icon_url=authorAvatar) 
    await ctx.send(embed=joinEmbed)

# If the command is sent with 'leave', leave all voice channels    
@bot.command(name='leave')
async def leave_voice(ctx):
    for vc in bot.voice_clients: 
        if(vc.guild == ctx.guild):
            await vc.disconnect()
            joinEmbed = discord.Embed(
                title = f"{voiceEmote} Leaving...",
                description = f"Left!",
                colour = embedColour
            )
            joinEmbed.set_author(name=f'{ctx.message.author.name}', icon_url=ctx.author.avatar_url) 
            await ctx.send(embed=joinEmbed)
       
# Retrieves member, exp, and level data from levellingDB
@bot.command(name='rank')
async def req_rank(ctx):
    # Open .csv that stores levelling data
    author = ctx.author.name
    authorAvatar = ctx.author.avatar_url
    guild = ctx.guild
    embed = discord.Embed(
        title = f"{levelEmote} Your stats for {guild}",
        colour = embedColour
    )
    embed.set_thumbnail(url="https://cdn.discordapp.com/attachments/758193066913562656/767867171391930458/ApprovingElite.png")
    embed.set_author(name=f'{author}', icon_url=authorAvatar)  
    searchQuery = ctx.author.id
    c.execute(f'SELECT * FROM userData WHERE userID=?', (searchQuery, ))
    fetchedRows = c.fetchall()
    for item in fetchedRows:             
        splitRow = str(item).split(", ")        
        for idx, item in enumerate(splitRow):
            splitRow[idx] = splitRow[idx].replace('(', '')
            splitRow[idx] = splitRow[idx].replace(')', '')
            splitRow[idx] = splitRow[idx].replace('\'', '')     
        level = math.floor(float(splitRow[1]))
        exp = splitRow[2]
        expRemaining = round((math.ceil(float(splitRow[1])) ** 2) / (levellingConstant * levellingConstant) - int(exp))
        msgsSent = splitRow[3]
        embed.add_field(name="Level:", value=f"{level}", inline=False)
        embed.add_field(name=f"Exp:", value=f"{exp}", inline=False)
        embed.add_field(name=f"Exp Until Next Level:", value=f"{expRemaining}", inline=False)
        embed.add_field(name=f"Messages Sent:", value=f"{msgsSent}", inline=False) 
        pass    
    await ctx.send(embed=embed)

# Retrieves user account info based on their public profile
@bot.command(name='userinfo')
async def req_userinfo(ctx):
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
        title = f"{accountEmote} Your Account Details",
        colour = embedColour
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

# DO NOT USE THIS UNLESS YOU WANT TO WIPE ALL LEVEL DATA
@bot.command(name='ResetServerLevelData')
@has_permissions(administrator=True, manage_messages=True, manage_roles=True)
async def collectLevelData(ctx):
    try:
        if(ctx.message.author.id == 218890729550774282):
            c.execute("CREATE TABLE IF NOT EXISTS userData(userID TEXT, userLevel TEXT, userExp TEXT, userSentMsgs TEXT)")
            for member in ctx.guild.members:
                memberID = str(member.id)             
                c.execute(f"INSERT INTO userData VALUES (?,0,0,0)", (memberID, ))
                conn.commit()
            print("Storing fresh data successful.")
            await ctx.send("Storing fresh data successful.")
    except:
        print("Error resetting database.")
        await ctx.send("Error resetting database.")

# WILL WIPE A USER'S DATA
@bot.command(name='resetmylevel')
async def resetUserData(ctx):
    authorID = str(ctx.author.id)
    try:
        c.execute(f"UPDATE userData SET userLevel = 0, userExp = 0, userSentMsgs = 0 WHERE userID = ?", (authorID, ))
        conn.commit()
        print(authorID+"'s data has been reset.")
        await ctx.send("Resetting level successful.") 
    except:
        print("Error resetting user data.")
        await ctx.send("Error resetting level.")

# WILL WIPE A USER'S DATA
@bot.command(name='giveexp')
async def giveExp(ctx, exp):
    searchQuery = ctx.author.id
    userID = ''
    userLevel = 0.00
    userExp = 0
    userMessagesSent = 0
    c.execute(f'SELECT * FROM userData WHERE userID=?', (searchQuery, ))
    fetchedRows = c.fetchall()
    for item in fetchedRows:             
        splitRow = str(item).split(", ")        
        for idx, item in enumerate(splitRow):
            splitRow[idx] = splitRow[idx].replace('(', '')
            splitRow[idx] = splitRow[idx].replace(')', '')
            splitRow[idx] = splitRow[idx].replace('\'', '')
        userID = splitRow[0]     
        userExp = int(splitRow[2]) + int(exp)
        userLevel = (levellingConstant * math.sqrt(userExp))
        userMessagesSent = int(splitRow[3]) + 1
        c.execute(f"UPDATE userData SET userID = {userID}, userLevel = {userLevel}, userExp = {ExpReward(userExp)}, userSentMsgs = {userMessagesSent} WHERE userID=?", (searchQuery, ))
        conn.commit()           
        break

# If the command is sent with 'rollhelp', query a roll from the sent dice rolling data
@bot.command(name='roll')
async def Roll(ctx, text: str):
    author = ctx.author.id
    author = ctx.author.name
    authorAvatar = ctx.author.avatar_url
    outcome = QueryRoll(text)
    embed = discord.Embed(
        title = f"{rollEmote} Rolling!",
        colour = embedColour
    )
    embed.set_thumbnail(url="https://cdn.discordapp.com/attachments/758193066913562656/767677300333477888/48cb5349f515f6e59edc2a4de294f439.png")
    embed.set_author(name=f'{author}', icon_url=authorAvatar)    
    embed.add_field(name="You Rolled", value=f"{outcome[0]}", inline=True)
    embed.add_field(name="Modifier", value=f"{outcome[1]}", inline=True)
    embed.add_field(name="Total", value=f"{outcome[2]}", inline=False)
    if len(outcome) > 3:
        embed.add_field(name="Total With Mod", value=f"{outcome[3]}", inline=True)
    
    await ctx.send(embed=embed)

# When a voice command asking to roll dice is said, convert it to text and query a roll from it
@bot.command(name='test')
async def Speech2Text(ctx,):
    # open the file
    filename = "TestCases/4d20plus4.wav"
    with sr.AudioFile(filename) as source:
        # listen for the data (load audio into memory)
        audio_data = r.record(source)
        # recognize (convert from speech to text)
        text = r.recognize_google(audio_data)

    author = ctx.author.id
    author = ctx.author.name
    authorAvatar = ctx.author.avatar_url
    outcome = QueryRoll(text)
    embed = discord.Embed(
        title = f"{rollEmote} Rolling!",
        description = f"You said: *\"{text}\"*",
        colour = embedColour
    )
    embed.set_thumbnail(url="https://cdn.discordapp.com/attachments/758193066913562656/767677300333477888/48cb5349f515f6e59edc2a4de294f439.png")
    embed.set_author(name=f'{author}', icon_url=authorAvatar)    
    embed.add_field(name="You Rolled:", value=f"{outcome[0]}", inline=False)
    embed.add_field(name="Modifier", value=f"{outcome[1]}", inline=True)
    embed.add_field(name="Total", value=f"{outcome[2]}", inline=True)
    if len(outcome) > 3:
        embed.add_field(name="Total With Mod", value=f"{outcome[3]}", inline=True)

    await ctx.send(embed=embed)

# Spawns an encounter
@bot.command(name='encounter')
@has_permissions(administrator=True, manage_messages=True, manage_roles=True)
async def Spawn_Encounter(ctx):
    # Generating an encounter  
    # Declaring variables to be used
    generalID = generalChannel
    global botID
    encounterTypeChance = 0.3
    encounterFloat = random.random()
    channelID = ctx.channel.id
    channel = bot.get_channel(channelID)
    print("here!")
    print(generalID)
    print(channelID)
    if(channelID == generalID and ctx.author.id != botID):
        global encounterType
        global encounterID 
        global encounterBool
        print("here 2!")
        if encounterFloat >= encounterTypeChance:
            encounterType = SkillRandomEncounter()
            encounterMsg = await channel.send(embed=encounterType[0])        
            encounterID = str(encounterMsg.id)
            encounterBool = True
            await encounterMsg.add_reaction(rollEmote) 
            print("here 3!")
        elif encounterFloat < encounterTypeChance:
            encounterType = DNDMonRandomEncounter()
            encounterMsg = await channel.send(embed=encounterType[0])        
            encounterID = str(encounterMsg.id)
            encounterBool = True
            print("here 4!")
            await encounterMsg.add_reaction(rollEmote)   

# Takes a string that is Regex'd to find specific dice rolling data
def QueryRoll(text):
    if re.match(r"(?:roll|rule)?(?: ?).+(?: ?)d(?: ?).+(?: ?)(?:[\+|\-|minus|plus](?: ?).+)*", text, flags=I):
        dieNum = re.findall(r"(?:(?:roll|rule)|r)?(.+)(?: ?)d(?: ?).+(?: ?)(?:[\+|\-|minus|plus](?: ?).+)*", text, flags=I)
        if re.match(r"(?: ?)a", dieNum[0]):
            dieNum[0] = 1;
        elif re.match(r"(?: ?)for", dieNum[0]):
            dieNum[0] = 4

        dieFaces = re.findall(r"(?:(?:roll|rule)|r)?(?: ?).+(?: ?)d(?: ?)(.+)(?: ?)(?:[\+|\-|minus|plus](?: ?).+)*", text, flags=I)
        if re.match(r".+(?: ?)(?:\+|\-|minus|plus)", dieFaces[0]):
            dieFaces = re.findall(r"(.+)(?: ?)(?:\+|\-|minus|plus)", dieFaces[0])

        dieModOperand = re.findall(r"(?:(?:roll|rule)|r)?(?: ?).+(?: ?)d(?: ?).+(?: ?)(\+|\-|minus|plus)(?: ?).+", text, flags=I)
        if len(dieModOperand) == 0:
            dieModOperand.append('+')
        elif dieModOperand[0] == '':
            dieModOperand[0] = '+'
        elif dieModOperand[0] == 'plus':
            dieModOperand[0] = '+'
        elif dieModOperand[0] == 'minus':
            dieModOperand[0] = '-'
        if dieModOperand[0] == '-':
            minusMod = True
        else:
            minusMod = False

        dieMod = re.findall(r"(?:(?:roll|rule)|r)?(?: ?).+(?: ?)d(?: ?).+(?: ?)[\+|\-|minus|plus](?: ?)(.+)", text, flags=I)
        if len(dieMod) == 0:
            dieMod.append(0)
        elif dieMod[0] == '':
            dieMod[0] = 0

        return RollDice(int(dieFaces[0]), int(dieNum[0]), int(dieMod[0]), minusMod)
    else:
        return 'Error in roll statement.'

# Takes int data from QueryRoll(), rolls dice based on those numbers, then outputs it in a string
def RollDice(dieSides, dieNum=1, dieMod=0, minus=False):
    dieOutcomes = ''
    dieList = []
    dieTotal = 0
    dieReturn = []

    for die in range(dieNum):
        diceRoll = random.randint(1, dieSides)
        if (diceRoll == 20 or diceRoll == 1) and dieSides == 20:
            dieList.append("__**"+str(diceRoll)+"**__")
        else:
            dieList.append(str(diceRoll))
        dieTotal += diceRoll

    dieOutcomes = ', '.join(dieList)
    dieReturn.append(f"{dieOutcomes}")
    dieReturn.append(f"{DieModConverter(dieMod, minus)}")
    if dieMod == 0:
        dieReturn.append(f"{dieTotal}")
    elif dieMod > 0:
        if minus:
            dieReturn.append(f"{dieTotal}")
            dieReturn.append(f"{dieTotal-dieMod}")
        else:
            dieReturn.append(f"{dieTotal}")
            dieReturn.append(f"{dieTotal+dieMod}")

    return dieReturn

# If the modifier is 0, it outputs 'With No Modifier', also formats '-' and '+'
def DieModConverter(dieMod, minus=False):
    output = ''
    if dieMod == 0:
        output = '*With No Modifier*'
    else:
        if minus:
            output = '*-'+str(dieMod)+'*'
        else:
            output = '*+'+str(dieMod)+'*'
    return output

# A method that is called when someone reacts the d20 to the message, calls RctExpSystem
def ClearEncounter(reaction, user):    
    botID = 715110532532797490
    global encounterBool
    global encounterType
    authorAvatar = user.avatar_url
    author = user.name
    outcome = QueryRoll("1d20")
    expReward = encounterType[1]
    rollNum = int(outcome[2])
    outcomeMsg = ''
    if str(reaction.message.id) == str(encounterID) and user.id != botID and encounterBool:   
        if rollNum == 20:
            RctExpSystem(user, int(expReward)*2)
            outcomeMsg = f'***Nat 20!*** You defeated the encounter! ***{int(expReward)*2}*** Exp rewarded!'
        elif int(rollNum) >= encounterType[2]:
            RctExpSystem(user, expReward)
            outcomeMsg = f'You defeated the encounter! **{expReward}** Exp rewarded!'  
        elif rollNum == 1:
                RctExpSystem(user, -int(expReward))
                outcomeMsg = f'***Nat 1!*** You were slain by the encounter! **{-int(expReward)}** Exp lost!'      
        else:
            outcomeMsg = 'You were defeated.'
        embed = discord.Embed(
            title = f"You rolled: {rollNum}",
            description = outcomeMsg,
            colour = discord.Colour.red()
        )        
        encounterBool = False
        embed.set_author(name=f'{author}', icon_url=authorAvatar)
        return embed

# Method to call to create a new monster encounter embedded message, stores monster data
def DNDMonRandomEncounter():    
    monsters = ["Wolf","Goblin","Bandit","Gorgon","Harpy","Green Dragon Wyrmling","Werewolf","Stone Giant"]
    experience = ["50","50","25","1800","200","450","700","2900"]
    challengeRating = ["1/4","1/4","1/8","5","1","2","3","7"]
    armourClass = [13,15,12,19,11,17,12,17]
    monPicture = ["https://media-waterdeep.cursecdn.com/avatars/thumbnails/0/54/1000/1000/636252725270715296.jpeg",
    "https://media-waterdeep.cursecdn.com/avatars/thumbnails/0/351/1000/1000/636252777818652432.jpeg",
    "https://media-waterdeep.cursecdn.com/avatars/thumbnails/0/181/1000/1000/636252761965117015.jpeg",
    "https://media-waterdeep.cursecdn.com/avatars/thumbnails/0/355/1000/1000/636252778125099430.jpeg",
    "https://media-waterdeep.cursecdn.com/avatars/thumbnails/0/391/1000/1000/636252781955908234.jpeg",
    "https://media-waterdeep.cursecdn.com/avatars/thumbnails/0/363/1000/1000/636252778639163748.jpeg",
    "https://media-waterdeep.cursecdn.com/avatars/thumbnails/0/74/1000/1000/636252734224239957.jpeg",
    "https://media-waterdeep.cursecdn.com/avatars/thumbnails/0/109/1000/1000/636252744518731463.jpeg"]
    randomInt = random.randint(0,len(monsters))

    embed = discord.Embed(
        title = f"A {monsters[randomInt]} appeared!",
        description= "Roll to attack!",
        colour = discord.Colour.red()
    )
    embed.set_thumbnail(url=f"{monPicture[randomInt]}")
    embed.set_author(name=f'Combat Encounter!', icon_url="https://i.pinimg.com/originals/48/cb/53/48cb5349f515f6e59edc2a4de294f439.png")
    embed.add_field(name=f"**AC**", value=f"{armourClass[randomInt]}", inline=True)
    embed.add_field(name=f"**CR**", value=f"{challengeRating[randomInt]}", inline=True)
    embed.add_field(name=f"**EXP**", value=f"{experience[randomInt]}", inline=True)    
    return embed, experience[randomInt], armourClass[randomInt] 

# Method to call to create a new skill encounter embedded message, stores encounter data
def SkillRandomEncounter():    
    monsters = ["A Boulder Is Falling!","Lockpick The Chest!","Withstand The Storm!","You Are Lost In A Desert","Flee The Treant!","A Thief Approaches!", "Save Rogue Bear!"]
    experience = ["100","200","350","300","1000","50", "1250"]
    challengeRating = ["1","2","3","2 1/2","5","1/2", "7"]
    armourClass = [14,15,16,14,18,12,19]
    monPicture = ["https://pbs.twimg.com/media/C8L2wgVWkAUCi32.png",
    "https://media-waterdeep.cursecdn.com/avatars/thumbnails/0/211/1000/1000/636252764731637373.jpeg",
    "https://i1.wp.com/nerdarchy.com/wp-content/uploads/2018/05/Brainstorm.png?fit=864%2C628&ssl=1",
    "https://static.wikia.nocookie.net/emerald-isles/images/8/87/Desert.jpg/revision/latest/top-crop/width/220/height/220?cb=20180209064004",
    "https://comicvine1.cbsistatic.com/uploads/original/11120/111209888/5139105-014afdf2e2481539ed8959752233f379.jpg",
    "https://roadbeerdotnet.files.wordpress.com/2020/07/thief-six-1024x1024-1.jpg",
    "https://static.wikia.nocookie.net/forgottenrealms/images/c/c3/Druid_and_bear-5e.jpg/revision/latest/scale-to-width-down/350?cb=20190808192744"]
    randomInt = random.randint(0,len(monsters))

    embed = discord.Embed(
        title = f"{monsters[randomInt]}",
        description= "Roll to test your skill!",
        colour = discord.Colour.red()
    )
    embed.set_thumbnail(url=f"{monPicture[randomInt]}")
    embed.set_author(name=f'Skill Encounter!', icon_url="https://i.pinimg.com/originals/48/cb/53/48cb5349f515f6e59edc2a4de294f439.png")
    embed.add_field(name=f"**DC**", value=f"{armourClass[randomInt]}", inline=True)
    embed.add_field(name=f"**CR**", value=f"{challengeRating[randomInt]}", inline=True)
    embed.add_field(name=f"**EXP**", value=f"{experience[randomInt]}", inline=True)    
    return embed, experience[randomInt], armourClass[randomInt] 

# A method to promote users with exp when they message
def MsgExpSystem(message, expBool):
    searchQuery = message.author.id
    stringMessage = str(message.content)
    userID = ''
    userLevel = 0.00
    userExp = 0
    userMessagesSent = 0
    c.execute(f'SELECT * FROM userData WHERE userID=?', (searchQuery, ))
    fetchedRows = c.fetchall()
    for item in fetchedRows:             
        splitRow = str(item).split(", ")        
        for idx, item in enumerate(splitRow):
            splitRow[idx] = splitRow[idx].replace('(', '')
            splitRow[idx] = splitRow[idx].replace(')', '')
            splitRow[idx] = splitRow[idx].replace('\'', '')
        userID = splitRow[0]     
        if expBool:
            userExp = int(splitRow[2]) + expPerMsg
            userLevel = (levellingConstant * math.sqrt(userExp))
        else:
            userExp = int(splitRow[2])
        userMessagesSent = int(splitRow[3]) + 1
        c.execute(f"UPDATE userData SET userID = {userID}, userLevel = {userLevel}, userExp = {ExpReward(userExp)}, userSentMsgs = {userMessagesSent} WHERE userID=?", (searchQuery, ))
        conn.commit()           
        break

# A method to promote users with exp when they complete random events
def RctExpSystem(rctUser, exp):
    searchQuery = rctUser.id
    userID = ''
    userLevel = 0
    userExp = 0
    userMessagesSent = 0
    c.execute(f'SELECT * FROM userData WHERE userID=?', (searchQuery, ))
    fetchedRows = c.fetchall()
    for item in fetchedRows:             
        splitRow = str(item).split(", ")        
        for idx, item in enumerate(splitRow):
            splitRow[idx] = splitRow[idx].replace('(', '')
            splitRow[idx] = splitRow[idx].replace(')', '')
            splitRow[idx] = splitRow[idx].replace('\'', '')
        userID = splitRow[0]
        userExp = int(splitRow[2]) + int(exp)
        userLevel = levellingConstant * math.sqrt(userExp)
        userMessagesSent = int(splitRow[3]) + 1
        c.execute(f"UPDATE userData SET userID = {userID}, userLevel = {userLevel}, userExp = {userExp}, userSentMsgs = {userMessagesSent} WHERE userID=?", (searchQuery, ))
        conn.commit()           
        break

# Split a string into characters
def splitChar(word): 
    return expPerMsg

def ExpReward(exp):
    exp = int(exp)
    return exp

def LevelUpMsg(level, user):    
    author = '@'+user.name
    authorAvatar = user.avatar_url
    embed = discord.Embed(
        title = f"You Leveled Up!",
        description = f"You are now *{level}* steps closer to the cosmos!",
        colour = discord.Colour.purple()
    )        
    embed.set_author(name=f'{author}', icon_url=authorAvatar)
    return embed

bot.run(TOKEN)

# ----------------------------------------------------------------------------------


    

 

    
