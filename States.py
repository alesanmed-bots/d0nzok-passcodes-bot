# -*- coding: utf-8 -*-
"""
Created on Wed Jan 25 14:17:07 2017

@author: Donzok
"""
from enum import Enum

class BotStates(Enum):
    AWAITING_COMMAND = 1
    AWAITING_PASSCODE = 2
    AWAITING_YESNO = 3
    AWAITING_REWARD = 4
