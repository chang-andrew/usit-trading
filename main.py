import os
import psycopg2
import json
from googlefinance import getQuotes
from decimal import Decimal
from operator import itemgetter
import urllib.parse as urlparse
import os

def print_ranking():
    DATABASE_URL = os.environ['DATABASE_URL']

    conn = psycopg2.connect(DATABASE_URL, sslmode='require')

    #Create a scrollable, client-side cursor for 'responses' table
    main_cursor = conn.cursor(None, None, True, False)
    #Create another cursor for our stocks table query
    stocks_cursor = conn.cursor(None, None, True, False)
    stocks_cursor.execute("SELECT * FROM stocks")

    #dictionary to store stock price information
    stock_price_changes = []

    #Convert our stocks table in DB to dictionary with mappings <Week# (String), $change (float)>
    current_stock_tuple = stocks_cursor.fetchone

    while(current_stock_tuple != None):
        stock_ticker = current_stock_tuple[1]
        buy_type = current_stock_tuple[2]
        buy_price = current_stock_tuple[3]

        #get the stock information from googlefinance, returns a json
        stock_quote_json = getQuotes(stock_ticker)

        #access price field from json
        current_price = float(stock_quote_json['LastTradePrice'])

        #change in percent of stock price
        percent_change = Decimal(((current_price-buy_price)/buy_price)*100)

        #if it is short, we want to reverse the sign of the change percent
        if buy_type == "SHORT":
            percent_change *= -1
        
        stock_price_changes.append(percent_change)


        


    #select all rows in the 'responses' table   
    main_cursor.execute("SELECT * FROM responses")

    #this is the dictionary we will use to store mappings of "name" : int($amount)
    performance_dict = {}

    #loop through every row in the table
    current_person_tuple = main_cursor.fetchone()

    #for each row/person, we want to...
    while(current_person_tuple != None):
        
        sum_percent = 100

        #loop over each one of their responses for each week/stock
        #start from the 1st index element since 0 is the ID
        for i in range(len(current_person_tuple)-1):
            #get the string response (Y/N/No position)
            response = current_person_tuple[i+1]
            #get that weeks stock price change
            cur_week_stock = stock_price_changes[i]
            if(response == "YES"):
                sum_percent += cur_week_stock
            elif(response == "NO"):
                sum_percent -= cur_week_stock

        #map their total money to their name
        name = current_person_tuple[0]
        performance_dict[name] = sum_percent

    rank_number = 1
    for name_perf_pair in sorted(performance_dict.items(), key=itemgetter(1)):
        name = name_perf_pair[0]
        performance = name_perf_pair[1]

        #do something with those values
        return_string = str(rank_number) + ". " + name + " :: " + str(performance) 
        print(return_string)



def update_responses():
    pass


def make_table():
    DATABASE_URL = os.environ['DATABASE_URL']

    conn = psycopg2.connect(DATABASE_URL, sslmode='require')

    main_cursor = conn.cursor()

    sql_string = "CREATE TABLE responses (PersonName varchar(255), "

    for i in range(1, 10):
        
        sql_string += "Stock"+str(i)+" varchar(10)"
        if(i != 10):
            sql_string +=  ", "

    sql_string += ")"
    
    main_cursor.execute(sql_string)

    print("Table created")


def make_person():
    DATABASE_URL = os.environ['DATABASE_URL']

    conn = psycopg2.connect(DATABASE_URL, sslmode='require')

    main_cursor = conn.cursor()

    name = str(input("Enter Name:"))

    main_cursor.execute("INSERT INTO responses (PersonName) VALUES (%s)", (name,))

    print("Inserted " + name)


def test_connection():
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
    except:
        print("Error connecting to DB")


    





    

            
                
                






