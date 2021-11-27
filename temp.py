import sqlite3

def select_orig(table, field, value, *args):
    columns = ', '.join(args) if len(args)>0 else '*'
    print(value.__repr__())
    if not isinstance(value, int) and not isinstance(value, tuple): value = f"'{value}'"
    print(value.__repr__())
    con = sqlite3.connect('test.sqlite3')
    con.row_factory = sqlite3.Row
    cur = con.cursor()
    q = f"SELECT {columns} FROM {table} WHERE {field} = {value}"
    log_msg(q)
    cur.execute(q)
    result = [dict(row) for row in cur.fetchall()]
    con.commit()
    con.close()
    return result


def log_msg(msg):
    print(msg)

def select(table, field, values, *args):
    values = tuple([values]) if not isinstance(values, tuple) else values
    columns = ', '.join(args) if len(args)>0 else '*'
    qmarks = ','.join('?'*len(values))
    # if not isinstance(value, int) and not isinstance(value, tuple): value = f"'{value}'"
    con = sqlite3.connect('test.sqlite3')
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

# f"SELECT {columns} FROM {table} WHERE {field} = ?", value
# f"SELECT {columns} FROM {table} WHERE {field} = (?)", value
# f"SELECT {columns} FROM {table} WHERE {field} = (?, ?)", value

# values = (23,26)
# qmarks = ','.join('?'*len(values))
# print(qmarks)

# id = 23
# input_num = 1
# res = select('person', '(user_id, pers_name)', (4, 'Govard'))
# res = select('person', 'user_id', 4)
# print(res)

#SELECT * from user where (user_id, username) = (23, 1)

def clear(table, field, value):
    # if not isinstance(value, int): value = f"'{value}'"
    value = tuple([value]) if not isinstance(value, tuple) else value
    con = sqlite3.connect('birthdaybot_db.sqlite3')
    con.set_trace_callback(log_msg)
    cur = con.cursor()
    q = f"DELETE FROM {table} WHERE {field} = ?"
    log_msg(q)
    cur.execute(q, value)
    con.commit()
    con.close()


# clear(table='add_cache', field='username', value='prokis')

def insert_orig(table, **kwargs):

    columns = list(kwargs.keys())
    values = [str(v) if isinstance(v, int) else f"'{v}'" for v in kwargs.values()]

    q = f"INSERT INTO {table} ({', '.join(columns)}) VALUES ({(', '.join(values))})"
    log_msg(q)

    con = sqlite3.connect('test.sqlite3')
    
    cur = con.cursor()
    cur.execute(q)
    con.commit()
    con.close()


def insert(table, **kwargs):

    columns = list(kwargs.keys())
    values = tuple(kwargs.values())
    qmarks = ','.join('?'*len(values))
    q = f"INSERT INTO {table} ({', '.join(columns)}) VALUES ({qmarks})"

    log_msg(q)
    con = sqlite3.connect('test.sqlite3')
    con.set_trace_callback(log_msg)
    cur = con.cursor()

    cur.execute(q, values)

    con.commit()
    con.close()

def update_orig(table, field, value, **kwargs):

    if not isinstance(value, int): value = f"'{value}'"
    query_params = [f"{k} = {v}" if isinstance(v, int) else f"{k} = '{v}'" for k, v in kwargs.items()]

    q = f"UPDATE {table} SET {', '.join(query_params)} WHERE {field} = {value}"
    log_msg(q)

    con = sqlite3.connect('tets.sqlite3')
    con.set_trace_callback(log_msg)
    cur = con.cursor()
    
    cur.execute(q)
    con.commit()
    con.close()

def update(table, field, values, **kwargs):

    values = tuple([values]) if not isinstance(values, tuple) else values
    query_params = [f"{k} = ?" for k in kwargs.keys()]
    query_values = tuple(kwargs.values())

    # q = f"UPDATE {table} SET {', '.join(query_params)} WHERE {field} = {value}"

    q = f"UPDATE {table} SET {', '.join(query_params)} WHERE {field} = ?"
    log_msg(q)

    con = sqlite3.connect('test.sqlite3')
    con.set_trace_callback(log_msg)
    cur = con.cursor()
    
    cur.execute(q, (*query_values, *values))
    # cur.execute("UPDATE user set username=? where user_id=?", ('user24',2))
    con.commit()
    con.close()

# update('user_command', 'user_id', 342821779, cmd_id=13333, step_id=2333)


# vals = {'user_id':2, 'username':'user2'}
# insert(table='user', user_id=4, username='user4')
# insert(table='user', kwargs={'user_id':33, 'username':'user33'})

# UPDATE add_cache SET pers_bday = '2021-10-17' WHERE user_id = 24

# show_list = [{'pers_num': 1, 'pers_name': 'Ludacris', 'pers_bday': '1977-09-11'}, {'pers_num': 2, 'pers_name': 'Walter Reed', 'pers_bday': '1851-09-13'}, {'pers_num': 3, 'pers_name': 'Barry Newman', 'pers_bday': '1938-11-07'}, {'pers_num': 4, 'pers_name': 'Anne Hathaway', 'pers_bday': '1982-11-12'}, {'pers_num': 5, 'pers_name': 'Ryan Gosling', 'pers_bday': '1980-11-12'}]

# msg = '\n'.join([f"{item['pers_num']} {item['pers_name']} {item['pers_bday']}" for item in show_list])
# print(msg)

# month_list = [{'pers_name': 'Barry Newman', 'pers_bday': '1938-11-07', 'user_id': 342821779}, {'pers_name': 'Anne Hathaway', 'pers_bday': '1982-11-12', 'user_id': 342821779}, {'pers_name': 'Ryan Gosling', 'pers_bday': '1980-11-12', 'user_id': 342821779}]
# msg = '\n'.join([f"{item['pers_name']} {item['pers_bday']}" for item in month_list])
# print(msg)
