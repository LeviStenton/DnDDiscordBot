import discord

class Poll():
    def __init__(self, title: str, options: str, timeStamp: str):
        self._title = title
        self._options = options
        self._timeStamp = timeStamp

    @property
    def title(self) -> str:
        return self._title
    @title.setter
    def title(self, value: str):
        self._title = value

    @property
    def options(self):
        return self._options
    @options.setter
    def options(self, value):
        self._options = value

    @property
    def timeStamp(self) -> str:
        return self._timeStamp
    @timeStamp.setter
    def timeStamp(self, value: str):
        self._timeStamp = value

    @property
    def view(self) -> discord.ui.View:
        return self._view
    @view.setter
    def view(self, value: discord.ui.View):
        self._view = value

class Option():
    def __init__(self, index: int, name: str):
        self._index = index
        self._name = name
        self._votes = 0
        self._voters = ""

    @property
    def index(self) -> str:
        return self._index
    @index.setter
    def index(self, value: str):
        self._index = value

    @property
    def name(self) -> str:
        return self._name
    @name.setter
    def name(self, value: str):
        self._name = value

    @property
    def votes(self) -> int:
        return self._votes
    @votes.setter
    def votes(self, value: int):
        self._votes = value

    @property
    def voters(self) -> str:
        return self._voters
    @voters.setter
    def voters(self, value: str):
        self._voters = value