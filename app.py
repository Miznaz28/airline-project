from flask import Flask, render_template, request, redirect, session
import sqlite3

app = Flask(__name__)
app.secret_key = "secret123"

def get_db():
    return sqlite3.connect("airline.db")

def init_db():
    db = get_db()
    cursor = db.cursor()

    cursor.execute('''CREATE TABLE IF NOT EXISTS users(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT,
        password TEXT
    )''')

    cursor.execute('''CREATE TABLE IF NOT EXISTS flights(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        source TEXT,
        destination TEXT,
        price INTEGER
    )''')

    cursor.execute('''CREATE TABLE IF NOT EXISTS bookings(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER,
        flight_id INTEGER
    )''')

    db.commit()
    db.close()

init_db()

@app.route('/')
def index():
    return render_template("index.html")

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        db = get_db()
        db.execute("INSERT INTO users (username, password) VALUES (?, ?)",
                   (request.form['username'], request.form['password']))
        db.commit()
        return redirect('/login')
    return render_template("register.html")

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        db = get_db()
        user = db.execute("SELECT * FROM users WHERE username=? AND password=?",
                          (request.form['username'], request.form['password'])).fetchone()
        if user:
            session['user'] = user[0]
            return redirect('/dashboard')
    return render_template("login.html")

@app.route('/dashboard')
def dashboard():
    db = get_db()
    flights = db.execute("SELECT * FROM flights").fetchall()
    return render_template("dashboard.html", flights=flights)

@app.route('/book/<int:flight_id>')
def book(flight_id):
    if 'user' not in session:
        return redirect('/login')

    db = get_db()
    db.execute("INSERT INTO bookings (user_id, flight_id) VALUES (?, ?)",
               (session['user'], flight_id))
    db.commit()

    return "Booking Confirmed!"

@app.route('/admin', methods=['GET', 'POST'])
def admin():
    if request.method == 'POST':
        db = get_db()
        db.execute("INSERT INTO flights (source, destination, price) VALUES (?, ?, ?)",
                   (request.form['source'], request.form['destination'], request.form['price']))
        db.commit()
    return render_template("admin.html")


import os

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))