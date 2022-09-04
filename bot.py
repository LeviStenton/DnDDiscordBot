#!/usr/bin/python

# ---------------------------------------------------------------------------
# IMPORT ALL NECESSARY ASSETS TO RUN THE PROGRAMS

# Operating System
from cmath import e, log
import os
from posixpath import split
from socket import inet_ntop
import sys
from os.path import splitdrive
import threading
# Random
import random
# Math
import math
import decimal
from time import time
from unicodedata import name
# Discord
import discord
from discord import reaction
from discord import user
from discord.ext import commands
from discord.ext.commands import has_permissions, CheckFailure
# Speech Recognition
#import speech_recognition as sr
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
# Dictionary
from collections import UserList, defaultdict
from controllers.DatabaseController import DatabaseController
from controllers.DiceController import DiceController
from controllers.EncounterController import EncounterController
# Encounter classes
from models.encounters.MonsterEncounter import MonsterEncounter
from models.encounters.SkillCheckEncounter import SkillCheckEncounter
# User class
from models.user.UserRank import UserRank


# ----------------------------------------------------------------------------
# DECLARE ALL VARIABLES NECESSARY TO RUN THE PROGRAM

# Parse the bot's token, my server, and the file the text to speech reads from
# This file is in the .gitignore and you will need to create your own
load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')
#GUILD = os.getenv('DISCORD_GUILD')

# Initialize the voice recognizer
#r = sr.Recognizer()
# Emotes
rollEmote = '🎲'
voiceEmote = ':microphone2:'
prefixEmote = ':exclamation:'
levelEmote = '🛡️'
leaderboardEmote = '📜'
accountEmote = ':desktop:'
cowboyEmote = ':cowboy:'
tickEmote = '✔️'
crossEmote = '❌'
challengeEmote = '⚔️'
equipmentEmote = '🗡️'
encounterEmote = '👹'
# Colours
embedColour = discord.Colour.dark_blue()
challengeColour = discord.Color.dark_orange()
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
bot = commands.Bot(command_prefix=ReadCommandPrefix(), intents=intents, activity = discord.Activity(type = discord.ActivityType.listening, name = f"{ReadCommandPrefix()}help"))  
# Remove the in-built help command to write my own
bot.remove_command("help")
# PvP variables for Challenges
challengesDict = defaultdict(dict)
challengeCount = 0
# Global channel variables
generalChannel = 0
levelUpChannel = 0
pvpChannel = 0
# Global ID variables
botID = 0
# Controllers
encounterCont: EncounterController = None

# ---------------------------------------------------------------------------
# ON EVENT METHODS

# When joining a server for the first time, send a message
@bot.event
async def on_guild_join(guild):
    channels = bot.get_all_channels()
    general = discord.utils.get(channels, name="general")
    await general.send(f":cowboy: Eyes up Moon Cowboys, I'm connected! Type **{ReadCommandPrefix()}help** to get started.")

# On ready, get channel IDs
@bot.event
async def on_ready():
    await bot.wait_until_ready()
    channels = bot.get_all_channels()
    for channel in channels:
        if(channel.name == "general"):
            global generalChannel
            generalChannel = channel
        if(channel.name == "level-ups"):
            global levelUpChannel
            levelUpChannel = channel
        if(channel.name == "pvp"):
            global pvpChannel
            pvpChannel = channel
    global botID
    botID = bot.user.id
    global encounterCont
    encounterCont = EncounterController()


# On disconnecting, send a message
@bot.event
async def close():     
    DatabaseController().CloseDatabase() 
    for vc in bot.voice_clients: 
        await vc.disconnect()
    
# When a member joins the server, send a welcoming message
@bot.event
async def on_member_join(member, role):
    global generalChannel
    print(f"{member.id} joined!")
    role = discord.utils.get(member.guild.roles, id='272748337256726528')
    embed = discord.Embed(
        title = f"{cowboyEmote} Eyes up",
        description = "You're a ｍｏｏｎ 𝒸𝑜𝓌𝒷𝑜𝓎 now.",
        colour = embedColour
    )
    embed.set_author(name=member.name, icon_url=member.display_avatar)
    DatabaseController().StoreNewUser(member, role)       
    await generalChannel.send(embed=embed)

# Method to do things when a message is sent
@bot.event
async def on_message(message):
    # If messages are sent to the bot through DMs, do not count for anything
    if (isinstance(message.channel, discord.channel.DMChannel)):
        pass
    else:
        # Declaring variables to be used
        global generalChannel
        global levelUpChannel
        messageChannel = bot.get_channel(message.channel.id)
        channelHistoryLength = 50
        expBool = True

        # Rate limiting the exp users gain from messages
        if(message.author.id != botID):
            channelMessages = [message async for message in message.channel.history(limit=channelHistoryLength, after=(datetime.now() + timedelta(seconds=3)))]   
            for chnlMsg in channelMessages:
                if chnlMsg.author.id == message.author.id:
                    expBool = False 
            DatabaseController().StoreUserExp(message.author.id, expBool, levelUpChannel)                    

        # Generating an encounter 
        global encounterCont    
        if(messageChannel.id == generalChannel.id and message.author.id != botID): 
            try:   
                encounterMsg = await messageChannel.send(embed=encounterCont.RollEncounter(message.author))
                encounterCont.encounterID = encounterMsg.id
                await encounterMsg.add_reaction(rollEmote) 
            except Exception:
                pass
        await bot.process_commands(message) 

# Method to do things when a reaction is added
@bot.event
async def on_reaction_add(reaction, user):
    global generalChannel
    global levelUpChannel
    global pvpChannel
    global encounterCont

    if(reaction.emoji == rollEmote and user.id != botID):
        await pvpChannel.send(embed=await FightPlayer(reaction.message, user))

    if encounterCont.encounterUserID == user.id and reaction.emoji == encounterCont.rollEmote and user.id != botID and reaction.message.id == encounterCont.encounterID and encounterCont.encounterActive:
        encClearMsg = await generalChannel.send(embed=encounterCont.ClearEncounter(user, levelUpChannel))
        encounterCont.encClearID = encClearMsg.id 
        if encounterCont.lootDropChance <= encounterCont.lootDropThresh and encounterCont.encClearSuccess:
            await encClearMsg.add_reaction(encounterCont.tickEmote)
    if user.id == encounterCont.encounterUserID and user.id != botID and reaction.message.id == encounterCont.encClearID and reaction.emoji == encounterCont.tickEmote:
        DatabaseController().StoreUserEquipment(user.id, encounterCont.encClearLoot)           

# ---------------------------------------------------------------------------
# COMMAND METHODS

# If the command is sent with 'help', send a message showing ways to use the bot
@bot.command(name='help')
async def help(ctx):
    author = ctx.author.name
    authorAvatar = ctx.author.display_avatar
    embed = discord.Embed(
        title = "Help Commands",
        description = "A list of how to use each command available:",
        colour = embedColour
    )
    embed.set_author(name=f'{author}', icon_url=authorAvatar)
    embed.add_field(name=f"{rollEmote} Dice rolling:", value=f"To roll, type something like: **{ReadCommandPrefix()}roll 1d20**\nThe modifiers '+' or '-' may be added: **{ReadCommandPrefix()}roll 1d20+3**", inline=False)
    embed.add_field(name=f"{challengeEmote} PvP:", value=f"To challenge another player, type: **{ReadCommandPrefix()}challenge @<opponent> <expamount>**", inline=False)
    embed.add_field(name=f"{leaderboardEmote} Leaderboard:", value=f"To view the leaderboard, type: **{ReadCommandPrefix()}leaderboard**", inline=False)
    embed.add_field(name=f"{levelEmote} Rank:", value=f"To view your or another user's level stats, type: **{ReadCommandPrefix()}rank <otheruser>**", inline=False)
    embed.add_field(name=f"{equipmentEmote} Equipment:", value=f"To view your or another user's current equipment, type: **{ReadCommandPrefix()}equipment <otheruser>**", inline=False)
    embed.add_field(name=f"{encounterEmote} Encounter Statistics:", value=f"To view the statistics for encounters, type: **{ReadCommandPrefix()}encounterstats**", inline=False)
    embed.add_field(name=f"{accountEmote} Account Info:", value=f"To view your or another user's account info, type: **{ReadCommandPrefix()}userinfo <otheruser>**", inline=False)
    embed.add_field(name=f"{prefixEmote} Command Prefixes:", value=f"To change the prefix, type: **{ReadCommandPrefix()}setprefix <prefix>** \nNote: you must be an administrator to do this", inline=False)
    await ctx.send(embed=embed)

# Sets a new prefix
@bot.command(name='setprefix')
@has_permissions(administrator=True, manage_messages=True, manage_roles=True)
async def set_prefix(ctx, newPrefix):    
    acceptablePrefixes = ['!' ,'@' ,'#' ,'$' ,'%' ,'^' ,'&' ,'*' ,'(' ,')' ,'-' ,'=' ,'_' ,'+']
    authorName = ctx.author.name
    authorAvatar = ctx.author.display_avatar
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
    authorAvatar = ctx.author.display_avatar
    global prefixPath
    prefixPath = f"prefixes/{guild}-prefix.txt"
    tempPrefix = ReadCommandPrefix()
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
# @bot.command(name='join')
# async def join_voice(ctx):
#     author = ctx.author.name
#     authorAvatar = ctx.author.display_avatar
#     embedMessage = '' 
#     connected = None
#     channel = None
#     try:
#         connected = ctx.author.voice
#         channel = ctx.author.voice.channel        
#     except:
#         embedMessage = f"You need to join a voice channel first!"
#     try:
#         if connected:           
#             await channel.connect()          
#             for client in bot.voice_clients:
#                 if client.channel == channel:
#                     embedMessage = f"I've connected to **{str(channel)}**!"
#     except:
#         embedMessage = f"I\'m already connected to **{str(channel)}**."
#     joinEmbed = discord.Embed(
#         title = f"{voiceEmote} Connecting...",
#         description = embedMessage,
#         colour = embedColour
#     )
#     joinEmbed.set_author(name=f'{author}', icon_url=authorAvatar) 
#     await ctx.send(embed=joinEmbed)

# # If the command is sent with 'leave', leave all voice channels    
# @bot.command(name='leave')
# async def leave_voice(ctx):
#     for vc in bot.voice_clients: 
#         if(vc.guild == ctx.guild):
#             await vc.disconnect()
#             joinEmbed = discord.Embed(
#                 title = f"{voiceEmote} Leaving...",
#                 description = f"Left!",
#                 colour = embedColour
#             )
#             joinEmbed.set_author(name=f'{ctx.message.author.name}', icon_url=ctx.author.display_avatar) 
#             await ctx.send(embed=joinEmbed)
       
# Retrieves member, exp, and level data from levellingDB
@bot.command(name='rank')
async def req_rank(ctx, userName = None):
    dbCont = DatabaseController()
    user = FixUser(ctx, userName)
    embed = discord.Embed(
        title = f"{levelEmote} Your stats for {ctx.guild}",
        colour = embedColour
    )
    userRankRaw = dbCont.RetrieveUserRank(user.id)
    userRank = UserRank(user.display_name, user.display_avatar, userRankRaw[0], userRankRaw[1], userRankRaw[2], userRankRaw[3])
    embed.set_thumbnail(url="https://cdn.discordapp.com/attachments/758193066913562656/767867171391930458/ApprovingElite.png")
    embed.set_author(name=f'{userRank.displayName}', icon_url=userRank.avatar)      
    embed.add_field(name="Level:", value=f"{userRank.level}", inline=False)
    embed.add_field(name=f"Exp:", value=f"{userRank.exp}", inline=False)
    embed.add_field(name=f"Exp Until Next Level:", value=f"{userRank.expRemaining}", inline=False)
    embed.add_field(name=f"Messages Sent:", value=f"{userRank.msgSent}", inline=False)   
    await ctx.send(embed=embed)

# Retrieves member, exp, and level data from levellingDB
@bot.command(name='leaderboard')
async def req_leaderboard(ctx):
    user = ctx.author
    userIdx = None
    author = user.name
    authorAvatar = user.display_avatar
    guild = ctx.guild
    embed = discord.Embed(
        title = f"{leaderboardEmote} The leaderboard for {guild}",
        colour = embedColour
    )
    embed.set_thumbnail(url="https://cdn.discordapp.com/attachments/758193066913562656/767867171391930458/ApprovingElite.png")
    embed.set_author(name=f'{author}', icon_url=authorAvatar)  
    leaderboardList = DatabaseController().RetrieveAllUsers(ctx)
    leaderboardList.sort(key=lambda member: int(member[2]), reverse=True)    
    userInTopTen = False
    for idx, item in enumerate(leaderboardList): 
        if(int(leaderboardList[idx][4]) == int(user.id)):
            if(idx < 10):
                userInTopTen = True
            userIdx = idx
            break
    leaderboardList = leaderboardList[:10]
    for idx, item in enumerate(leaderboardList):   
        embed.add_field(name=str(idx+1)+". "+leaderboardList[idx][0], value=f"Level: {leaderboardList[idx][1]}, Exp: {leaderboardList[idx][2]}", inline=True)
    if(not userInTopTen):
        userList = DatabaseController().RetrieveUserRank(user.id)
        embed.add_field(name=f"*{str(userIdx)}. {userList[0]}*", value=f"*Level: {userList[1]}, Exp: {userList[2]}*", inline=False)
    await ctx.send(embed=embed)

# Retrieves user account info based on their public profile
@bot.command(name='userinfo')
async def req_userinfo(ctx, userName = None):
    user = FixUser(ctx, userName)
    authorName = user.name
    authorAvatar = user.display_avatar
    currentTime = datetime.now()
    accCreatedAt = str(user.created_at).split(" ")
    accJoinedAt = str(user.joined_at).split(" ")
    timeCreated = accCreatedAt[1].split(".")
    timeJoined = accJoinedAt[1].split(".")
    timeSinceAccCreated = str(currentTime - user.created_at).split(",")
    timeSinceAccJoined = str(currentTime - user.joined_at).split(",")
    authorNick = user.nick
    authorID = user.id
    authorRoles = ""
    if(len(user.roles) != 0):
        for idx, role in enumerate(user.roles):
            authorRoles = authorRoles+"<@&"+str(role.id)+"> "
            
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

# Retrieves user account info based on their public profile
@bot.command(name='encounterstats')
async def encounterStats(ctx):
    global encounterCont
    embed = discord.Embed(
        title = f"{encounterEmote} Encounter Statistics",
        colour = embedColour
    )
    embed.set_author(name=f'{ctx.author.name}', icon_url=ctx.author.display_avatar)  
    embed.add_field(name=f"Encounter Spawn", value=f"{decimal.Decimal(encounterCont.encounterDropChance*100).normalize()}%", inline=True)  
    embed.add_field(name=f"Loot Drop", value=f"{decimal.Decimal(encounterCont.lootDropThresh*100).normalize()}%", inline=True) 
    await ctx.send(embed=embed)  

# DO NOT USE THIS UNLESS YOU WANT TO WIPE ALL LEVEL DATA
@bot.command(name='ResetServerRankData')
@has_permissions(administrator=True, manage_messages=True, manage_roles=True)
async def collectLevelData(ctx):
    try:
        if(ctx.message.author.id == 218890729550774282):
            DatabaseController().ResetServerRankData(ctx)
            print("Storing fresh data successful.")
            await ctx.send("Storing fresh data successful.")
    except:
        print("Error resetting database.")
        await ctx.send("Error resetting database.")

# WILL WIPE A USER'S DATA
@bot.command(name='ResetMyData')
async def resetUserData(ctx):
    authorID = str(ctx.author.id)
    try:
        DatabaseController().ResetUserData(authorID)
        print(authorID+"'s data has been reset.")
        await ctx.send("Resetting level successful.") 
    except:
        print("Error resetting user data.")
        await ctx.send("Error resetting level.")

# Give yourself as much EXP as specified
# @bot.command(name='giveexp')
# @has_permissions(administrator=True, manage_messages=True, manage_roles=True)
# async def giveExp(ctx, exp):
#     searchQuery = ctx.author.id
#     userID = ''
#     userLevel = 0.00
#     userExp = 0
#     userMessagesSent = 0
#     c.execute(f'SELECT * FROM userData WHERE userID=?', (searchQuery, ))
#     fetchedRows = c.fetchall()
#     for item in fetchedRows:             
#         splitRow = str(item).split(", ")        
#         for idx, item in enumerate(splitRow):
#             splitRow[idx] = splitRow[idx].replace('(', '')
#             splitRow[idx] = splitRow[idx].replace(')', '')
#             splitRow[idx] = splitRow[idx].replace('\'', '')
#         userID = splitRow[0]     
#         userExp = int(splitRow[2]) + int(exp)
#         userLevel = (levellingConstant * math.sqrt(userExp))
#         userMessagesSent = int(splitRow[3]) + 1
#         c.execute(f"UPDATE userData SET userID = {userID}, userLevel = {userLevel}, userExp = {ExpReward(userExp)}, userSentMsgs = {userMessagesSent} WHERE userID=?", (searchQuery, ))
#         conn.commit()           
#         break

# If the command is sent with 'rollhelp', query a roll from the sent dice rolling data
@bot.command(name='roll')
async def Roll(ctx, text: str):
    author = ctx.author.id
    author = ctx.author.name
    authorAvatar = ctx.author.display_avatar
    outcome = DiceController().QueryRoll(text)
    embed = discord.Embed(
        title = f"{rollEmote} Rolling!",
        colour = embedColour
    )
    embed.set_thumbnail(url="https://cdn.discordapp.com/attachments/758193066913562656/767677300333477888/48cb5349f515f6e59edc2a4de294f439.png")
    embed.set_author(name=f'{author}', icon_url=authorAvatar)    
    embed.add_field(name="You Rolled", value=f"{outcome[0]}", inline=True)
    embed.add_field(name="Modifier", value=f"{outcome[1]}", inline=True)
    if len(outcome) > 3:
        embed.add_field(name="Total With Mod", value=f"{outcome[3]}", inline=True)    
    await ctx.send(embed=embed)

# When a voice command asking to roll dice is said, convert it to text and query a roll from it
# @bot.command(name='test')
# async def Speech2Text(ctx,):
#     # open the file
#     filename = "TestCases/4d20plus4.wav"
#     with sr.AudioFile(filename) as source:
#         # listen for the data (load audio into memory)
#         audio_data = r.record(source)
#         # recognize (convert from speech to text)
#         text = r.recognize_google(audio_data)

#     authorName = ctx.author.name
#     authorAvatar = ctx.author.display_avatar
#     outcome = QueryRoll(text)
#     embed = discord.Embed(
#         title = f"{rollEmote} Rolling!",
#         description = f"You said: *\"{text}\"*",
#         colour = embedColour
#     )
#     embed.set_thumbnail(url="https://cdn.discordapp.com/attachments/758193066913562656/767677300333477888/48cb5349f515f6e59edc2a4de294f439.png")
#     embed.set_author(name=f'{authorName}', icon_url=authorAvatar)    
#     embed.add_field(name="You Rolled:", value=f"{outcome[0]}", inline=False)
#     embed.add_field(name="Modifier", value=f"{outcome[1]}", inline=True)
#     if len(outcome) > 3:
#         embed.add_field(name="Total With Mod", value=f"{outcome[3]}", inline=True)

#     await ctx.send(embed=embed)

# Spawns an encounter
@bot.command(name='encounter')
@has_permissions(administrator=True, manage_messages=True, manage_roles=True)
async def Spawn_Encounter(ctx):
    # Generating an encounter  
    global encounterCont
    global generalChannel
    if(ctx.channel.id == generalChannel.id and ctx.author.id != botID and encounterCont.encounterProcFloat < encounterCont.encounterChance):
        encounterMsg = await generalChannel.send(embed=encounterCont.RollEncounter(ctx.author, 1))
        encounterCont.encounterID = encounterMsg.id
        await encounterMsg.add_reaction(rollEmote)  

# Display the current equipment and modifier for a user that calls this command
@bot.command(name='equipment')
async def ShowEquipment(ctx, userName = None):
    user = FixUser(ctx, userName)
    userData = DatabaseController().RetrieveUser(user.id)
    embed = discord.Embed(
        title = f"Your Equipment",
        colour = embedColour
    )
    embed.set_thumbnail(url="https://cdn.discordapp.com/attachments/758193066913562656/767677300333477888/48cb5349f515f6e59edc2a4de294f439.png")
    embed.set_author(name=f'{user.display_name}', icon_url=user.display_avatar)    
    embed.add_field(name="Item", value=f"{userData[4]}", inline=True)
    embed.add_field(name="Modifier", value=f"{userData[5]}", inline=True)
    await ctx.send(embed=embed)

# Ping another player to fight
@bot.command(name='challenge')
async def ChallengePlayer(ctx, opponent: discord.User, wager: str):
    global pvpChannel
    if(ctx.channel.id == pvpChannel.id):
        global challengesDict
        challengerID = None
        challengerName = None
        challengerMod = None
        challengerEquip = None
        opponentID = None
        opponentName = None
        opponentMod = None
        opponentEquip = None
        print(challengesDict)
        embedTitle = ''
        embed = discord.Embed(
            title = embedTitle,
            colour = challengeColour
        )
        if(int(wager) >= 0):                
            challenger = ctx.author  
            if(challenger.id == opponent.id):
                embedTitle = 'You cannot challenge yourself.'
                embed.add_field(name='You cannot challenge yourself.', value="You must challenge another user.", inline=True)
            else:
                embedTitle = 'A New Challenger Approaches!'
                challengerID = challenger.id
                challengerName = challenger.name
                challengerAvatar = challenger.display_avatar
                challengerExp = 0
                challengerMod = ""
                challengerEquip = ""    
                challengerData = DatabaseController().RetrieveUser(str(challengerID))  
                challengerExp = challengerData[2]
                challengerMod = challengerData[4]
                challengerEquip = challengerData[5]

                opponentID = opponent.id
                opponentName = opponent.name
                opponentAvatar = opponent.display_avatar
                opponentExp = 0
                opponentMod = ""
                opponentEquip = ""           
                opponentData = DatabaseController().RetrieveUser(opponentID)    
                opponentExp = opponentData[2]
                opponentMod = opponentData[4]
                opponentEquip = opponentData[5]
                    
                if(int(challengerExp) < int(wager) and int(opponentExp) < int(wager)):
                    raise Exception(challengerName+' does not have enough exp.\n'+opponentName+' does not have enough exp.')
                elif(int(challengerExp) < int(wager)):
                    raise Exception(challengerName+' does not have enough exp.')
                elif(int(opponentExp) < int(wager)):
                    raise Exception(opponentName+' does not have enough exp.')
                embed.set_thumbnail(url="https://cdn.discordapp.com/attachments/758193066913562656/767677300333477888/48cb5349f515f6e59edc2a4de294f439.png")
                embed.set_author(name=f'{challengerName}', icon_url=challengerAvatar)    
                embed.add_field(name=challengerName, value=f"{challengerEquip}, +{challengerMod}", inline=True)
                embed.add_field(name=f"***WAGERING***", value=f"***{wager}xp AGAINST***", inline=True)
                embed.add_field(name=opponentName, value=f"{opponentEquip}, +{opponentMod}", inline=True)
                embed.add_field(name=f"TO ACCEPT,", value=f"*Click the dice to fight!*", inline=False)
                embed.set_footer(text=opponentName, icon_url=opponentAvatar)    

            challenge = await ctx.send(embed=embed)
            if(embedTitle == 'A New Challenger Approaches!'):
                dictKeyName = str(opponentID)+'_'+str(challenge.id)
                challengesDict[dictKeyName][0] = {'challengerID' : challengerID, 'challengerName' : challengerName, 'challengerEquip' : challengerEquip, 'challengerMod' : challengerMod}
                challengesDict[dictKeyName][1] = {'opponentID' : opponentID, 'opponentName' : opponentName, 'opponentEquip' : opponentEquip, 'opponentMod' : opponentMod}
                challengesDict[dictKeyName][2] = {'challengeID' : challenge.id, 'challengeWager' : wager}
                await challenge.add_reaction(rollEmote)

async def FightPlayer(reactionMessage, reactingUser):
    global challengesDict
    dictKeyName = str(reactingUser.id)+'_'+str(reactionMessage.id)
    print(str(reactingUser.id)+'_'+str(reactionMessage.id))
    global levelUpChannel
    print(challengesDict)
    if(challengesDict[dictKeyName].get(1).get('opponentID') == reactingUser.id and challengesDict[dictKeyName].get(2).get('challengeID') == reactionMessage.id):
        embedTitle = ""
        embed = discord.Embed(
            title = embedTitle,
            colour = challengeColour
        )
        challenger = challengesDict[dictKeyName].get(0)
        challengerID = challenger.get('challengerID')
        challengerName = challenger.get('challengerName')
        challengerMod = challenger.get('challengerMod')
        challengerRoll = DiceController().QueryRoll(f'1d20+{challengerMod}')
        challengerRollTotal = challengerRoll[3] if int(challengerMod) > 0 else challengerRoll[0]
        opponent = challengesDict[dictKeyName].get(1)
        opponentID = opponent.get('opponentID')
        opponentName = opponent.get('opponentName')
        opponentMod = opponent.get('opponentMod')
        opponentRoll = DiceController().QueryRoll(f'1d20+{opponentMod}')
        opponentRollTotal = opponentRoll[3] if int(opponentMod) > 0 else opponentRoll[0]
        challengeWager = challengesDict[dictKeyName].get(2).get('challengeWager')
        outcome = int(challengerRollTotal) > int(opponentRollTotal)
        tie = challengerRoll == opponentRoll  
        embed.set_thumbnail(url="https://cdn.discordapp.com/attachments/758193066913562656/767677300333477888/48cb5349f515f6e59edc2a4de294f439.png")
        embed.add_field(name=challengerName, value=f"**{challengerRollTotal}** (*{challengerRoll[0]}, +{challengerMod}*)", inline=True)
        if(tie):
            embed.add_field(name='**Tie!**', value="No one wins.", inline=True)
        else:
            embed.add_field(name="***WINS OVER***" if outcome else "***LOSES TO***", value=f"*Winning **{challengeWager}**xp*", inline=True)             
            DatabaseController().StoreUserExp(challengerID if outcome else opponentID, True, levelUpChannel, int(challengeWager))
            DatabaseController().StoreUserExp(opponentID if outcome else challengerID, True, levelUpChannel, -int(challengeWager))
        embed.add_field(name=opponentName, value=f"**{opponentRollTotal}** (*{opponentRoll[0]}, +{opponentMod}*)", inline=True)
        challengesDict.pop(dictKeyName)  
        return embed

def FixUser(ctx, userName):
    if(userName != None):
        userNameInt = int(str(userName).replace('<', '').replace('>', '').replace('@', ''))
        return bot.get_user(userNameInt)
    else:
        return ctx.author

bot.run(TOKEN)

# ----------------------------------------------------------------------------------