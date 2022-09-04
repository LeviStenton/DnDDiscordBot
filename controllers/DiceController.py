import random
import re
from re import I

class DiceController:

    def QueryRoll(self, text):
        if re.match(r"(?:roll|rule)?(?: ?).+(?: ?)d(?: ?).+(?: ?)(?:[\+|\-|minus|plus](?: ?).+)*", text, flags=I):
            dieNum = re.findall(r"(?:(?:roll|rule)|r)?(.+)(?: ?)d(?: ?).+(?: ?)(?:[\+|\-|minus|plus](?: ?).+)*", text, flags=I)
            if re.match(r"(?: ?)a", dieNum[0]):
                dieNum[0] = 1;
            elif re.match(r"(?: ?)for", dieNum[0]):
                dieNum[0] = 4

            dieFaces = re.findall(r"(?:(?:roll|rule)|r)?(?: ?).+(?: ?)d(?: ?)(.+)(?: ?)(?:[\+|\-|minus|plus](?: ?).+)*", text, flags=I)
            if re.match(r".+(?: ?)(?:\+|\-|minus|plus)", dieFaces[0]):
                dieFaces = re.findall(r"(.+)(?: ?)(?:\+|\-|minus|plus)", dieFaces[0])

            dieModOperand = re.findall(r"(?:(?:roll|rule)|r)?(?: ?).+(?: ?)d(?: ?).+(?: ?)(\+|\-|minus|plus)(?: ?).+", text, flags=I)
            if len(dieModOperand) == 0:
                dieModOperand.append('+')
            elif dieModOperand[0] == '':
                dieModOperand[0] = '+'
            elif dieModOperand[0] == 'plus':
                dieModOperand[0] = '+'
            elif dieModOperand[0] == 'minus':
                dieModOperand[0] = '-'
            if dieModOperand[0] == '-':
                minusMod = True
            else:
                minusMod = False

            dieMod = re.findall(r"(?:(?:roll|rule)|r)?(?: ?).+(?: ?)d(?: ?).+(?: ?)[\+|\-|minus|plus](?: ?)(.+)", text, flags=I)
            if len(dieMod) == 0:
                dieMod.append(0)
            elif dieMod[0] == '':
                dieMod[0] = 0

            return self.RollDice(int(dieFaces[0]), int(dieNum[0]), int(dieMod[0]), minusMod)
        else:
            return 'Error in roll statement.'

    # Takes int data from QueryRoll(), rolls dice based on those numbers, then outputs it in a string
    def RollDice(self, dieSides, dieNum=1, dieMod=0, minus=False):
        dieOutcomes = ''
        dieList = []
        dieTotal = 0
        dieReturn = []

        for die in range(dieNum):
            diceRoll = random.randint(1, dieSides)
            if (diceRoll == 20 or diceRoll == 1) and dieSides == 20:
                dieList.append("__**"+str(diceRoll)+"**__")
            else:
                dieList.append(str(diceRoll))
            dieTotal += diceRoll

        dieOutcomes = ', '.join(dieList)
        dieReturn.append(f"{dieOutcomes}")
        dieReturn.append(f"{self.DieModConverter(dieMod, minus)}")
        if dieMod == 0:
            dieReturn.append(f"{dieTotal}")
        elif dieMod > 0:
            if minus:
                dieReturn.append(f"{dieTotal}")
                dieReturn.append(f"{dieTotal-dieMod}")
            else:
                dieReturn.append(f"{dieTotal}")
                dieReturn.append(f"{dieTotal+dieMod}")

        return dieReturn

    # If the modifier is 0, it outputs 'With No Modifier', also formats '-' and '+'
    def DieModConverter(self, dieMod, minus=False):
        output = ''
        if dieMod == 0:
            output = '*With No Modifier*'
        else:
            if minus:
                output = '*-'+str(dieMod)+'*'
            else:
                output = '*+'+str(dieMod)+'*'
        return output