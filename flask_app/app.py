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
<<<<<<< Updated upstream
@app.route('/login', methods=['GET', 'POST'])
def login():
=======

# @app.route('/login', methods=['GET', 'POST'])
# def login():
#     # For GET requests, just render the template
#     if request.method == 'GET':
#         return render_template('login.html', msg='')
    
#     # Only process login for actual POST requests with form data
#     msg = ''
#     if request.method == 'POST' and request.form.get('username') and request.form.get('password'):
#         username = request.form['username']
#         password = request.form['password']
        
#         try:
#             check_cursor = mydb.cursor()
#             check_cursor.execute('SELECT * FROM users WHERE username = %s', (username,))
#             username_present = check_cursor.fetchone()
#             check_cursor.close()
            
#             if username_present:
#                 check_cursor = mydb.cursor()
#                 check_cursor.execute('SELECT * FROM users WHERE username = %s AND password = %s', (username, password))
#                 pass_check = check_cursor.fetchone()
#                 check_cursor.close()
                
#                 if pass_check:
#                     return redirect(url_for('index'))
#                 else:
#                     msg = "Incorrect password!"
#             else:
#                 msg = "Username not found!"
                
#         except mysql.connector.Error as err:
#             msg = 'Database error occurred!'
#             mydb.rollback()
    
#     return render_template('login.html', msg=msg)

#new

@app.route('/login', methods=['GET', 'POST'])
def login():
    # For GET requests, render the login page
    if request.method == 'GET':
        return render_template('login.html', msg='')

    # For POST requests, process login data
>>>>>>> Stashed changes
    msg = ''
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')

        if not username or not password:
            msg = "Username and password are required!"
            return render_template('login.html', msg=msg)

        try:
<<<<<<< Updated upstream
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
=======
            # Use a single query to validate both username and password
            query = "SELECT user_id, username FROM users WHERE username = %s AND password = %s"
            mycursor = mydb.cursor(dictionary=True)  # Use dictionary cursor for better readability
            mycursor.execute(query, (username, password))
            user = mycursor.fetchone()
            mycursor.close()

            if user:
                # Save user session and redirect to the index page
                session['user_id'] = user['user_id']
                session['username'] = user['username']
                return redirect(url_for('index'))
>>>>>>> Stashed changes
            else:
                msg = "Invalid username or password!"

        except mysql.connector.Error as err:
            print("Database error:", err)
            msg = "An error occurred. Please try again later."

    return render_template('login.html', msg=msg)
<<<<<<< Updated upstream
=======


>>>>>>> Stashed changes
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
<<<<<<< Updated upstream
=======
    
@app.route('/group-list')
def group_list():
    if 'user_id' not in session:
        return redirect(url_for('login'))  # Redirect to login if not authenticated

    user_id = session['user_id']

    try:
        # Fetch group details where the user is associated
        query = """
        SELECT g.group_id, g.group_name 
        FROM groups g 
        JOIN user_groups ug ON g.group_id = ug.group_id 
        WHERE ug.user_id = %s
        """
        mycursor.execute(query, (user_id,))
        groups = mycursor.fetchall()

        return render_template('group_list.html', groups=groups)
    except Exception as e:
        print("Error in group_list:", str(e))
        print("Traceback:", traceback.format_exc())
        return "An error occurred loading the group list", 500

# @app.route('/group/<int:group_id>/invoices')
# def group_invoices(group_id):
#     if 'user_id' not in session:
#         return redirect(url_for('login'))  # Redirect to login if not authenticated

#     try:
#         # Fetch invoices related to the selected group_id
#         query = """
#         SELECT InvoiceID, OrderNumber, Date, Total, Tax
#         FROM Invoice
#         WHERE InvoiceID IN (
#             SELECT InvoiceID 
#             FROM user_groups
#             WHERE group_id = %s
#         )
#         """
#         mycursor = mydb.cursor(dictionary=True)
#         mycursor.execute(query, (group_id,))
#         invoices = mycursor.fetchall()
#         mycursor.close()

#         return render_template('invoices.html', invoices=invoices, group_id=group_id)
#     except Exception as e:
#         print("Error in group_invoices:", str(e))
#         print("Traceback:", traceback.format_exc())
#         return "An error occurred loading the invoices", 500

#new

@app.route('/group/<int:group_id>/invoices')
def group_invoices(group_id):
    if 'user_id' not in session:
        return redirect(url_for('login'))  # Redirect to login if not authenticated

    user_id = session['user_id']

    try:
        # Step 1: Fetch group details to ensure the group_id exists
        mycursor = mydb.cursor(dictionary=True)
        mycursor.execute("SELECT * FROM groups WHERE group_id = %s", (group_id,))
        group = mycursor.fetchone()

        if not group:
            return "Group not found", 404  # If the group does not exist in the groups table

        # Step 2: Fetch the user_group_id based on user_id and group_id
        mycursor.execute("""
            SELECT user_group_id
            FROM user_groups
            WHERE user_id = %s AND group_id = %s
        """, (user_id, group_id))
        user_group = mycursor.fetchone()

        if not user_group:
            return "User is not associated with this group", 403  # Unauthorized if user is not part of the group

        user_group_id = user_group['user_group_id']

        # Step 3: Fetch invoices related to the user_group_id
        mycursor.execute("""
            SELECT InvoiceID, OrderNumber, Date, Total, Tax
            FROM Invoice
            WHERE user_group_id = %s
        """, (user_group_id,))
        invoices = mycursor.fetchall()

        mycursor.close()

        return render_template('invoices.html', invoices=invoices, group_id=group_id)
    
    except Exception as e:
        print("Error in group_invoices:", str(e))
        print("Traceback:", traceback.format_exc())
        return "An error occurred loading the invoices", 500


# @app.route('/invoice/<int:invoice_id>/details')
# def invoice_details(invoice_id):
#     if 'user_id' not in session:
#         return redirect(url_for('login'))  # Redirect to login if not authenticated

#     try:
#         # Fetch details from InvoiceDetails table for the given InvoiceID
#         query = """
#         SELECT DetailID, ItemName, Quantity, Price 
#         FROM InvoiceDetails 
#         WHERE InvoiceID = %s
#         """
#         mycursor = mydb.cursor(dictionary=True)
#         mycursor.execute(query, (invoice_id,))
#         details = mycursor.fetchall()
#         mycursor.close()

#         return render_template('invoice_details.html', details=details, invoice_id=invoice_id)
#     except Exception as e:
#         print("Error in invoice_details:", str(e))
#         print("Traceback:", traceback.format_exc())
#         return "An error occurred loading the invoice details", 500

#new

@app.route('/invoice-details/<int:invoice_id>', methods=['GET'])
def invoice_details(invoice_id):
    if 'user_id' not in session:
        return redirect(url_for('login'))  # Redirect to login if not authenticated

    try:
        # Fetch invoice details related to the selected InvoiceID
        query = """
        SELECT ItemName, Quantity, Price
        FROM InvoiceDetails
        WHERE InvoiceID = %s
        """
        mycursor = mydb.cursor(dictionary=True)
        mycursor.execute(query, (invoice_id,))
        invoice_details = mycursor.fetchall()
        mycursor.close()

        # Render the details on a new page
        return render_template('invoice_details.html', invoice_details=invoice_details, invoice_id=invoice_id)
    except Exception as e:
        print("Error fetching invoice details:", str(e))
        return "An error occurred while fetching invoice details.", 500


>>>>>>> Stashed changes
