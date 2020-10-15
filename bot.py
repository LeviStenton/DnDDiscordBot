# bot.py
#!/usr/bin/python

import os
import random
import discord
import speech_recognition as sr
import re

from discord.ext import commands
from dotenv import load_dotenv


load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')
GUILD = os.getenv('DISCORD_GUILD')
filename = "/home/pi/DiscordBot/TheMoonCowboy/TestCases/ad20plus5.wav"

#initialize the recognizer
r = sr.Recognizer()

bot = commands.Bot(command_prefix='!')

@bot.command(name='roll')
async def Roll(ctx, text: str):
    print(text)
    outcome = QueryRoll(text)

    await ctx.send(outcome)

@bot.command(name='test')
async def Speech2Text(ctx):
    # open the file
    with sr.AudioFile(filename) as source:
        # listen for the data (load audio into memory)
        audio_data = r.record(source)
        # recognize (convert from speech to text)
        text = r.recognize_google(audio_data)

        outcome = QueryRoll(text)
    
    await ctx.send(outcome)

def QueryRoll(text):
    if re.match("(?:(?i)roll|(?i)rule)?(?: ?).+(?: ?)d(?: ?).+(?: ?)(?:[+|-](?: ?).+)*", text):
        
            dieNum = re.findall("(?:(?:(?i)roll|(?i)rule)|r)?(.+)(?: ?)d(?: ?).+(?: ?)(?:[+|-](?: ?).+)*", text)           
            if dieNum[0] == 'a': dieNum[0] = 1;
            print(dieNum[0])

            dieFaces = re.findall("(?:(?:(?i)roll|(?i)rule)|r)?(?: ?).+(?: ?)d(?: ?)(.+)(?: ?)(?:[+|-](?: ?).+)*", text)
            if re.match(".+[+|-]", dieFaces[0]):
                dieFaces = re.findall("(.+)[+|-]", dieFaces[0])
            print(dieFaces[0])

            dieModOperand = re.findall("(?:(?:(?i)roll|(?i)rule)|r)?(?: ?).+(?: ?)d(?: ?).+(?: ?)([+|-])(?: ?).+", text)
            if len(dieModOperand) == 0:
                dieModOperand.append('+')
            elif dieModOperand[0] == '':
                dieModOperand[0] = '+'            
            print(dieModOperand[0])

            dieMod = re.findall("(?:(?:(?i)roll|(?i)rule)|r)?(?: ?).+(?: ?)d(?: ?).+(?: ?)[+|-](?: ?)(.+)", text)
            if len(dieMod) == 0:
                dieMod.append(0)
            elif dieMod[0] == '':
                dieMod[0] = 0           
            print(dieMod[0])
    
            return str(RollDice(int(dieFaces[0]), int(dieNum[0]), int(dieMod[0])))
    else:
        return 'Error in roll statement.'

def RollDice(dieSides, dieNum=1, dieMod=0):
    dieOutcomes = ''
    dieList = []
    dieTotal = 0
    totalOutcomes = ''

    for die in range(dieNum):
        diceRoll = random.randint(1, dieSides)
        if diceRoll == 20 or diceRoll == 1:
            dieList.append("***"+str(diceRoll)+"***")
        else:
            dieList.append(str(diceRoll))
        dieTotal += diceRoll

    dieOutcomes = ', '.join(dieList)
    if dieMod == 0:
        totalOutcomes = ', Total: '+str(dieTotal)
    elif dieMod > 0:
        totalOutcomes = ', Total: '+str(dieTotal)+', Total With Mod: '+str(dieTotal+dieMod)
    return ('You rolled: '+dieOutcomes+', '+DieModConverter(dieMod)+totalOutcomes)

def DieModConverter(dieMod):
    output = ''
    if dieMod == 0:
        output = 'With No Modifier'
    else:
        output = '+'+str(dieMod)
    return output

bot.run(TOKEN)
