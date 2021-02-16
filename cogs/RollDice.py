
import discord
from discord.ext import commands
# Speech Recognition
import speech_recognition as sr
# Regex
import re
from re import I
# Random
import random
# Other Scripts
from cogs.DisplayData import UserDataCommands as displayData

class DiceRolling(commands.Cog):
    # Initialize the voice recognizer
    r = sr.Recognizer()

    def __init__(self, bot):
        self.bot = bot

    # If the command is sent with 'join', join the voice channel that the author is in
    @commands.command(name='join')
    async def join_voice(self, ctx):
        dat = displayData(self.bot)
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
                for client in self.bot.voice_clients:
                    if client.channel == channel:
                        embedMessage = f"I've connected to **{str(channel)}**!"
        except:
            embedMessage = f"I\'m already connected to **{str(channel)}**."
        joinEmbed = discord.Embed(
            title = f"{dat.voiceEmote} Connecting...",
            description = embedMessage,
            colour = dat.embedColour
        )
        joinEmbed.set_author(name=f'{author}', icon_url=authorAvatar) 
        await ctx.send(embed=joinEmbed)

    # If the command is sent with 'leave', leave all voice channels    
    @commands.command(name='leave')
    async def leave_voice(self, ctx):
        dat = displayData(self.bot)
        for vc in self.bot.voice_clients: 
            if(vc.guild == ctx.guild):
                await vc.disconnect()
                joinEmbed = discord.Embed(
                    title = f"{dat.voiceEmote} Leaving...",
                    description = f"Left!",
                    colour = dat.embedColour
                )
                joinEmbed.set_author(name=f'{ctx.message.author.name}', icon_url=ctx.author.avatar_url) 
                await ctx.send(embed=joinEmbed)

    # If the command is sent with 'rollhelp', query a roll from the sent dice rolling data
    @commands.command(name='roll')
    async def Roll(self, ctx, text: str):
        dat = displayData(self.bot)
        author = ctx.author.id
        author = ctx.author.name
        authorAvatar = ctx.author.avatar_url
        outcome = self.QueryRoll(text)
        embed = discord.Embed(
            title = f"{dat.rollEmote} Rolling!",
            colour = dat.embedColour
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
    @commands.command(name='test')
    async def Speech2Text(self, ctx):
        dat = displayData(self.bot)
        # open the file
        filename = "TestCases/4d20plus4.wav"
        with sr.AudioFile(filename) as source:
            # listen for the data (load audio into memory)
            audio_data = self.r.record(source)
            # recognize (convert from speech to text)
            text = self.r.recognize_google(audio_data)

        authorName = ctx.author.name
        authorAvatar = ctx.author.avatar_url
        outcome = self.QueryRoll(text)
        embed = discord.Embed(
            title = f"{dat.rollEmote} Rolling!",
            description = f"You said: *\"{text}\"*",
            colour = dat.embedColour
        )
        embed.set_thumbnail(url="https://cdn.discordapp.com/attachments/758193066913562656/767677300333477888/48cb5349f515f6e59edc2a4de294f439.png")
        embed.set_author(name=f'{authorName}', icon_url=authorAvatar)    
        embed.add_field(name="You Rolled:", value=f"{outcome[0]}", inline=False)
        embed.add_field(name="Modifier", value=f"{outcome[1]}", inline=True)
        embed.add_field(name="Total", value=f"{outcome[2]}", inline=True)
        if len(outcome) > 3:
            embed.add_field(name="Total With Mod", value=f"{outcome[3]}", inline=True)

        await ctx.send(embed=embed)

    # Takes a string that is Regex'd to find specific dice rolling data
    def QueryRoll(self, text):
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

            return self.RollDice(int(dieFaces[0]), int(dieNum[0]), int(dieMod[0]), minusMod)
        else:
            return 'Error in roll statement.'

    # Takes int data from QueryRoll(), rolls dice based on those numbers, then outputs it in a string
    def RollDice(self, dieSides, dieNum=1, dieMod=0, minus=False):
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
        dieReturn.append(f"{self.DieModConverter(dieMod, minus)}")
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
    def DieModConverter(self, dieMod, minus=False):
        output = ''
        if dieMod == 0:
            output = '*With No Modifier*'
        else:
            if minus:
                output = '*-'+str(dieMod)+'*'
            else:
                output = '*+'+str(dieMod)+'*'
        return output

def setup(bot):
    bot.add_cog(DiceRolling(bot))
