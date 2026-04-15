from flask import Flask, render_template, request
import sqlite3
from datetime import datetime

app = Flask(__name__)

def get_db():
    conn = sqlite3.connect("expenses.db")
    conn.row_factory = sqlite3.Row
    return conn

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/add", methods = ["GET","POST"])
def add_expense():
    if request.method == "POST":
        amount = request.form["amount"]
        category = request.form["category"]
        note = request.form["note"]
        date = datetime.now().strftime("%Y-%m-%d")

        conn = get_db()
        cursor = conn.cursor()
        cursor.execute("INSERT into expenses(amount,category,note,date) values (?,?,?,?)",(amount,category,note,date))

        conn.commit()
        conn.close()
        return render_template("success.html")
    return render_template("add_expense.html")

