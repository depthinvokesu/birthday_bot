import sqlite3

class SQLtools():

    def __init__(self, db_name, callback_func=print) -> None:
        self.db_name = db_name
        self.callback_func = callback_func


    def select_all(self, table: str, where: dict, columns=['*']) -> list:

        """SELECT [* | col1, col2...] FROM table WHERE w_key1=w_val1 AND w_key2=w_val2 ..."""

        columns = ','.join(columns) # str: "col1, col2 ..."
        where_vals = list(where.values()) # list: [w_val1, w_val2 ...]
        where_clause = " AND ".join([f"{item}=?" for item in where.keys()]) # str: "w_key1=? AND w_key2=?"

        q = f"SELECT {columns} FROM {table} WHERE {where_clause}"

        con = sqlite3.connect(self.db_name)
        # con.set_trace_callback(self.callback_func) # Output logs
        con.row_factory = sqlite3.Row
        cur = con.cursor()
        # self.callback_func(q) # Output logs
        cur.execute(q, where_vals)
        result = [dict(row) for row in cur.fetchall()]
        con.commit()
        con.close()
        return result

    def select_one(self, table: str, where: dict, columns=['*']) -> dict:

        """SELECT [* | col1, col2...] FROM table WHERE w_key1=w_val1 AND w_key2=w_val2 ..."""

        columns = ','.join(columns) # str: "col1, col2 ..."
        where_vals = list(where.values()) # list: [w_val1, w_val2 ...]
        where_clause = " AND ".join([f"{item}=?" for item in where.keys()]) # str: "w_key1=? AND w_key2=?"

        q = f"SELECT {columns} FROM {table} WHERE {where_clause}"

        con = sqlite3.connect(self.db_name)
        # con.set_trace_callback(self.callback_func) # Output logs
        con.row_factory = sqlite3.Row
        cur = con.cursor()
        # self.callback_func(q) # Output logs
        cur.execute(q, where_vals)
        result = cur.fetchone()
        con.commit()
        con.close()
        return dict(result) if result else None

    def delete(self, table: str, where: dict):

        """DELETE FROM table WHERE w_key1=w_val1 AND w_key2=w_val2 ..."""

        where_vals = list(where.values()) # list: [w_val1, w_val2 ...]
        where_clause = " AND ".join([f"{item}=?" for item in where.keys()]) # str: "w_key1=? AND w_key2=?"

        q = f"DELETE FROM {table} WHERE {where_clause}"

        con = sqlite3.connect(self.db_name)
        # con.set_trace_callback(self.callback_func) # Output logs
        con.row_factory = sqlite3.Row
        cur = con.cursor()
        # self.callback_func(q) # Output logs
        cur.execute(q, where_vals)
        con.commit()
        con.close()

    def insert(self, table: str, data: dict):

        """INSERT INTO table (key1, key2...) VALUES (val1, val2...) """

        keys = ','.join(data.keys()) # str: "key1, key2 ..."
        vals = list(data.values()) # str: "val1, val2 ..."
        qmarks = ','.join('?'*len(vals)) # palceholders for values, str: "?, ? ..."

        q = f"INSERT INTO {table} ({keys}) VALUES ({qmarks})"

        con = sqlite3.connect(self.db_name)
        # con.set_trace_callback(self.callback_func) # Output logs
        con.row_factory = sqlite3.Row
        cur = con.cursor()
        # self.callback_func(q) # Output logs
        cur.execute(q, vals)
        con.commit()
        con.close()

    def update(self, table: str, set: dict, where: dict):

        """UPDATE table SET s_key1=s_val1 AND s_key2=s_val2 ... WHERE w_key1=w_val1 AND w_key2=w_val2 ..."""

        set_vals = list(set.values()) # str: "s_val1, s_val2 ..."
        set_clause = " AND ".join([f"{item}=?" for item in set.keys()]) # str: "s_key1=? AND s_key2=?"

        where_vals = list(where.values()) # list: [w_val1, w_val2 ...]
        where_clause = " AND ".join([f"{item}=?" for item in where.keys()]) # str: "key1=? AND key2=? ..."

        q = f"UPDATE {table} SET {set_clause} WHERE {where_clause}"

        con = sqlite3.connect(self.db_name)
        # con.set_trace_callback(self.callback_func) # Output logs
        con.row_factory = sqlite3.Row
        cur = con.cursor()
        # self.callback_func(q) # Output logs
        cur.execute(q, [*set_vals, *where_vals])
        con.commit()
        con.close()
