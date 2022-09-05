# Discord
import discord
import random
import sqlite3
from models.encounters.IEncounterable import IEncounterable

class IEncounter(discord.Embed):
    
    def __init__(self, title, description, colour):            
        self._tableName = None
        super().__init__(
            title=title,
            description=description,
            colour=colour
        )

    @property
    def encounter(self) -> IEncounterable:
        return self._encounter
    @encounter.setter
    def encounter(self, value: IEncounterable):
        self._encounter = value     

    @property
    def tableName(self) -> str:
        if self._tableName == None:
            raise NotImplementedError("No table name supplied.")
        return self._tableName
    @tableName.setter
    def tableName(self, value: str):
        self._tableName = value

    def GenerateEncounter(self) -> IEncounterable:
        rarity = self.GetRarity()
        conn = sqlite3.connect('databases/encountersdb.db')
        c = conn.cursor()
        c.execute("SELECT name, experience, challengeRating, armourClass, picturePath " +
           f"FROM {self.tableName} " + 
            "WHERE rarity=?; ", 
            (rarity,))
        encounters = []
        for row in c.fetchall():
            encounters.append(IEncounterable(row[0], row[1], row[2], row[3], row[4], rarity)) 
        self.encounter = encounters[random.randint(0, len(encounters) - 1)]

    def GetRarity(self) -> str:
        randomInt = random.random()
        match randomInt:
            case _ if randomInt > IEncounterable.uncommonChance:
                return "common"
            case _ if randomInt > IEncounterable.rareChance and randomInt < IEncounterable.uncommonChance:
                return "uncommon"
            case _ if randomInt > IEncounterable.veryrareChance and randomInt < IEncounterable.rareChance:
                return "rare"
            case _ if randomInt > IEncounterable.legendaryChance and randomInt < IEncounterable.veryrareChance:
                return "veryrare"
            case _ if randomInt < IEncounterable.legendaryChance:
                return "legendary"




