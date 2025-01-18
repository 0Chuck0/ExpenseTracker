from flask import Flask, render_template, request, jsonify
import pyodbc
import json

app = Flask(__name__)

# Database connection details
server = 'myexpense.database.windows.net'
database = 'MyExpense'
username = 'SqlDbAdmin'
password = 'MyExpense1'
driver= '{ODBC Driver 17 for SQL Server}'

# Connect to the database
def get_db_connection():
    conn = pyodbc.connect(f'DRIVER={driver};SERVER={server};PORT=1433;DATABASE={database};UID={username};PWD={password}')
    return conn

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/insert', methods=['POST'])
def insert_expense():
    data = request.get_json()
    date = data['date']
    description = data['description']
    amount = data['amount']

    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO expenses (date, description, amount)
        VALUES (?, ?, ?)
    ''', (date, description, amount))
    conn.commit()
    conn.close()
    return jsonify({"message": "Expense added successfully!"})

@app.route('/get_total_expense', methods=['POST'])
def get_total_expense():
    data = request.get_json()
    year = data['year']
    month = data['month']

    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('''
        SELECT total_expense
        FROM monthly_expenses
        WHERE month = ? AND year = ?
    ''', (month, year))
    
    result = cursor.fetchone()
    conn.close()

    if result:
        return jsonify({"total_expense": result[0]})
    else:
        return jsonify({"error": "No data found for the selected month and year."})

@app.route('/get_detailed_expenses', methods=['POST'])
def get_detailed_expenses():
    data = request.get_json()
    year = data['year']
    month = data['month']

    # Database connection
    conn = get_db_connection()
    cursor = conn.cursor()

    # Query to fetch only the day, description, and amount for the given month and year
    cursor.execute('''
        SELECT DAY(date) AS day, description, amount
        FROM expenses
        WHERE YEAR(date) = ? AND MONTH(date) = ?
    ''', (year, month))

    # Fetch all results
    result = cursor.fetchall()
    conn.close()

    # Convert results into a list of dictionaries
    detailed_expenses = [
        {"day": row[0], "description": row[1], "amount": row[2]} for row in result
    ]

    return jsonify(detailed_expenses)

if __name__ == '__main__':
    app.run(debug=True)
