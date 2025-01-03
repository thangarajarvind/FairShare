from flask import Flask, render_template, request, jsonify, session, url_for, redirect
import traceback
import mysql.connector
import re
import subprocess
import os
import pdfplumber

from datetime import datetime
from flaskext.mysql import MySQL
from flask_session import Session
from decimal import *
import random
import string

from werkzeug.utils import secure_filename
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
                        msg = 'Email already exists !'
                    elif not re.match(r'[^@]+@[^@]+\.[^@]+', email):
                        msg = 'Invalid email address !'
                    elif not re.match(r'[A-Za-z0-9]+', username):
                        msg = 'Username must contain only characters and numbers !'
                    elif not username or not password or not email:
                        msg = 'Please fill out the form !'
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
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')

        if not username or not password:
            msg = "Username and password are required!"
            return render_template('login.html', msg=msg)

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
                msg = "Invalid username or password!"

        except mysql.connector.Error as err:
            print("Database error:", err)
            msg = "An error occurred. Please try again later."

    return render_template('login.html', msg=msg)


@app.route('/split-page')
def split():
    user_id = session.get('user_id')
    if not user_id:
        return redirect(url_for('login')) 
    
    #Fetch the invoices and invoice details relevant to the logged-in user
    # mycursor.execute("""
    #     SELECT * FROM InvoiceDetails
    #     WHERE InvoiceID IN (
    #         SELECT InvoiceID FROM user_groups WHERE user_id = %s
    #     )
    # """, (user_id,))
    
    mycursor.execute("Select * from InvoiceDetails where InvoiceID='140'")

@app.route('/')
def invoice():
   
    invoice_id = request.args.get('invoice_id', type=int) 

    # Execute the query using the dynamic invoice_id
    mycursor.execute("SELECT * FROM InvoiceDetails where InvoiceID = %s", (invoice_id,))
    data = mycursor.fetchall()

    # mycursor.execute("""
    #     SELECT * FROM Invoice
    #     WHERE InvoiceID IN (
    #         SELECT InvoiceID FROM user_groups WHERE user_id = %s
    #     )
    # """, (user_id,))
    mycursor.execute("Select * from Invoice where InvoiceID = %s", (invoice_id,))
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

#new
@app.route('/homepage')
def homepage():
    return render_template('index.html')

@app.route('/')
def index():
    user_id = session.get('user_id')
    if not user_id:
        return redirect(url_for('login')) 
    
    try:
        # Fetch groups associated with the logged-in user
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
        print("Error fetching groups:", str(e))
        return "An error occurred loading the groups", 500


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
        
        group_code = group.get('code')

        # Step 2: Fetch the user_group_id based on user_id and group_id
        mycursor.execute("""
            SELECT user_group_id
            FROM user_groups
            WHERE user_id = %s AND group_id = %s
        """, (user_id, group_id))
        user_group = mycursor.fetchone()

        if not user_group:
            return "User is not associated with this group", 403  # Unauthorized if user is not part of the group

        # Step 3: Fetch all invoices related to the group_id
        mycursor.execute("""
            SELECT InvoiceID, OrderNumber, Date, Total, Tax
            FROM Invoice
            WHERE group_id = %s
        """, (group_id,))
        invoices = mycursor.fetchall()

        mycursor.close()

        return render_template('invoices.html', invoices=invoices, group_id=group_id, group_code=group_code)
    
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

# @app.route('/split-summary/<int:invoice_id>', methods=['GET'])
# def split_summary(invoice_id):
#     user_id = session.get('user_id')
#     if not user_id:
#         return redirect(url_for('login'))  # Redirect to login if not authenticated
    
#     try:
#         # Fetch invoice details for the specific InvoiceID
#         mycursor.execute("""
#             SELECT id.DetailID, id.ItemName, id.Quantity, id.Price, us.user_id, us.split_amount
#             FROM InvoiceDetails id
#             JOIN user_item_splits us ON id.DetailID = us.DetailID
#             WHERE id.InvoiceID = %s
#         """, (invoice_id,))
#         data = mycursor.fetchall()

#         # Organize data by username
#         result = {}
#         for row in data:
#             detail_id, item_name, quantity, price, user_id, split_amount = row
#             original_price = price * quantity
#             total_shares = sum(1 for r in data if r[0] == detail_id)  # Total number of shares
#             user_share = split_amount * total_shares

#             # Get the username for this user_id
#             mycursor.execute("SELECT username FROM users WHERE user_id = %s", (user_id,))
#             username = mycursor.fetchone()[0]

#             if username not in result:
#                 result[username] = []

#             result[username].append({
#                 'ItemName': item_name,
#                 'Quantity': quantity,
#                 'OriginalPrice': original_price,
#                 'Shares': total_shares,
#                 'YourShare': user_share
#             })

#         return render_template('split_summary.html', result=result)

#     except Exception as e:
#         print("Error in split-summary:", str(e))
#         return "An error occurred", 500

#new 

@app.route('/split-summary/<int:invoice_id>')
def split_summary(invoice_id):
    if 'user_id' not in session:
        return redirect(url_for('login'))

    try:
        query = """
        SELECT 
            id.ItemName, 
            COUNT(us.user_id) AS shares,  -- Number of shares
            id.Price, 
            u.username, 
            SUM(us.split_amount) AS total_share,  -- Sum of user's share amount
            MAX(us.created_at) AS last_updated
        FROM user_item_splits us
        JOIN InvoiceDetails id ON id.DetailID = us.DetailID
        JOIN users u ON u.user_id = us.user_id
        WHERE id.InvoiceID = %s
        GROUP BY id.ItemName, id.Price, u.username
        ORDER BY u.username, id.ItemName
        """
        mycursor.execute(query, (invoice_id,))
        data = mycursor.fetchall()

        print("Query Result:", data)  # Debugging: Print fetched data

        # Group data by username for structured display
        user_groups = {}
        for row in data:
            username = row[3]  # 'username'
            if username not in user_groups:
                user_groups[username] = {'items': [], 'total_share': Decimal(0)}
            user_groups[username]['items'].append(row)
            user_groups[username]['total_share'] += row[4]  # 'total_share'

        return render_template('split_summary.html', user_groups=user_groups)
    except Exception as e:
        print(f"Error in split_summary: {str(e)}")
        return "An error occurred loading the split summary", 500


@app.route('/join_group', methods=['GET', 'POST'])
def join_group():
    # Check if the user is authenticated (user_id in session)
    if 'user_id' not in session:
        return redirect(url_for('login'))  # Redirect to login if not authenticated

    # Get the user_id from the session
    user_id = session['user_id']

    if request.method == 'POST':
        group_code = request.form['group_code']

        # Check if the group code exists in the groups table with case-sensitivity
        mycursor.execute("SELECT * FROM `groups` WHERE `code` = BINARY %s", (group_code,))
        group = mycursor.fetchone()

        if not group:
            # If the group code is invalid
            return render_template('join_group.html', error_message="Invalid group code!")
        
        group_id = group[0]  # Assuming group_id is the first column in the result
        
        # Check if the user is already a member of the group
        mycursor.execute("SELECT * FROM `user_groups` WHERE `user_id` = %s AND `group_id` = %s", (user_id, group_id))
        user_group = mycursor.fetchone()
        
        if user_group:
            # If the user is already in the group
            return render_template('join_group.html', error_message="You are already a member of this group!")
        
        # Add the user to the group in the user_groups table
        mycursor.execute("INSERT INTO `user_groups` (`user_id`, `group_id`) VALUES (%s, %s)", (user_id, group_id))
        mydb.commit()

        # Redirect to the group's invoices page
        return redirect(url_for('group_invoices', group_id=group_id))

    return render_template('join_group.html')

@app.route('/create_group', methods=['GET', 'POST'])
def create_group():
    # Check if the user is authenticated (user_id in session)
    if 'user_id' not in session:
        return redirect(url_for('login'))  # Redirect to login if not authenticated

    # Get the user_id from the session
    user_id = session['user_id']

    if request.method == 'POST':
        group_name = request.form['group_name']

        mycursor.execute("SELECT * FROM `groups` WHERE `group_name` = %s", (group_name,))
        group = mycursor.fetchone()
        
        if(group is not None):
            return render_template('create_group.html', error_message="Group name already exists!")
        
        characters = string.ascii_letters + string.digits
        group_code = ''.join(random.choice(characters.upper()) for _ in range(6))

        mycursor.execute("INSERT INTO `groups` (`group_name`, `code`) VALUES (%s, %s)", (group_name, group_code))

        mycursor.execute("SELECT * FROM `groups` WHERE `group_name` = %s", (group_name,))
        group = mycursor.fetchone()

        group_id = group[0]  # Assuming group_id is the first column in the result

        mycursor.execute("INSERT INTO `user_groups` (`user_id`, `group_id`) VALUES (%s, %s)", (user_id, group_id))

        mydb.commit()

        # Redirect to the group's invoices page
        return redirect(url_for('group_invoices', group_id=group_id))

    return render_template('create_group.html')


# @app.route('/group_invoices/<int:group_id>')
# def group_invoices(group_id):
#     # Logic for displaying group invoices, replace with actual logic
#     return f"Displaying invoices for group ID: {group_id}"

@app.route('/group_invoices/<int:group_id>')
def group_invoices_page(group_id):
    # Your existing logic here
    if 'user_id' not in session:
        return redirect(url_for('login'))  # Redirect to login if not authenticated

    user_id = session['user_id']

    mycursor.execute("SELECT user_group_id FROM `user_groups` WHERE `user_id` = %s AND `group_id` = %s", (user_id, group_id))
    user_group = mycursor.fetchone()

    if not user_group:
        return redirect(url_for('join_group'))

    user_group_id = user_group[0]

    mycursor.execute("SELECT * FROM `Invoice` WHERE `user_group_id` = %s", (user_group_id,))
    invoices = mycursor.fetchall()

    if not invoices:
        return render_template('group_invoices.html', group_id=group_id, message="No invoices found for this group.")

    return render_template('group_invoices.html', group_id=group_id, invoices=invoices)


if __name__ == '__main__':
    app.run(port=5009, debug=True)
    