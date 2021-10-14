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

def select(table, field, values: tuple, *args):
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
    con.set_trace_callback(log_msg)
    cur = con.cursor()
    q = f"DELETE FROM {table} WHERE {field} = ?"
    log_msg(q)
    cur.execute(q, value)
    con.commit()
    con.close()


clear(table='add_cache', field='username', value='prokis')