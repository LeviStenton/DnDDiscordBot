# import speech_recognition as sr
# import random
# import re

# filename = "TestCases/d20plus5withAdv.wav"

# # initialize the recognizer
# r = sr.Recognizer()

# # open the file
# with sr.AudioFile(filename) as source:
#     # listen for the data (load audio into memory)
#     audio_data = r.record(source)
#     # recognize (convert from speech to text)
#     text = r.recognize_google(audio_data)
#     print(text)


# def RollDice(dieSides, dieNum=1, dieMod=0):
#     dieOutcomes = ''
#     dieList = []
#     dieTotal = 0

#     for die in range(dieNum):
#         diceRoll = random.randint(1, dieSides)+dieMod
#         dieList.append(str(diceRoll-dieMod)+'+'+str(dieMod))
#         dieTotal += diceRoll

#     dieOutcomes = ', '.join(dieList)
#     return ('You rolled: '+dieOutcomes+', Total: '+str(dieTotal))

# def RollDiceAdv(dieSides, dieNum=1, dieMod=0):
#     dieOutcomes = ''
#     dieList = []
#     dieTotal = 0

#     for die in range(dieNum*2):
#         diceRoll = random.randint(1, dieSides)+dieMod
#         dieList.append(str(diceRoll-dieMod)+'+'+str(dieMod))
#         dieTotal += diceRoll

#     dieOutcomes = ', '.join(dieList)
#     return ('You rolled: '+dieOutcomes)

# if re.match("(?i)roll|(?i)rule) .+ d(?: ?).+ .+ .+", text):
#     dieNum = re.findall("(?:(?:(?i)roll|(?i)rule)|r)?(.+)(?: ?)d(?: ?).+(?: ?)(?:.+(?: ?).+)*", text)
#             print(dieNum[0])
#             if dieNum[0] == 'a': dieNum[0] = 1;
#             dieFaces = re.findall("(?:(?:(?i)roll|(?i)rule)|r)?(?: ?).+(?: ?)d(?: ?)(.+)(?: ?)(?:.+(?: ?).+)*", text)
#             if re.match(".+[+|-]", dieFaces[0]):
#                 dieFaces = re.findall("(.+)[+|-]", dieFaces[0])
#             print(dieFaces[0])
#             dieModOperand = re.findall("(?:(?:(?i)roll|(?i)rule)|r)?(?: ?).+(?: ?)d(?: ?).+(?: ?)(.+)(?: ?).+", text)
#             if len(dieModOperand) == 0:
#                 dieModOperand.append('+')
#             elif dieModOperand[0] == '':
#                 dieModOperand[0] = '+'            
#             print(dieModOperand[0])
#             dieMod = re.findall("(?:(?:(?i)roll|(?i)rule)|r)?(?: ?).+(?: ?)d(?: ?).+(?: ?).+(?: ?)(.+)", text)
#             if len(dieMod) == 0:
#                 dieMod.append(0)
#             elif dieMod[0] == '':
#                 dieMod[0] = 0           
#             print(dieMod[0])    
#     print(str(RollDice(int(dieFaces[0]), int(dieNum[0]), int(dieNum[0])))

print("\033[1m"+"Hello"+"\033[1m")
print("Hello")
