#!/usr/bin/python

# ---------------------------------------------------------------------------
# IMPORT ALL NECESSARY ASSETS TO RUN THE PROGRAMS

# Operating System
import os
from unicodedata import name
# Discord
import discord
from discord import app_commands
from discord.ext import tasks
# Speech Recognition
#import speech_recognition as sr
# .env 
from dotenv import load_dotenv
# Datetime
from datetime import datetime
from datetime import timedelta
import asyncio
# Dictionary
from collections import defaultdict
# Controllers
from controllers.DatabaseController import DatabaseController
from controllers.DiceController import DiceController
from controllers.EncounterController import EncounterController
from controllers.RaidController import RaidController
from controllers.PollController import PollController
from models.encounters.IEncounterable import IEncounterable
from models.polls.poll import Poll
from models.polls.poll import Option
# User class
from models.user.UserRank import UserRank
# Groq
import groq


# ----------------------------------------------------------------------------
# DECLARE ALL VARIABLES NECESSARY TO RUN THE PROGRAM

# Parse the bot's token, my server, and the file the text to speech reads from
# This file is in the .gitignore and you will need to create your own
load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')

class client(discord.Client):
    def __init__(self):
        super().__init__(intents=discord.Intents.all())       

global bot
bot: discord.Client = client()
tree = app_commands.CommandTree(bot)

# Initialize OpenAI client
client = groq.AsyncGroq(
    api_key=os.environ.get('GROQ_API_KEY')
)
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
huntEmote = '👹'
raidEmote = '☠️'
# Colours
embedColour = discord.Colour.dark_blue()
challengeColour = discord.Color.dark_orange()
# PvP variables for Challenges
challengesDict = defaultdict(dict)
challengeCount = 0
# Raid variables
initiationCost: int = 50
raidPreludeTimer: int = 10
raidConclusionTimer: int = 30
# Global channel variables
generalChannel: discord.channel = None
privateChannel: discord.channel = None
eventsChannel: discord.ForumChannel = None
levelUpChannel: discord.channel = None
pvpChannel: discord.channel = None
huntChannel: discord.channel = None
raidChannel: discord.channel = None
# Global ID variables
botID = 0
guildID = 249391493880479744
# Controllers
encounterCont: EncounterController = None
raidCont: RaidController = None
pollCont: PollController = None

# ---------------------------------------------------------------------------
# ON EVENT METHODS

# When joining a server for the first time, send a message
@bot.event
async def on_guild_join(guild):
    channels = bot.get_all_channels()
    general = discord.utils.get(channels, name="general")
    await general.send(f":cowboy: Eyes up Moon Cowboys, I'm connected!") # Type **{ReadCommandPrefix()}help** to get started.")

# On ready, get channel IDs
@bot.event
async def on_ready():
    await tree.sync(guild=discord.Object(id=guildID))
    channels = bot.get_all_channels()
    for channel in channels:
        if(channel.name == "general"):
            global generalChannel
            generalChannel = channel
        if(channel.name == "private"):
            global privateChannel
            privateChannel = channel
        if(channel.name == "events" and type(channel) == discord.ForumChannel):
            global eventsChannel
            eventsChannel = channel
        if(channel.name == "level-ups"):
            global levelUpChannel
            levelUpChannel = channel
        if(channel.name == "pvp"):
            global pvpChannel
            pvpChannel = channel
        if(channel.name == "hunts"):
            global huntChannel
            huntChannel = channel
        if(channel.name == "raids"):
            global raidChannel
            raidChannel = channel
    global botID
    botID = bot.user.id
    global encounterCont
    encounterCont = EncounterController()
    global pollCont
    pollCont = PollController()
    global raidCont
    raidCont = RaidController()
    print("Connected and ready to go.")
    await bot.change_presence(activity=discord.Activity(type=discord.ActivityType.listening, name="that yee haw"))


# On disconnecting, send a message
@bot.event
async def close():     
    DatabaseController().CloseDatabase() 
    for vc in bot.voice_clients: 
        await vc.disconnect()
    
# When a member joins the server, send a welcoming message
@bot.event
async def on_member_join(member: discord.Member):
    if (bot.is_ready()):
        global generalChannel
        print(f"{member.id} joined!")
        DatabaseController().StoreNewUser(member) 
        role = discord.utils.get(member.guild.roles, name='Wayward Wanderer')
        embed = discord.Embed(
            title = f"{cowboyEmote} Howdy pardner!",
            description = "Welcome to the cowbs.",
            colour = embedColour
        )
        embed.set_author(name=member.name, icon_url=member.display_avatar)          
        await member.add_roles(role)    
        await generalChannel.send(embed=embed)

# Method to do things when a message is sent
@bot.event
async def on_message(message):
    if (bot.is_ready()):
        # OpenAI
        if("The Moon Cowboy" in message.content or "715110532532797490" in message.content):
            messageWithoutMention = message.content.strip().replace("The Moon Cowboy", "").replace("715110532532797490", "")
            chat_completion = await client.chat.completions.create(
                messages=[
                    {
                        "role": "system",
                        "content": "Your name is The Moon Cowboyand you are a cowboy who lives on a ranch on the moon. You're a helpful cowboy from outer space who looks after a community of other moon cowboys. You don't talk much."
                    },
                    {
                        "role": "user",
                        "content": messageWithoutMention,
                    }
                ],
                model="llama3-8b-8192",
                temperature=0.5,
                max_tokens=512,
                top_p=1,
                stop=None,
                stream=False,
            )
            await bot.get_channel(message.channel.id).send(chat_completion.choices[0].message.content)
                    

        # If messages are sent to the bot through DMs, do not count for anything
        if (isinstance(message.channel, discord.channel.DMChannel)):
            pass
        else:            
            # Rate limiting the exp users gain from messages
            if(message.author.id != botID):
                # Declaring variables to be used
                global generalChannel
                global levelUpChannel
                messageChannel = bot.get_channel(message.channel.id)
                channelHistoryLength = 50
                rateLimitBool = True

                channelMessages = [message async for message in message.channel.history(limit=channelHistoryLength, after=(datetime.now() - timedelta(seconds=3)))]   
                for chnlMsg in channelMessages:
                    if chnlMsg.author.id == message.author.id and message.id != chnlMsg.id:                    
                        rateLimitBool = False 
                if(not rateLimitBool):
                    print(chnlMsg.author.display_name + " is being gold rate limited.")
                try:
                    msgExpEmbed = DatabaseController().StoreUserExp(bot, message.author.id, rateLimitBool)
                    if(msgExpEmbed != None):
                        await levelUpChannel.send(embed=msgExpEmbed)    
                except Exception as e:    
                    print(e.with_traceback())    
                # Generating an encounter                    
                # if(messageChannel.id == generalChannel.id): 
                #     if(rateLimitBool):
                #         global encounterCont 
                #         encounterEmbed = encounterCont.RollEncounter(message.author)
                #         if(encounterEmbed != None):
                #             encounterMsg = await messageChannel.send(embed=encounterEmbed)                        
                #             encounterCont.encounterID = encounterMsg.id
                #             await encounterMsg.add_reaction(rollEmote)   
                        

# Method to do things when a reaction is added
@bot.event
async def on_reaction_add(reaction, user):
    if (bot.is_ready()):
        global generalChannel
        global levelUpChannel
        global pvpChannel
        global encounterCont

        if(reaction.emoji == challengeEmote and user.id != botID):
            await pvpChannel.send(embed=await FightPlayer(reaction.message, user))

        if encounterCont.encounterUserID == user.id and reaction.emoji == encounterCont.rollEmote and user.id != botID and reaction.message.id == encounterCont.encounterID and encounterCont.encounterActive:
            embeds = encounterCont.ClearEncounter(bot, user)
            if (len(embeds) == 1):
                encClearMsg = await reaction.message.channel.send(embed=embeds[0])
            else:
                encClearMsg = await reaction.message.channel.send(embed=embeds[1])
                await levelUpChannel.send(embed=embeds[0])
            encounterCont.encClearID = encClearMsg.id 
            if encounterCont.lootDropFloat <= encounterCont.lootDropChance and encounterCont.encClearSuccess:
                await encClearMsg.add_reaction(encounterCont.tickEmote)
        if user.id == encounterCont.encounterUserID and user.id != botID and reaction.message.id == encounterCont.encClearID and reaction.emoji == encounterCont.tickEmote:
            DatabaseController().StoreUserEquipment(user.id, encounterCont.encClearLoot)           

@bot.event
async def on_scheduled_event_create(event):
    if(bot.is_ready()):
        global eventsChannel
        eventThread = await eventsChannel.create_thread(name=event.name, content=event.url)
        global privateChannel
        await privateChannel.send(f"## New Event!\nDiscuss here: {eventThread.thread.mention}\n\n{event.url}");

    

# ---------------------------------------------------------------------------
# COMMAND METHODS

# If the command is sent with 'help', send a message showing ways to use the bot
@tree.command(name="help", description="Displays a user's rank data.", guild=discord.Object(id=guildID))
async def help(interaction: discord.Interaction):
    author = interaction.user.name
    authorAvatar = interaction.user.display_avatar
    embed = discord.Embed(
        title = "Help Commands",
        description = "A list of how to use each command available:",
        colour = embedColour
    )
    embed.set_author(name=f'{author}', icon_url=authorAvatar)
    embed.add_field(name=f"{accountEmote} Account Info:", value=f"To view your or another user's account info, type: **/userinfo <otheruser>.**", inline=False)    
    embed.add_field(name=f"{leaderboardEmote} Leaderboard:", value=f"To view the leaderboard, type: **/leaderboard.**", inline=False)        
    embed.add_field(name=f"{equipmentEmote} Equipment:", value=f"To view your or another user's current equipment, type: **/equipment <otheruser>.**", inline=False)    
    embed.add_field(name=f"{levelEmote} Rank:", value=f"To view your or another user's level stats, type: **/rank <otheruser>.**", inline=False)   
    embed.add_field(name=f"{huntEmote} Hunt Info:", value=f"To view the info on hunts, type: **/huntinfo.**", inline=False)
    embed.add_field(name=f"{raidEmote} Raid Info:", value=f"To view the info on raids, type: **/raidinfo.**", inline=False)
    embed.add_field(name=f"{challengeEmote} PvP:", value=f"To challenge another player type: **/challenge @<opponent> <goldamount>** in the *# pvp* channel.", inline=False)
    embed.add_field(name=f"{huntEmote} Hunt:", value=f"To summon an encounter, type: **/hunt <rarity>** in the *# hunt* channel. The rarities are 'common', 'uncommon', 'rare', 'veryrare', 'legendary'.", inline=False)
    embed.add_field(name=f"{raidEmote} Raid:", value=f"To initiate another raid, type: **/raid** in the *# raid* channel. To beat the raid, surpass the raid's health with cumulative equipment modifiers.", inline=False)
    embed.add_field(name=f"{rollEmote} Dice rolling:", value=f"To roll, type something like: **/roll 1d20**\nThe modifiers '+' or '-' may be added: **/roll 1d20+3.**", inline=False)
    await interaction.response.send_message(embed=embed)

#     # If the command is sent with 'help', send a message showing ways to use the bot
# @tree.command(name="poll", description="Create a poll with options of your choice.", guild=discord.Object(id=guildID))
# async def poll(interaction: discord.Interaction, title: str, options: str):
#     pollOptions = options.strip().split(",")
#     optionsList = list()
#     for idx, option in enumerate(pollOptions):
#         optionsList.append(Option(index = idx, name = option))    

#     embed, view = pollCont.AddPoll(interaction, Poll(title, optionsList, datetime.now()))    

#     await interaction.response.send_message(embed=embed, view=view)

# # If the command is sent with 'join', join the voice channel that the author is in
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
@tree.command(name="rank", description="Displays a user's rank data.", guild=discord.Object(id=guildID))
async def req_rank(interaction: discord.Interaction, otheruser: discord.User = None):
    user = CheckIfOtherUser(interaction.user, otheruser)
    dbCont = DatabaseController()
    embed = discord.Embed(
        title = f"{levelEmote} Your stats for {interaction.guild}",
        colour = embedColour
    )
    userRankRaw = dbCont.RetrieveUserRank(user.id)
    userRank = UserRank(user.display_name, user.display_avatar, userRankRaw[0], userRankRaw[1], userRankRaw[2], userRankRaw[3])
    userTitlesRaw = dbCont.RetrieveUserTitles(user.id)
    userTitles = ""
    for title in userTitlesRaw:
        if userTitles:
            userTitles + ", "
        userTitles += title
    if not userTitles:
        userTitles = 'None'
    embed.set_thumbnail(url="https://cdn.discordapp.com/attachments/758193066913562656/767867171391930458/ApprovingElite.png")
    embed.set_author(name=f'{userRank.displayName}', icon_url=userRank.avatar)      
    embed.add_field(name="Level:", value=f"{userRank.level}", inline=False)
    embed.add_field(name=f"Gold:", value=f"{userRank.exp}", inline=False)
    embed.add_field(name=f"Gold Until Next Level:", value=f"{userRank.expRemaining}", inline=False)
    embed.add_field(name=f"Messages Sent:", value=f"{userRank.msgSent}", inline=False)   
    embed.add_field(name=f"Titles:", value=userTitles, inline=False)   
    await interaction.response.send_message(embed=embed)

# Display the current equipment and modifier for a user that calls this command
@tree.command(name="equipment", description="Displays your equipment name and modifier.", guild=discord.Object(id=guildID))
async def ShowEquipment(interaction: discord.Interaction, otheruser: discord.User = None):
    user = CheckIfOtherUser(interaction.user, otheruser)
    userData = DatabaseController().RetrieveUser(user.id)
    embed = discord.Embed(
        title = f"Your Equipment",
        colour = embedColour
    )
    embed.set_thumbnail(url="https://cdn.discordapp.com/attachments/758193066913562656/767677300333477888/48cb5349f515f6e59edc2a4de294f439.png")
    embed.set_author(name=f'{user.display_name}', icon_url=user.display_avatar)    
    embed.add_field(name="Item", value=f"*{userData[5]}*", inline=True)
    embed.add_field(name="Modifier", value=f"*+{userData[4]}*", inline=True)
    await interaction.response.send_message(embed=embed)

# WILL WIPE A USER'S DATA
@tree.command(name="resetmydata", description="Reset your rank and equipment in the database.", guild=discord.Object(id=guildID))
async def resetUserData(interaction: discord.Interaction):
    authorID = str(interaction.user.id)
    try:
        DatabaseController().ResetUserData(authorID)
        print(authorID+"'s data has been reset.")
        await interaction.response.send_message("Resetting level successful.") 
    except:
        print("Error resetting user data.")
        await interaction.response.send_message("Error resetting level.")

# Retrieves user account info based on their public profile
@tree.command(name="userinfo", description="Displays miscellaneous discord info.", guild=discord.Object(id=guildID))
async def req_userinfo(interaction: discord.Interaction, otheruser: discord.User = None):
    user = CheckIfOtherUser(interaction.user, otheruser)
    authorName = user.name
    authorAvatar = user.display_avatar
    currentTime = datetime.now()
    accCreatedAt = str(user.created_at).split(" ")
    accJoinedAt = str(user.joined_at).split(" ")
    timeCreated = accCreatedAt[1].split(".")
    timeJoined = accJoinedAt[1].split(".")
    timeSinceAccCreated = str(currentTime.replace(tzinfo=None) - user.created_at.replace(tzinfo=None)).split(",")
    timeSinceAccJoined = str(currentTime.replace(tzinfo=None) - user.joined_at.replace(tzinfo=None)).split(",")
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
    embed.set_author(name=f'{authorName}', icon_url=authorAvatar)  
    embed.add_field(name=f"Current Nickname:", value=f"{authorNick}", inline=True)
    embed.add_field(name=f"Account Name:", value=f"{authorName}", inline=True)
    embed.add_field(name=f"Roles:", value=f"{authorRoles}", inline=False)
    embed.add_field(name=f"Account Created {timeSinceAccCreated[0]} ago", value=f"**{accCreatedAt[0]}** {timeCreated[0]} UTC", inline=True)
    embed.add_field(name=f"Server Joined {timeSinceAccJoined[0]} ago", value=f"**{accJoinedAt[0]}** {timeJoined[0]} UTC", inline=True)    
    embed.set_footer(text=f"UserID: {authorID}")
    await interaction.response.send_message(embed=embed)  

# Retrieves member, exp, and level data from levellingDB
@tree.command(name="leaderboard", description="Displays the top 10 users sorted by gold.", guild=discord.Object(id=guildID))
async def req_leaderboard(interaction: discord.Interaction):
    user = interaction.user
    userIdx = None
    author = user.name
    authorAvatar = user.display_avatar
    guild = interaction.guild
    embed = discord.Embed(
        title = f"{leaderboardEmote} The leaderboard for {guild}",
        colour = embedColour
    )
    embed.set_thumbnail(url="https://cdn.discordapp.com/attachments/758193066913562656/767867171391930458/ApprovingElite.png")
    embed.set_author(name=f'{author}', icon_url=authorAvatar)  
    leaderboardList = DatabaseController().RetrieveAllUsers(interaction)
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
        embed.add_field(name=str(idx+1)+". "+leaderboardList[idx][0], value=f"Level: {leaderboardList[idx][1]}, Gold: {leaderboardList[idx][2]}", inline=True)
    if(not userInTopTen):
        userList = DatabaseController().RetrieveUserRank(interaction.user.id)
        embed.add_field(name=f"*{str(userIdx)}. {userList[0]}*", value=f"*Level: {userList[1]}, Gold: {userList[2]}*", inline=False)
    await interaction.response.send_message(embed=embed)

# Retrieves user account info based on their public profile
@tree.command(name="huntinfo", description="Displays hunt costs and equipment droprates.", guild=discord.Object(id=guildID))
async def encounterStats(interaction: discord.Interaction):
    global encounterCont
    embed = discord.Embed(
        title = f"{huntEmote} Hunt Info",
        colour = embedColour
    )
    embed.set_author(name=f'{interaction.user.name}', icon_url=interaction.user.display_avatar)  
    embed.add_field(name="Hunt Costs:", value=f"", inline=False)
    embed.add_field(name="common", value=f"26", inline=True)
    embed.add_field(name="uncommon", value=f"48", inline=True)
    embed.add_field(name="rare", value=f"76", inline=True)
    embed.add_field(name="veryrare", value=f"110", inline=True)
    embed.add_field(name="legendary", value=f"150", inline=True)
    embed.add_field(name="Loot Info:", value=f"", inline=False)
    embed.add_field(name=f"Loot Drop", value=f"{(encounterCont.lootDropChance * 100)}%", inline=True) 
    embed.add_field(name=f"Encounter Rarity", value=f"Common: {(IEncounterable.commonDropChance * 100)}% \nUncommon: {(IEncounterable.uncommonDropChance * 100)}% \nRare: {(IEncounterable.rareDropChance * 100)}% \nVery Rare: {(IEncounterable.veryrareDropChance * 100)}% \nLegendary: {(IEncounterable.legendaryDropChance * 100)}% \n", inline=False) 
    await interaction.response.send_message(embed=embed)  

# DO NOT USE THIS UNLESS YOU WANT TO WIPE ALL LEVEL DATA
# @tree.command(name="resetserverranks", description="Reset all users' rank and equipment in the database.", guild=discord.Object(id=guildID))
# @has_permissions(administrator=True, manage_messages=True, manage_roles=True)
# async def collectLevelData(interaction: discord.Interaction):
#     try:
#         if(interaction.user.id == 218890729550774282):
#             DatabaseController().ResetServerRankData(interaction)
#             await interaction.response.send_message("Storing fresh data successful.")
#     except:
#         print("Error resetting database.")
#         await interaction.response.send_message("Error resetting database.")

# @tree.command(name="huntcosts", description="Display the cost of each tier of hunting.", guild=discord.Object(id=guildID))
# async def Hunt(interaction: discord.Interaction):
#     author = interaction.user.display_name
#     authorAvatar = interaction.user.display_avatar
#     embed = discord.Embed(
#         title = f"Hunt Costs",
#         description="Gold cost for each hunt \n(Case & whitespace sensitive)",
#         colour = embedColour
#     )
#     embed.set_thumbnail(url="https://cdn.discordapp.com/attachments/758193066913562656/767677300333477888/48cb5349f515f6e59edc2a4de294f439.png")
#     embed.set_author(name=f'{author}', icon_url=authorAvatar)    
#     embed.add_field(name="common", value=f"26", inline=True)
#     embed.add_field(name="uncommon", value=f"48", inline=True)
#     embed.add_field(name="rare", value=f"76", inline=True)
#     embed.add_field(name="veryrare", value=f"110", inline=True)
#     embed.add_field(name="legendary", value=f"150", inline=True)
#     await interaction.response.send_message(embed=embed)

@tree.command(name="hunt", description="Summon an encounter using a certain amount of your own gold. Rarity costs can be found at /huntinfo.", guild=discord.Object(id=guildID))
async def Hunt(interaction: discord.Interaction, tier: str):
    global huntChannel
    if interaction.channel.id == huntChannel.id:
        rarity = 0
        expSpent = 0
        if tier == "common":
            rarity = 1
            expSpent = 26
        elif tier == "uncommon":
            rarity = 0.39
            expSpent = 48
        elif tier == "rare":
            rarity = 0.149
            expSpent = 76
        elif tier == "veryrare":
            rarity = 0.049
            expSpent = 110
        elif tier == "legendary":
            rarity = 0.009
            expSpent = 150
        if rarity == 0:
            return        
        encounterEmbed = encounterCont.RollEncounter(interaction.user, encounterChance=1,rarityOverride=rarity)
        if(encounterEmbed != None):
            encounterMsg = await huntChannel.send(embed=encounterEmbed)                        
            encounterCont.encounterID = encounterMsg.id
            await encounterMsg.add_reaction(rollEmote)   
            msgExpEmbed = DatabaseController().StoreUserExp(bot, interaction.user.id, True, -expSpent)
            if(msgExpEmbed != None):
                await levelUpChannel.send(embed=msgExpEmbed)  
            await interaction.response.send_message(content=f"You paid {expSpent} gold to hunt!", ephemeral=False)
        else:
            return
        
@tree.command(name="raidinfo", description="Display the cost of a raid and the odds of each rarity.", guild=discord.Object(id=guildID))
async def Hunt(interaction: discord.Interaction):
    global raidConclusionTimer 
    author = interaction.user.display_name
    authorAvatar = interaction.user.display_avatar
    embed = discord.Embed(
        title = f"Raid Information",
        description="Gold cost for initiating a raid and the odds of each rarity",
        colour = embedColour
    )
    embed.set_thumbnail(url="https://cdn.discordapp.com/attachments/758193066913562656/767677300333477888/48cb5349f515f6e59edc2a4de294f439.png")
    embed.set_author(name=f'{author}', icon_url=authorAvatar)    
    embed.add_field(name="Cost", value=f"{initiationCost} gold", inline=False)
    embed.add_field(name="Raid Timer", value=f"{raidConclusionTimer} seconds", inline=False)
    embed.add_field(name=f"Rarity", value=f"Common: {(RaidController.commonDropChance * 100)}% \nUncommon: {(RaidController.uncommonDropChance * 100)}% \nRare: {(RaidController.rareDropChance * 100)}% \nVery Rare: {(RaidController.veryrareDropChance * 100)}% \nLegendary: {(RaidController.legendaryDropChance * 100)}% \n", inline=False) 
    await interaction.response.send_message(embed=embed)

@tree.command(name="raid", description=f"Initiate a raid and fight a boss using {initiationCost} gold.", guild=discord.Object(id=guildID))
async def Raid(interaction: discord.Interaction):
    global raidChannel
    if interaction.channel.id == raidChannel.id:
        global raidCont
        global raidPreludeTimer
        global raidConclusionTimer   
        global initiationCost
        await interaction.response.send_message(f"# Raid starting in {raidPreludeTimer} seconds.")
        await asyncio.sleep(raidPreludeTimer)
        raidStartEmbed, raidView = raidCont.InitiateRaid(interaction.user.id, initiationCost, bot, raidConclusionTimer)
        raidStartMsg = await interaction.channel.send(embed=raidStartEmbed, view=raidView)   
        await asyncio.sleep(raidConclusionTimer)
        raidEndEmbed = raidCont.ConcludeRaid()
        raidEndMsg = await interaction.channel.send(embed=raidEndEmbed)   

# If the command is sent with 'rollhelp', query a roll from the sent dice rolling data
@tree.command(name="roll", description="To roll, type something like: 1d20. The modifiers '+' or '-' may be added: 1d20+3.", guild=discord.Object(id=guildID))
async def Roll(interaction: discord.Interaction, dice: str):
    author = interaction.user.id
    author = interaction.user.display_name
    authorAvatar = interaction.user.display_avatar
    outcome = DiceController().QueryRoll(dice)
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
    await interaction.response.send_message(embed=embed)

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
# @tree.command(name="spawnencounter", description="Manually spawn an encounter.", guild=discord.Object(id=guildID))
# @has_permissions(administrator=True, manage_messages=True, manage_roles=True)
# async def Spawn_Encounter(interaction: discord.Interaction):
#     # Generating an encounter  
#     global encounterCont
#     global generalChannel
#     try:
#         if(interaction.channel.id == generalChannel.id and interaction.user.id != botID):
#             await interaction.response.send_message(content="Encounter manually spawned.")
#             encounterMsg: discord.abc.Messageable = await generalChannel.send(embed=encounterCont.RollEncounter(interaction.user, 1))
#             encounterCont.encounterID = encounterMsg.id
#             await encounterMsg.add_reaction(rollEmote)  
#     except Exception:
#         pass

# Ping another player to fight
@tree.command(name="challenge", description="To challenge another player, type: @<opponent> <goldamount>", guild=discord.Object(id=guildID))
async def ChallengePlayer(interaction: discord.Interaction, opponent: discord.User, wager: str):
    global pvpChannel
    if(interaction.channel.id == pvpChannel.id):
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
            challenger = interaction.user  
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
                    raise Exception(challengerName+' does not have enough gold.\n'+opponentName+' does not have enough gold.')
                elif(int(challengerExp) < int(wager)):
                    raise Exception(challengerName+' does not have enough gold.')
                elif(int(opponentExp) < int(wager)):
                    raise Exception(opponentName+' does not have enough gold.')
                embed.set_thumbnail(url="https://cdn.discordapp.com/attachments/758193066913562656/767677300333477888/48cb5349f515f6e59edc2a4de294f439.png")
                embed.set_author(name=f'{challengerName}', icon_url=challengerAvatar)    
                embed.add_field(name=challengerName, value=f"{challengerEquip}, +{challengerMod}", inline=True)
                embed.add_field(name=f"***WAGERING***", value=f"***{wager} gold AGAINST***", inline=True)
                embed.add_field(name=opponentName, value=f"{opponentEquip}, +{opponentMod}", inline=True)
                embed.add_field(name=f"TO ACCEPT,", value=f"*Click the dice to fight!*", inline=False)
                embed.set_footer(text=opponentName, icon_url=opponentAvatar)    
            await interaction.response.send_message(content="<@"+str(opponentID)+">")
            challenge = await pvpChannel.send(embed=embed)
            if(embedTitle == 'A New Challenger Approaches!'):
                dictKeyName = str(opponentID)+'_'+str(challenge.id)
                challengesDict[dictKeyName][0] = {'challengerID' : challengerID, 'challengerName' : challengerName, 'challengerEquip' : challengerEquip, 'challengerMod' : challengerMod}
                challengesDict[dictKeyName][1] = {'opponentID' : opponentID, 'opponentName' : opponentName, 'opponentEquip' : opponentEquip, 'opponentMod' : opponentMod}
                challengesDict[dictKeyName][2] = {'challengeID' : challenge.id, 'challengeWager' : wager}
                await challenge.add_reaction(challengeEmote)

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
            storeExpEmbed = DatabaseController().StoreUserExp(bot, challengerID if outcome else opponentID, True, int(challengeWager))
            removeExpEmbed = DatabaseController().StoreUserExp(bot, opponentID if outcome else challengerID, True, -int(challengeWager))
            if(storeExpEmbed != None):
                await levelUpChannel.send(embed=storeExpEmbed)
            if(removeExpEmbed != None):
                await levelUpChannel.send(embed=removeExpEmbed)
        embed.add_field(name=opponentName, value=f"**{opponentRollTotal}** (*{opponentRoll[0]}, +{opponentMod}*)", inline=True)
        challengesDict.pop(dictKeyName)  
        return embed

def CheckIfOtherUser(interactionUser: discord.User, otherUser: discord.User):
    if(otherUser == None):
        return interactionUser
    else:
        return otherUser

bot.run(TOKEN)

# ----------------------------------------------------------------------------------