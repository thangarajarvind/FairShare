from flask import Flask, render_template, request, jsonify, session, url_for, redirect
import traceback
import mysql.connector
import re
from flaskext.mysql import MySQL
from flask_session import Session
from decimal import *

app = Flask(__name__)

mydb = mysql.connector.connect(
  host = "localhost",
  user = "root",
  password = "",
  database = "InvoiceDB"
)
app.config['SECRET_KEY'] = 'FairShare'
app.config['SESSION_TYPE'] = 'filesystem'
app.config.from_object(__name__)
Session(app)
mycursor = mydb.cursor()

@app.route('/register', methods =['GET', 'POST'])
def register():
    msg = ''  
    print(f"Request method: {request.method}") 
    
    if request.method == 'POST':
        if 'username' in request.form and 'password' in request.form and 'email' in request.form:
            username = request.form['username']
            password = request.form['password']
            email = request.form['email']
            
            try:
                check_cursor = mydb.cursor()
                check_cursor.execute('SELECT * FROM users WHERE username = %s', (username,))
                username_check = check_cursor.fetchone()
                check_cursor.close()
                print(f"Username check result: {username_check}") 
                
                if username_check:
                    msg = 'Username already exists !'
                else:
                    check_cursor = mydb.cursor()
                    check_cursor.execute('SELECT * FROM users WHERE email = %s', (email,))
                    email_check = check_cursor.fetchone()
                    check_cursor.close()
                    print(f"Email check result: {email_check}") 
                    
                    if email_check:
                        msg = 'Email already exists!'
                    elif not re.match(r'[^@]+@[^@]+\.[^@]+', email):
                        msg = 'Invalid email address!'
                    elif not re.match(r'[A-Za-z0-9]+', username):
                        msg = 'Username must contain only characters and numbers!'
                    elif not username or not password or not email:
                        msg = 'Please fill out the form!'
                    else:
                        insert_cursor = mydb.cursor()
                        insert_cursor.execute('INSERT INTO users (username, email, password) VALUES (%s, %s, %s)', 
                                            (username, email, password))
                        mydb.commit()
                        insert_cursor.close()
                        msg = 'You have successfully registered !'
                
            except mysql.connector.Error as err:
                print(f"Database error: {err}")
                msg = 'Database error occurred!'
                mydb.rollback()
                
    else: 
        msg = ''  
        
    print(f"Final message: {msg}") 
    return render_template('register.html', msg = msg)
@app.route('/login', methods=['GET', 'POST'])
def login():
    msg = ''
    if request.method == 'POST' and request.form.get('username') and request.form.get('password'):
        username = request.form['username']
        password = request.form['password']
        
        try:
            check_cursor = mydb.cursor()
            check_cursor.execute('SELECT * FROM users WHERE username = %s', (username,))
            username_present = check_cursor.fetchone()
            check_cursor.close()
            
            if username_present:
                check_cursor = mydb.cursor()
                check_cursor.execute('SELECT * FROM users WHERE username = %s AND password = %s', (username, password))
                pass_check = check_cursor.fetchone()
                check_cursor.close()
                
                if pass_check:
                    session['user_id'] = pass_check[0]
                    return redirect(url_for('index'))
                else:
                    msg = "Incorrect password!"
            else:
                msg = "Username not found!"
                
        except mysql.connector.Error as err:
            msg = 'Database error occurred!'
            mydb.rollback()
    
    return render_template('login.html', msg=msg)
@app.route('/')
def index():
    user_id = session.get('user_id')
    if not user_id:
        return redirect(url_for('login')) 
    
    # Fetch the invoices and invoice details relevant to the logged-in user
    # mycursor.execute("""
    #     SELECT * FROM InvoiceDetails
    #     WHERE InvoiceID IN (
    #         SELECT InvoiceID FROM user_groups WHERE user_id = %s
    #     )
    # """, (user_id,))
    
    mycursor.execute("Select * from InvoiceDetails where InvoiceID='140'")
    data = mycursor.fetchall()

    # mycursor.execute("""
    #     SELECT * FROM Invoice
    #     WHERE InvoiceID IN (
    #         SELECT InvoiceID FROM user_groups WHERE user_id = %s
    #     )
    # """, (user_id,))
    meta_data = mycursor.fetchall()

    mycursor.execute("SELECT user_id FROM user_groups where group_id='2'")
    user_id_list = mycursor.fetchall()

    user_name_list = []
    for i in user_id_list:
        mycursor.execute("SELECT username FROM users where user_id='"+str(i[0])+"'")
        user_name = mycursor.fetchall()
        user_name_list.append(user_name[0][0])

    headers = ("", "Item name", "Quantity", "Price")
    
    return render_template('display_table.html', title='FairShare', headings=headers, data=data, meta_data=meta_data, group_data = user_name_list)

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
    user_id = session.get('user_id')
    if not user_id:
        return redirect(url_for('login'))
    
    try:
        bill_data = session.get('bill_data', {})

        mycursor.execute("""
            SELECT * FROM Invoice
            WHERE InvoiceID IN (
                SELECT InvoiceID FROM user_groups WHERE user_id = %s
            )
        """, (user_id,))
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
    
@app.route('/group-list')
def group_list():
    mycursor.execute("SELECT group_id FROM user_groups WHERE user_id = '1'")
    group_list = mycursor.fetchall()

    parsed_group = []
    for i in group_list:
        parsed_group.append(i[0])
    return render_template('group_list.html',blocks = parsed_group)

@app.route('/confirm-splits', methods=['POST'])
def confirm_splits():
    try:
        # Get bill data from session
        bill_data = session.get('bill_data', {})
        if not bill_data:
            return jsonify({
                'success': False,
                'error': 'No bill data found in session'
            }), 400

        cursor = mydb.cursor()
        
        try:
            # Start transaction
            mydb.start_transaction()
            
            # Process each item and its splits
            for item in bill_data['items']:
                detail_id = item['detailID']
                
                # First delete any existing splits for this item
                cursor.execute(
                    'DELETE FROM user_item_splits WHERE DetailID = %s',
                    (detail_id,)
                )
                
                # Insert new splits
                for split in item['splits']:
                    username = split['userId']
                    mycursor.execute("SELECT user_id FROM users where username='"+username+"'")
                    user_id = mycursor.fetchall()
                    user = user_id[0][0]
                    cursor.execute('''
                        INSERT INTO user_item_splits 
                        (DetailID, user_id, split_amount)
                        VALUES (%s, %s, %s)
                    ''', (
                        detail_id,
                        str(user),
                        Decimal(str(split['splitAmount']))
                    ))
            
            # Commit transaction
            mydb.commit()
            
            # Clear the bill data from session
            session.pop('bill_data', None)
            
            return jsonify({
                'success': True,
                'message': 'Splits confirmed successfully'
            })
            
        except mysql.connector.Error as err:
            # Rollback in case of error
            mydb.rollback()
            print(f"Database error: {err}")
            return jsonify({
                'success': False,
                'error': f"Database error: {str(err)}"
            }), 500
            
        finally:
            cursor.close()
            
    except Exception as e:
        print(f"Error in confirm_splits: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500
