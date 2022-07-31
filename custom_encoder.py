#This file to check if the obj is an instance of decimal,
#if it is it returns a float obj,
#if not we return a default value of the obj

import json
from decimal import Decimal


class CustomEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, Decimal): #if it is it returns a float obj 
            return float(obj)
        #if not we return a default value of the obj    
        return json.JSONEncoder.decimal.default(self, obj) 