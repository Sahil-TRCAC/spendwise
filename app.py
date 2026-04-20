import sqlite3
from flask import Flask, render_template, request, redirect, url_for, jsonify
from datetime import datetime
import calendar

app = Flask(__name__)

def get_db_connection():
    conn = sqlite3.connect('expenses.db')
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    """Create the expenses table if it doesn't exist"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Create table with proper schema
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS expenses (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            amount REAL NOT NULL,
            category TEXT NOT NULL,
            note TEXT,
            date TEXT NOT NULL
        )
    ''')
    
    conn.commit()
    conn.close()

# Initialize the database when the app starts
init_db()

@app.route('/')
def index():
    conn = get_db_connection()
    expenses = conn.execute('SELECT * FROM expenses ORDER BY date DESC').fetchall()
    conn.close()
    
    # Calculate statistics
    total = sum(expense['amount'] for expense in expenses)
    
    # Get current month and year
    now = datetime.now()
    current_month = now.strftime('%Y-%m')
    
    # Filter current month expenses
    monthly_expenses = [e for e in expenses if e['date'].startswith(current_month)]
    monthly_total = sum(e['amount'] for e in monthly_expenses)
    
    # Category breakdown
    categories = {}
    for expense in expenses:
        cat = expense['category']
        categories[cat] = categories.get(cat, 0) + expense['amount']
    
    return render_template('index.html', 
                         expenses=expenses, 
                         total=total,
                         monthly_total=monthly_total,
                         categories=categories,
                         expense_count=len(expenses))

@app.route('/add', methods=['GET', 'POST'])
def add_expense():
    if request.method == 'POST':
        amount = float(request.form['amount'])
        category = request.form['category']
        note = request.form.get('note', '')
        date = request.form.get('date', datetime.now().strftime('%Y-%m-%d'))
        
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO expenses (amount, category, note, date) VALUES (?, ?, ?, ?)",
            (amount, category, note, date)
        )
        conn.commit()
        conn.close()
        
        return redirect(url_for('index'))
    
    return render_template('add_expense.html')

@app.route('/delete/<int:id>')
def delete_expense(id):
    conn = get_db_connection()
    conn.execute('DELETE FROM expenses WHERE id = ?', (id,))
    conn.commit()
    conn.close()
    return redirect(url_for('index'))

@app.route('/monthly')
def monthly_view():
    conn = get_db_connection()
    expenses = conn.execute('SELECT * FROM expenses ORDER BY date DESC').fetchall()
    conn.close()
    
    # Group expenses by month
    monthly_data = {}
    for expense in expenses:
        month_key = expense['date'][:7]  # YYYY-MM
        if month_key not in monthly_data:
            monthly_data[month_key] = []
        monthly_data[month_key].append(expense)
    
    # Calculate monthly totals
    monthly_totals = {month: sum(e['amount'] for e in expenses) 
                     for month, expenses in monthly_data.items()}
    
    return render_template('monthly.html', 
                         monthly_data=monthly_data, 
                         monthly_totals=monthly_totals)

@app.context_processor
def utility_processor():
    from datetime import datetime
    return {'datetime': datetime}

if __name__ == '__main__':
    app.run(debug=True)