import discord
import random
from models.polls.poll import Poll
from models.polls.poll import Option

class PollController():
    _activePolls = list()

    def AddPoll(self, interaction: discord.Interaction, poll: Poll):
        self._activePolls.append(poll)

        author = interaction.user.name
        authorAvatar = interaction.user.display_avatar
        embed = discord.Embed(
            title = "Poll: " + poll.title,
            colour = discord.Colour.purple()
        )
        embed.set_author(name=f'{author}', icon_url=authorAvatar)
        embed.set_footer(text=f"Time: {poll.timeStamp}")
        for idx, option in enumerate(poll.options):
            embed.add_field(name=f"{idx+1}: {option.name} *({option.votes})*", value=f"{option.voters}", inline=True)
        
        #poll.view = discord.ui.View()
        poll.view = PollButtons(poll.options)
        
        return embed, poll.view

class PollButtons(discord.ui.View):
    def __init__(self, options: list):
        super().__init__(timeout = 86400) # 1 day in seconds
        for idx, option in enumerate(options):
            self.add_item(PollButton(label=f"{idx+1}", style=discord.ButtonStyle.green, option=option))

class PollButton(discord.ui.Button):  
    def __init__(self, label: str, style: discord.ButtonStyle, option: Option):
        super().__init__(label=label, style = style)
        self.option = option
    async def callback(self, interaction):
        assert self.option is not None
        embed = interaction.message.embeds[0]
        currentVoters = embed.fields[self.option.index].value
        if interaction.user.name in currentVoters:
              return
        if currentVoters:
            currentVoters += ", "
        currentVoters += interaction.user.name   
        self.option.votes += 1
        #embed.description += " " + interaction.user.name + f"(**{self.option.index+1}**), "        
        embed.set_field_at(index=self.option.index, name=f"{self.option.index+1}: {self.option.name} *({self.option.votes})*", value=currentVoters)
        await interaction.response.edit_message(content =f"{interaction.user.name} has voted for {self.option.name}!", embed=embed)
            
        





