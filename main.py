import os
import psycopg2
import json
from decimal import Decimal
from operator import itemgetter
import urllib.parse as urlparse
import os
import requests
import csv

def print_ranking():
    conn = test_connection()

    print("Connected")

    #Create a scrollable, client-side cursor for 'responses' table
    main_cursor = conn.cursor()
    #Create another cursor for our stocks table query
    stocks_cursor = conn.cursor()
    stocks_cursor.execute("SELECT * FROM stocks")

    print("Executed")

    #dictionary to store stock price information
    stock_price_changes = []

    #Convert our stocks table in DB to dictionary with mappings <Week# (String), $change (float)>
    current_stock_tuple = stocks_cursor.fetchone()

    while(current_stock_tuple != None):
        stock_ticker = current_stock_tuple[1]
        buy_type = current_stock_tuple[2]
        buy_price = current_stock_tuple[3]

        #get stock price through worldtradingdata
        URL = "https://www.worldtradingdata.com/api/v1/stock?symbol="+stock_ticker+"&api_token=tjBiDeMFxKrXPt4sS5Kr5XCi2h2kVIG6JtzOXlakrSnICR7iRmjlyejoSd4B"
        req = requests.get(URL)
        stock_json = req.json()
        stock_data = stock_json['data']
        current_price = Decimal(stock_data[0]['price'])

        

        #change in percent of stock price
        percent_change = Decimal(((current_price-buy_price)/buy_price)*100)

        #if it is short, we want to reverse the sign of the change percent
        if buy_type == "SHORT":
            percent_change *= -1
        
        stock_price_changes.append(percent_change)

        #iterate to next stock
        current_stock_tuple = stocks_cursor.fetchone()

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
        for i in range(len(current_person_tuple)-3):
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

        #iterate to next person
        current_person_tuple = main_cursor.fetchone()

    rank_number = 1
    for name_perf_pair in sorted(performance_dict.items(), key=itemgetter(1), reverse=True):
        name = name_perf_pair[0]
        performance = name_perf_pair[1]

        #do something with those values
        return_string = str(rank_number) + ". " + name + ", " + str(performance) 
        rank_number+=1
        print(return_string)

    #commit and close connection
    conn.commit()
    main_cursor.close()
    stocks_cursor.close()
    conn.close()

def update_responses():
    conn = test_connection()
    main_cursor = conn.cursor()

    keep_going = True

    while keep_going:
        name = input("Enter a name: ").lower()
        week = "Stock" + input("Enter week number wish to update: ")
        response = input("Enter response: ")

        print("Changing " + name + "'s response for " + week + " to '"+response+"', is this correct?")
        confirm = input("Y/N?")
        if confirm in ['Y', 'y', 'yes', 'YES']:
            exec_string = "UPDATE responses SET " + week + " = %s WHERE PersonName=%s"
            main_cursor.execute(exec_string, (response, name))
            print("Updated")
        else:
            print("Did not update")

        print("Would you like to continue?")
        confirm_continue = input("Y/N?")
        if confirm_continue not in ['Y', 'y', 'yes', 'YES']:
            keep_going = False
    
    conn.commit()
    main_cursor.close()
    conn.close()


# def make_table():
#     conn = test_connection()

#     main_cursor = conn.cursor()

#     sql_string = "CREATE TABLE responses (PersonName varchar(255), "

#     for i in range(1, 11):
        
#         sql_string += "Stock"+str(i)+" varchar(10)"
#         if(i != 10):
#             sql_string +=  ", "

#     sql_string += ")"
    
#     main_cursor.execute(sql_string)

#     #commit and close session
#     conn.commit()
#     main_cursor.close()
#     conn.close()

#     print("Table created")
def make_table():
    conn = test_connection()

    main_cursor = conn.cursor()

    sql_string = "CREATE TABLE stocks (StockNumber varchar(10), Ticker varchar(15), Type varchar(10), BuyPrice DECIMAL(10, 2))"

    
    
    main_cursor.execute(sql_string)

    main_cursor.execute("INSERT INTO stocks VALUES('Stock1', 'VWDRY', 'LONG', 21.91)")
    main_cursor.execute("INSERT INTO stocks VALUES('Stock2', 'ARNC', 'LONG', 21.54)")
    main_cursor.execute("INSERT INTO stocks VALUES('Stock3', 'LEA', 'LONG', 135.06)")
    main_cursor.execute("INSERT INTO stocks VALUES('Stock4', 'ATHM', 'LONG', 68.89)")
    main_cursor.execute("INSERT INTO stocks VALUES('Stock5', 'ADMP', 'LONG', 2.87)")
    main_cursor.execute("INSERT INTO stocks VALUES('Stock6', 'ALCO', 'SHORT', 33.01)")
    main_cursor.execute("INSERT INTO stocks VALUES('Stock7', 'PPG', 'SHORT', 109.53)")
    main_cursor.execute("INSERT INTO stocks VALUES('Stock8', 'BLKB', 'LONG', 70.98)")
    


    #commit and close session
    conn.commit()
    main_cursor.close()
    conn.close()

    print("Table created")

def print_stocks_table():
    conn = test_connection()
    main_cursor = conn.cursor()

    main_cursor.execute("SELECT * FROM stocks")

    current_person_tuple = main_cursor.fetchone()

    while(current_person_tuple != None):
        print(current_person_tuple)
        current_person_tuple = main_cursor.fetchone()


def make_person():

    conn = test_connection()

    main_cursor = conn.cursor()

    name = str(input("Enter Name:"))

    main_cursor.execute("INSERT INTO responses VALUES (%s, 'None', 'None', 'None', 'None', 'None', 'None', 'None', 'None', 'None', 'None')", (name,))

    #commit and close session
    conn.commit()
    main_cursor.close()
    conn.close()

    print("Inserted " + name)

#Deletes an entire row, given a specific name
def delete_person():
    conn = test_connection()
    main_cursor = conn.cursor()

    name = str(input("Enter Name:")).lower()

    main_cursor.execute("DELETE FROM responses WHERE PersonName=%s", (name,))

    #commit and close session
    confirm = input("Warning: User data cannot be retrieved after deleting. Are you sure? (Y/N)")
    if confirm in ['Y', 'y', 'yes', 'YES', 'Yes']:
        conn.commit()
        print("Change saved")
    else:
        print("Change reverted")
    main_cursor.close()
    conn.close()

def print_table():
    conn = test_connection()
    main_cursor = conn.cursor()

    main_cursor.execute("SELECT * FROM responses")

    current_person_tuple = main_cursor.fetchone()

    while(current_person_tuple != None):
        print(current_person_tuple)
        current_person_tuple = main_cursor.fetchone()


#reads a response file and updates data accordingly
def read_file():
    conn = test_connection()
    main_cursor = conn.cursor()

    names = ["9-18-2018", "9-25-18", "10-9-18", "10-16-18", "10-23-18", "10-30-18", "11-6-18", "11-13-18"]
    num = 1

    for name in names:
        file_name = name
        week = "Stock" + str(num)
        num +=1
        in_file = open("./Response Sheets/"+file_name+".csv")
        csv_file = csv.reader(in_file, delimiter=",")

        line_count = 0
        
        for row in csv_file:
            if line_count == 0:
                line_count+=1
                continue
            
            email = row[2].lower()
            response = row[3]

            #check if this person already exists, if not, create new row
            main_cursor.execute("SELECT * FROM responses WHERE PersonName=%s", (email,))
            if main_cursor.fetchone() == None:
                main_cursor.execute("INSERT INTO responses VALUES (%s, 'None', 'None', 'None', 'None', 'None', 'None', 'None', 'None', 'None', 'None')", (email,))
                conn.commit()

            if response == "YES" or response == "NO" or response == "n/a":
                exec_string = "UPDATE responses SET " + week + " = %s WHERE PersonName=%s"
                main_cursor.execute(exec_string, (response, email))
                print("Added " + email +" as " + response)
                conn.commit()
            else:
                print("Response not yes, no, or n/a huh")

    conn.commit()
    main_cursor.close()
    conn.close()


def clear_table():
    conn = test_connection()
    main_cursor = conn.cursor()

    main_cursor.execute("DELETE FROM responses")
    main_cursor.execute("DROP TABLE stocks")

    conn.commit()
    main_cursor.close()
    conn.close()

def cross_ref():
    conn = test_connection()
    main_cursor = conn.cursor()
    
    in_file = open("./Response Sheets/signin.csv")
    csv_file = csv.reader(in_file, delimiter=",")

    for row in csv_file:
        email = row[3]
        

    


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
        return con
    except:
        print("Error connecting to DB")


if __name__ == '__main__':
    print("Welcome to USIT Trading")
    while True:
        print("Select from the following options:")
        print("0. Quit")
        print("1. Print Ranking")
        print("2. Update Response")
        print("3. Make Person")
        print("4. Test Connection")
        print("5. Make Table")
        print("6. Delete Person")
        print("7. Print Stocks Table")
        print("8. Print Responses Table")
        print("9. read file")
        print("10. clear table")
        user_input = input("Enter your option: ")
        while not user_input.isdigit():
            user_input = input("Enter a valid option: ")

        user_input = int(user_input)

        if user_input == 0:
            break
        elif user_input == 1:
            print_ranking()
        elif user_input == 2:
            update_responses()
        elif user_input == 3:
            make_person()
        elif user_input == 4:
            test_connection()
        elif user_input == 5:
            make_table()
        elif user_input == 6:
            delete_person()
        elif user_input == 7:
            print_stocks_table()
        elif user_input == 8:
            print_table()
        elif user_input == 9:
            read_file()
        elif user_input == 10:
            clear_table()
    print("Thanks for playing")





    

            
                
                






