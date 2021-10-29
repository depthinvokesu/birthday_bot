import sqlite3
import re
from datetime import datetime as dt

db_name = 'birthdaybot_db.sqlite3'

m1 = {'text':'/delete', 'chat':{'id':12, 'username':'user12'}}

def wf(msg):

    t = msg['text']
    id = msg['chat']['id']
    username = msg['chat']['username']

    user_command = select_one(table='user_command', where={'user_id':id}) # {user_id: x, cmd_id: y, step_id: z}

    if t == '/add':
        clear(table='user_command', where={'user_id':id})
        clear(table='add_cache', where={'user_id':id})
        insert(table='user_command', data={'user_id': id, 'cmd_id': 1, 'step_id': 1})
        add(msg)

    elif t == '/delete':
        clear(table='user_command', where={'user_id':id})
        clear(table='delete_cache', where={'user_id':id})
        insert(table='user_command', data={'user_id': id, 'cmd_id': 2, 'step_id': 1})
        delete(msg)

    elif t == '/month':
        response = this_month(id)
        send_msg(id, response)

    elif user_command: # Record with the id exists in user_command
        if user_command['cmd_id'] == 1: # command_id=1 (add) for the user_id in user_command
            add(msg)
        elif user_command['cmd_id'] == 2: # command_id=2 (delete) for the user_id in user_command
            delete(msg)
        else:
            clear(table='user_command', where={'user_id':id})
            show_start_msg(id)
    else:
        show_start_msg(id)
        


def add(msg):
    log_msg("ADD PROCESS HAS STARTED")
    t = msg['text']
    id = msg['chat']['id']
    username = msg['chat']['username']
   
    step_id = select_one(table='user_command', where={'user_id':id})['step_id']
    log_msg(f"step id is {step_id}")

    if step_id == 1: # add message has come

        # Inserting user's data to cache table, incrementing step_id and sending a message with result
        insert(table='add_cache', data={'user_id':id, 'username': username})
        update(table='user_command', set={'step_id':2}, where={'user_id':id})
        send_msg(id, "Enter a person name")

    elif step_id == 2: # pers_name has come

        if not istext(t):
            send_msg(id, "Name should contain only letters or numbers")
            return
        
        # Inserting the input to the cache, incrementing step_id and sending a message with result
        update(table='add_cache', set={'pers_name':t}, where={'user_id':id})
        update(table='user_command', set={'step_id':3}, where={'user_id':id})
        send_msg(id, "OK, now enter a persson birthday (YYYY-MM-DD)")

    elif step_id == 3: # pers_bday has come

        # Validating the input
        if not isdate(t):
            send_msg(id, "Enter a date in YYYY-MM-DD format")
            return
        if not ispast(t):
            send_msg(id, "The date should be earlier than today")
            return
        
        # Converting the date
        date_obj = dt.strptime(t, '%Y-%m-%d') # parse input to a date obj
        date_frnd = date_obj.strftime('%d %b %Y') # YYYY-MM-DD string
        date_sql = date_obj.strftime('%Y-%m-%d') # DD Mon YYYY string

        # Inserting the input to the cache
        update(table='add_cache', set={'pers_bday':date_sql}, where={'user_id':id})
        
        # Copying the data from cache to person table
        pers_name = select_one(table='add_cache', where={'user_id':id})['pers_name']
        insert(table='person', data={'pers_name':pers_name, 'pers_bday':date_sql, 'user_id':id})

        # Inserting user's data to user table
        user_tb = select_one(table='user', where={'user_id': id})
        if user_tb: # record is already exists
            update(table='user', set={'username':username}, where={'user_id':id})
        else:
            insert(table='user', data={'user_id':id, 'username': username})

        # Deleting cache and sending the final message
        clear(table='add_cache', where={'user_id':id})
        clear(table='user_command', where={'user_id':id})
        send_msg(id, f"{pers_name}, born {date_frnd} has been added")
    else:
        clear(table='add_cache', where={'user_id':id})
        clear(table='user_command', where={'user_id':id})
        show_start_msg(id)

def delete(msg):
    log_msg("DELETE PROCESS HAS STARTES")
    t = msg['text']
    id = msg['chat']['id']
    username = msg['chat']['username']

    step_id = select_one(table='user_command', where={'user_id':id})['step_id']
    log_msg(f"step id is {step_id}")

    if step_id == 1: # delete message has come

        # Composing lists of people for current user
        person_tb = select_all(table='person', where={'user_id':id}, columns=['rowid as pers_id', '*']) #[{}, {}, ...]
        show_list = [] # list to show to the user
        insert_list = [] # list to insert into delete_cache

        # Populating the lists with extra attributes
        for number, person in enumerate(person_tb):
            person['pers_num'] = number+1 # ordinal number when showing to the user
            show_list.append({'pers_num':person['pers_num'], 'pers_name':person['pers_name'], 'pers_bday':person['pers_bday']})
            insert_list.append({'user_id':person['user_id'], 'pers_id':person['pers_id'], 'pers_num':person['pers_num']})
        
        # Inserting the list into delete_cache table
        for person in insert_list:
            insert(table='delete_cache', data=person)

        # Incrementing step_id and sending a message with result
        update(table='user_command', set={'step_id': 2}, where={'user_id': id})
        send_msg(id, "Enter numner of a person you want to delete")
        send_msg(id, show_list)

    elif step_id == 2: #Number of person to delete has come

        if not t.isdigit(): # returns True for int only
            send_msg(id, "Enter a number")
            return
        input_num = int(t)

        # Checking if input number is valid
        delete_cache_tb = select_all(table='delete_cache', where={'user_id': id})
        pers_numbers = [item['pers_num'] for item in delete_cache_tb]
        if input_num not in pers_numbers:
            send_msg(id, "Wrong number, send /delete to get a list")
            return
        
        # Getting id, name, bday of the person to delete
        pers_id = select_one(table='delete_cache', where={'user_id': id, 'pers_num': input_num})['pers_id']
        person = select_one(table='person', where={'rowid': pers_id}) # {pers_name :x, pers_bday: y}

        # Deleting target person from person table and deleting cache
        clear(table='person', where={'rowid': pers_id})
        clear(table='delete_cache', where={'user_id':id})
        clear(table='user_command', where={'user_id':id})

        # Final message
        send_msg(id, f"{person['pers_name']} born {person['pers_bday']} has been deleted")

    else:
        clear(table='delete_cache', where={'user_id':id})
        clear(table='user_command', where={'user_id':id})
        show_start_msg(id)

def this_month(id):
    month = str(dt.now().month)
    result = select_all(table='person', where={"user_id": id, "STRFTIME('%m', pers_bday)": month})
    return result

def show_start_msg(id):
    msg = "/add - add a person, /delete - delete a person, /month - show birthdays of this month"
    send_msg(id, msg)

def send_msg(id, msg):
    print(f">>> id is: {id},", f"msg is: {msg}")

def log_msg(msg):
    print(msg)

def isdate(date_text):
    try:
        dt.strptime(date_text, '%Y-%m-%d')
    except ValueError:
        # raise ValueError("Incorrect data format, should be YYYY-MM-DD")
        return False
    else:
        return True

def ispast(date_text):
    return dt.strptime(date_text, '%Y-%m-%d') < dt.today()

def istext(text):
    p = re.compile(r'[\w+ ]+')
    m = re.fullmatch(p, text)
    if m:
        return True
    else:
        return False

def select_all(table: str, where: dict, columns=['*']) -> list:

    """SELECT [* | col1, col2...] FROM table WHERE (w_key1, w_key2...) = (w_val1, w_val2...)"""

    columns = ','.join(columns) # str: "col1, col2 ..."
    where_keys = ','.join(where.keys()) # str: "w_key1, w_key2 ..."
    where_vals = list(where.values()) # list: [w_val1, w_val2 ...]
    where_qmrks = ','.join('?'*len(where_vals)) # palceholders for values, str: "?, ? ..."

    q = f"SELECT {columns} FROM {table} WHERE ({where_keys}) = ({where_qmrks})"

    con = sqlite3.connect(db_name)
    con.set_trace_callback(log_msg)
    con.row_factory = sqlite3.Row
    cur = con.cursor()
    log_msg(q)
    cur.execute(q, where_vals)
    result = [dict(row) for row in cur.fetchall()]
    con.commit()
    con.close()
    return result

def select_one(table: str, where: dict, columns=['*']) -> dict:

    """SELECT [* | col1, col2...] FROM table WHERE (w_key1, w_key2...) = (w_val1, w_val2...)"""

    columns = ','.join(columns) # str: "col1, col2 ..."
    where_keys = ','.join(where.keys()) # str: "w_key1, w_key2 ..."
    where_vals = list(where.values()) # list: [w_val1, w_val2 ...]
    where_qmrks = ','.join('?'*len(where_vals)) # palceholders for values, str: "?, ? ..."

    q = f"SELECT {columns} FROM {table} WHERE ({where_keys}) = ({where_qmrks})"

    con = sqlite3.connect(db_name)
    con.set_trace_callback(log_msg)
    con.row_factory = sqlite3.Row
    cur = con.cursor()
    log_msg(q)
    cur.execute(q, where_vals)
    result = cur.fetchone()
    con.commit()
    con.close()
    return dict(result) if result else None

def clear(table: str, where: dict):

    """DELETE FROM table WHERE (w_key1, w_key2...) = (w_val1, w_val2...)"""

    where_keys = ','.join(where.keys()) # str: "w_key1, w_key2 ..."
    where_vals = list(where.values()) # str: "w_val1, w_val2 ..."
    where_qmrks = ','.join('?'*len(where_vals)) # palceholders for values, str: "?, ? ..."

    q = f"DELETE FROM {table} WHERE ({where_keys}) = ({where_qmrks})"

    con = sqlite3.connect(db_name)
    con.set_trace_callback(log_msg)
    con.row_factory = sqlite3.Row
    cur = con.cursor()
    log_msg(q)
    cur.execute(q, where_vals)
    con.commit()
    con.close()

def insert(table: str, data: dict):

    """INSERT INTO table (key1, key2...) VALUES (val1, val2...) """

    keys = ','.join(data.keys()) # str: "key1, key2 ..."
    vals = list(data.values()) # str: "val1, val2 ..."
    qmarks = ','.join('?'*len(vals)) # palceholders for values, str: "?, ? ..."

    q = f"INSERT INTO {table} ({keys}) VALUES ({qmarks})"
    
    con = sqlite3.connect(db_name)
    con.set_trace_callback(log_msg)
    con.row_factory = sqlite3.Row
    cur = con.cursor()
    log_msg(q)
    cur.execute(q, vals)
    con.commit()
    con.close()

def update(table: str, set: dict, where: dict):

    """UPDATE table SET (s_key1, s_key2...) = (s_val1, s_val2...) WHERE (w_key1, w_key2...) = (w_val1, w_val2...)"""

    set_keys = ','.join(set.keys()) # str: "s_key1, s_key2 ..."
    set_vals = list(set.values()) # str: "s_val1, s_val2 ..."
    set_qmarks = ','.join('?'*len(set_vals)) # palceholders for values, str: "?, ? ..."

    where_keys = ','.join(where.keys()) # str: "w_key1, w_key2 ..."
    where_vals = list(where.values()) # str: "w_val1, w_val2 ..."
    where_qmrks = ','.join('?'*len(where_vals)) # palceholders for values, str: "?, ? ..."

    q = f"UPDATE {table} SET ({set_keys}) = ({set_qmarks}) WHERE ({where_keys}) = ({where_qmrks})"

    con = sqlite3.connect(db_name)
    con.set_trace_callback(log_msg)
    con.row_factory = sqlite3.Row
    cur = con.cursor()
    log_msg(q)
    cur.execute(q, [*set_vals, *where_vals])
    con.commit()
    con.close()


# wf(m1)

