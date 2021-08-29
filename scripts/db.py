import os
import sqlite3

from scripts.initial_values import *


def create_db():
    db_filename = 'slack.db'

    db_is_new = not os.path.exists(db_filename)

    with sqlite3.connect(db_filename) as conn:
        if db_is_new:
            c = conn.cursor()
            # create initial table schema
            c.execute("""CREATE TABLE employees (
            name text
            slack_id text
            )""")
            conn.commit()
