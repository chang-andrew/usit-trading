import os
import psycopg2
import json
from googlefinance import getQuotes
from decimal import Decimal
from operator import itemgetter
import urllib.parse as urlparse
import os

def get_connection():
    try:
        url = urlparse.urlparse(os.environ['DATABASE_URL'])
        dbname = url.path[1:]
        user = url.username
        password = url.password
        host = url.hostname
        port = url.port

        con = psycopg2.connect(
                    dbname=dbname,
                    user=user,
                    password=password,
                    host=host,
                    port=port
                    )
        print("Successfully connected")
        return con
    except:
        print("Error connecting to DB")


def print_table():
    conn = get_connection()
    main_cursor = conn.cursor()

    main_cursor.execute("SELECT * FROM responses")

    current_person_tuple = main_cursor.fetchone()

    while(current_person_tuple != None):
        print(current_person_tuple)
        current_person_tuple = main_cursor.fetchone()

