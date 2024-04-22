import sqlite3
import discord
import math
from webbrowser import get
from models.equipment.Equipment import Equipment

class DatabaseController(): 
    __levellingConstant = 0.1
    __expPerMessage = 1
    # Initialize the database
    __conn = sqlite3.connect('databases/levellingDB.db')
    __c = __conn.cursor()

    def __init__(self):
        pass

    def CloseDatabase(self):
        self.__conn.close()

    def StoreNewUser(self, member):
        self.__c.execute("INSERT or IGNORE INTO userData VALUES(?,0,0,0,0,?)", (member.id, "Fists", ))
        self.__conn.commit()  
        
    def RetrieveUser(self, userId: int) -> tuple:
        self.__c.execute(f'SELECT * FROM userData WHERE userID=?', (userId, ))
        splitRow = str(self.__c.fetchone()).split(", ")
        for idx, item in enumerate(splitRow):
            splitRow[idx] = splitRow[idx].replace('(', '')
            splitRow[idx] = splitRow[idx].replace(')', '')
            splitRow[idx] = splitRow[idx].replace('\'', '')
        return splitRow

    def RetrieveUserRank(self, userId: int) -> list:
        userStats = []
        userData = self.RetrieveUser(userId)
        userStats.append(math.floor(float(userData[1])))
        exp = userData[2]
        userStats.append(exp)
        userStats.append(self.ExpRemainingAlgorithm(exp))
        userStats.append(userData[3])
        return userStats
    def RetrieveUserTitles(self, userId: int) -> list:
        self.__c.execute(f'SELECT * FROM userTitles WHERE userID=?', (userId, ))
        splitRow = str(self.__c.fetchone()).split(", ")
        for idx, item in enumerate(splitRow):
            splitRow[idx] = splitRow[idx].replace('(', '')
            splitRow[idx] = splitRow[idx].replace(')', '')
            splitRow[idx] = splitRow[idx].replace('\'', '')
        return splitRow

    def RetrieveAllUsers(self, ctx) -> list:
        leaderboardList = []
        self.__c.execute(f'SELECT * FROM userData')
        fetchedRows = self.__c.fetchall()
        for idx, row in enumerate(fetchedRows):
            splitRow = str(fetchedRows[idx]).split(", ")  
            for idx3, item in enumerate(splitRow):
                splitRow[idx3] = splitRow[idx3].replace('(', '')
                splitRow[idx3] = splitRow[idx3].replace(')', '')
                splitRow[idx3] = splitRow[idx3].replace('\'', '') 
            row = []
            member = ctx.guild.get_member(int(splitRow[0]))
            if(member != None):
                row.append(member.name)
                row.append(math.floor(float(splitRow[1])))
                row.append(splitRow[2])
                row.append(splitRow[3])
                row.append(splitRow[0])
                leaderboardList.append(row)
        return leaderboardList

    def CheckUserLevelUp(self, bot: discord.Client, authorId, userData, experience):
        if(bot != None):
            author: discord.Member = bot.get_user(authorId)
            userExp = int(userData[2])
            userLevelBefore = self.LevellingAlgorithm(userExp)
            userLevelAfter = self.LevellingAlgorithm(userExp + experience)
            if (userLevelBefore != userLevelAfter):
                embed = discord.Embed(
                    title = f"You Leveled Up!",                    
                    description = f"You are now *{str(int(float(userData[1]))+1)}* steps closer to the cosmos!",
                    colour = discord.Colour.purple()
                )        
                embed.set_author(name=f'@'+author.display_name, icon_url=author.display_avatar)
                return embed
            else:
                pass 

    def StoreUserExp(self, bot: discord.Client, authorId, getExp: bool, expAmount: int = __expPerMessage):
        userData = self.RetrieveUser(authorId)  
        levelUpEmbed = None
        if getExp:            
            userExp = int(userData[2]) + expAmount
            userLevel = self.LevellingAlgorithm(userExp)
        else:
            userExp = int(userData[2])
            userLevel = self.LevellingAlgorithm(userExp)
        userMessagesSent = int(userData[3]) + 1
        self.__c.execute(f"UPDATE userData SET userID = {authorId}, userLevel = {userLevel}, userExp = {int(userExp)}, userSentMsgs = {userMessagesSent} WHERE userID=?", (authorId, ))
        self.__conn.commit()  
        if(getExp):
            levelUpEmbed = self.CheckUserLevelUp(bot, authorId, userData, expAmount)
            return levelUpEmbed

    def StoreUserEquipment(self, userId, equipment: Equipment):
        self.__c.execute(f"UPDATE userData SET userMod = \"{equipment.modifier}\", userEquipment = \"{equipment.name}\" WHERE userID=?", (userId, ))
        self.__conn.commit()

    def StoreUserTitle(self, userId, title: str):
        self.__c.execute(f"INSERT INTO userTitles (userID, userTitle) VALUES (?, ?)", (userId, title, ))
        self.__conn.commit()

    def ResetServerRankData(self, interaction: discord.Interaction):
        self.__c.execute("DELETE FROM userData")
        self.__c.execute("CREATE TABLE IF NOT EXISTS userData(userID TEXT, userLevel TEXT, userExp TEXT, userSentMsgs TEXT)")
        for member in interaction.guild.members:
            memberID = str(member.id)             
            self.__c.execute(f"INSERT INTO userData VALUES (?,0,0,0,0,?)", (memberID, "Fists", ))
        self.__conn.commit()
        print("Storing fresh data successful.")

    def ResetUserData(self, authorId):
        self.__c.execute(f"UPDATE userData SET userLevel = 0, userExp = 0 WHERE userID = ?", (authorId, ))
        self.__conn.commit()

    def LevellingAlgorithm(self, exp):
        return int(self.__levellingConstant * math.sqrt(exp))

    def ExpRemainingAlgorithm(self, exp):
        return round((math.ceil(float(self.__levellingConstant * math.sqrt(int(exp) + 1))) ** 2) / (self.__levellingConstant * self.__levellingConstant) - int(exp))