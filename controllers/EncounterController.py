import discord
import random
from controllers.DiceController import DiceController
from controllers.EquipmentController import EquipmentController
from models.encounters.IEncounter import IEncounter
from models.encounters.MonsterEncounter import MonsterEncounter
from models.encounters.SkillCheckEncounter import SkillCheckEncounter
from controllers.DatabaseController import DatabaseController

class EncounterController():
    botID = 809671030519889960
    # Encounter variables
    rollEmote = '🎲'
    tickEmote = '✅'
    crossEmote = '❌'       
    encounterID = 0
    encounterActive = False
    encounter = None
    encounterUserID = 0
    encClearID = 0
    encClearLoot = None
    encClearSuccess = False
    encounterDropChance = 1
    encounterTypeChance = 0.5
    lootDropChance = 0.33
    lootDropFloat = 0.0

    def __init__(self):
        pass

    def RollEncounter(self, author, encounterChance = encounterDropChance) -> IEncounter:  
        self.ClearEncounterVariables()      
        encounterDropFloat = random.uniform(0, 1)        
        encounterTypeFloat = random.uniform(0, 1)
        self.encounterUserID = author.id
        if encounterDropFloat < encounterChance and encounterTypeFloat >= self.encounterTypeChance:
            encounterEmbed = MonsterEncounter(author) 
            self.encounter = encounterEmbed.encounter
            self.encounterActive = True
            return encounterEmbed 
        elif encounterDropFloat < encounterChance and encounterTypeFloat < self.encounterTypeChance:
            encounterEmbed = SkillCheckEncounter(author) 
            self.encounter = encounterEmbed.encounter
            self.encounterActive = True
            return encounterEmbed    
        else:
            return None     

    def ClearEncounter(self, author, levelUpChannel) -> discord.Embed:       
        userDB = DatabaseController().RetrieveUser(author.id)
        rollNum = int(DiceController().QueryRoll("1d20")[2])
        userMod =  int(userDB[4])
        userEquipment = userDB[5]
        expReward = self.encounter.experience
        rollTotal = rollNum+userMod
        self.lootDropFloat = random.random() 
        if rollNum == 20:
            DatabaseController().StoreUserExp(author.id, True, levelUpChannel, int(expReward)*2)
            outcomeMsg = f'***Nat 20!*** You defeated the encounter with your {userEquipment}! ***{int(expReward)*2}*** Exp rewarded!'
            self.encClearSuccess = True 
        elif rollTotal >= self.encounter.armourClass:
            DatabaseController().StoreUserExp(author.id, True, levelUpChannel, expReward)
            outcomeMsg = f'You defeated the encounter with your {userEquipment}! **{expReward}** Exp rewarded!'
            self.encClearSuccess = True  
        elif rollNum == 1:
            DatabaseController().StoreUserExp(author.id, True, levelUpChannel, -int(expReward))
            outcomeMsg = f'***Nat 1!*** You were slain by the encounter! **{-int(expReward)}** Exp lost!'
            self.encClearSuccess = False    
        else:
            outcomeMsg = 'You were defeated.'
            self.encClearSuccess = False  
        embed = discord.Embed(
            title = f"You rolled: *{rollNum} +{userMod}*",
            description = outcomeMsg,
            colour = discord.Colour.red()
        )                       
        if self.lootDropFloat <= self.lootDropChance and rollTotal >= self.encounter.armourClass:
            self.encClearLoot = EquipmentController().RollEquipment()
            embed.add_field(name=f"You got", value=f"*{self.encClearLoot.name}*", inline=True)
            embed.add_field(name=f"It's modifier", value=f"+{self.encClearLoot.modifier}", inline=True)
            embed.add_field(name=f"Do you pick it up?", value="React to equip.", inline=False)  
        else:
            self.ClearEncounterVariables()          
        embed.set_author(name=f'{author.display_name }', icon_url=author.display_avatar)
        return embed                       
    
    def ClearEncounterVariables(self):   
        self.encounterType = 0
        self.encounterID = 0
        self.lootChance = 0
        self.encounterUserID = 0
        self.encounterActive = False 