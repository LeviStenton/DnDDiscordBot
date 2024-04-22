# Discord
import discord
from controllers.DatabaseController import DatabaseController

class Raid(discord.Embed):
    name: str = ""
    hitPoints: int = 0
    rarity: str = ""
    title: str = ""
    image: str = ""
    conclusionTime: int = 0
    raiderPower: int = 0
    raidParticipants = []
    raidView: discord.ui.View    

    def __init__(self, name: str, hitPoints: int, title: str, image: str, rarity: str, conclusionTime: int):  
        def GetRarityCircle(rarity: str) -> str:
            match rarity:
                case "common":
                    return "⚪"
                case "uncommon":
                    return "🟢"
                case "rare":
                    return "🔵"
                case "veryrare":
                    return "🟣"
                case "legendary":
                    return "🟠"
        self.name = name
        self.hitPoints  = hitPoints
        self.title = title
        self.rarity = rarity
        self.image = image
        self.conclusionTime = conclusionTime
        super().__init__(
            title=name,
            description= GetRarityCircle(str(rarity)) + " " + title,
            colour=discord.Colour.gold()
        )
        super().set_author(name="Raid!", icon_url="https://i.pinimg.com/originals/48/cb/53/48cb5349f515f6e59edc2a4de294f439.png")
        super().set_image(url=image)
        super().add_field(name="Hitpoints", value=self.hitPoints)
        super().add_field(name="Your Power", value=self.raiderPower)
        super().add_field(name="Participants", value="")
        super().set_footer(text=f"Reach its hitpoints in cumulative equipment modifiers within {conclusionTime} seconds to defeat it and claim its title!")