from datetime import datetime as dt
import json
from SQLtools import SQLtools
import re
from settings import URL, APP_PATH, DB_NAME, log_msg, StateId
from typing import Tuple
from flask import Flask, request
import requests

sql = SQLtools(db_name=DB_NAME, callback_func=log_msg)

app = Flask(__name__)


@app.route(APP_PATH, methods=["POST"])
def workflow() -> None:

    update = request.json

    err_msg, is_valid = validate_update(update)
    if not is_valid:
        return err_msg

    msg = update["message"]
    text = msg["text"]
    chat_id = msg["chat"]["id"]

    if text == "/add":
        sql.replace(
            table="user",
            data={"chat_id": chat_id, "state_id": StateId.ADD_ADDMSG.value},
        )
        add_person(chat_id, text)

    elif text == "/delete":
        sql.replace(
            table="user",
            data={"chat_id": chat_id, "state_id": StateId.DEL_DELMSG.value},
        )
        delete_person(chat_id, text)

    elif text == "/month":
        sql.replace(table="user", data={"chat_id": chat_id})
        show_birthdays_of_this_month(chat_id)

    elif text in ("/list", "/all"):
        sql.replace(table="user", data={"chat_id": chat_id})
        show_all_birhdays(chat_id)

    elif text == "/help":
        sql.replace(table="user", data={"chat_id": chat_id})
        msg = "Hello, I am a Birthday bot! \nI can help you to keep track of your friends birthdays. \nJust tell me the dates and I will notify you once it's time to congratulate ;) \nCommand list: \n/add - add a person \n/delete - delete a person \n/month - show birthdays of this month \n/list or /all - show all the people you've added"
        send_msg(chat_id, msg)

    else:
        user = sql.select_one(table="user", where={"chat_id": chat_id})
        if not user:
            show_start_msg(chat_id)

        elif user["state_id"] in StateId.ADD.value:  # /add process is in progress
            add_person(chat_id, text)

        elif user["state_id"] in StateId.DELETE.value:  # /delete process is in progress
            delete_person(chat_id, text)

        else:
            show_start_msg(chat_id)

    return 'RECEIVED A POST REQUEST'

    
def add_person(chat_id: str, text: str) -> None:

    log_msg("ADD PROCESS HAS STARTED")
    state_id = sql.select_one(table="user", where={"chat_id": chat_id})["state_id"]
    log_msg(f"state id is {state_id}")

    if state_id == StateId.ADD_ADDMSG.value:  # add message has come

        # Increment state_id and send a message with result
        sql.update(
            table="user",
            set={"state_id": StateId.ADD_PERSNAME.value},
            where={"chat_id": chat_id},
        )
        send_msg(chat_id, "Enter a person name")

    elif state_id == StateId.ADD_PERSNAME.value:  # pers_name has come

        # Validate the input
        if not istext(text):
            send_msg(chat_id, "Name should contain only letters or numbers")
            return

        # Insert the input to the cache, increment state_id and send a message with result
        state_data = {"pers_name": text}
        sql.update(
            table="user",
            set={
                "state_id": StateId.ADD_PERSBDAY.value,
                "state_data": json.dumps(state_data),
            },
            where={"chat_id": chat_id},
        )
        send_msg(
            chat_id, f"OK, now enter {state_data['pers_name']}'s birthday (YYYY-MM-DD)"
        )

    elif state_id == StateId.ADD_PERSBDAY.value:  # pers_bday has come

        # Validate the input
        if not isdate(text):
            send_msg(chat_id, "Enter a date in YYYY-MM-DD format")
            return
        if not ispast(text):
            send_msg(chat_id, "The date should be earlier than today")
            return

        # Convert the date
        date_obj = dt.strptime(text, "%Y-%m-%d")  # parse input to a date obj
        date_frnd = date_obj.strftime("%d %b %Y")  # DD Mon YYYY string
        date_sql = date_obj.strftime("%Y-%m-%d")  # YYYY-MM-DD string DD

        state_data = get_state_data(chat_id)
        state_data.update({"pers_bday": date_sql, "chat_id": chat_id})

        # Insert data to person table
        sql.insert(table="person", data=state_data)

        # Delete cache and send final message
        sql.replace(table="user", data={"chat_id": chat_id})
        send_msg(chat_id, f"{state_data['pers_name']}, born {date_frnd} has been added")
    else:
        sql.replace(table="user", data={"chat_id": chat_id})
        show_start_msg(chat_id)


def delete_person(chat_id: str, text: str) -> None:

    log_msg("DELETE PROCESS HAS STARTED")
    state_id = sql.select_one(table="user", where={"chat_id": chat_id})["state_id"]
    log_msg(f"step id is {state_id}")

    if state_id == StateId.DEL_DELMSG.value:  # delete message has come

        # Create lists of people added by current user
        people_list = sql.select_all(
            table="person",
            where={"chat_id": chat_id},
            columns=["rowid as pers_id", "*"],
        )  # [{pers_name, pers_bday, chat_id, pers_id}, ...]

        if len(people_list) == 0:  # there is no one in the list
            sql.replace(table="user", data={"chat_id": chat_id})
            send_msg(chat_id, "There is no one to delete")
            show_start_msg(chat_id)
            return

        # Populate the list with extra attribute
        for number, person in enumerate(people_list):
            person["ord_num"] = number + 1

        # The list formatted as string for telegram message
        list_to_show = "\n".join(
            [
                f"{item['ord_num']} {item['pers_name']} {item['pers_bday']}"
                for item in people_list
            ]
        )

        # Incremente state_id and send a message with result
        sql.update(
            table="user",
            set={
                "state_id": StateId.DEL_ORDNUM.value,
                "state_data": json.dumps(people_list),
            },
            where={"chat_id": chat_id},
        )
        send_msg(
            chat_id, f"Enter a number of a person you want to delete:\n{list_to_show}"
        )

    elif state_id == StateId.DEL_ORDNUM.value:  # Number of person to delete has come

        # Check if input is integer
        if not text.isdigit():
            send_msg(chat_id, "Enter a number")
            return
        input_num = int(text)

        state_data = get_state_data(chat_id)

        # Check if input number presents in one of ordinal numbers generated in previous step
        is_number_present = False
        for item in state_data:
            if item["ord_num"] == input_num:
                person_to_delete, is_number_present = item, True
                break

        if not is_number_present:
            send_msg(chat_id, "Wrong number, send /delete to get a list")
            return

        # Delete target person from person table
        sql.delete(table="person", where={"rowid": person_to_delete["pers_id"]})

        # Delete cache and send final message
        sql.replace(table="user", data={"chat_id": chat_id})
        send_msg(
            chat_id,
            f"{person_to_delete['pers_name']} born {person_to_delete['pers_bday']} has been deleted",
        )
    else:
        sql.replace(table="user", data={"chat_id": chat_id})
        show_start_msg(chat_id)


def show_birthdays_of_this_month(chat_id: str) -> None:
    log_msg("MONTH PROCESS HAS STARTED")
    month = dt.now().strftime("%m")
    result = sql.select_all(
        table="person", where={"chat_id": chat_id, "STRFTIME('%m', pers_bday)": month}
    )
    if len(result) == 0:
        send_msg(chat_id, "You didn't add anybody yet")
    else:
        msg = "\n".join([f"{item['pers_name']} {item['pers_bday']}" for item in result])
        send_msg(chat_id, msg)


def show_all_birhdays(chat_id: str) -> None:
    log_msg("LIST ALL PROCESS HAS STARTED")
    result = sql.select_all(table="person", where={"chat_id": chat_id})
    if len(result) == 0:
        send_msg(chat_id, "You didn't add anybody yet")
    else:
        msg = "\n".join([f"{item['pers_name']} {item['pers_bday']}" for item in result])
        send_msg(chat_id, msg)


def show_start_msg(chat_id: str) -> None:
    log_msg("START_MSG PROCESS HAS STARTED")
    msg = "Command list: \n/add - add a person \n/delete - delete a person \n/month - show birthdays of this month \n/list or /all - show all the people you've added"
    send_msg(chat_id, msg)


def send_msg(chat_id: str, msg: str) -> None:
    url = URL + 'sendMessage'
    debug_msg = f"chat_id is: {chat_id}, msg is: {msg}"
    tg_msg = f"{msg}"
    resp = requests.post(url, data={'chat_id':chat_id, 'text':tg_msg, 'parse_mode':'HTML'}).json()
    log_msg(f">>> Telegram response: {resp}")
    log_msg(f">>> Debug message: {debug_msg}")


def get_state_data(chat_id: str) -> dict:
    state_data_str = sql.select_one(table="user", where={"chat_id": chat_id})[
        "state_data"
    ]
    return json.loads(state_data_str)


def isdate(date_text: str) -> bool:
    try:
        dt.strptime(date_text, "%Y-%m-%d")
    except ValueError:
        # raise ValueError("Incorrect data format, should be YYYY-MM-DD")
        return False
    else:
        return True


def ispast(date_text: str) -> bool:
    return dt.strptime(date_text, "%Y-%m-%d") < dt.today()


def istext(text: str) -> bool:
    """Returns True if text consists only of letters and numbers"""
    p = re.compile(r"[\w+ ]+")
    m = re.fullmatch(p, text)
    if m:
        return True
    else:
        return False


def validate_update(update: dict) -> Tuple[str, bool]:
    if "message" not in update:
        return "No message key", False
    msg = update["message"]
    if "text" not in msg:
        return "No text key", False
    if "chat" not in msg:
        return "No chat key", False
    if "id" not in msg["chat"]:
        return "No id key in chat", False
    return None, True


if __name__ == "__main__":
    app.run()
