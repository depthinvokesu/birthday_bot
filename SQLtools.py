import sqlite3
from typing import List, Dict, Tuple, Optional


class Connection:

        """Class to work with SQLite3 connection object"""

        def __init__(self, db_name, callback_func):
            self.db_name = db_name
            self.callback_func = callback_func

            self.conn = sqlite3.connect(self.db_name)
            self.conn.set_trace_callback(self.callback_func) # Set which func outputs logs
            self.conn.row_factory = sqlite3.Row

        def get_cursor(self) -> sqlite3.Cursor:
            return self.conn.cursor()

        def commit(self) -> None:
            self.conn.commit()

        def close(self) -> None:
            self.conn.close()
        

class Cursor:

    """Context manager to get a cursor from a given connection object"""

    def __init__(self, connection):
        self.conn = connection

    def __enter__(self):
        return self.conn.get_cursor()

    def __exit__(self, type, value, traceback):
        self.conn.commit()



class SQLtools:

    """Class containing basic SQL functions e.g. SELECT, UPDATE, INSERT, DELETE, REPLACE in SQLite3 implementation"""
    
    def __init__(self, connection):
        self.conn = connection

    def select_all(self, table: str, where: dict, columns: list = ['*']) -> List[Dict]:

        """SELECT [* | col1, col2...] FROM table WHERE w_key1=w_val1 AND w_key2=w_val2 ..."""

        columns = ','.join(columns) # str: "col1, col2 ..."
        where_vals, where_expr = self.__get_query_params(clause_data=where, clause_type='where')

        q = f"SELECT {columns} FROM {table} WHERE {where_expr}"

        with Cursor(self.conn) as cur:
            cur.execute(q, where_vals)
            result = [dict(row) for row in cur.fetchall()]
        return result

    def select_one(self, table: str, where: dict, columns=['*']) -> Optional[dict]:

        """SELECT [* | col1, col2...] FROM table WHERE w_key1=w_val1 AND w_key2=w_val2 ..."""

        columns = ','.join(columns) # str: "col1, col2 ..."
        where_vals, where_expr = self.__get_query_params(clause_data=where, clause_type='where')

        q = f"SELECT {columns} FROM {table} WHERE {where_expr}"

        with Cursor(self.conn) as cur:
            cur.execute(q, where_vals)
            result = cur.fetchone()
        return dict(result) if result else None

    def delete(self, table: str, where: dict) -> None:

        """DELETE FROM table WHERE w_key1=w_val1 AND w_key2=w_val2 ..."""

        where_vals, where_expr = self.__get_query_params(clause_data=where, clause_type='where')

        q = f"DELETE FROM {table} WHERE {where_expr}"

        with Cursor(self.conn) as cur:
            cur.execute(q, where_vals)

    def update(self, table: str, set: dict, where: dict) -> None:

        """UPDATE table SET s_key1=s_val1 AND s_key2=s_val2 ... WHERE w_key1=w_val1 AND w_key2=w_val2 ..."""

        set_vals, set_expr = self.__get_query_params(clause_data=set, clause_type='set')
        where_vals, where_expr = self.__get_query_params(clause_data=where, clause_type='where')

        q = f"UPDATE {table} SET {set_expr} WHERE {where_expr}"

        with Cursor(self.conn) as cur:
            cur.execute(q, [*set_vals, *where_vals])

    def insert(self, table: str, data: dict) -> None:

        """INSERT INTO table (key1, key2...) VALUES (val1, val2...) """

        keys, vals, qmarks = self.__get_query_params(clause_data=data, clause_type='insert_replace')

        q = f"INSERT INTO {table} ({keys}) VALUES ({qmarks})"

        with Cursor(self.conn) as cur:
            cur.execute(q, vals)

    def replace(self, table: str, data: dict) -> None:

        """INSERT OR REPLACE INTO table (key1, key2...) VALUES (val1, val2...) """

        keys, vals, qmarks = self.__get_query_params(clause_data=data, clause_type='insert_replace')

        q = f"REPLACE INTO {table} ({keys}) VALUES ({qmarks})"

        with Cursor(self.conn) as cur:
            cur.execute(q, vals)


    def __get_query_params(self, clause_data: dict, clause_type: str) -> Tuple:
        if clause_type == 'insert_replace':
            keys = ','.join(clause_data.keys()) # str: "key1, key2 ..."
            vals = list(clause_data.values()) # str: "val1, val2 ..."
            qmarks = ','.join('?'*len(vals)) # palceholders for values, str: "?, ? ..."
            return keys, vals, qmarks
        else:
            if clause_type == 'where' : delim = ' AND '
            if clause_type == 'set' : delim = ', '
            vals = list(clause_data.values()) # str: "val1, val2 ..."
            expr = delim.join([f"{item}=?" for item in clause_data.keys()]) # str: "key1=? AND key2=?" or "key1=?, key2=?"
            return vals, expr






