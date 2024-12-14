import pandas as pd
from nltk.tokenize import word_tokenize
from pypdf import PdfReader
import re
import mysql.connector
from datetime import datetime

# Initialize reader and datasets
reader = PdfReader("uploads/reciept.pdf")
product_data = pd.DataFrame(columns=["Product_Name", "Qnt", "Price"])
totals_data = {"Subtotal": None, "Savings": None, "Tax": None, "Total": None}
meta_data = {"Date": None, "Order_Number": None}

# Helper function to extract product details
def extract_details(line):
    # Match the price format
    price_match = re.search(r"\$\d+(\.\d+)?", line)
    price = price_match.group(0) if price_match else "Unknown"
    # Match quantity (number before the price)
    qnt_match = re.search(r"(\d+)\s+\$", line)
    qnt = qnt_match.group(1) if qnt_match else "1"
    return price, qnt

def clean_product_name(buffer):
    # Extract product name and description up to the last numeric value before quantity or price
    match = re.search(r"^(.*?)(?:(?:Weight-adjustedQty|ShoppedQty|Qty|$))", buffer)
    if match:
        name = match.group(1).strip()
        return name
    return buffer.strip()

# Parsing logic
buffer = ""
processing_products = True

for j, page in enumerate(reader.pages):
    text = page.extract_text()
    for i, line in enumerate(text.splitlines()):
        if j == 0 and i < 1:
            continue  # Skip header for page 0
        elif j > 0 and i < 1:
            continue  # Skip header for other pages
        line = line.strip()
        if not line or "http" in line or "Order details" in line:
            continue  # Skip headers and irrelevant lines

        # Detect and stop product processing when totals start
        if "Subtotal" in line:
            processing_products = False
            totals_data["Subtotal"] = line.split("$")[-1].strip()
            continue
            
        if "Order#" in line:
            order_match = re.search(r'Order#\s*(\d+-?\d*)', line)
            if order_match:
                meta_data["Order_Number"] = order_match.group(1)
            continue
            
        # Extract date
        date_match = re.search(r'([A-Za-z]{3}\s+\d{1,2},\s+\d{4})', line)
        if date_match:
            meta_data["Date"] = date_match.group(1)

        if not processing_products:
            # Extract totals
            if "Savings" in line:
                totals_data["Savings"] = line.split("$")[-1].strip()
            elif "Tax" in line:
                totals_data["Tax"] = line.split("$")[-1].strip()
            elif "Total" in line:
                totals_data["Total"] = line.split("$")[-1].strip()
            continue

        # Accumulate lines for multi-line product descriptions
        if re.search(r"\$\d+(\.\d+)?", line):
            buffer += " " + line
            price, qnt = extract_details(buffer)
            item_name = clean_product_name(buffer)
            product_data = pd.concat(
                [product_data, pd.DataFrame([[item_name, qnt, price]], columns=product_data.columns)],
                ignore_index=True,
            )
            buffer = ""
        else:
            buffer += " " + line

# Ensure the last buffered product is processed
if buffer:
    price, qnt = extract_details(buffer)
    item_name = clean_product_name(buffer)
    product_data = pd.concat(
        [product_data, pd.DataFrame([[item_name, qnt, price]], columns=product_data.columns)],
        ignore_index=True,
    )

# Ensure that totals and meta data are correct
print("\nTotals Data:")
print(totals_data)
print("\nMeta Data:")
print(meta_data)

receipt_date = meta_data["Date"]
order_number = meta_data["Order_Number"]
tax = totals_data["Tax"]
sub_total = totals_data["Subtotal"]

mydb = mysql.connector.connect(
  host="localhost",
  user="root",
  password="",
  database="InvoiceDB"
)

mycursor = mydb.cursor()

def mdy_to_ymd(d):
    return datetime.strptime(d, '%b %d, %Y').strftime('%Y-%m-%d')

receipt_date = mdy_to_ymd(receipt_date)

# Check if OrderNumber already exists
sql = "SELECT COUNT(*) FROM Invoice WHERE OrderNumber = %s"
mycursor.execute(sql, (order_number,))
existing_count = mycursor.fetchone()[0]

if existing_count == 0:  # If the OrderNumber doesn't exist, insert it
    sql = "INSERT INTO Invoice (OrderNumber, Date, Total, Tax) VALUES (%s, %s, %s, %s)"
    val = (order_number, receipt_date, sub_total, tax)
    mycursor.execute(sql, val)

    # Get the InvoiceID after insertion
    sql = "SELECT InvoiceID FROM Invoice WHERE OrderNumber = %s"
    mycursor.execute(sql, (order_number,))
    myresult = mycursor.fetchall()
    for x in myresult:
        invoice_id = x[0]
else:
    # If the OrderNumber exists, fetch the existing InvoiceID
    sql = "SELECT InvoiceID FROM Invoice WHERE OrderNumber = %s"
    mycursor.execute(sql, (order_number,))
    myresult = mycursor.fetchall()
    for x in myresult:
        invoice_id = x[0]

# Insert product details into InvoiceDetails
for i in range(len(product_data.index)):
    item_name = product_data['Product_Name'].iloc[i]
    qnt = product_data['Qnt'].iloc[i]
    price = product_data['Price'].iloc[i][1:]  # Removing the dollar sign

    # Validate if price is a valid number
    if price.lower() == "unknown" or not re.match(r"^\d+(\.\d+)?$", price):
        price = "0.0"  # or you can choose to skip this product if preferred

    sql = "INSERT INTO InvoiceDetails (InvoiceID, ItemName, Quantity, Price) VALUES (%s, %s, %s, %s)"
    val = (invoice_id, item_name, qnt, price)
    print(invoice_id, item_name, qnt, price)

    mycursor.execute(sql, val)

mydb.commit()

print(mycursor.rowcount, "record inserted.")
print(product_data)
