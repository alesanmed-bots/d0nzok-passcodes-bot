# -*- coding: utf-8 -*-
"""
Created on Tue Jan 24 20:42:55 2017

@author: Donzok
"""
import json
import requests
import sqlite3
import logging
import telepot
from telepot.aio.helper import ChatHandler
import database.transactions as db
import re
import dateutil.parser

from States import BotStates
from telepot.namedtuple import ReplyKeyboardMarkup, KeyboardButton, ReplyKeyboardRemove, InlineKeyboardMarkup, \
    InlineKeyboardButton


class SecureTelegramBot(ChatHandler):
    def __init__(self, *args, **kwargs):
        super(SecureTelegramBot, self).__init__(*args, **kwargs)

        self._channel = None

        self._v_api_key = None

        self._rocks_api_key = None

        self._state = BotStates.AWAITING_COMMAND

        self._passcode = None

        with open('files/security.json', 'r') as secutiry_file:
            security_json = json.load(secutiry_file)
            self._channel = security_json['channel_id']
            self._v_api_key = security_json['v_api_key']
            self._rocks_api_key = security_json['rocks_api_key']

        self.logger = logging.getLogger('passcode-bot')
        self.logger.setLevel(logging.DEBUG)

        file_handler = logging.FileHandler('./passcode_bot.log')
        file_handler.setLevel(logging.DEBUG)

        formatter = logging.Formatter(fmt='[%(asctime)s] %(levelname)s: %(message)s', datefmt='%d/%m/%Y %H:%M:%S')

        file_handler.setFormatter(formatter)
        self.logger.addHandler(file_handler)

        self.passcodesLogger = logging.getLogger('passcodes-log')
        self.passcodesLogger.setLevel(logging.DEBUG)

        file_handler = logging.FileHandler('./sended_passcodes.log')
        file_handler.setLevel(logging.DEBUG)

        formatter = logging.Formatter(fmt='[%(asctime)s] %(levelname)s: %(message)s', datefmt='%d/%m/%Y %H:%M:%S')

        file_handler.setFormatter(formatter)
        self.passcodesLogger.addHandler(file_handler)

    async def on_chat_message(self, msg):
        content_type, chat_type, chat_id = telepot.glance(msg)

        print(str(chat_id) == self._channel)

        if str(chat_id) == self._channel:
            return

        if content_type != 'text':
            await self.sender.sendMessage('I only accept text messages. Thank you.')
            return

        try:
            user_input = msg['text'].rstrip('\r\n')
        except ValueError:
            await self.sender.sendMessage('It seems that your message is invalid. I\'m sorry')
            return

        command = user_input.split()

        print("Processing message: {0}".format(command))
        self.logger.debug("Processing message: {0}".format(command))

        if self._state == BotStates.AWAITING_COMMAND and command[0][0] != '/':

            self._state = BotStates.AWAITING_COMMAND
            await self.sender.sendMessage(
                'I can\'t understand you. If you want to know the available commands, please type `/help`.',
                parse_mode='Markdown')
        elif command[0][0] == '/':

            if command[0] == '/start':

                self._state = BotStates.AWAITING_COMMAND
                self._passcode = None

                remove_keyboard = ReplyKeyboardRemove(remove_keyboard=True, selective=False)
                text = 'Hi,\nthis bot has restricted access. It\'s only accessible by ENL agents. ' \
                       'If you want to know how to use this bot, type `/help`'

                await self.sender.sendMessage(text, parse_mode='Markdown', reply_markup=remove_keyboard)
            elif command[0] == '/sendcode':

                self._state = BotStates.AWAITING_PASSCODE
                self._passcode = None

                remove_keyboard = ReplyKeyboardRemove(remove_keyboard=True, selective=False)
                await self.sender.sendMessage('Please, send me your valid passcode', reply_markup=remove_keyboard)
            elif command[0] == '/help':

                self._state = BotStates.AWAITING_COMMAND
                self._passcode = None

                remove_keyboard = ReplyKeyboardRemove(remove_keyboard=True, selective=False)
                text = 'Bot usage:\n-/start: Starts the conversation with the bot\n' \
                       '-/help: Shows this help\n' \
                       '-/sendcode: Starts the sending process. Please remind that you need to be verified at ' \
                       'rocks and/or V to send a passcode. You have to link your Telegram ID in ' \
                       'Rocks or V so I can look for you.'
                await self.sender.sendMessage(text, parse_mode='Markdown', reply_markup=remove_keyboard)
            elif command[0] == '/lastsended' and msg['from']['username'] == 'd0nzok':
                if len(command) > 1:
                    passcodes = db.get_last_n_passcodes(command[1])

                    text = ''

                    for passcode in passcodes:
                        text += '{0}: {1} - {2}\n'.format(dateutil.parser.parse(passcode[1])
                                                          .strftime("%Y-%m-%d %H:%M:%S"), passcode[0], passcode[2])

                    await self.sender.sendMessage(text)
                else:
                    await self.sender.sendMessage("You know that I need the number of records you want.")
            else:

                self._state = BotStates.AWAITING_COMMAND
                self._passcode = None

                remove_keyboard = ReplyKeyboardRemove(remove_keyboard=True, selective=False)
                await self.sender.sendMessage(
                    'I can\'t understand you. If you want to know the available command, please type `/help`.',
                    parse_mode='Markdown', reply_markup=remove_keyboard)
        elif self._state == BotStates.AWAITING_PASSCODE:

            await self.process_code(command[0], msg['from']['id'], msg['from']['first_name'])

        elif self._state == BotStates.AWAITING_YESNO and (command[0] == "Yes" or command[0] == "No"):

            if command[0] == "Yes":
                self._state = BotStates.AWAITING_REWARD
                remove_keyboard = ReplyKeyboardRemove(remove_keyboard=True, selective=False)
                await self.sender.sendMessage(
                    "Please, send the reward with the following format "
                    "(take notice of the dash at the beggining of each line):\n-Reward 1 (Amount)\n-Reward 2 (Amount)",
                    reply_markup=remove_keyboard)
            else:
                self._state = BotStates.AWAITING_COMMAND
                remove_keyboard = ReplyKeyboardRemove(remove_keyboard=True, selective=False)
                await self.sender.sendMessage("Ok. Thank you very much for your contribution.",
                                              reply_markup=remove_keyboard)

                try:
                    if msg['from']['username']:
                        user = msg['from']['username']
                    else:
                        user = msg['from']['id']

                    db.insert_passcode(passcode=self._passcode, user=user)

                    inline_button = InlineKeyboardMarkup(
                        inline_keyboard=[[InlineKeyboardButton(text="Passcode Fully Redeemed - 0",
                                                               callback_data=str(msg['from']['id']))]])

                    await self.sender.sendMessage(self._passcode)
                    await self.bot.sendMessage(self._channel, self._passcode, reply_markup=inline_button)

                    self._passcode = None
                except sqlite3.IntegrityError:
                    self.sender.sendMessage(
                        "Sorry, there was a problem processing your request. "
                        "Please, try again and, if the problem persists, please contact @d0nzok")

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

                if msg['from']['username']:
                    user = msg['from']['username']
                else:
                    user = msg['from']['id']

                try:
                    db.insert_passcode(self._passcode, user)

                    await self.sender.sendMessage(self._passcode)
                    await self.sender.sendMessage(msg['text'])

                    inline_button = InlineKeyboardMarkup(
                        inline_keyboard=[[InlineKeyboardButton(text="Passcode Fully Redeemed - 0",
                                                               callback_data=str(msg['from']['id']))]])

                    await self.bot.sendMessage(self._channel, self._passcode)
                    await self.bot.sendMessage(self._channel, msg['text'], reply_markup=inline_button)

                    self._passcode = None
                except sqlite3.IntegrityError:
                    self.sender.sendMessage(
                        "Sorry, there was a problem processing your request. "
                        "Please, try again and, if the problem persists, please contact @d0nzok")

                self.close()
            else:
                await self.sender.sendMessage(
                    "I'm sorry. I can't understand the reward. Please, send me the reward with the "
                    "following format (take notice of the dash at the beggining of each line):"
                    "\n-Reward 1 (Amount)\n-Reward 2 (Amount)")

    async def process_code(self, passcode, user_id, user_name):
        if await self.user_has_rights(user_id):

            self.passcodesLogger.debug('From: {0}. Command: {1}'.format(user_name, passcode))

            # if self.is_passcode_valid(passcode):
            if True:
                passcode_exists = db.check_passcode_exists(passcode)

                if not passcode_exists:
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
                    await self.sender.sendMessage(
                        "Sorry but that passcode has been already sended."
                        " You can look for it and its reward in the channel")
            else:
                await self.sender.sendMessage(
                    "I'm sorry but the passcode is invalid. If you think that the code you sended is valid, "
                    "please contact either with @d0nzok or @Hulk32. I'll wait for a valid one...")
        else:
            await self.sender.sendMessage(
                "I'm sorry, but the use of this bot is restricted. You need to be registered, "
                "verified and not be flagged, quearantined or blacklisted in V or Rocks in order to use this bot. "
                "If you don't know about V or Rocks, please ask your local community.")

    async def on_callback_query(self, msg):
        query_id, from_id, query_data = telepot.glance(msg, flavor='callback_query')

        if db.check_user_voted(msg_id=msg['message']['message_id'], user_id=from_id):

            db.remove_vote(msg_id=msg['message']['message_id'], user_id=from_id)
        else:

            db.add_vote(msg_id=msg['message']['message_id'], user_id=from_id)

        votes = db.count_votes(msg['message']['message_id'])

        inline_button = InlineKeyboardMarkup(
            inline_keyboard=[[InlineKeyboardButton(text="Passcode Fully Redeemed - {0} {1}".format(votes, u'\U0000274C'),
                                                   callback_data=query_data)]])

        msg_ident = telepot.message_identifier(msg['message'])

        _editor = telepot.aio.helper.Editor(self.bot, msg_ident)

        try:
            await _editor.editMessageReplyMarkup(reply_markup=inline_button)
        except telepot.exception.TelegramError as e:
            self.logger.error("TELEGRAM ERROR: {0}".format(e))

    async def on__idle(self, event):
        if self._state != BotStates.AWAITING_COMMAND:
            remove_keyboard = ReplyKeyboardRemove(remove_keyboard=True, selective=False)

            await self.sender.sendMessage(
                "I'm sorry, you have taken too long to complete the process (more than 2 minutes). "
                "Please, start again.",
                reply_markup=remove_keyboard)

        self.close()

    async def user_has_rights(self, user_id):
        v_url = "https://v.enl.one/api/v1/search?telegramId={0}&apikey={1}".format(user_id, self._v_api_key)
        rocks_url = "https://enlightened.rocks/api/user/status/{0}?apikey={1}".format(user_id, self._rocks_api_key)

        response = requests.get(v_url)
        v_content = json.loads(response.content.decode("utf8"))

        response = requests.get(rocks_url)
        rocks_content = json.loads(response.content.decode("utf-8"))
        print(rocks_content)

        res = False

        if v_content['status'] == "ok" and len(v_content['data']):
            # await self.sender.sendMessage(
            #   'Hi, you are in V. Your V agent name is {0}, your level is {1} and you have {2} points.'.format(
            #       v_content['data'][0]['agent'], v_content['data'][0]['vlevel'], v_content['data'][0]['vpoints']))

            res = (v_content['status'] == "ok"
                   and v_content['data'][0]['verified']
                   and not v_content['data'][0]['blacklisted']
                   and not v_content['data'][0]['flagged']
                   and not v_content['data'][0]['quarantine'])

        if len(rocks_content):
            # await self.sender.sendMessage(
            #   'Hi, you are in Rocks. Your Rocks agent name is {0}, and your "verify" status is:{1}.'.format(
            #       rocks_content['agentid'], rocks_content['verified']))

            res = res or rocks_content['verified']

        return res

    @staticmethod
    def is_passcode_valid(passcode):
        # xxx##keyword###xx
        # (# are 2 to 9)
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
