import sqlite3
import requests
from settings import log_msg

global TOKEN
global URL
with open('token.txt') as inf:
    TOKEN = inf.read().strip()
URL = f'https://api.telegram.org/bot{TOKEN}/'

def get_today_bdays():
    con = sqlite3.connect('birthdaybot_db.sqlite3')
    con.row_factory = sqlite3.Row
    cur = con.cursor()
    q = f"""
    SELECT
      pers_name,
      pers_bday,
      chat_id,
      (STRFTIME('%Y') - STRFTIME('%Y', pers_bday)) as 'age'
    FROM
      person
    WHERE
      STRFTIME('%m%d', pers_bday) = STRFTIME('%m%d')"""
    #log_msg(q)
    cur.execute(q)
    result = [dict(row) for row in cur.fetchall()]
    con.commit()
    con.close()
    return result 

def send_msg(chat_id, msg):
    url = URL + 'sendMessage'
    debug_msg = f"chat_id is: {chat_id}, msg is: {msg}"
    tg_msg = f"{msg}"
    resp = requests.post(url, data={'chat_id':chat_id, 'text':tg_msg, 'parse_mode':'HTML'}).json()
    log_msg(f">>> Telegram response: {resp}")
    log_msg(f">>> Debug message: {debug_msg}")

bday_people = get_today_bdays()
for item in bday_people:
    chat_id = item['chat_id']
    msg = f"Today is {item['pers_name']}'s birthday. They've turned {item['age']} years! ({item['pers_bday']})"
    send_msg(chat_id, msg)
    log_msg(msg)