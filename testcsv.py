import csv
import sys
import datetime

key = "shortATR15:AATR1:AATRD:ACCI15:OCCIA15:OCCIA1h:ILCCIA1d:ILBBW15:HBBb15:TBBW1h:ABBb1h:OBBW1d:HBBb1d:T"

csv_file = csv.reader(open('data/ccibb.csv', "rt"), delimiter=",")
for row in csv_file:
    #print(row[0])
    if key == row[0]:
        print("match: ",row[0])
        break
key = "longATR15:LATR1:AATRD:ACCI15:ILCCIA15:UCCIA1h:IUCCIA1d:O"
csv_file = csv.reader(open('data/cci.csv', "rt"), delimiter=",")
for row in csv_file:
    #print(row[0])
    if key == row[0]:
        print("match ***********************************************************************************: ",row[0])
        break




#with open('employee_file.csv', mode='a') as employee_file:
#    employee_writer = csv.writer(employee_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)

 #   employee_writer.writerow(['John Smith', 'Accounting', 'November'])
  #  employee_writer.writerow(['Erica Meyers', 'IT', 'March'])
   # employee_writer.writerow([test])
