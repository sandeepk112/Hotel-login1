from flask import Flask, render_template, request, redirect, session
import sqlite3
from datetime import datetime

app = Flask(__name__)
app.secret_key = "secret123"

# 🔌 Database connect
def connect_db():
    return sqlite3.connect("database.db")

# 🔐 Login page
@app.route('/')
def login():
    return render_template("login.html")

# 🔐 Login check
@app.route('/login', methods=['POST'])
def login_check():
    username = request.form['username']
    password = request.form['password']

    if username == "admin" and password == "1234":
        session['user'] = username
        return redirect('/dashboard')
    else:
        return "Invalid Login"

# 💰 Room price
def get_room_price(room):
    if room == "AC":
        return 200
    elif room == "Non-AC":
        return 100
    elif room == "Deluxe":
        return 300

# 📊 Dashboard
@app.route('/dashboard')
def dashboard():
    conn = connect_db()
    cursor = conn.cursor()

    cursor.execute("SELECT COUNT(*) FROM bookings")
    total = cursor.fetchone()[0]

    cursor.execute("SELECT * FROM bookings")
    bookings = cursor.fetchall()

    conn.close()

    return render_template("dashboard.html", total=total, bookings=bookings)

# 🛏️ Booking page
@app.route('/booking')
def booking():
    return render_template("booking.html")

# 📥 Save booking + bill
@app.route('/book', methods=['POST'])
def book():
    name = request.form['name']
    room = request.form['room']
    checkin = request.form['checkin']
    checkout = request.form['checkout']

    checkin_dt = datetime.strptime(checkin, "%Y-%m-%dT%H:%M")
    checkout_dt = datetime.strptime(checkout, "%Y-%m-%dT%H:%M")

    hours = (checkout_dt - checkin_dt).total_seconds() / 3600

    price = get_room_price(room)
    bill = hours * price

    conn = connect_db()
    cursor = conn.cursor()

    cursor.execute("""
    INSERT INTO bookings (name, room, checkin, checkout, bill)
    VALUES (?, ?, ?, ?, ?)
    """, (name, room, checkin, checkout, bill))

    conn.commit()
    conn.close()

    return redirect('/dashboard')

# ❌ Delete booking
@app.route('/delete/<int:id>')
def delete(id):
    conn = connect_db()
    cursor = conn.cursor()

    cursor.execute("DELETE FROM bookings WHERE id=?", (id,))
    conn.commit()
    conn.close()

    return redirect('/dashboard')

# ✏️ Edit page
@app.route('/edit/<int:id>')
def edit(id):
    conn = connect_db()
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM bookings WHERE id=?", (id,))
    data = cursor.fetchone()

    conn.close()
    return render_template("edit.html", b=data)

# ✏️ Update booking
@app.route('/update/<int:id>', methods=['POST'])
def update(id):
    name = request.form['name']
    room = request.form['room']
    checkin = request.form['checkin']
    checkout = request.form['checkout']

    conn = connect_db()
    cursor = conn.cursor()

    cursor.execute("""
    UPDATE bookings
    SET name=?, room=?, checkin=?, checkout=?
    WHERE id=?
    """, (name, room, checkin, checkout, id))

    conn.commit()
    conn.close()

    return redirect('/dashboard')

# ▶️ Run app
app.run(debug=True)