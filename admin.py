import csv

file_name = input("enter file name (don't include .csv): ")
week = "Stock" + input("Enter week number wish to update: ")
in_file = open("./Response Sheets/"+file_name+".csv")
csv_file = csv.reader(in_file, delimiter=",")

line_count = 0
    
for row in csv_file:
        if line_count == 0:
                line_count+=1
                continue
        
        email = row[2]
        response = row[3]

        print("Email : " + email)
        print("response: " + response)
        print("----")