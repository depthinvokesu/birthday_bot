import sqlite3
from typing import List, Dict, Tuple, Optional
from settings import log_msg

class SQLtools:

    def __init__(self, db_name, callback_func=print):
        self.db_name = db_name
        self.callback_func = callback_func

    def select_all(self, table: str, where: dict, columns: list = ['*']) -> List[Dict]:

        """SELECT [* | col1, col2...] FROM table WHERE w_key1=w_val1 AND w_key2=w_val2 ..."""

        q, where_vals = self.__prepare_select_query(table, where, columns)

        cur, connection = self.__get_cursor(q)
        cur.execute(q, where_vals)
        result = [dict(row) for row in cur.fetchall()]
        connection.close()
        return result

    def select_one(self, table: str, where: dict, columns=['*']) -> Optional[dict]:

        """SELECT [* | col1, col2...] FROM table WHERE w_key1=w_val1 AND w_key2=w_val2 ..."""

        q, where_vals = self.__prepare_select_query(table, where, columns)

        cur, connection = self.__get_cursor(q)
        cur.execute(q, where_vals)
        result = cur.fetchone()
        connection.close()
        return dict(result) if result else None

    def delete(self, table: str, where: dict) -> None:

        """DELETE FROM table WHERE w_key1=w_val1 AND w_key2=w_val2 ..."""

        where_vals = list(where.values()) # list: [w_val1, w_val2 ...]
        where_clause = self.__join_conditions(where) # str: "w_key1=? AND w_key2=?"

        q = f"DELETE FROM {table} WHERE {where_clause}"

        cur, connection = self.__get_cursor(q)
        cur.execute(q, where_vals)
        connection.commit()
        connection.close()

    def insert(self, table: str, data: dict) -> None:

        """INSERT INTO table (key1, key2...) VALUES (val1, val2...) """

        keys = ','.join(data.keys()) # str: "key1, key2 ..."
        vals = list(data.values()) # str: "val1, val2 ..."
        qmarks = ','.join('?'*len(vals)) # palceholders for values, str: "?, ? ..."

        q = f"INSERT INTO {table} ({keys}) VALUES ({qmarks})"

        cur, connection = self.__get_cursor(q)
        cur.execute(q, vals)
        connection.commit()
        connection.close()

    def update(self, table: str, set: dict, where: dict) -> None:

        """UPDATE table SET s_key1=s_val1 AND s_key2=s_val2 ... WHERE w_key1=w_val1 AND w_key2=w_val2 ..."""

        set_vals = list(set.values()) # str: "s_val1, s_val2 ..."
        set_clause = ", ".join([f"{item}=?" for item in set.keys()]) # str: "s_key1=?, s_key2=? ..."

        where_vals = list(where.values()) # list: [w_val1, w_val2 ...]
        where_clause = self.__join_conditions(where) # str: "w_key1=? AND w_key2=?"

        q = f"UPDATE {table} SET {set_clause} WHERE {where_clause}"

        cur, connection = self.__get_cursor(q)
        cur.execute(q, [*set_vals, *where_vals])
        connection.commit()
        connection.close()

    def replace(self, table: str, data: dict) -> None:

        """INSERT OR REPLACE INTO table (key1, key2...) VALUES (val1, val2...) """

        keys = ','.join(data.keys()) # str: "key1, key2 ..."
        vals = list(data.values()) # str: "val1, val2 ..."
        qmarks = ','.join('?'*len(vals)) # palceholders for values, str: "?, ? ..."

        q = f"REPLACE INTO {table} ({keys}) VALUES ({qmarks})"

        cur, connection = self.__get_cursor(q)
        cur.execute(q, vals)
        connection.commit()
        connection.close()

    def __prepare_select_query(self, table: str, where: dict, columns) -> Tuple[list]:
        columns = ','.join(columns) # str: "col1, col2 ..."
        where_vals = list(where.values()) # list: [w_val1, w_val2 ...]
        where_clause = self.__join_conditions(where) # str: "w_key1=? AND w_key2=?"
        return f"SELECT {columns} FROM {table} WHERE {where_clause}", where_vals

    def __join_conditions(self, cond: dict) -> str:
        return " AND ".join([f"{item}=?" for item in cond.keys()]) # str: "key1=? AND key2=? ..."

    def __get_cursor(self, q):
        con = sqlite3.connect(self.db_name)
        con.set_trace_callback(self.callback_func) # Output logs
        con.row_factory = sqlite3.Row
        cur = con.cursor()
        self.callback_func(q) # Output logs
        return cur, con


sql = SQLtools(db_name="birthdaybot_db.sqlite3", callback_func=log_msg)
        
sql.select_all("user", {1:1})