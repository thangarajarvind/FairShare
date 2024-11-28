from flask import Flask, render_template
import mysql.connector

app = Flask(__name__)

headers = ("","Item name", "Quantity", "Price")


mydb = mysql.connector.connect(
  host = "localhost",
  user = "root",
  password = "",
  database = "InvoiceDB"
)

mycursor = mydb.cursor()

@app.route('/')
def index():
    mycursor.execute("SELECT * FROM InvoiceDetails where InvoiceID='140'")
    data = mycursor.fetchall()

    mycursor.execute("SELECT * FROM Invoice where InvoiceID='140'")
    meta_data = mycursor.fetchall()

    return render_template('display_table.html', title='FairShare', headings = headers, data = data, meta_data = meta_data)