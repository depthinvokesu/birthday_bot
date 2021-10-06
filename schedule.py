import sqlite3
import os

os.chdir('/home/unknown/Documents/birthday_bot')

def get_today_bdays():
    con = sqlite3.connect('birthdaybot_db.sqlite3')
    con.row_factory = sqlite3.Row
    cur = con.cursor()
    q = f"""
    SELECT
      pers_name,
      pers_bday,
      user_id,
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

def log_msg(msg):
    print(msg)

def send_msg(id, msg):
    print(f"> id is: {id},", f"msg is: {msg}")

bday_people = get_today_bdays()
for item in bday_people:
    id = item['user_id']
    msg = f"Today is {item['pers_name']}'s birthday. They've turned {item['age']} years! ({item['pers_bday']})"
    send_msg(id, msg)
print("")