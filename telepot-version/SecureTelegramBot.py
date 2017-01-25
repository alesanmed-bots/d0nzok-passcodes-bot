# -*- coding: utf-8 -*-
"""
Created on Tue Jan 24 20:42:55 2017

@author: Donzok
"""
import json
import requests
import logging
import telepot
import re
from States import BotStates
from telepot.namedtuple import ReplyKeyboardMarkup, KeyboardButton, ReplyKeyboardRemove

class SecureTelegramBot(telepot.aio.helper.ChatHandler):
    
    def __init__(self, *args, **kwargs):
        super(SecureTelegramBot, self).__init__(*args, **kwargs)
        
        self._channel = None;
        
        self._v_api_key = None;
        
        self._state = BotStates.AWAITING_COMMAND
        
        self._passcode = None
        
        with open('files/security.json', 'r') as secutiry_file:
            security_json = json.load(secutiry_file)
            self._channel = security_json['channel_test_id'];
            self._v_api_key = security_json['v_api_key']
        
        self.logger = logging.getLogger('passcode-bot');
        self.logger.setLevel(logging.DEBUG);
    
        fileHandler = logging.FileHandler('./passcode_bot.log');
        fileHandler.setLevel(logging.DEBUG);
    
        formatter = logging.Formatter(fmt='[%(asctime)s] %(levelname)s: %(message)s', datefmt='%d/%m/%Y %H:%M:%S')
    
        fileHandler.setFormatter(formatter)
        self.logger.addHandler(fileHandler)
        
        self.passcodesLogger = logging.getLogger('passcodes-log');
        self.passcodesLogger.setLevel(logging.DEBUG);
    
        fileHandler = logging.FileHandler('./sended_passcodes.log');
        fileHandler.setLevel(logging.DEBUG);
    
        formatter = logging.Formatter(fmt='[%(asctime)s] %(levelname)s: %(message)s', datefmt='%d/%m/%Y %H:%M:%S')
    
        fileHandler.setFormatter(formatter)
        self.passcodesLogger.addHandler(fileHandler)
    
    async def on_chat_message(self, msg):
        content_type, chat_type, chat_id = telepot.glance(msg)
        
        if content_type != 'text':
            await self.sender.sendMessage('I only accept text messages. Thank you.')
            return
            
        try:
           user_input = msg['text'].rstrip('\r\n')
        except ValueError:
            await self.sender.sendMessage('It seems that your message is invalid. I\'m sorry')
            return
            
        command = user_input.split();
        
        print("Processing message: {0}".format(command))
        self.logger.debug("Processing message: {0}".format(command))
        
        if self._state == BotStates.AWAITING_COMMAND and command[0][0] != '/':
            self._state = BotStates.AWAITING_COMMAND
            await self.sender.sendMessage('I can\'t understand you. If you want to know the available command, please type `/help`.', parse_mode='Markdown')
        elif command[0][0] == '/':
            if command[0] == '/start':
                self._state = BotStates.AWAITING_COMMAND
                self._passcode = None
                
                removeKeyboard = ReplyKeyboardRemove(remove_keyboard=True, selective=False)                
                text = 'Hi,\nthis bot has restricted access. It\'s only accessible by ENL agents. If you want to know how to use this bot, type `/help`'
                
                await self.sender.sendMessage(text, parse_mode='Markdown', reply_markup=removeKeyboard)
            elif command[0] == '/sendcode':
                self._state = BotStates.AWAITING_PASSCODE
                self._passcode = None
                
                removeKeyboard = ReplyKeyboardRemove(remove_keyboard=True, selective=False)
                await self.sender.sendMessage('Please, send me your valid passcode', reply_markup=removeKeyboard)
            elif command[0] == '/help':
                self._state = BotStates.AWAITING_COMMAND
                self._passcode = None
                
                removeKeyboard = ReplyKeyboardRemove(remove_keyboard=True, selective=False)
                text = 'El uso de este bot es el siguiente:\n-/start: Comienza la conversación con el bot\n-/help: Muestra esta ayuda\n-/registra contraseña: Te registras al bot con la contraseña indicada. Esto permite que envíes códigos de acceso.\n-/sendcode passcode;recompensa 1;recompensa 2;recompensa X: Envía el código de acceso `passcode` con las recompensas `recompensa 1`, `recompensa 2` y así todas las que quieras. Las recompensas son opcionales.'
                await self.sender.sendMessage(text, parse_mode='Markdown', reply_markup=removeKeyboard)
            else:
                self._state = BotStates.AWAITING_COMMAND
                self._passcode = None
                
                removeKeyboard = ReplyKeyboardRemove(remove_keyboard=True, selective=False)
                await self.sender.sendMessage('I can\'t understand you. If you want to know the available command, please type `/help`.', parse_mode='Markdown', reply_markup=removeKeyboard)
        elif self._state == BotStates.AWAITING_PASSCODE:
            await self.process_code(command[0], msg['from']['id'], msg['from']['first_name'])
        elif self._state == BotStates.AWAITING_YESNO and (command[0] == "Yes" or command[0] == "No"):
            if command[0] == "Yes":
                self._state = BotStates.AWAITING_REWARD
                removeKeyboard = ReplyKeyboardRemove(remove_keyboard=True, selective=False)
                await self.sender.sendMessage(
                "Please, send the reward with the following format:\n-Reward 1 (Amount)\n-Reward 2 (Amount)", 
                reply_markup=removeKeyboard)
            else:
                self._state = BotStates.AWAITING_COMMAND
                removeKeyboard = ReplyKeyboardRemove(remove_keyboard=True, selective=False)
                await self.sender.sendMessage("Ok. Thank you very much for your contribution.", 
                reply_markup=removeKeyboard)
                
                await self.sender.sendMessage(self._passcode)
                self._passcode = None
                
                self.close()
        elif self._state == BotStates.AWAITING_REWARD:
            rewards = msg['text'].split("\n")
            
            all_ok = True
            for reward in rewards:                
                if not reward[0] == "-":
                    all_ok = False
                    break
            if all_ok:
                self._state = BotStates.AWAITING_COMMAND
                
                await self.sender.sendMessage(self._passcode)
                await self.sender.sendMessage(msg['text'])
                
                self._passcode = None
                self.close()
            else:
                await self.sender.sendMessage("I'm sorry. I can't understand the reward. Please, send me the reward with the following format:\n-Reward 1 (Amount)\n-Reward 2 (Amount)")
  
    async def process_code(self, passcode, user_id, user_name):
        if await self.user_has_rigths(user_id):
            
            self.passcodesLogger.debug('From: {0}. Command: {1}'.format(user_name, passcode))
            
            if self.is_passcode_valid(passcode):
                self._passcode = passcode
                
                keyboard = ReplyKeyboardMarkup(
                    keyboard=[[KeyboardButton(text="Yes", 
                                             request_contact=False, 
                                             request_location=False),
                            KeyboardButton(text="No", 
                                             request_contact=False, 
                                             request_location=False)]],
                    resize_keyboard=True,
                    one_time_keyboard=True,
                    selective=True
                )
                
                self._state = BotStates.AWAITING_YESNO
                await self.sender.sendMessage("Do you know the passcode reward?", reply_markup=keyboard)
                
                # self.send_message("{0}".format(passcode), self.channel, 'Markdown')
                # self.send_message("{0}".format(items), self.channel, 'Markdown')
            else:
               await self.sender.sendMessage("I'm sorry but the passcode is invalid") 
        else:
            await self.sender.sendMessage("I'm sorry, but the use of this bot is restricted. You need to be registered, verified and not be flagged, quearantined or blacklisted in V in order to use this bot. If you don't know about V, please ask your local community.")
            
    async def on__idle(self, event):
        await self.sender.sendMessage("I'm sorry, you have taken too long to complete the process (more than 2 minutes). Please, start again.")
        self.close()
            
    async def user_has_rigths(self, user_id):
        v_url = "https://v.enl.one/api/v1/search?telegramId={0}&apikey={1}".format(user_id, self._v_api_key)
        
        response = requests.get(v_url)
        v_content = json.loads(response.content.decode("utf8"))
        
        res = False        
        
        if v_content['status'] == "ok" and len(v_content['data']):    
            await self.sender.sendMessage('Hi, you are in V. Your V agent name is {0}, your level is {1} and you have {2} points.'.format(v_content['data'][0]['agent'], v_content['data'][0]['vlevel'], v_content['data'][0]['vpoints']))
            
            res = (v_content['status'] == "ok" 
                    and v_content['data'][0]['verified'] 
                    and not v_content['data'][0]['blacklisted']
                    and not v_content['data'][0]['flagged']
                    and not v_content['data'][0]['quarantine'])
        
        return res
        
    def is_passcode_valid(self, passcode):        
        '''
        xxx##keyword###xx
        (# are 2 to 9)
        '''
        passcode_regex_1 = re.compile('[A-Za-z]{3}[2-9]{2}[A-Za-z]+[2-9]{3}[A-Za-z]{2}')
        
        '''
        x#x#keywordx#xx
        (# are 0 to 9)
        '''
        passcode_regex_2 = re.compile('[A-Za-z][0-9][A-Za-z][0-9][A-Za-z]+[0-9][A-Za-z]{2}')
        
        '''        
        keyword#xx##xx#
        (# are 0 to 9)
        '''
        passcode_regex_3 = re.compile('[A-Za-z]+[0-9][A-Za-z]{2}[0-9]{2}[A-Za-z]{2}[0-9]')
        
        '''        
        xxxxxxxx#keyword#
        (# are 2 to 9)
        '''
        passcode_regex_4 = re.compile('[A-Za-z]+[2-9][A-Za-z]+[2-9]')
        
        '''        
        #xxx#keywordx#x#x
        (# are 2 to 9)
        '''
        passcode_regex_5 = re.compile('[2-9][A-Za-z]{3}[2-9][A-Za-z]+[2-9][A-Za-z][2-9][A-Za-z]')
        
        return (passcode_regex_1.match(passcode) 
                or passcode_regex_2.match(passcode) 
                or passcode_regex_3.match(passcode) 
                or passcode_regex_4.match(passcode) 
                or passcode_regex_5.match(passcode))