import re
import random

from app import app


@app.message(re.compile(r"^\b(hi|hello|hey|yo)\b$"))
def say_hello(message, say):
    """
    Reply hello.
    :param message: slack json/dict
    :param say: slack bolt send message func
    :return: None
    """
    greeting_lst = ['hello', 'hi', 'whats up', 'yo']
    greeting = random.choice(greeting_lst)
    user = message['user']
    say(f'{greeting} <@{user}>!✌')
