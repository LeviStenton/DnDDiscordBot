from models.equipment.Equipment import Equipment
import discord

import random

class EquipmentController:
    _condition = ["Worthless ", "Rusty ", "Damascus ", "Overdriven ", "Astral ", "Eldritch "]
    _equipment = ["Limp Noodle", "Boot Knife", "Lasso", "Six Shooter", "Gatling Laser", "Cow"]
    _enchantment = [" of Garbage", " of Mediocrity", " of Moondust", " of Unfallible Accuracy", " of Starfire",  " of Cosmic Knowledge"]

    def RollEquipment(self) -> Equipment:        
        ranCond = random.randint(0,len(self._condition)-1)        
        ranEquip = random.randint(0,len(self._equipment)-1)        
        ranEnchant = random.randint(0,len(self._enchantment)-1)
        totalEquipmentName = self._condition[ranCond]+self._equipment[ranEquip]+self._enchantment[ranEnchant]
        totalEquipmentMod = str(ranCond+ranEquip+ranEnchant)
        return Equipment(totalEquipmentName, totalEquipmentMod)
