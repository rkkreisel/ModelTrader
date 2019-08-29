import csv
import sys
import datetime

key = "longATR15:AATR1:AATRD:ACCI15:ILCCIA15:ILCCIA1h:ILCCIA1d:UBBW15:ABBb15:TBBW1h:ABBb1h:BBBW1d:HBBb1d:B"

csv_file = csv.reader(open('data\ccibb.csv', "rt"), delimiter=",")

for row in csv_file:
    #print(row[0])
    if key == row[0]:
        print(row)

teststr = "'teststr',"
test = teststr+"'test name'"
test += ",'test first'"
test += "1,100,1000, 100%"
print(test)
with open('employee_file.csv', mode='a') as employee_file:
    employee_writer = csv.writer(employee_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)

    employee_writer.writerow(['John Smith', 'Accounting', 'November'])
    employee_writer.writerow(['Erica Meyers', 'IT', 'March'])
    employee_writer.writerow([test])