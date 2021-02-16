# Discord
import discord
from discord.ext import commands
from discord.ext.commands import has_permissions, CheckFailure
# Random
import random
# Other scripts
from cogs.Experience import ExperienceSystem as experience
from cogs.DisplayData import UserDataCommands as displayData
from cogs.Main import BotMain as main

class RandomEncounters(commands.Cog):
    # Global variables for Encounters
    encounterID = 0
    encounterBool = False
    encounterType = []
    encClearID = 0
    encClearBool = False
    encClearLoot = []
    encClearUser = 0
    lootDropThresh = 0.33 
    lootChance = 0.0

    def __init__(self, bot):
        self.bot = bot

    # Spawns an encounter
    @commands.command(name='encounter')
    @has_permissions(administrator=True, manage_messages=True, manage_roles=True)
    async def Spawn_Encounter(self, ctx):
        dat = displayData(self.bot)
        mai = main(self.bot)
        # Generating an encounter  
        # Declaring variables to be used
        generalID = mai.generalChannel
        encounterTypeChance = 0.3
        encounterFloat = random.random()
        channelID = ctx.channel.id
        channel = self.bot.get_channel(channelID)
        if(channelID == generalID and ctx.author.id != mai.botID):
            global encounterType
            global encounterID 
            global encounterBool
            if encounterFloat >= encounterTypeChance:
                encounterType = self.SkillRandomEncounter()
                encounterMsg = await channel.send(embed=encounterType[0])        
                encounterID = encounterMsg.id
                encounterBool = True
                await encounterMsg.add_reaction(dat.rollEmote) 
            elif encounterFloat < encounterTypeChance:
                encounterType = self.DNDMonRandomEncounter()
                encounterMsg = await channel.send(embed=encounterType[0])        
                encounterID = encounterMsg.id
                encounterBool = True
                await encounterMsg.add_reaction(dat.rollEmote)   

    # A method that is called when someone reacts the d20 to the message, calls RctExpSystem
    def ClearEncounter(self, reaction, user, rollNum, userMod, equipment): 
        mai = main(self.bot)
        exp = experience(self.bot)
        # global lootChance
        encClearUser = user.id
        authorAvatar = user.avatar_url
        author = user.name    
        expReward = encounterType[1]    
        outcomeMsg = ''
        rollTotal = rollNum+userMod
        if reaction.message.id == encounterID and user.id != mai.botID and self.encounterBool:   
            if rollNum == 20:
                exp.RctExpSystem(user, int(expReward)*2)
                outcomeMsg = f'***Nat 20!*** You defeated the encounter with your {equipment}! ***{int(expReward)*2}*** Exp rewarded!'
            elif rollTotal >= encounterType[2]:
                exp.RctExpSystem(user, expReward)
                outcomeMsg = f'You defeated the encounter with your {equipment}! **{expReward}** Exp rewarded!'  
            elif rollNum == 1:
                    exp.RctExpSystem(user, -int(expReward))
                    outcomeMsg = f'***Nat 1!*** You were slain by the encounter! **{-int(expReward)}** Exp lost!'      
            else:
                outcomeMsg = 'You were defeated.'
            embed = discord.Embed(
                title = f"You rolled: *{rollNum} +{userMod}*",
                description = outcomeMsg,
                colour = discord.Colour.red()
            )        
            encounterBool = False        
            if self.lootChance >= self.lootDropThresh and rollTotal >= encounterType[2]:
                encClearLoot = self.EncounterLoot()
                embed.add_field(name=f"You got", value=f"*{encClearLoot[0]}*", inline=True)
                embed.add_field(name=f"It's modifier", value=f"+{encClearLoot[1]}", inline=True)
                embed.add_field(name=f"Do you pick it up?", value="React to equip.", inline=False)            
            embed.set_author(name=f'{author}', icon_url=authorAvatar)
            return embed

    # The loot that is dropped by defeating an encounter
    def EncounterLoot(self):
        condition = ["Worthless ", "Rusty ", "Damascus ", "Overdriven ", "Astral ", "Eldritch "]
        ranCond = random.randint(0,len(condition)-1)
        equipment = ["Limp Noodle", "Boot Knife", "Lasso", "Six Shooter", "Gatling Laser", "Cow"]
        ranEquip = random.randint(0,len(equipment)-1)
        enchantment = [" of Garbage", " of Mediocrity", " of Moondust", " of Unfallible Accuracy", " of Starfire",  " of Cosmic Knowledge"]
        ranEnchant = random.randint(0,len(enchantment)-1)
        totalEquipment = condition[ranCond]+equipment[ranEquip]+enchantment[ranEnchant]
        totalEquipmentMod = str(ranCond+ranEquip+ranEnchant)
        return totalEquipment, totalEquipmentMod

    # Method to call to create a new monster encounter embedded message, stores monster data
    def DNDMonRandomEncounter(self):    
        monsters = ["Wolf","Goblin","Bandit","Gorgon","Harpy","Green Dragon Wyrmling","Werewolf","Stone Giant"]
        experience = ["50","50","25","1800","200","450","700","2900"]
        challengeRating = ["1/4","1/4","1/8","5","1","2","3","7"]
        armourClass = [13,15,12,19,11,17,12,17]
        monPicture = ["https://media-waterdeep.cursecdn.com/avatars/thumbnails/0/54/1000/1000/636252725270715296.jpeg",
        "https://media-waterdeep.cursecdn.com/avatars/thumbnails/0/351/1000/1000/636252777818652432.jpeg",
        "https://media-waterdeep.cursecdn.com/avatars/thumbnails/0/181/1000/1000/636252761965117015.jpeg",
        "https://media-waterdeep.cursecdn.com/avatars/thumbnails/0/355/1000/1000/636252778125099430.jpeg",
        "https://media-waterdeep.cursecdn.com/avatars/thumbnails/0/391/1000/1000/636252781955908234.jpeg",
        "https://media-waterdeep.cursecdn.com/avatars/thumbnails/0/363/1000/1000/636252778639163748.jpeg",
        "https://media-waterdeep.cursecdn.com/avatars/thumbnails/0/74/1000/1000/636252734224239957.jpeg",
        "https://media-waterdeep.cursecdn.com/avatars/thumbnails/0/109/1000/1000/636252744518731463.jpeg"]
        randomInt = random.randint(0,len(monsters)-1)

        embed = discord.Embed(
            title = f"A {monsters[randomInt]} appeared!",
            description= "Roll to attack!",
            colour = discord.Colour.red()
        )
        embed.set_thumbnail(url=f"{monPicture[randomInt]}")
        embed.set_author(name=f'Combat Encounter!', icon_url="https://i.pinimg.com/originals/48/cb/53/48cb5349f515f6e59edc2a4de294f439.png")
        embed.add_field(name=f"**AC**", value=f"{armourClass[randomInt]}", inline=True)
        embed.add_field(name=f"**CR**", value=f"{challengeRating[randomInt]}", inline=True)
        embed.add_field(name=f"**EXP**", value=f"{experience[randomInt]}", inline=True)    
        return embed, experience[randomInt], armourClass[randomInt] 

    # Method to call to create a new skill encounter embedded message, stores encounter data
    def SkillRandomEncounter(self):    
        monsters = ["A Boulder Is Falling!","Lockpick The Chest!","Withstand The Storm!","You Are Lost In A Desert","Flee The Treant!","A Thief Approaches!", "Save Rogue Bear!"]
        experience = ["100","200","350","300","1000","50", "1250"]
        challengeRating = ["1","2","3","2 1/2","5","1/2", "7"]
        armourClass = [14,15,16,14,18,12,19]
        monPicture = ["https://pbs.twimg.com/media/C8L2wgVWkAUCi32.png",
        "https://media-waterdeep.cursecdn.com/avatars/thumbnails/0/211/1000/1000/636252764731637373.jpeg",
        "https://i1.wp.com/nerdarchy.com/wp-content/uploads/2018/05/Brainstorm.png?fit=864%2C628&ssl=1",
        "https://static.wikia.nocookie.net/emerald-isles/images/8/87/Desert.jpg/revision/latest/top-crop/width/220/height/220?cb=20180209064004",
        "https://comicvine1.cbsistatic.com/uploads/original/11120/111209888/5139105-014afdf2e2481539ed8959752233f379.jpg",
        "https://roadbeerdotnet.files.wordpress.com/2020/07/thief-six-1024x1024-1.jpg",
        "https://static.wikia.nocookie.net/forgottenrealms/images/c/c3/Druid_and_bear-5e.jpg/revision/latest/scale-to-width-down/350?cb=20190808192744"]
        randomInt = random.randint(0,len(monsters)-1)

        embed = discord.Embed(
            title = f"{monsters[randomInt]}",
            description= "Roll to test your skill!",
            colour = discord.Colour.red()
        )
        embed.set_thumbnail(url=f"{monPicture[randomInt]}")
        embed.set_author(name=f'Skill Encounter!', icon_url="https://i.pinimg.com/originals/48/cb/53/48cb5349f515f6e59edc2a4de294f439.png")
        embed.add_field(name=f"**DC**", value=f"{armourClass[randomInt]}", inline=True)
        embed.add_field(name=f"**CR**", value=f"{challengeRating[randomInt]}", inline=True)
        embed.add_field(name=f"**EXP**", value=f"{experience[randomInt]}", inline=True)    
        return embed, experience[randomInt], armourClass[randomInt] 

def setup(bot):
    bot.add_cog(RandomEncounters(bot))