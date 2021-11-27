import sqlite3

def log_msg(msg):
    print(msg)

db_name = 'test.sqlite3'

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

# res = select_one(table='person', where={'user_id':'17', 'pers_name':'Hugh Grant'}, columns=['pers_name', 'user_id'])
# res = select_all(table='person', where={'user_id':'17'}, columns=['pers_name', 'user_id'])
# print(res)


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

# clear(table='delete_cache', where={'user_id':4})


def insert(table: str, data: dict):

    """INSERT INTO table (key1, key2...) VALUES (val1, val2...) """

    keys = ','.join(data.keys()) # str: "key1, key2 ..."
    vals = list(data.values()) # list: "val1, val2 ..."
    qmarks = ','.join('?'*len(vals)) # str, palceholders for values: "?, ? ..."

    q = f"INSERT INTO {table} ({keys}) VALUES ({qmarks})"
    
    con = sqlite3.connect(db_name)
    con.set_trace_callback(log_msg)
    con.row_factory = sqlite3.Row
    cur = con.cursor()
    log_msg(q)
    cur.execute(q, vals)
    con.commit()
    con.close()

# insert(table='add_cache', data={'user_id':342821779, 'username': 'prokis1'})


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

# update(table='add_cache', set={'pers_name':'Guy 2', 'pers_bday':'1900-01-01'}, where={'user_id':342821779, 'username':'prokis1'})
