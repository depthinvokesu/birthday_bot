
from datetime import datetime as dt
from SQLtools import SQLtools
import re

def log_msg(msg):
    print(msg)

sql = SQLtools(db_name='birthdaybot_db.sqlite3', callback_func=log_msg)


m1 = {'text':'/help', 'chat':{'id':4, 'username':'user13'}}

def workflow(msg):

    text = msg['text']
    id = msg['chat']['id']
    username = msg['chat']['username']

    user_command = sql.select_one(table='user_command', where={'user_id':id}) # {user_id: x, cmd_id: y, step_id: z}

    if text == '/add':
        sql.delete(table='user_command', where={'user_id':id})
        sql.delete(table='add_cache', where={'user_id':id})
        sql.delete(table='delete_cache', where={'user_id':id})
        sql.insert(table='user_command', data={'user_id': id, 'cmd_id': 1, 'step_id': 1})
        add_person(id, text, username)

    elif text == '/delete':
        sql.delete(table='user_command', where={'user_id':id})
        sql.delete(table='add_cache', where={'user_id':id})
        sql.delete(table='delete_cache', where={'user_id':id})
        sql.insert(table='user_command', data={'user_id': id, 'cmd_id': 2, 'step_id': 1})
        delete_person(id, text)

    elif text == '/month':
        sql.delete(table='user_command', where={'user_id':id})
        sql.delete(table='add_cache', where={'user_id':id})
        sql.delete(table='delete_cache', where={'user_id':id})
        response = this_month(id)
        if response:
            send_msg(id, response)
        else:
            send_msg(id, "No one celebrates birthday this month")

    elif text in ('/list', '/all'):
        sql.delete(table='user_command', where={'user_id':id})
        sql.delete(table='add_cache', where={'user_id':id})
        sql.delete(table='delete_cache', where={'user_id':id})            
        response = list_all(id)
        if response:
            send_msg(id, response)
        else:
            send_msg(id, "You didn't add anybody yet")

    elif text == '/help':
        sql.delete(table='user_command', where={'user_id':id})
        sql.delete(table='add_cache', where={'user_id':id})
        sql.delete(table='delete_cache', where={'user_id':id})
        msg = "Hello, I am a Birthday bot! \nI can help you to keep track of your friends birthdays. \nJust tell me the dates and I will notify you once it's time to congratulate ;) \nCommand list: \n/add - add a person \n/delete - delete a person \n/month - show birthdays of this month \n/list or /all - show the people you've added"
        send_msg(id, msg)

    elif user_command: # Record with the id exists in user_command
        if user_command['cmd_id'] == 1: # command_id=1 (add) for the user_id in user_command
            add_person(id, text, username)
        elif user_command['cmd_id'] == 2: # command_id=2 (delete) for the user_id in user_command
            delete_person(id, text)
        else:
            sql.delete(table='user_command', where={'user_id':id})
            show_start_msg(id)
    else:
        show_start_msg(id)
        


def add_person(id, text, username):
    log_msg("ADD PROCESS HAS STARTED")
   
    step_id = sql.select_one(table='user_command', where={'user_id':id})['step_id']
    log_msg(f"step id is {step_id}")

    if step_id == 1: # add message has come

        # Inserting user's data to cache table, incrementing step_id and sending a message with result
        sql.insert(table='add_cache', data={'user_id':id, 'username': username})
        sql.update(table='user_command', set={'step_id':2}, where={'user_id':id})
        send_msg(id, "Enter a person name")

    elif step_id == 2: # pers_name has come

        if not istext(text): # returns True if t consists only of letters and numbers
            send_msg(id, "Name should contain only letters or numbers")
            return
        
        # Inserting the input to the cache table, incrementing step_id and sending a message with result
        sql.update(table='add_cache', set={'pers_name':text}, where={'user_id':id})
        sql.update(table='user_command', set={'step_id':3}, where={'user_id':id})
        send_msg(id, f"OK, now enter {text}'s birthday (YYYY-MM-DD)")

    elif step_id == 3: # pers_bday has come

        # Validating the input
        if not isdate(text):
            send_msg(id, "Enter a date in YYYY-MM-DD format")
            return
        if not ispast(text):
            send_msg(id, "The date should be earlier than today")
            return
        
        # Converting the date
        date_obj = dt.strptime(text, '%Y-%m-%d') # parse input to a date obj
        date_frnd = date_obj.strftime('%d %b %Y') # DD Mon YYYY string
        date_sql = date_obj.strftime('%Y-%m-%d') # YYYY-MM-DD string DD

        # Inserting the input to the cache table
        sql.update(table='add_cache', set={'pers_bday':date_sql}, where={'user_id':id})
        
        # Copying the data from cache to person table
        pers_name = sql.select_one(table='add_cache', where={'user_id':id})['pers_name']
        sql.insert(table='person', data={'pers_name':pers_name, 'pers_bday':date_sql, 'user_id':id})

        # Inserting user's data to user table
        user_tb = sql.select_one(table='user', where={'user_id': id})
        if user_tb: # record is already exists
            sql.update(table='user', set={'username':username}, where={'user_id':id})
        else:
            sql.insert(table='user', data={'user_id':id, 'username': username})

        # Deleting cache and sending the final message
        sql.delete(table='add_cache', where={'user_id':id})
        sql.delete(table='user_command', where={'user_id':id})
        send_msg(id, f"{pers_name}, born {date_frnd} has been added")
    else:
        sql.delete(table='add_cache', where={'user_id':id})
        sql.delete(table='user_command', where={'user_id':id})
        show_start_msg(id)

def delete_person(id, text):
    log_msg("DELETE PROCESS HAS STARTED")

    step_id = sql.select_one(table='user_command', where={'user_id':id})['step_id']
    log_msg(f"step id is {step_id}")

    if step_id == 1: # delete message has come

        # Composing lists of people for current user
        person_tb = sql.select_all(table='person', where={'user_id':id}, columns=['rowid as pers_id', '*']) # [{pers_name, pers_bday, user_id, pers_id}, ...]
        if len(person_tb) == 0: # there is no one in person table
            send_msg(id, "There is no one to delete")
            sql.delete(table='delete_cache', where={'user_id':id})
            sql.delete(table='user_command', where={'user_id':id})
            show_start_msg(id)
            return

        show_list = [] # list to show to the user
        insert_list = [] # list to insert into delete_cache

        # Populating the lists with extra attributes
        for number, person in enumerate(person_tb): 
            person['pers_num'] = number+1 # ordinal number when showing to the user
            show_list.append({'pers_num':person['pers_num'], 'pers_name':person['pers_name'], 'pers_bday':person['pers_bday']})
            insert_list.append({'pers_num':person['pers_num'], 'pers_id':person['pers_id'], 'user_id':person['user_id']})
        show_list_str = '\n'.join([f"{item['pers_num']} {item['pers_name']} {item['pers_bday']}" for item in show_list])

        # Inserting the list into delete_cache table
        for person in insert_list:
            sql.insert(table='delete_cache', data=person)

        # Incrementing step_id and sending a message with result
        sql.update(table='user_command', set={'step_id': 2}, where={'user_id': id})
        send_msg(id, f"Enter a number of a person you want to delete:\n{show_list_str}")

    elif step_id == 2: # Number of person to delete has come

        if not text.isdigit(): # returns True only if t covertable to int
            send_msg(id, "Enter a number")
            return
        input_num = int(text)

        # Checking if input number is valid
        delete_cache_tb = sql.select_all(table='delete_cache', where={'user_id': id}) # [{user_id, pers_id, pers_num}, ..]
        pers_numbers = [item['pers_num'] for item in delete_cache_tb] # [1, 2...]
        if input_num not in pers_numbers:
            send_msg(id, "Wrong number, send /delete to get a list")
            return
        
        # Getting id, name, bday of the person to delete
        pers_id = sql.select_one(table='delete_cache', where={'user_id': id, 'pers_num': input_num})['pers_id']
        person = sql.select_one(table='person', where={'rowid': pers_id}) # {pers_name, pers_bday}

        # Deleting target person from person table and deleting cache
        sql.delete(table='person', where={'rowid': pers_id})
        sql.delete(table='delete_cache', where={'user_id':id})
        sql.delete(table='user_command', where={'user_id':id})

        # Final message
        send_msg(id, f"{person['pers_name']} born {person['pers_bday']} has been deleted")

    else:
        sql.delete(table='delete_cache', where={'user_id':id})
        sql.delete(table='user_command', where={'user_id':id})
        show_start_msg(id)

def this_month(id):
    log_msg("MONTH PROCESS HAS STARTED")
    month = dt.now().strftime("%m")
    result = sql.select_all(table='person', where={"user_id": id, "STRFTIME('%m', pers_bday)": month})
    if len(result) == 0:
        return None
    else:
        return '\n'.join([f"{item['pers_name']} {item['pers_bday']}" for item in result])

def list_all(id):
    log_msg("LIST ALL PROCESS HAS STARTED")
    result = sql.select_all(table='person', where={"user_id": id})
    if len(result) == 0:
        return None
    else:
        return '\n'.join([f"{item['pers_name']} {item['pers_bday']}" for item in result])

def show_start_msg(id):
    log_msg("START_MSG PROCESS HAS STARTED")
    msg = "Command list: \n/add - add a person \n/delete - delete a person \n/month - show birthdays of this month \n/list or /all - show all people you've added"
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

workflow(m1)

