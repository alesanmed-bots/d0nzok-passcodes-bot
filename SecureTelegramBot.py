# -*- coding: utf-8 -*-
"""
Created on Sun Jan 22 21:23:04 2017

@author: Donzok
"""
import json
import requests
import hashlib
import codecs
import os
import re
import logging


class SecureTelegramBot:
    
    def __init__(self, URL, token, password):
        self.URL = URL
        self.token = token
        
        self.md5 = hashlib.md5();
        self.md5.update(bytes(password, 'utf-8'))
        self.password = self.md5.hexdigest()
        
        self.startup_check()
        
        self.users = None;
    
        with open('files/users.json', 'r') as users_file:
            self.users = json.load(users_file);
        
        self.logger = logging.getLogger('passcode-bot');
        self.logger.setLevel(logging.DEBUG);
    
        fileHandler = logging.FileHandler('./passcode_bot.log');
        fileHandler.setLevel(logging.DEBUG);
    
        formatter = logging.Formatter(fmt='[%(asctime)s] %(levelname)s: %(message)s', datefmt='%d/%m/%Y %H:%M:%S')
    
        fileHandler.setFormatter(formatter)
        self.logger.addHandler(fileHandler)
    
    def url_request_get(self, url):
        response = requests.get(url)
        content = response.content.decode("utf8")
        return content

    def get_json_from_url(self, url):
        content = self.url_request_get(url)
        js = json.loads(content)
        return js
        
    def get_updates(self, offset=None):
        url = self.URL + "getUpdates"
        if offset:
            url += "?offset=***REMOVED******REMOVED***".format(offset)
        js = self.get_json_from_url(url)
        return js
    
    def get_last_update_id(self, updates):
        update_ids = []
        for update in updates["result"]:
            update_ids.append(int(update["update_id"]))
        return max(update_ids)
    
    
    def get_last_chat_id_and_text(self, updates):
        num_updates = len(updates["result"])
        last_update = num_updates - 1
        text = updates["result"][last_update]["message"]["text"]
        chat_id = updates["result"][last_update]["message"]["chat"]["id"]
        return (text, chat_id)
        
    def send_message(self, text, chat_id, markdown='HTML'):
        url = self.URL + "sendMessage?text=***REMOVED******REMOVED***&chat_id=***REMOVED******REMOVED***&parse_mode=***REMOVED******REMOVED***".format(text, chat_id, markdown)
        self.url_request_get(url)
        
    def startup_check(self):
        if not os.path.isfile('files/users.json') or not os.access('files/users.json', os.R_OK):
            with codecs.open(os.path.join('files/', 'users.json'), 'w') as users_file:
                users_file.write(json.dumps(***REMOVED***'users': []***REMOVED***))
    
    def process_messages(self, updates):
        for update in updates['result']:
            try:
                message = update['message'];
            except KeyError:
                message = update['edited_message']
            
            message_text = message['text'];
            command = message_text.split();
    
            print("Processing message: ***REMOVED***0***REMOVED***".format(command))
            self.logger.debug("Processing message: ***REMOVED***0***REMOVED***".format(command))
    
            print("Length: ***REMOVED***0***REMOVED***\nCommand[0]: ***REMOVED***1***REMOVED***".format(len(command), command[0]))
            self.logger.debug("Length: ***REMOVED***0***REMOVED*** Command[0]: ***REMOVED***1***REMOVED***".format(len(command), command[0]))
    
            if command[0] == "/registra":
                self.register_user(message, command)
            elif command[0] == '/start':
                self.send_start_message(message)
            elif command[0] == '/sendcode':
                self.process_code(message, command)
            elif command[0] == '/help':
                self.send_help(message)
            else:
                self.send_message("Comando desconocido", message['chat']['id'])
                
    def register_user(self, message, command):
        if len(command) == 2:
            input_pass = command[-1]
            self.md5 = hashlib.md5()
            input_pass_md5 = self.md5.update(bytes(input_pass, 'utf-8'))
            input_pass_md5 = self.md5.hexdigest()

            if input_pass_md5 == self.password:
                self.users['users'].append(
                    ***REMOVED*** 'user_id': message['from']['id'], 
                      'chat_id': message['chat']['id']
                    ***REMOVED***
                )

                with open('files/users.json', 'w') as users_file:
                    json.dump(self.users, users_file)

                self.send_message("Registro correcto. Bienvenido, ***REMOVED***0***REMOVED***".format(message['from']['first_name']), message['chat']['id'])
            else:
                self.send_message("Contraseña incorrecta", message['chat']['id'])
        else:
            self.send_message("Falta la contraseña", message['chat']['id'])
            
    def send_start_message(self, message):
        text = 'Hola,\neste es un bot privado de los Iluminados. Para saber cómo empezar a usarlo, escribe /help'
        self.send_message(text, message['chat']['id'])
    
    def user_has_rigths(self, user_id):
        users = self.users['users']
                
        user_ids = [user['user_id'] for user in users]
        
        try:
            user_ids.index(user_id)
            return True
        except ValueError:
            return False
            
    def is_passcode_valid(self, passcode):        
        '''
        xxx##keyword###xx
        (# are 2 to 9)
        '''
        passcode_regex_1 = re.compile('[A-Za-z]***REMOVED***3***REMOVED***[2-9]***REMOVED***2***REMOVED***[A-Za-z]+[2-9]***REMOVED***3***REMOVED***[A-Za-z]***REMOVED***2***REMOVED***')
        
        '''
        x#x#keywordx#xx
        (# are 0 to 9)
        '''
        passcode_regex_2 = re.compile('[A-Za-z][0-9][A-Za-z][0-9][A-Za-z]+[0-9][A-Za-z]***REMOVED***2***REMOVED***')
        
        '''        
        keyword#xx##xx#
        (# are 0 to 9)
        '''
        passcode_regex_3 = re.compile('[A-Za-z]+[0-9][A-Za-z]***REMOVED***2***REMOVED***[0-9]***REMOVED***2***REMOVED***[A-Za-z]***REMOVED***2***REMOVED***[0-9]')
        
        '''        
        xxxxxxxx#keyword#
        (# are 2 to 9)
        '''
        passcode_regex_4 = re.compile('[A-Za-z]+[2-9][A-Za-z]+[2-9]')
        
        '''        
        #xxx#keywordx#x#x
        (# are 2 to 9)
        '''
        passcode_regex_5 = re.compile('[2-9][A-Za-z]***REMOVED***3***REMOVED***[2-9][A-Za-z]+[2-9][A-Za-z][2-9][A-Za-z]')
        
        return (passcode_regex_1.match(passcode) 
                or passcode_regex_2.match(passcode) 
                or passcode_regex_3.match(passcode) 
                or passcode_regex_4.match(passcode) 
                or passcode_regex_5.match(passcode))
    
    def process_code(self, message, command):
        if len(command) >= 2:
            if self.user_has_rigths(message['from']['id']):
                command_text = command[1].split(';')
                
                passcode = command_text[0]
                
                command_text = message['text'].split(';');
                
                if self.is_passcode_valid(passcode):
                    items = ""
                    
                    for item in command_text[1:]:
                        items += "-`***REMOVED***0***REMOVED***`\n".format(item)                   
                    
                    res_text = "***REMOVED***0***REMOVED***\n***REMOVED***1***REMOVED***".format(passcode, items)                    
                    
                    self.send_message("***REMOVED***0***REMOVED***".format(res_text), message['chat']['id'], 'Markdown') 
                else:
                   self.send_message("Código inválido. El formato no es correcto. Para más información acerca de los formatos válidos visita: https://ingress.codes/", message['chat']['id']) 
            else:
                self.send_message("Lo siento, pero este bot es privado. Necesitas usar el comando /registra para registrarte con la contraseña. Si quieres tener acceso al bot, pregunta en tu comunidad local.", message['chat']['id'])
        else:
            self.send_message("Falta el código", message['chat']['id'])
            
    def send_help(self, message):
        text = 'El uso de este bot es el siguiente:\n-/start: Comienza la conversación con el bot\n-/help: Muestra esta ayuda\n-/registra contraseña: Te registras al bot con la contraseña indicada. Esto permite que envíes códigos de acceso.\n-/sendcode passcode;recompensa 1;recompensa 2;recompensa X: Envía el código de acceso `passcode` con las recompensas `recompensa 1`, `recompensa 2` y así todas las que quieras. Las recompensas son opcionales.'
        self.send_message(text, message['chat']['id'], 'Markdown')