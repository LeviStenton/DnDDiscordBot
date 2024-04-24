import discord
from discord.ext import commands
import random
import sqlite3
from models.raids.raid import Raid
from controllers.DatabaseController import DatabaseController

class RaidController():
    tableName = 'raids'
    uncommonChance = 0.4
    rareChance = 0.15
    veryrareChance = 0.05
    legendaryChance = 0.01

    _currentRaid: Raid
    costMultiplier: int = 10

    def __init__(self):
        pass

    def InitiateRaid(self, authorID: str, bot: discord.Client, initiationCost: int, conclusionTime: int, rarityOverride: float = None) -> discord.Embed:                
        conn = sqlite3.connect('databases/raidsdb.db')
        c = conn.cursor()
        raids = []
        while not raids:
            rarity = self.GetRarity(rarityOverride)
            c.execute("SELECT name, hitpoints, title, image " +
            f"FROM {self.tableName} " + 
                "WHERE rarity=?; ", 
                (rarity,))
            for row in c.fetchall():
                raids.append(Raid(row[0], row[1], row[2], row[3], rarity, conclusionTime))         
        
        self._currentRaid = raids[random.randint(0, len(raids) - 1)]
        engagementCost: int = self._currentRaid.hitPoints * self.costMultiplier # cost to engage is 10 x hitpoints in gold
        self._currentRaid.view = RaidButtons(bot=bot, currentRaid=self._currentRaid, engagementCost=engagementCost)
        DatabaseController().StoreUserExp(bot, authorID, False, initiationCost)
        return self._currentRaid, self._currentRaid.view
    
    def ConcludeRaid(self) -> discord.Embed:
        print(self._currentRaid.raiderPower)
        print(self._currentRaid.hitPoints)
        if(self._currentRaid.raiderPower >= self._currentRaid.hitPoints):
            embed = discord.Embed(
                title = "You conquered the raid!",
                colour = discord.Colour.gold()
            )
            embed.set_author(name=self._currentRaid.title, icon_url=self._currentRaid.image)  
            embed.add_field(name=f"All participents have been earned the raid's title!", value=self._currentRaid.title, inline=True)  
            for participant in self._currentRaid.raidParticipants:
                try:
                    DatabaseController().StoreUserTitle(participant, self._currentRaid.title)
                except:
                    pass
            return embed
        else:
            embed = discord.Embed(
                title = "You failed the raid!",
                colour = discord.Colour.gold()
            )
            embed.set_author(name=self._currentRaid.title, icon_url=self._currentRaid.image)  
            return embed

    def GetRarity(self, rarityOverride: float) -> str:
        if rarityOverride == None:
            randomInt = random.random()
        else:
            randomInt = rarityOverride

        global uncom
        match randomInt:
            case _ if randomInt > self.uncommonChance:
                return "common"
            case _ if randomInt > self.rareChance and randomInt < self.uncommonChance:
                return "uncommon"
            case _ if randomInt > self.veryrareChance and randomInt < self.rareChance:
                return "rare"
            case _ if randomInt > self.legendaryChance and randomInt < self.veryrareChance:
                return "veryrare"
            case _ if randomInt < self.IEncounterable.legendaryChance:
                return "legendary"           

class RaidButtons(discord.ui.View):
    def __init__(self, bot: discord.Client, currentRaid: Raid, engagementCost: int):
        super().__init__(timeout = 86400) # 1 day in seconds
        self.add_item(PollButton(label=f"🗡️ {engagementCost} Gold", style=discord.ButtonStyle.red, bot=bot, currentRaid=currentRaid, engagementCost=engagementCost))
            

class PollButton(discord.ui.Button): 
    bot: discord.Client
    currentRaid: Raid 
    engagementCost: int
    def __init__(self, label: str, style: discord.ButtonStyle, bot: discord.Client, currentRaid: Raid, engagementCost: int):
        super().__init__(label=label, style = style)
        self.engagementCost = engagementCost
        self.bot = bot
        self.currentRaid = currentRaid
    async def callback(self, interaction):
        embed = interaction.message.embeds[0]
        currentRaiders = embed.fields[2].value
        if interaction.user.name in currentRaiders:
              return     
        if currentRaiders:
            currentRaiders += ", "
        currentRaiders += interaction.user.name 
        self.currentRaid.raidParticipants.append(interaction.user.id)   
        DatabaseController().StoreUserExp(self.bot, interaction.user.id, False, -self.engagementCost)
        userData = DatabaseController().RetrieveUser(interaction.user.id)
        userPower = int(userData[4])
        self.currentRaid.raiderPower += userPower
        embed.set_field_at(index=1, name=f"Your Power", value=self.currentRaid.raiderPower)
        embed.set_field_at(index=2, name=f"Participants", value=currentRaiders)
        await interaction.response.edit_message(content =f"{interaction.user.name} has joined the fray!", embed=embed)