# bot.py
#!/usr/bin/python

# Import all necessary modules for building the bot
import os
from os import close
import random
from re import I
from asyncio.subprocess import Process
import discord
from discord import client
from discord import message
from discord import channel
from discord.client import Client
import speech_recognition as sr
import re

from discord.ext import commands
from dotenv import load_dotenv
# ---------------------------------------------
# Build a bot that parses dice rolling via Regex from in-channel messages or voice commands

# Parse the bot's token, my server, and the file the text to speech reads from
load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')
GUILD = os.getenv('DISCORD_GUILD')
filename = "/home/pi/DiscordBot/TheMoonCowboy/TestCases/4d20plus4.wav"

# Initialize the recognizer
r = sr.Recognizer()
# Initialize the bot with a custom command
commandPrefix = '#'
bot = commands.Bot(command_prefix=commandPrefix)  
bot.remove_command("help")

# On ready, send a message and set the custom status
@bot.event
async def on_guild_join():
    channel = bot.get_channel(449967222652141568)
    await channel.send(f":cowboy: Eyes up Moon Cowboys, I'm connected! Type **{commandPrefix}help** to get started.")

@bot.event
async def on_ready():
    await bot.change_presence(activity = discord.Activity(type = discord.ActivityType.listening, name = f"{commandPrefix}help"))

# On disconnecting, send a message
@bot.event
async def close():
    channel = bot.get_channel(449967222652141568)
    # await channel.send(":cowboy: Eyes down Moon Cowboys, I'm disconnecting! Stay safe.")
    for vc in bot.voice_clients:
        await vc.disconnect()    

@bot.event
async def on_member_join(member):
    channel = bot.get_channel(449967222652141568)
    await channel.send(f":cowboy: Eyes up, {member.name}, you're a ｍｏｏｎ 𝒸𝑜𝓌𝒷𝑜𝓎 now. :cowboy:")

# If the command is sent with 'help', send a message showing ways to use the bot
@bot.command(name='help')
async def help(ctx):
    diceLines = f"<:d20:766295310129430568> **Dice rolling:** \nTo roll, type something like: **{commandPrefix}roll 1d20** \nThe modifiers '+' or '-' may be added: **{commandPrefix}roll 1d20+3** \n\n:microphone2: **Voice Chat:** \nTo join voice chat, type: **{commandPrefix}join** \nTo leave voice chat, type: **{commandPrefix}leave**"
    await ctx.send(diceLines)

@bot.command(name='join')
async def join_voice(ctx):
    connected = ctx.author.voice
    channel = ctx.author.voice.channel
    try:
        if connected:
            await connected.channel.connect()
            for client in bot.voice_clients:
                if client.channel == channel:
                    await ctx.send('Connecting to **'+str(channel)+'**!')
    except:
        await ctx.send('I\'m already connected to **'+str(channel)+'**!')
        
@bot.command(name='leave')
async def leave_voice(ctx):
    for vc in bot.voice_clients:
            if vc.guild == ctx.guild:
                await vc.disconnect()              

# If the command is sent with 'rollhelp', query a roll from the sent dice rolling data
@bot.command(name='roll')
async def Roll(ctx, text: str):
    outcome = QueryRoll(text)

    await ctx.send(outcome)

# When a voice command asking to roll dice is said, convert it to text and query a roll from it
@bot.command(name='test')
async def Speech2Text(ctx):
    # open the file
    with sr.AudioFile(filename) as source:
        # listen for the data (load audio into memory)
        audio_data = r.record(source)
        # recognize (convert from speech to text)
        text = r.recognize_google(audio_data)

        outcome = QueryRoll(text)

    await ctx.send("**You said:** *\""+text+"\"*")
    await ctx.send(outcome)

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

            return str(RollDice(int(dieFaces[0]), int(dieNum[0]), int(dieMod[0]), minusMod))
    else:
        return 'Error in roll statement.'

# Takes int data from QueryRoll(), rolls dice based on those numbers, then outputs it in a string
def RollDice(dieSides, dieNum=1, dieMod=0, minus=False):
    dieOutcomes = ''
    dieList = []
    dieTotal = 0
    totalOutcomes = ''

    for die in range(dieNum):
        diceRoll = random.randint(1, dieSides)
        if (diceRoll == 20 or diceRoll == 1) and dieSides == 20:
            dieList.append("__**"+str(diceRoll)+"**__")
        else:
            dieList.append(str(diceRoll))
        dieTotal += diceRoll

    dieOutcomes = ', '.join(dieList)
    if dieMod == 0:
        totalOutcomes = '\n**Total:** '+str(dieTotal)
    elif dieMod > 0:
        if minus:
            totalOutcomes = '\n**Total:** '+str(dieTotal)+'\n**Total With Mod:** '+str(dieTotal-dieMod)
        else:
            totalOutcomes = '\n**Total:** '+str(dieTotal)+'\n**Total With Mod:** '+str(dieTotal+dieMod)
    return ('<:d20:766295310129430568> **You rolled:** '+dieOutcomes+', '+DieModConverter(dieMod, minus)+totalOutcomes)

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

bot.run(TOKEN)
