# -*- coding: utf-8 -*-
"""
Created on Wed Jan 25 23:15:01 2017

@author: Donzok
"""
import telepot
import sqlite3
import json
from telepot.aio.delegate import per_chat_id, create_open, pave_event_space
from SecureTelegramBot import SecureTelegramBot
import asyncio

if __name__ == "__main__":
    security = None    
    
    with open('files/security.json', 'r') as security_file:
        security = json.load(security_file);
    
    conn = sqlite3.connect('files/passcodes.db')
    
    cursor = conn.cursor()
    
    cursor.execute('''CREATE TABLE IF NOT EXISTS passcodes (passcode  text primary key, date text, user text)''')
    
    conn.commit()
    
    conn.close()
    
    bot = telepot.aio.DelegatorBot(security['token_test'], [
        pave_event_space()(
            per_chat_id(), create_open, SecureTelegramBot, timeout=120),
    ])
    
    loop = asyncio.get_event_loop()
    loop.create_task(bot.message_loop())
    print('Listening ...')
    
    loop.run_forever()