import sqlite3
from sqlite3 import Error
from typing import Optional

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
                                    user_id INTEGER,
                                    FOREIGN KEY (user_id) REFERENCES user (chat_id) ON DELETE CASCADE
                                    );"""

conn = create_connection("db1.sqlite3")

if conn is not None:
    create_table(conn, query_create_user_table)
    create_table(conn, query_create_person_table)
    conn.close()
