import sqlite3
from flask import Flask, render_template, request, redirect, url_for, session

app = Flask(__name__)
app.secret_key = 'your_permanent_secret_key_here'
DB_NAME = 'showroom.db'

# ডাটাবেজ কানেকশন ফাংশন
def get_db_connection():
    conn = sqlite3.connect(DB_NAME)
    conn.row_factory = sqlite3.Row
    return conn

# ডাটাবেজ টেবিল ও ডিফল্ট ডাটা তৈরির ফাংশন
def init_db():
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # ইউজার টেবিল
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL,
            role TEXT NOT NULL
        )
    ''')
    
    # কার টেবিল
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS cars (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            car_name TEXT,
            model TEXT,
            cc TEXT,
            colour TEXT,
            grade TEXT,
            mileage TEXT,
            extra_feature TEXT,
            hybrid_status TEXT
        )
    ''')
    
    # ডিফল্ট ওনার (ROJA / SAINUL) যোগ করা (যদি না থাকে)
    cursor.execute("SELECT * FROM users WHERE role = 'owner'")
    if not cursor.fetchone():
        cursor.execute("INSERT INTO users (username, password, role) VALUES (?, ?, ?)", ('ROJA', 'SAINUL', 'owner'))
        cursor.execute("INSERT INTO users (username, password, role) VALUES (?, ?, ?)", ('salesman', '1234', 'salesman'))

    conn.commit()
    conn.close()

# অ্যাপ শুরুতেই ডাটাবেজ চেক করবে
init_db()

@app.route('/')
def home():
    return render_template('login.html')

@app.route('/login', methods=['POST'])
def login():
    username = request.form.get('username')
    password = request.form.get('password')
    
    conn = get_db_connection()
    user = conn.execute("SELECT * FROM users WHERE username = ? AND password = ?", (username, password)).fetchone()
    conn.close()
    
    if user:
        session['user_role'] = user['role']
        if user['role'] == 'owner':
            return redirect(url_for('owner_dashboard'))
        else:
            return redirect(url_for('salesman_dashboard'))
    else:
        return "Invalid Username or Password! <a href='/'>Try Again</a>"

@app.route('/owner')
def owner_dashboard():
    if 'user_role' in session and session['user_role'] == 'owner':
        tab = request.args.get('tab', 'menu')
        conn = get_db_connection()
        cars = conn.execute("SELECT * FROM cars").fetchall()
        conn.close()
        return render_template('owner.html', cars=cars, active_tab=tab)
    return redirect(url_for('home'))

@app.route('/salesman')
def salesman_dashboard():
    if 'user_role' in session and session['user_role'] == 'salesman':
        conn = get_db_connection()
        cars = conn.execute("SELECT * FROM cars").fetchall()
        conn.close()
        return render_template('salesman.html', cars=cars)
    return redirect(url_for('home'))

@app.route('/update_credentials', methods=['POST'])
def update_credentials():
    if 'user_role' in session and session['user_role'] == 'owner':
        new_username = request.form.get('new_username')
        current_password = request.form.get('current_password')
        new_password = request.form.get('new_password')
        
        conn = get_db_connection()
        user = conn.execute("SELECT * FROM users WHERE role = 'owner' AND password = ?", (current_password,)).fetchone()
        
        if user:
            if new_username and new_username.strip():
                conn.execute("UPDATE users SET username = ? WHERE role = 'owner'", (new_username,))
            if new_password and new_password.strip():
                conn.execute("UPDATE users SET password = ? WHERE role = 'owner'", (new_password,))
            conn.commit()
            conn.close()
            return redirect(url_for('owner_dashboard', tab='settings'))
        else:
            conn.close()
            return "Incorrect Current Password! <a href='/owner?tab=settings'>Go Back</a>"
    return redirect(url_for('home'))

@app.route('/add_car', methods=['POST'])
def add_car():
    if 'user_role' in session and session['user_role'] == 'owner':
        car_name = request.form.get('car_name')
        model = request.form.get('model')
        cc = request.form.get('cc')
        colour = request.form.get('colour')
        grade = request.form.get('grade')
        mileage = request.form.get('mileage')
        extra_feature = request.form.get('extra_feature')
        hybrid_status = request.form.get('hybrid_status')
        
        conn = get_db_connection()
        conn.execute('''
            INSERT INTO cars (car_name, model, cc, colour, grade, mileage, extra_feature, hybrid_status)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        ''', (car_name, model, cc, colour, grade, mileage, extra_feature, hybrid_status))
        conn.commit()
        conn.close()
        
    return redirect(url_for('owner_dashboard', tab='menu'))

@app.route('/delete_car/<int:car_id>', methods=['POST', 'GET'])
def delete_car(car_id):
    if 'user_role' in session and session['user_role'] == 'owner':
        conn = get_db_connection()
        conn.execute("DELETE FROM cars WHERE id = ?", (car_id,))
        conn.commit()
        conn.close()
            
    return redirect(url_for('owner_dashboard', tab='menu'))

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('home'))

if __name__ == '__main__':
    app.run(debug=True)