import discord
import random
import datetime
import time
from controllers.DatabaseController import DatabaseController

class SaidditController():  
    bot: discord.Client = None
    gameRunning = False
    maxOtherGuessees = 4
    historyLength = 100
    chosenGuessees: list[discord.Member] = []
    correctGuessee: discord.Member = None
    chosenMessage: discord.Message = ""
    channel: discord.channel = None
    guesser: discord.Member = None
    goldReward = 10

    def __init__(self):
        pass

    async def InitiateGuessing(self, bot: discord.Client, interaction: discord.Interaction) -> discord.Embed:
        try:
            self.bot = bot
            self.gameRunning = True
            self.channel = interaction.channel
            self.guesser = interaction.user
            channelMembers = self.channel.members             
            randDateTime = self.GetRandomDateTime(interaction.guild.created_at, datetime.datetime.now())
            messages: list[discord.Message] = [message async for message in self.channel.history(limit=self.historyLength, before=randDateTime) if message.content != ""] 

            # Check for if there is only one author for the all the messages sent
            onlyAuthor = True
            for message in messages:
                if(messages[0].author.id != message.author.id):
                    onlyAuthor = False
            if onlyAuthor:
                self.ResetGame()
                return discord.Embed(
                    title="Not enough message authors!",
                    description= "More than one message author must exist to play.",
                    colour=discord.Colour.blurple()
                ), None

            # Choose a message and take it's author as the correct author, appending it to the list or guessees
            chosenMessageIdx = random.randint(0, len(messages) - 1)
            self.chosenMessage = messages[chosenMessageIdx]
            self.correctGuessee = self.chosenMessage.author
            self.chosenGuessees.append(self.correctGuessee)

            # Select a random group of authors form previous messages in the channel, appending them to the list of guessees        
            chosenMembersIds: list[str] = []
            if len(channelMembers)-1 < self.maxOtherGuessees:
                self.maxOtherGuessees = len(channelMembers)-1
            for idx in range(self.maxOtherGuessees):      
                currentChosenAuthor = random.choice([message for message in messages if message.author.id not in chosenMembersIds]).author
                chosenMembersIds.append(currentChosenAuthor.id)       
                if currentChosenAuthor.id == self.correctGuessee.id:
                    continue
                self.chosenGuessees.append(currentChosenAuthor)

            # Shuffle the guessees so that it is presented randomly
            random.shuffle(self.chosenGuessees)

            initiateEmbed = discord.Embed(
                title="❓ Guess who **saiddit**!",
                description= "\"" + self.chosenMessage.content + "\"",
                colour=discord.Colour.blurple()
            )
            initiateEmbed.set_author(name=self.guesser.display_name, icon_url=self.guesser.display_avatar)
            initiateEmbed.set_footer(text=f"Click the name of who you think said the message!")
            initiateView = SaidditButtons(guessees=self.chosenGuessees, saidditController=self, guesserId=self.guesser.id)
            return initiateEmbed, initiateView
        except:
            self.ResetGame()
    
    async def ConcludeGuessing(self, buttonIndex: int) -> discord.Embed:
        title = ""
        description = ""
        correctGuesseeIdx = self.GetCorrectGuesseeIndex(self.chosenGuessees, self.correctGuessee)
        if buttonIndex == correctGuesseeIdx:
            DatabaseController().StoreUserExp(self.bot, self.guesser.id, True, self.goldReward)
            title = "You won!"
            description = "You correctly guessed: " + self.correctGuessee.display_name + "\nYou received " + str(self.goldReward) + " gold"
        else:
            title = "You lost!"
            description = "The correct guess was: " + self.correctGuessee.display_name
        self.ResetGame()
        return discord.Embed(
            title=title,
            description= description,
            colour=discord.Colour.blurple()
        )

    async def DeclareWait(self) -> discord.Embed:
        return discord.Embed(
            title="Please Wait",
            description= "Another game is running.",
            colour=discord.Colour.blurple()
        )

    def ResetGame(self):
        self.gameRunning = False
        self.maxGuesses = 5
        self.historyLength = 500
        self.chosenGuessees: list[discord.Member] = []
        self.correctGuessee: discord.Member = None
        self.chosenMessage: str = ""
        self.channel: discord.channel = None
        self.guesser: discord.Member = None
        self.goldReward = 10

    def GetCorrectGuesseeIndex(self, guessees: list[discord.Member], correctGuessee: discord.Member) -> int:
        for idx, guessee in enumerate(guessees):
            if correctGuessee.id == guessee.id:
                return idx
        return 0
    
    def GetRandomDateTime(self, startDateTime: datetime, endDateTime: datetime) -> datetime:
        startInUnixSeconds = time.mktime(startDateTime.date().timetuple())
        endInUnixSeconds = time.mktime(endDateTime.date().timetuple())
        return datetime.datetime.fromtimestamp(random.randint(int(startInUnixSeconds), int(endInUnixSeconds)))

class SaidditButtons(discord.ui.View):
    def __init__(self, guessees: list[discord.Member], saidditController: SaidditController, guesserId: str):
        super().__init__(timeout = 60) # 1 day in seconds
        for idx, guessee in enumerate(guessees):
            self.add_item(SaidditButton(label=guessee.display_name, style=discord.ButtonStyle.red, saidditController=saidditController, idx=idx, guesserId=guesserId))
            

class SaidditButton(discord.ui.Button): 
    saidditController = SaidditController
    guesserId: str
    buttonIndex: int

    def __init__(self, label: str, style: discord.ButtonStyle, saidditController: SaidditController, idx: int, guesserId: str):
        super().__init__(label=label, style = style)
        self.saidditController = saidditController
        self.guesserId = guesserId
        self.buttonIndex = idx

    async def callback(self, interaction: discord.Member):
        if interaction.user.id != self.guesserId:
            await interaction.response.defer()
            return
        saidditEndEmbed = await self.saidditController.ConcludeGuessing(self.buttonIndex)
        await interaction.response.send_message(embed=saidditEndEmbed) 