import sqlite3
import discord
import math

from models.equipment.Equipment import Equipment

class DatabaseController: 
    __levellingConstant = 0.1
    __expPerMessage = 1
    # Initialize the database
    __conn = sqlite3.connect('databases/levellingDB.db')
    __c = __conn.cursor()


    def __init__(self):
        pass

    def CloseDatabase(self):
        self.__conn.close()

    async def StoreNewUser(self, member, role):
        self.__c.execute(f"INSERT or IGNORE INTO userData VALUES(?,0,0,0,0,?)", (member.id, "Fists", ))
        self.__conn.commit()  
        await member.add_roles(role)

        
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
        userStats.append(round((math.ceil(float(userData[1])) ** 2) / (self.__levellingConstant * self.__levellingConstant) - int(exp)))
        userStats.append(userData[3])
        return userStats

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
                    


    async def CheckUserLevelUp(self, author, userData, levelUpChannel, experience):
        userExp = userData[2]
        expRemaining = round((math.ceil(float(userData[1])) ** 2) / (self.__levellingConstant * self.__levellingConstant) - int(userExp))
        if expRemaining - experience <= 0:
            embed = discord.Embed(
                title = f"You Leveled Up!",
                description = f"You are now *{int(float(userData[1]))}* steps closer to the cosmos!",
                colour = discord.Colour.purple()
            )        
            embed.set_author(name=f'@'+author.display_name, icon_url=author.display_avatar)
            await levelUpChannel.send(embed=embed)
        else:
            pass 

    def StoreUserExp(self, authorId, getExp: bool, levelUpChannel, expAmount: int = __expPerMessage):
        userData = self.RetrieveUser(authorId)  
        if getExp:
            #self.CheckUserLevelUp(author, userData, levelUpChannel, expAmount)
            userExp = int(userData[2]) + expAmount
            userLevel = (self.__levellingConstant * math.sqrt(userExp))
        else:
            userExp = int(userData[2])
            userLevel = (self.__levellingConstant * math.sqrt(userExp))
        userMessagesSent = int(userData[3]) + 1
        self.__c.execute(f"UPDATE userData SET userID = {authorId}, userLevel = {userLevel}, userExp = {int(userExp)}, userSentMsgs = {userMessagesSent} WHERE userID=?", (authorId, ))
        self.__conn.commit()  

    def StoreUserEquipment(self, userId, equipment: Equipment):
        self.__c.execute(f"UPDATE userData SET userMod = \"{equipment.modifier}\", userEquipment = \"{equipment.name}\" WHERE userID=?", (userId, ))
        self.__conn.commit()

    def ResetServerRankData(self, ctx):
        self.__c.execute("CREATE TABLE IF NOT EXISTS userData(userID TEXT, userLevel TEXT, userExp TEXT, userSentMsgs TEXT)")
        for member in ctx.guild.members:
            memberID = str(member.id)             
            self.__c.execute(f"INSERT INTO userData VALUES (?,0,0,0,0,?)", (memberID, "Fists", ))
            self.__conn.commit()
        print("Storing fresh data successful.")

    def ResetUserData(self, authorId):
        self.__c.execute(f"UPDATE userData SET userLevel = 0, userExp = 0, userSentMsgs = 0 WHERE userID = ?", (authorId, ))
        self.__conn.commit()
