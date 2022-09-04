class UserRank:
    def __init__(self, displayName, avatar, level, exp, expRemaining, msgSent):
        self._displayName = displayName
        self._avatar = avatar
        self._level = level
        self._exp = exp
        self._expRemaining = expRemaining
        self._msgSent = msgSent    

    @property
    def displayName(self) -> str:
        return self._displayName
    @displayName.setter
    def displayName(self, value: str):
        self._displayName = value

    @property
    def avatar(self) -> int:
        return self._avatar
    @avatar.setter
    def avatar(self, value: int):
        self._avatar = value

    @property
    def level(self) -> int:
        return self._level
    @level.setter
    def level(self, value: int):
        self._level = value

    @property
    def exp(self) -> int:
        return self._exp
    @exp.setter
    def exp(self, value: int):
        self._exp = value

    @property
    def expRemaining(self) -> int:
        return self._expRemaining
    @expRemaining.setter
    def expRemaining(self, value: int):
        self._expRemaining = value

    @property
    def msgSent(self) -> int:
        return self._msgSent
    @msgSent.setter
    def msgSent(self, value: int):
        self._msgSent = value