#!/usr/bin/python

# ---------------------------------------------------------------------------
# IMPORT ALL NECESSARY ASSETS TO RUN THE PROGRAMS

# Async
from asyncio.tasks import wait_for
# Operating System
import os
from os.path import splitdrive
# Random
import random
from typing import Text
# Discord
import discord
from discord.ext import commands
from discord.ext.commands import has_permissions, CheckFailure
# Speech Recognition
import speech_recognition as sr
# Regex
import re
from re import I
# .env
from dotenv import load_dotenv
# .csv
import csv
# SQLite
import sqlite3
# Datetime
from datetime import datetime

# ----------------------------------------------------------------------------
# DECLARE ALL VARIABLES NECESSARY TO RUN THE PROGRAM

# Parse the bot's token, my server, and the file the text to speech reads from
load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')
GUILD = os.getenv('DISCORD_GUILD')

# Initialize the database
conn = sqlite3.connect('databases/levellingDB.db')
c = conn.cursor()
# Initialize the voice recognizer
r = sr.Recognizer()
# Emotes
rollEmote = '<:d20:766295310129430568>'
voiceEmote = ':microphone2:'
prefixEmote = ':exclamation:'
restartEmote = ':electric_plug:'
levelEmote = ':crossed_swords:'
accountEmote = ':desktop:'
cowboyEmote = ':cowboy:'
# Embed Colour
embedColour = discord.Colour.orange()
# Write to the prefix file
def WriteCommandPrefix(prefix):
    commandPrefix = open("prefix.txt", "w")
    commandPrefix.write(prefix)
    commandPrefix.close()
# Write to the prefix file
def ReadCommandPrefix():
    commandPrefix = open("prefix.txt", "r")
    return commandPrefix.read()
intents = discord.Intents.default()
intents.members = True
# Sets the bot's command prefix to the prefix in prefix.txt
bot = commands.Bot(command_prefix=ReadCommandPrefix(), intents=intents)  
# Remove the in-built help command to write my own
bot.remove_command("help")
# ---------------------------------------------------------------------------
# ON EVENT METHODS

# When joining a server for the first time, send a message
@bot.event
async def on_guild_join():
    channel = bot.get_channel(449967222652141568)
    await channel.send(f":cowboy: Eyes up Moon Cowboys, I'm connected! Type **{ReadCommandPrefix()}help** to get started.")

# On ready, set the custom status
@bot.event
async def on_ready():
    await bot.change_presence(activity = discord.Activity(type = discord.ActivityType.listening, name = f"{ReadCommandPrefix()}help"))

# On disconnecting, send a message
@bot.event
async def close():
    channel = bot.get_channel(449967222652141568)      
    conn.close()  
    for vc in bot.voice_clients:        
        await vc.disconnect()
    
# When a member joins the server, send a welcoming message
@bot.event
async def on_member_join(member):
    print(f"{member.id} joined!")
    memberID = str(member.id)
    author = member.name
    authorAvatar = member.avatar_url
    role = discord.utils.get(member.guild.roles, name='ｄｅｂｒｉｓ 𝓭𝓻𝓲𝓯𝓽𝓮𝓻𝓼')
    channel = bot.get_channel(449967222652141568)
    embed = discord.Embed(
        title = f"{cowboyEmote} Eyes up",
        description = "You're a ｍｏｏｎ 𝒸𝑜𝓌𝒷𝑜𝓎 now.",
        colour = embedColour
    )
    embed.set_author(name=author, icon_url=authorAvatar)
    c.execute(f"INSERT IGNORE INTO userData VALUES (?,0,0,0)", (memberID, ))
    conn.commit()              
    await member.add_roles(role)
    await channel.send(embed=embed)

# Method to do things when a message is sent
@bot.event
async def on_message(message):
    guild = bot.get_guild(249391493880479744)
    searchQuery = message.author.id
    stringMessage = str(message.content)
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
        userLevel = int(splitRow[1])
        userExp = int(splitRow[2]) + len(splitChar(stringMessage))
        userMessagesSent = int(splitRow[3]) + 1
        c.execute(f"UPDATE userData SET userID = {userID}, userLevel = {userLevel}, userExp = {userExp}, userSentMsgs = {userMessagesSent} WHERE userID=?", (searchQuery, ))
        conn.commit()    
        break 
    await bot.process_commands(message)   

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
    embed.add_field(name=f"{restartEmote} Restarting:", value=f"To restart the bot, type: **{ReadCommandPrefix()}restart** \nNote: you must be an administrator to do this", inline=False)
    await ctx.send(embed=embed)

# Sets a new prefix
@bot.command(name='setprefix')
@has_permissions(administrator=True, manage_messages=True, manage_roles=True)
async def set_prefix(ctx, newPrefix):    
    acceptablePrefixes = ['!' ,'@' ,'#' ,'$' ,'%' ,'^' ,'&' ,'*' ,'(' ,')' ,'-' ,'=' ,'_' ,'+']
    author = ctx.author.name
    authorAvatar = ctx.author.avatar_url
    embedMessage = ''
    if newPrefix == ReadCommandPrefix():
        embedMessage = f"The command prefix is already: **{ReadCommandPrefix()}**!"
    else:
        for prefix in acceptablePrefixes:
            if str(newPrefix) == prefix:            
                WriteCommandPrefix(newPrefix)
                embedMessage = f"You changed the command prefix to: **{ReadCommandPrefix()}**\nRestart the bot for the changes to take effect."
                break
            
            else:
                embedMessage = f"You must use one of the following symbols: **` ~ ! @ # $ % ^ & * ( ) _ + - =**"
    embed = discord.Embed(
        title = f"{prefixEmote} Setting Prefix...",
        description = embedMessage,
        colour = embedColour
    )
    embed.set_author(name=f'{author}', icon_url=authorAvatar)
    await ctx.send(embed=embed)

# BROKEN, FIX SOON
@bot.command(name='restart')
@has_permissions(administrator=True, manage_messages=True, manage_roles=True)
async def restart_bot(ctx):
    restartDesc = ""
    try:
        reboot = subprocess.call("restart.bash")
        restartDesc = "Restarted!"   
    except:
        restartDesc = "Failed!"
    embed = discord.Embed(
            title = f"{restartEmote} Restarting...",
            description = restartDesc,
            colour = embedColour
        )
    await ctx.send(embed=embed)        

# If the command is sent with 'join', join the voice channel that the autor is in
@bot.command(name='join')
async def join_voice(ctx):
    connected = ctx.author.voice
    channel = ctx.author.voice.channel
    author = ctx.author.name
    authorAvatar = ctx.author.avatar_url
    embedMessage = ''       
    try:
        if connected:
            await connected.channel.connect()
            for client in bot.voice_clients:
                if client.channel == channel:
                    embedMessage = f"I've connected to **{str(channel)}**!"
    except:
        embedMessage = f"I\'m already connected to **{str(channel)}**."
    embed = discord.Embed(
        title = f"{voiceEmote} Connecting...",
        description = embedMessage,
        colour = embedColour
    )
    embed.set_author(name=f'{author}', icon_url=authorAvatar) 
    await ctx.send(embed=embed)

# If the command is sent with 'leave', leave all voice channels    
@bot.command(name='leave')
async def leave_voice(ctx):
    for vc in bot.voice_clients:
            if vc.guild == ctx.guild:
                await vc.disconnect()              

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
    try:
        c.execute(f'SELECT * FROM userData WHERE userID=?', (searchQuery, ))
        fetchedRows = c.fetchall()
        for item in fetchedRows:             
            splitRow = str(item).split(", ")        
            for idx, item in enumerate(splitRow):
                splitRow[idx] = splitRow[idx].replace('(', '')
                splitRow[idx] = splitRow[idx].replace(')', '')
                splitRow[idx] = splitRow[idx].replace('\'', '')
                print(splitRow[idx])                              
            embed.add_field(name="Level:", value=f"{splitRow[1]}", inline=False)
            embed.add_field(name=f"Exp:", value=f"{splitRow[2]}", inline=False)
            embed.add_field(name=f"Messages Sent:", value=f"{splitRow[3]}", inline=False) 
            pass      
    except:
        embed.add_field(name="Error", value=f"Could not retriece data.", inline=False)
    print("Author: "+str(ctx.author.id))
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
    guild = ctx.guild
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
    embed.add_field(name="You Rolled:", value=f"{outcome[0]}", inline=False)
    embed.add_field(name="Modifier:", value=f"{outcome[1]}", inline=False)
    embed.add_field(name="Total:", value=f"{outcome[2]}", inline=False)
    if len(outcome) > 3:
        embed.add_field(name="Total With Mod:", value=f"{outcome[3]}", inline=False)
    
    await ctx.send(embed=embed)

# When a voice command asking to roll dice is said, convert it to text and query a roll from it
@bot.command(name='test')
async def Speech2Text(ctx,):
    # open the file
    filename = "/home/pi/TheMoonCowboy/TestCases/4d20plus4.wav"
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
    embed.add_field(name="Modifier:", value=f"{outcome[1]}", inline=False)
    embed.add_field(name="Total:", value=f"{outcome[2]}", inline=False)
    if len(outcome) > 3:
        embed.add_field(name="Total With Mod:", value=f"{outcome[3]}", inline=False)

    await ctx.send(embed=embed)

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

# Split a string into characters
def splitChar(word): 
    return [char for char in word]

bot.run(TOKEN)

# ----------------------------------------------------------------------------------


    

 

    
