import mysql.connector
from datetime import datetime

mydb = mysql.connector.connect(
  host = "localhost",
  user = "root",
  password = "",
  database = "InvoiceDB"
)

mycursor = mydb.cursor()

def mdy_to_ymd(d):
    return datetime.strptime(d, '%b %d, %Y').strftime('%Y-%m-%d')

receipt_date = mdy_to_ymd('Nov 19, 2024')

sql = "INSERT INTO Invoice (OrderNumber, Date, Total, Tax) VALUES (%s, %s, %s, %s)"
val = ("14", receipt_date, "123", "12")
mycursor.execute(sql, val)

mydb.commit()

print(mycursor.rowcount, "record inserted.")

def mdy_to_ymd(d):
    return datetime.strptime(d, '%b %d, %Y').strftime('%Y-%m-%d')
