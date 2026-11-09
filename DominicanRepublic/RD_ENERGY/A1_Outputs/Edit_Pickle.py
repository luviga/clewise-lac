# -*- coding: utf-8 -*-
"""
Created on Wed Oct 15 11:14:03 2025

@author: yds3
"""
import pickle
 
# Cargar el pickle existente
with open("A-O_Fleet_Groups.pickle", "rb") as f:
    data = pickle.load(f)
 
# Agregar la nueva lista
data["Techs_Bus_Efi"] = ["TRXBUSEFIELE"]
 
# Guardar el pickle actualizado
with open("A-O_Fleet_Groups.pickle", "wb") as f:
    pickle.dump(data, f)
 
print("Pickle actualizado correctamente")
