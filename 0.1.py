import sqlite3
import re
from datetime import datetime as dt

m1 = {'text':'1986-10-10', 'chat':{'id':23, 'username':'user23'}}

def wf(msg):

    t = msg['text']
    id = msg['chat']['id']
    username = msg['chat']['username']

    user_command = select('user_command', 'user_id', id)

    if t == '/add':
        clear('user_command', 'user_id', id)
        clear('add_cache', 'user_id', id)
        insert('user_command', user_id=id, cmd_id=1, step_id=1)
        add(msg)
    elif t == '/delete':
        clear('user_command', 'user_id', id)
        clear('delete_cache', 'user_id', id)
        insert('user_command', user_id=id, cmd_id=2, step_id=1)
        delete(msg)
    elif t == '/month':
        response = this_month(id)
        send_msg(id, response)
    elif len(user_command)>0: # Record with the id exists in user_command
        if user_command[0]['cmd_id'] == 1: # command_id=1 (add) for the user_id in user_command
            add(msg)
        elif user_command[0]['cmd_id'] == 2: # command_id=2 (delete) for the user_id in user_command
            delete(msg)
        else:
            clear('user_command', 'user_id', id)
            show_start_msg(id)
    else:
        show_start_msg(id)
        


def add(msg):
    log_msg("ADD PROCESS HAS STARTED")
    t = msg['text']
    id = msg['chat']['id']
    username = msg['chat']['username']
   
    user_command = select('user_command', 'user_id', id)
    step_id = user_command[0]['step_id']
    log_msg(f"step id is {step_id}")
    if step_id == 1: # add message has come
        insert('add_cache', user_id=id, username=username)
        update('user_command', 'user_id', id, step_id=2)
        send_msg(id, "Enter a person name")
    elif step_id == 2: # pers_name has come
        if not istext(t):
            send_msg(id, "Name should contain only letters or numbers")
            return
        update('add_cache', 'user_id', id, pers_name=t)
        update('user_command', 'user_id', id, step_id=3)
        send_msg(id, "OK, now enter a persson birthday")
    elif step_id == 3: # pers_bday has come
        if not isdate(t):
            send_msg(id, "Enter a date in YYYY-MM-DD format")
            return
        if not ispast(t):
            send_msg(id, "The date should be earlier than today")
            return
        date_obj = dt.strptime(t, '%Y-%m-%d') # parse input to a date obj
        date_frnd = date_obj.strftime('%d %b %Y') # YYYY-MM-DD string
        date_sql = date_obj.strftime('%Y-%m-%d') # DD Mon YYYY string

        update('add_cache', 'user_id', id, pers_bday=date_sql)
        pers_name = select('add_cache', 'user_id', id)[0]['pers_name']
        user_tb = select('user', 'user_id', id)
        if len(user_tb)>0: # there is a record in user table
            update('user', 'user_id', id, username=username)
        else:
            insert('user', user_id=id, username=username)

        insert('person', pers_name=pers_name, pers_bday=date_sql, user_id=id)

        clear('add_cache', 'user_id', id)
        clear('user_command', 'user_id', id)
        send_msg(id, f"{pers_name}, born {date_frnd} has been added")
    else:
        clear('add_cache', 'user_id', id)
        clear('user_command', 'user_id', id)
        show_start_msg(id)

def delete(msg):
    log_msg("DELETE PROCESS HAS STARTES")
    t = msg['text']
    id = msg['chat']['id']
    username = msg['chat']['username']

    user_command = select('user_command', 'user_id', id)
    step_id = user_command[0]['step_id']
    log_msg(f"step id is {step_id}")
    if step_id == 1: # delete message has come
        person_list = select('person', 'user_id', id, 'rowid as pers_id', '*')
        show_list = [] # list to display a user
        insert_list = [] # list to insert in delete_cache
        for count, person in enumerate(person_list):
            person['pers_num'] = count+1
            show_list.append({'pers_num':person['pers_num'], 'pers_name':person['pers_name'], 'pers_bday':person['pers_bday']})
            insert_list.append({'user_id':person['user_id'], 'pers_id':person['pers_id'], 'pers_num':person['pers_num']})
        for person in insert_list:
            insert('delete_cache', **person)
        update('user_command', 'user_id', id, step_id=2)
        send_msg(id, "Enter numner of a person you want to delete")
        send_msg(id, show_list)
    elif step_id == 2: #Number of person to delete has come
        if not t.isdigit(): # returns True for int only
            send_msg(id, "Enter a number")
            return
        input_num = int(t)
        delete_cache = select('delete_cache', 'user_id', id, 'pers_num')
        pers_numbers = [item['pers_num'] for item in delete_cache]
        if input_num in pers_numbers:
            pers_id = select('delete_cache', '(user_id, pers_num)', (id, input_num))[0]['pers_id']
            person = select('person', 'rowid', pers_id)[0]
            clear('person', 'rowid', pers_id)
            clear('delete_cache', 'user_id', id)
            clear('user_command', 'user_id', id)
            send_msg(id, f"{person['pers_name']} born {person['pers_bday']} has been deleted")
        else:
            send_msg(id, "Wrong number, send /delete to get a list")
    else:
        clear('delete_cache', 'user_id', id)
        clear('user_command', 'user_id', id)
        show_start_msg(id)

def this_month(id):
    con = sqlite3.connect('birthdaybot_db.sqlite3')
    con.row_factory = sqlite3.Row
    cur = con.cursor()
    q = f"SELECT * from person where STRFTIME('%m', 'now') = STRFTIME('%m', pers_bday) and user_id = {id}"
    log_msg(q)
    cur.execute(q)
    result = [dict(row) for row in cur.fetchall()]
    con.commit()
    con.close()
    return result 

def select_orig(table, field, value, *args):
    columns = ', '.join(args) if len(args)>0 else '*'
    if not isinstance(value, int) and not isinstance(value, tuple): value = f"'{value}'"
    con = sqlite3.connect('birthdaybot_db.sqlite3')
    con.row_factory = sqlite3.Row
    cur = con.cursor()
    q = f"SELECT {columns} FROM {table} WHERE {field} = {value}"
    log_msg(q)
    cur.execute(q)
    result = [dict(row) for row in cur.fetchall()]
    con.commit()
    con.close()
    return result

def select(table, field, values: tuple, *args):
    values = tuple([values]) if not isinstance(values, tuple) else values
    columns = ', '.join(args) if len(args)>0 else '*'
    qmarks = ','.join('?'*len(values))
    # if not isinstance(value, int) and not isinstance(value, tuple): value = f"'{value}'"
    con = sqlite3.connect('birthdaybot_db.sqlite3')
    con.set_trace_callback(log_msg)
    con.row_factory = sqlite3.Row
    cur = con.cursor()
    q = f"SELECT {columns} FROM {table} WHERE {field} = ({qmarks})"
    log_msg(q)
    cur.execute(q, values)
    # cur.execute(f"SELECT {columns} FROM {table} WHERE {field} = ({qmarks})", values)
    result = [dict(row) for row in cur.fetchall()]
    con.commit()
    con.close()
    return result

def clear_orig(table, field, value):
    if not isinstance(value, int): value = f"'{value}'"
    con = sqlite3.connect('birthdaybot_db.sqlite3')
    cur = con.cursor()
    q = f"DELETE FROM {table} WHERE {field} = {value}"
    log_msg(q)
    cur.execute(q)
    con.commit()
    con.close()

def clear(table, field, value):
    # if not isinstance(value, int): value = f"'{value}'"
    value = tuple([value]) if not isinstance(value, tuple) else value
    con = sqlite3.connect('birthdaybot_db.sqlite3')
    con.set_trace_callback(log_msg)
    con.set_trace_callback(log_msg)
    cur = con.cursor()
    q = f"DELETE FROM {table} WHERE {field} = ?"
    log_msg(q)
    cur.execute(q, value)
    con.commit()
    con.close()

def insert(table, **kwargs):

    columns = list(kwargs.keys())
    values = [str(v) if isinstance(v, int) else f"'{v}'" for v in kwargs.values()]

    q = f"INSERT INTO {table} ({', '.join(columns)}) VALUES ({(', '.join(values))})"
    log_msg(q)

    con = sqlite3.connect('birthdaybot_db.sqlite3')
    cur = con.cursor()
    cur.execute(q)
    con.commit()
    con.close()

def update(table, field, value, **kwargs):

    if not isinstance(value, int): value = f"'{value}'"
    query_params = [f"{k} = {v}" if isinstance(v, int) else f"{k} = '{v}'" for k, v in kwargs.items()]

    q = f"UPDATE {table} SET {', '.join(query_params)} WHERE {field} = {value}"
    log_msg(q)

    con = sqlite3.connect('birthdaybot_db.sqlite3')
    cur = con.cursor()
    cur.execute(q)
    con.commit()
    con.close()

def show_start_msg(id):
    print(id, "/add - add a person, /delete - delete a person, /month - show birthdays of this month")

def send_msg(id, msg):
    print(f"> id is: {id},", f"msg is: {msg}")

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

wf(m1)


# print(isdate('2021-09-31'))
# print(ispast(dt.strptime('2021-10-08', '%Y-%m-%d')))


# da1 = dt.strptime('1991-08-10', '%Y-%m-%d')
# print(da1)
# da2 = datetime.datetime.today()
# print(da2)
# # print(da1 < da2)
# print(da1.strftime("%d %b %Y"))
# print(dt.strftime(dt.today(), '%Y-%m-%d'))
# print(da1.strftime("%d %b %Y"))
# print(ispast('2022-08-10'))
# print(da1.strftime('%Y-%m-%d'))