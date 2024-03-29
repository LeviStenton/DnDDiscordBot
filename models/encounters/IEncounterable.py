class IEncounterable():
    uncommonChance = 0.4
    rareChance = 0.15
    veryrareChance = 0.05
    legendaryChance = 0.01
    commonDropChance = 1 - uncommonChance
    uncommonDropChance = uncommonChance - rareChance
    rareDropChance = rareChance - veryrareChance
    veryrareDropChance = veryrareChance - legendaryChance
    legendaryDropChance = legendaryChance   

    def __init__(self, name, experience, challengeRating, armourClass, picturePath, rarity):
        self._name = name
        self._experience = experience
        self._challengeRating = challengeRating
        self._armourClass = armourClass
        self._picturePath = picturePath
        self._rarity = rarity

    @property
    def name(self):
        return self._name
    @name.setter
    def name(self, value):
        self._name = value

    @property
    def experience(self):
        return self._experience
    @experience.setter
    def experience(self, value):
        self._experience = value

    @property
    def challengeRating(self):
        return self._challengeRating
    @challengeRating.setter
    def challengeRating(self, value):
        self._challengeRating = value

    @property
    def armourClass(self):
        return self._armourClass
    @armourClass.setter
    def armourClass(self, value):
        self._armourClass = value

    @property
    def picturePath(self):
        return self._picturePath
    @picturePath.setter
    def picturePath(self, value):
        self._picturePath = value
        
    @property
    def rarity(self):
        return self._rarity
    @rarity.setter
    def rarity(self, value):
        self._rarity = value
