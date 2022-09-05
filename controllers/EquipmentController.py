from models.equipment.Equipment import Equipment
import sqlite3

import random

class EquipmentController:
    __descriptorTableName = "equipmentDescriptors"
    __materialTableName = "equipmentMaterials"
    __objectTableName = "equipmentObjects"

    def RollEquipment(self, rarity) -> Equipment:  
        descriptors = self.__RetrieveEquipmentPiece(self.__descriptorTableName, rarity)        
        materials = self.__RetrieveEquipmentPiece(self.__materialTableName, rarity) 
        objects = self.__RetrieveEquipmentPiece(self.__objectTableName, rarity) 
        ranDesc = random.randint(0,len(descriptors)-1)        
        ranMat = random.randint(0,len(materials)-1)        
        ranObj = random.randint(0,len(objects)-1)
        totalEquipmentName = descriptors[ranDesc][0]+ " " + materials[ranMat][0] + " " + objects[ranObj][0]
        totalEquipmentMod = descriptors[ranDesc][1] + materials[ranMat][1] + objects[ranObj][1]

        return Equipment(totalEquipmentName, totalEquipmentMod, rarity)

    def __RetrieveEquipmentPiece(self, tableName, rarity) -> list:
        conn = sqlite3.connect("databases/equipmentdb.db")
        c = conn.cursor()
        c.execute("SELECT name, weight " +
           f"FROM {tableName} " + 
            "WHERE rarity=?; ", 
            (rarity,))
        retrieved = []
        for row in c.fetchall():
            retrieved.append([row[0], row[1]])
        return retrieved
