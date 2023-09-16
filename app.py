from flask import Flask, render_template, request, redirect
import mysql.connector

app = Flask(__name__)
app.config.from_object('config')

# Configure MySQL connection
db_config = {
    "host": app.config['DB_HOST'],
    "user": app.config['DB_USER'],
    "password": app.config['DB_PASSWORD'],
    "database": app.config['DB_NAME'],
}

# Function to retrieve customer details by ID
def get_customer_by_id(customer_id):
    try:
        # Connect to the database
        conn = mysql.connector.connect(**db_config)
        cursor = conn.cursor(dictionary=True)

        # Query the customer by ID
        query = "SELECT * FROM customers WHERE id = %s"
        cursor.execute(query, (customer_id,))
        customer = cursor.fetchone()

        return customer

    except mysql.connector.Error as err:
        print(f"Error: {err}")
        return None

    finally:
        cursor.close()
        conn.close()

# Function to update customer balance
def update_balance(customer_id, amount):
    try:
        # Connect to the database
        conn = mysql.connector.connect(**db_config)
        cursor = conn.cursor()

        # Update the balance of the customer
        query = "UPDATE customers SET balance = balance + %s WHERE id = %s"
        cursor.execute(query, (amount, customer_id))

        # Commit the transaction
        conn.commit()

    except mysql.connector.Error as err:
        print(f"Error: {err}")

    finally:
        cursor.close()
        conn.close()

# Function to record a money transfer
def record_transfer(sender_id, receiver_id, amount):
    try:
        # Connect to the database
        conn = mysql.connector.connect(**db_config)
        cursor = conn.cursor()

        # Insert the transfer record into the transfers table
        query = "INSERT INTO transfers (sender_id, receiver_id, amount) VALUES (%s, %s, %s)"
        cursor.execute(query, (sender_id, receiver_id, amount))

        # Commit the transaction
        conn.commit()

    except mysql.connector.Error as err:
        print(f"Error: {err}")

    finally:
        cursor.close()
        conn.close()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/customers')
def customer_list():
    # Fetch and display the list of customers from the database
    try:
        # Connect to the database
        conn = mysql.connector.connect(**db_config)
        cursor = conn.cursor(dictionary=True)

        # Query all customers
        query = "SELECT * FROM customers"
        cursor.execute(query)
        customers = cursor.fetchall()

        return render_template('customer_list.html', customers=customers)

    except mysql.connector.Error as err:
        print(f"Error: {err}")
        return "An error occurred while fetching customer data."

    finally:
        cursor.close()
        conn.close()


@app.route('/customer/<int:id>')
def customer_details(id):
    # Fetch and display the details of a specific customer
    customer = get_customer_by_id(id)
    if customer:
        return render_template('customer_details.html', customer=customer)
    else:
        return "Customer not found."



@app.route('/transfer_money')
def transfer_money():
    # Fetch and display the list of customers for money transfer
    try:
        # Connect to the database
        conn = mysql.connector.connect(**db_config)
        cursor = conn.cursor(dictionary=True)

        # Query all customers
        query = "SELECT * FROM customers"
        cursor.execute(query)
        customers = cursor.fetchall()

        return render_template('transfer_money.html', customers=customers)

    except mysql.connector.Error as err:
        print(f"Error: {err}")
        return "An error occurred while fetching customer data."

    finally:
        cursor.close()
        conn.close()


@app.route('/transfer_money', methods=['POST'])
def perform_transfer():
    sender_id = int(request.form.get('sender'))
    receiver_id = int(request.form.get('receiver'))
    amount = float(request.form.get('amount'))

    # Validate the sender, receiver, and amount

    # Check if the sender has sufficient balance
    sender = get_customer_by_id(sender_id)
    if sender['balance'] < amount:
        return "Insufficient balance."

    # Update sender and receiver balances in the database
    update_balance(sender_id, -amount)  # Deduct amount from sender
    update_balance(receiver_id, amount)  # Add amount to receiver

    # Record the transfer in the transfers table
    record_transfer(sender_id, receiver_id, amount)

    return redirect('/customers')

if __name__ == '__main__':
    app.run(debug=True)
