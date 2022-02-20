import sqlite3
from sqlite3 import Error
from typing import Optional
from settings import DB_NAME


def create_connection(db_file) -> Optional[sqlite3.Connection]:
    try:
        conn = sqlite3.connect(db_file)
    except Error as e:
        conn = None
    return conn

def create_table(conn, create_table_query) -> None:
        cur = conn.cursor()
        cur.execute(create_table_query)

query_create_user_table = """ CREATE TABLE IF NOT EXISTS user (
                                chat_id INTEGER PRIMARY KEY,
                                state_id INTEGER,
                                state_data VARCHAR
                                );"""

query_create_person_table = """ CREATE TABLE IF NOT EXISTS person (
                                    pers_name VARCHAR,
                                    pers_bday VARCHAR,
                                    chat_id INTEGER
                                    );"""

conn = create_connection(DB_NAME)

if conn is not None:
    create_table(conn, query_create_user_table)
    create_table(conn, query_create_person_table)
    conn.close()
