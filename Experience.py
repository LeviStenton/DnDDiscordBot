# Discord
import discord
from discord.ext import commands
# SQLite
import sqlite3
# Math
import math

from discord.ext.commands.core import command

class ExperienceSystem(commands.Cog):
    # Initialize the database
    conn = sqlite3.connect('databases/levellingDB.db')
    c = conn.cursor()
    # Global variables for levelling
    levellingConstant = 0.1
    expPerMsg = 1
    rateLimit = 2

    def __init__(self, bot):
        self.bot = bot

    # DO NOT USE THIS UNLESS YOU WANT TO WIPE ALL LEVEL DATA
    @commands.command(name='ResetServerLevelData')
    @commands.has_permissions(administrator=True, manage_messages=True, manage_roles=True)
    async def collectLevelData(self, ctx):
        try:
            if(ctx.message.author.id == 218890729550774282):
                self.c.execute("CREATE TABLE IF NOT EXISTS userData(userID TEXT, userLevel TEXT, userExp TEXT, userSentMsgs TEXT)")
                for member in ctx.guild.members:
                    memberID = str(member.id)             
                    self.c.execute(f"INSERT INTO userData VALUES (?,0,0,0)", (memberID, ))
                    self.conn.commit()
                print("Storing fresh data successful.")
                await ctx.send("Storing fresh data successful.")
        except:
            print("Error resetting database.")
            await ctx.send("Error resetting database.")

    # WILL WIPE A USER'S DATA
    @commands.command(name='resetmylevel')
    async def resetUserData(self, ctx):
        authorID = str(ctx.author.id)
        try:
            self.c.execute(f"UPDATE userData SET userLevel = 0, userExp = 0, userSentMsgs = 0 WHERE userID = ?", (authorID, ))
            self.conn.commit()
            print(authorID+"'s data has been reset.")
            await ctx.send("Resetting level successful.") 
        except:
            print("Error resetting user data.")
            await ctx.send("Error resetting level.")

    # Give yourself as much EXP as specified
    @commands.command(name='giveexp')
    @commands.has_permissions(administrator=True, manage_messages=True, manage_roles=True)
    async def giveExp(self, ctx, userexp):
        searchQuery = ctx.author.id
        userID = ''
        userLevel = 0.00
        userExp = 0
        userMessagesSent = 0
        self.c.execute(f'SELECT * FROM userData WHERE userID=?', (searchQuery, ))
        fetchedRows = self.c.fetchall()
        for item in fetchedRows:             
            splitRow = str(item).split(", ")        
            for idx, item in enumerate(splitRow):
                splitRow[idx] = splitRow[idx].replace('(', '')
                splitRow[idx] = splitRow[idx].replace(')', '')
                splitRow[idx] = splitRow[idx].replace('\'', '')
            userID = splitRow[0]     
            userExp = int(splitRow[2]) + int(userexp)
            userLevel = (self.levellingConstant * math.sqrt(userExp))
            userMessagesSent = int(splitRow[3]) + 1
            self.c.execute(f"UPDATE userData SET userID = {userID}, userLevel = {userLevel}, userExp = {userExp}, userSentMsgs = {userMessagesSent} WHERE userID=?", (searchQuery, ))
            self.conn.commit()           
            break
    
    # A method to promote users with exp when they message
    def MsgExpSystem(self, message, expBool):
        searchQuery = message.author.id
        userID = ''
        userLevel = 0.00
        userExp = 0
        userMessagesSent = 0
        self.c.execute(f'SELECT * FROM userData WHERE userID=?', (searchQuery, ))
        fetchedRows = self.c.fetchall()
        for item in fetchedRows:             
            splitRow = str(item).split(", ")        
            for idx, item in enumerate(splitRow):
                splitRow[idx] = splitRow[idx].replace('(', '')
                splitRow[idx] = splitRow[idx].replace(')', '')
                splitRow[idx] = splitRow[idx].replace('\'', '')
            userID = splitRow[0]     
            if expBool:
                userExp = int(splitRow[2]) + self.expPerMsg
                userLevel = (self.levellingConstant * math.sqrt(userExp))
            else:
                userExp = int(splitRow[2])
                userLevel = (self.levellingConstant * math.sqrt(userExp))
            userMessagesSent = int(splitRow[3]) + 1
            self.c.execute(f"UPDATE userData SET userID = {userID}, userLevel = {userLevel}, userExp = {userExp}, userSentMsgs = {userMessagesSent} WHERE userID=?", (searchQuery, ))
            self.conn.commit()           
            break

    # A method to promote users with exp when they complete random events
    def RctExpSystem(self, rctUser, exp):
        searchQuery = rctUser.id
        userID = ''
        userLevel = 0
        userExp = 0
        userMessagesSent = 0
        self.c.execute(f'SELECT * FROM userData WHERE userID=?', (searchQuery, ))
        fetchedRows = self.c.fetchall()
        for item in fetchedRows:             
            splitRow = str(item).split(", ")        
            for idx, item in enumerate(splitRow):
                splitRow[idx] = splitRow[idx].replace('(', '')
                splitRow[idx] = splitRow[idx].replace(')', '')
                splitRow[idx] = splitRow[idx].replace('\'', '')
            userID = splitRow[0]
            userExp = int(splitRow[2]) + int(exp)
            userLevel = self.levellingConstant * math.sqrt(userExp)
            userMessagesSent = int(splitRow[3]) + 1
            self.c.execute(f"UPDATE userData SET userID = {userID}, userLevel = {userLevel}, userExp = {userExp}, userSentMsgs = {userMessagesSent} WHERE userID=?", (searchQuery, ))
            self.conn.commit()           
            break

    def LevelUpMsg(self, level, user):    
        author = '@'+user.name
        authorAvatar = user.avatar_url
        embed = discord.Embed(
            title = f"You Leveled Up!",
            description = f"You are now *{level}* steps closer to the cosmos!",
            colour = discord.Colour.purple()
        )        
        embed.set_author(name=f'{author}', icon_url=authorAvatar)
        return embed

def setup(bot):
    bot.add_cog(ExperienceSystem(bot))   