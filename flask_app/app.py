from flask import Flask, render_template, request, jsonify, session, url_for
import traceback
import mysql.connector

app = Flask(__name__)

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

    headers = ("","Item name", "Quantity", "Price")

    return render_template('display_table.html', title='FairShare', headings = headers, data = data, meta_data = meta_data)

@app.route('/api/bills/store', methods=['POST'])
def receive_api_data():
    try:
        print("Received request data:", request.get_data())
        
        data = request.get_json()
        if not data:
            print("No JSON data received")
            return jsonify({
                'success': False,
                'error': 'No data received'
            }), 400

        print("Parsed JSON data:", data)
        
        user_splits = {}
        for item in data['items']:
            for split in item['splits']:
                user_id = split['userId']
                if user_id not in user_splits:
                    user_splits[user_id] = 0
                user_splits[user_id] += split['splitAmount']
        
        splits_list = [(user, amount) for user, amount in user_splits.items()]
        
        session['bill_data'] = {
            'items': data['items'],
            'splits': splits_list
        }
        
        return jsonify({
            'success': True,
            'redirect_url': url_for('bill_summary')
        })
        
    except Exception as e:
        print("Error in receive_api_data:", str(e))
        print("Traceback:", traceback.format_exc())
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

app.secret_key = 'FairShare'

@app.route('/bill-summary')
def bill_summary():
    try:
        # Get bill data from session
        bill_data = session.get('bill_data', {})
        
        # Fetch original invoice data
        mycursor.execute("SELECT * FROM Invoice WHERE InvoiceID = '140'")
        invoice_data = mycursor.fetchall()
        
        return render_template('bill_summary.html',
                             splits=bill_data.get('splits', []),
                             items=bill_data.get('items', []),
                             invoice=invoice_data[0],
                             title='Bill Summary')
    except Exception as e:
        print("Error in bill_summary:", str(e))
        print("Traceback:", traceback.format_exc())
        return "An error occurred loading the summary", 500