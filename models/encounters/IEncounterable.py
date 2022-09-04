class IEncounterable():
    def __init__(self, name, experience, challengeRating, armourClass, picturePath):
        self._name = name
        self._experience = experience
        self._challengeRating = challengeRating
        self._armourClass = armourClass
        self._picturePath = picturePath

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