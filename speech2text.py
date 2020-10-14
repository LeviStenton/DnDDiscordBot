import speech_recognition as sr
import random
import re

filename = "TestCases/d20plus5withAdv.wav"

# initialize the recognizer
r = sr.Recognizer()

# open the file
with sr.AudioFile(filename) as source:
    # listen for the data (load audio into memory)
    audio_data = r.record(source)
    # recognize (convert from speech to text)
    text = r.recognize_google(audio_data)
    print(text)


def RollDice(dieSides, dieNum=1, dieMod=0):
    dieOutcomes = ''
    dieList = []
    dieTotal = 0

    for die in range(dieNum):
        diceRoll = random.randint(1, dieSides)+dieMod
        dieList.append(str(diceRoll-dieMod)+'+'+str(dieMod))
        dieTotal += diceRoll

    dieOutcomes = ', '.join(dieList)
    return ('You rolled: '+dieOutcomes+', Total: '+str(dieTotal))

def RollDiceAdv(dieSides, dieNum=1, dieMod=0):
    dieOutcomes = ''
    dieList = []
    dieTotal = 0

    for die in range(dieNum*2):
        diceRoll = random.randint(1, dieSides)+dieMod
        dieList.append(str(diceRoll-dieMod)+'+'+str(dieMod))
        dieTotal += diceRoll

    dieOutcomes = ', '.join(dieList)
    return ('You rolled: '+dieOutcomes)

if re.match("(?iroll|(?i)rule) .+ d(?: ?).+ .+ .+", text):
    dieNum = re.findall("(?:(?:r|R)oll|(?:r|R)ule) (.+) d .+ .+ .+", text)
    print(dieNum[0])
    dieFaces = re.findall("(?:(?:r|R)oll|(?:r|R)ule) .+ d(?: ?)(.+) .+ .+", text)
    print(dieFaces[0])
    dieModOperand = re.findall("(?:(?:r|R)oll|(?:r|R)ule) .+ d .+ (.+) .+", text)
    print(dieModOperand[0])
    dieMod = re.findall("(?:(?:r|R)oll|(?:r|R)ule) .+ d .+ .+ (.+)", text)
    print(dieMod[0])
    
    print(str(RollDice(int(dieFaces[0]), int(dieNum[0]), int(dieNum[0]))))

elif re.match("(?iroll|(?i)rule) .+ d(?: ?).+ .+ .+", text):
    dieNum = re.findall("(?:(?:r|R)oll|(?:r|R)ule) (.+) d .+ .+ .+", text)
    print(dieNum[0])
    dieFaces = re.findall("(?:(?:r|R)oll|(?:r|R)ule) .+ d(?: ?)(.+) .+ .+", text)
    print(dieFaces[0])
    dieModOperand = re.findall("(?:(?:r|R)oll|(?:r|R)ule) .+ d .+ (.+) .+", text)
    print(dieModOperand[0])
    dieMod = re.findall("(?:(?:r|R)oll|(?:r|R)ule) .+ d .+ .+ (.+)", text)
    print(dieMod[0])
    
    print(str(RollDice(int(dieFaces[0]), int(dieNum[0]), int(dieNum[0]))))
