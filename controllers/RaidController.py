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

    def __init__(self):
        pass

    def InitiateRaid(self, authorID: str, cost: int, bot: discord.Client, conclusionTime: int, rarityOverride: float = None) -> discord.Embed:
        #DatabaseController().StoreUserExp(bot, authorID, False, cost)
        rarity = self.GetRarity(rarityOverride)
        conn = sqlite3.connect('databases/raidsdb.db')
        c = conn.cursor()
        c.execute("SELECT name, hitpoints, title, image " +
           f"FROM {self.tableName} " + 
            "WHERE rarity=?; ", 
            (rarity,))
        raids = []
        for row in c.fetchall():
            raids.append(Raid(row[0], row[1], row[2], row[3], rarity, conclusionTime)) 
        global _currentRaid
        _currentRaid = raids[random.randint(0, len(raids) - 1)]
        _currentRaid.view = RaidButtons(cost)
        return _currentRaid, _currentRaid.view
    
    def ConcludeRaid(self, bot: discord.Client) -> discord.Embed:
        global _currentRaid
        if(_currentRaid.raiderPower >= _currentRaid.hitPoints):
            embed = discord.Embed(
                title = "You conquered the raid!",
                colour = discord.Colour.gold()
            )
            embed.set_author(name=_currentRaid.title, icon_url=_currentRaid.image)  
            embed.add_field(name=f"All participents have been earned the raid's title!", value=_currentRaid.title, inline=True)  
            for participant in _currentRaid.raidParticipants:
                DatabaseController().StoreUserTitle(participant, _currentRaid.title)
            return embed
        else:
            embed = discord.Embed(
                title = "You failed the raid!",
                colour = discord.Colour.gold()
            )
            embed.set_author(name=_currentRaid.title, icon_url=_currentRaid.image)  
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
    def __init__(self, engagementCost: float):
        super().__init__(timeout = 86400) # 1 day in seconds
        self.add_item(PollButton(label=f"🗡️ 100 Gold", style=discord.ButtonStyle.red))
            

class PollButton(discord.ui.Button):  
    def __init__(self, label: str, style: discord.ButtonStyle):
        super().__init__(label=label, style = style)
    async def callback(self, interaction):
        global _currentRaid
        embed = interaction.message.embeds[0]
        currentRaiders = embed.fields[2].value
        if interaction.user.name in currentRaiders:
              return     
        if currentRaiders:
            currentRaiders += ", "
        currentRaiders += interaction.user.name   
        _currentRaid.raidParticipants.append(interaction.user.id)
        userData = DatabaseController().RetrieveUser(interaction.user.id)
        currentPower: int = int(embed.fields[1].value) + int(userData[4])
        embed.set_field_at(index=1, name=f"Your Power", value=currentPower)
        embed.set_field_at(index=2, name=f"Participants", value=currentRaiders)
        await interaction.response.edit_message(content =f"{interaction.user.name} has joined the fray!", embed=embed)