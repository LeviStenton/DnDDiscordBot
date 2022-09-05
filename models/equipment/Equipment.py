class Equipment:
    def __init__(self, name, mod, rarity):
        self._name = name
        self._modifier = mod
        self._rarity = rarity

    @property
    def name(self) -> str:
        return self._name
    @name.setter
    def name(self, value: str):
        self._name = value

    @property
    def modifier(self) -> int:
        return self._modifier
    @modifier.setter
    def modifier(self, value: int):
        self._modifier = value

    @property
    def rarity(self) -> int:
        return self._rarity
    @rarity.setter
    def rarity(self, value: int):
        self._rarity = value