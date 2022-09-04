from models.encounters.IEncounter import IEncounter
import discord

class MonsterEncounter(IEncounter):
    def __init__(self, user):
        self.tableName = "monsters"
        self.GenerateEncounter()
        super().__init__(
            title=f"A {self.encounter.name} appeared!",
            description="Roll to attack!",
            colour=discord.Colour.red()
        )
        self.set_thumbnail(url=f"{self.encounter.picturePath}")
        self.set_author(name=f'Monster Encounter!', icon_url="https://i.pinimg.com/originals/48/cb/53/48cb5349f515f6e59edc2a4de294f439.png")
        self.add_field(name=f"**AC**", value=f"{self.encounter.armourClass}", inline=True)
        self.add_field(name=f"**CR**", value=f"{self.encounter.challengeRating}", inline=True)
        self.add_field(name=f"**EXP**", value=f"{self.encounter.experience}", inline=True)    
        self.set_footer(text=user.display_name, icon_url=user.display_avatar)
