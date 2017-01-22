import time
import json
from SecureTelegramBot import SecureTelegramBot

if __name__ == "__main__":
    security = None    
    
    with open('files/security.json', 'r') as security_file:
        security = json.load(security_file);
    
    URL = "https://api.telegram.org/bot***REMOVED******REMOVED***/".format(security["token"])
    
    PasscodesBot = SecureTelegramBot(URL, security["token"], "e7tSaADNsTBTXu6a")
    
    logger = PasscodesBot.logger
    offset = None;
    print("Waiting for messages...");
    logger.debug("Waiting for messages...")

    while True:
        updates = PasscodesBot.get_updates(offset);
        if(len(updates["result"]) > 0):
            offset = PasscodesBot.get_last_update_id(updates) + 1;
            PasscodesBot.process_messages(updates);

            time.sleep(1);    