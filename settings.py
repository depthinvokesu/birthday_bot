import logging
from enum import Enum

DB_NAME = "birthdaybot_db.sqlite3"

with open('token.txt') as inf:
    TOKEN = inf.read().strip()
URL = f'https://api.telegram.org/bot{TOKEN}/'

APP_PATH = '/'+TOKEN

class StateId(Enum):
    ADD_ADDMSG = 10 # \add message has come 
    ADD_PERSNAME =20 # person name has come
    ADD_PERSBDAY = 30 # person bday has come
    DEL_DELMSG = 40 # delete message has come
    DEL_ORDNUM = 50 # ordinal number of person to delete has come
    ADD = [10, 20, 30]
    DELETE = [40, 50]


logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.FileHandler("debug.log"),
        logging.StreamHandler()
    ]
)
log_msg = logging.info
