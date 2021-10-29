"""basic SQL functions"""

def select_orig(table, field, value, *args):
    columns = ', '.join(args) if len(args)>0 else '*'
    if not isinstance(value, int) and not isinstance(value, tuple): value = f"'{value}'"
    con = sqlite3.connect(db_name)
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
    con = sqlite3.connect(db_name)
    con.set_trace_callback(log_msg)
    con.row_factory = sqlite3.Row
    cur = con.cursor()
    q = f"SELECT {columns} FROM {table} WHERE {field} = ({qmarks})"
    log_msg(q)
    cur.execute(q, values)
    result = [dict(row) for row in cur.fetchall()]
    con.commit()
    con.close()
    return result

def clear_orig(table, field, value):
    if not isinstance(value, int): value = f"'{value}'"
    con = sqlite3.connect(db_name)
    cur = con.cursor()
    q = f"DELETE FROM {table} WHERE {field} = {value}"
    log_msg(q)
    cur.execute(q)
    con.commit()
    con.close()

def clear(table, field, value):
    # if not isinstance(value, int): value = f"'{value}'"
    value = tuple([value]) if not isinstance(value, tuple) else value
    con = sqlite3.connect(db_name)
    con.set_trace_callback(log_msg)
    cur = con.cursor()
    q = f"DELETE FROM {table} WHERE {field} = ?"
    log_msg(q)
    cur.execute(q, value)
    con.commit()
    con.close()

def insert_orig(table, **kwargs):

    columns = list(kwargs.keys())
    values = [str(v) if isinstance(v, int) else f"'{v}'" for v in kwargs.values()]

    q = f"INSERT INTO {table} ({', '.join(columns)}) VALUES ({(', '.join(values))})"
    log_msg(q)

    con = sqlite3.connect(db_name)
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
    con = sqlite3.connect(db_name)
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

    con = sqlite3.connect(db_name)
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

    con = sqlite3.connect(db_name)
    con.set_trace_callback(log_msg)
    cur = con.cursor()
    
    cur.execute(q, (*query_values, *values))
    # cur.execute("UPDATE user set username=? where user_id=?", ('user24',2))
    con.commit()
    con.close()
