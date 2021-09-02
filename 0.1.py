import sqlite3

m1 = {'chat_id':13, 'username':'user13', 'text':3}

def wf(msg):
    t = msg['text']
    id = msg['chat_id']
    username = msg['username']
    user_command = select('user_command', 'user_id', id)

    if t == 'add':
        clear('user_command', 'user_id', id)
        clear('add_cache', 'user_id', id)
        insert('user_command', user_id=id, cmd_id=1, step_id=1)
        add(msg)
    elif t == 'delete':
        clear('user_command', 'user_id', id)
        clear('delete_cache', 'user_id', id)
        insert('user_command', user_id=id, cmd_id=2, step_id=1)
        delete(msg)
    elif len(user_command)>0: # Record with the id exists in user_command
        if user_command[0]['cmd_id'] == 1: # command_id=1 (add) for the user_id in user_command
            add(msg)
        elif user_command[0]['cmd_id'] == 2: # command_id=2 (delete) for the user_id in user_command
            delete(msg)
        else:
            clear('user_command', 'user_id', id)
            show_start_msg()
    else:
        show_start_msg()

def add(msg):
    print("ADD PROCESS HAS STARTED")
    t = msg['text']
    id = msg['chat_id']
    username = msg['username']
    user_command = select('user_command', 'user_id', id)
    step_id = user_command[0]['step_id']
    print(f"step id is {step_id}")
    if step_id == 1: # add message has come
        insert('add_cache', user_id=id, username=username)
        update('user_command', 'user_id', id, step_id=2)
        print("Enter a person name")
    elif step_id == 2: # pers_name has come
        update('add_cache', 'user_id', id, pers_name=t)
        update('user_command', 'user_id', id, step_id=3)
        print("OK, now enter a persson birthday")
    elif step_id == 3: #pers_bday has come
        update('add_cache', 'user_id', id, pers_bday=t)
        add_cache = select('add_cache', 'user_id', id)
        id, username, pers_name, pers_bday = add_cache[0]['user_id'], add_cache[0]['username'], add_cache[0]['pers_name'], add_cache[0]['pers_bday']
        user = select('user', 'user_id', id)
        if len(user)>0: # there is a record in user table
            update('user', 'user_id', id, username=username)
        else:
            insert('user', user_id=id, username=username)
        insert('person', pers_name=pers_name, pers_bday=pers_bday, user_id=id)

        clear('add_cache', 'user_id', id)
        clear('user_command', 'user_id', id)
        print("The person has been added")
    else:
        clear('add_cache', 'user_id', id)
        clear('user_command', 'user_id', id)
        show_start_msg()


def delete(msg):
    print("DELETE PROCESS HAS STARTES")
    t = msg['text']
    id = msg['chat_id']
    username = msg['username']
    user_command = select('user_command', 'user_id', id)
    step_id = user_command[0]['step_id']
    print(f"step id is {step_id}")
    if step_id == 1: # deletete message has come
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
        print("Enter numner of a person you want to delete")
        print(show_list)
    elif step_id == 2: #Number of person to delete has come
        delete_cache = select('delete_cache', 'user_id', id, 'pers_num')
        pers_numbers = [item['pers_num'] for item in delete_cache]
        if t in pers_numbers:
            pers_id = select('delete_cache', '(user_id, pers_num)', (id, t))[0]['pers_id']
            person = select('person', 'rowid', pers_id)[0]
            clear('person', 'rowid', pers_id)
            clear('delete_cache', 'user_id', id)
            clear('user_command', 'user_id', id)
            print(f"{person['pers_name']} born in {person['pers_bday']} has been deleted")
        else:
            print("Wrong number, send delete to get a list")
    else:
        clear('delete_cache', 'user_id', id)
        clear('user_command', 'user_id', id)
        show_start_msg()



def select(table, field, value, *args):
    columns = ', '.join(args) if len(args)>0 else '*'
    if not isinstance(value, int) and not isinstance(value, tuple): value = f"'{value}'"
    con = sqlite3.connect('birthdaybot_db.sqlite3')
    con.row_factory = sqlite3.Row
    cur = con.cursor()
    q = f"SELECT {columns} FROM {table} WHERE {field} = {value}"
    print(q)
    cur.execute(q)
    result = [dict(row) for row in cur.fetchall()]
    con.commit()
    con.close()
    return result

def clear(table, field, value):
    if not isinstance(value, int): value = f"'{value}'"
    con = sqlite3.connect('birthdaybot_db.sqlite3')
    cur = con.cursor()
    q = f"DELETE FROM {table} WHERE {field} = {value}"
    print(q)
    cur.execute(q)
    con.commit()
    con.close()

def insert(table, **kwargs):

    columns = list(kwargs.keys())
    values = [str(v) if isinstance(v, int) else f"'{v}'" for v in kwargs.values()]

    q = f"INSERT INTO {table} ({', '.join(columns)}) VALUES ({(', '.join(values))})"
    print(q)

    con = sqlite3.connect('birthdaybot_db.sqlite3')
    cur = con.cursor()
    cur.execute(q)
    con.commit()
    con.close()

def update(table, field, value, **kwargs):

    if not isinstance(value, int): value = f"'{value}'"
    query_params = [f"{k} = {v}" if isinstance(v, int) else f"{k} = '{v}'" for k, v in kwargs.items()]

    q = f"UPDATE {table} SET {', '.join(query_params)} WHERE {field} = {value}"
    print(q)

    con = sqlite3.connect('birthdaybot_db.sqlite3')
    cur = con.cursor()
    cur.execute(q)
    con.commit()
    con.close()

def show_start_msg():
    print("/add - add a person, /delete - delete a person")



wf(m1)
# r = select('delete_cache', '(user_id, pers_num)', (7, 1))[0]['pers_id']
# print(r)
# clear('person', 'rowid', 10)

