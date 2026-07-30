from flask import Flask, render_template, request, redirect, url_for, session

app = Flask(__name__)
app.secret_key = 'your_secret_key_here'

# লগইন ক্রেডেনশিয়াল (ইউজারনেম এবং পাসওয়ার্ড পরিবর্তনের জন্য ডিকশনারি)
USER_CREDENTIALS = {
    'username': 'ROJA',
    'password': 'SAINUL'
}

# কার ডাটাবেজ
cars_db = [
    {
        'car_name': 'Toyota',
        'model': 'Hiace',
        'cc': '3000cc',
        'colour': 'White',
        'grade': '4',
        'mileage': '45,000 km',
        'extra_feature': 'AC, Dual Airbag',
        'hybrid_status': 'N/A'
    }
]

@app.route('/')
def home():
    return render_template('login.html')

@app.route('/login', methods=['POST'])
def login():
    username = request.form.get('username')
    password = request.form.get('password')
    
    if username == USER_CREDENTIALS['username'] and password == USER_CREDENTIALS['password']:
        session['user_role'] = 'owner'
        return redirect(url_for('owner_dashboard'))
    elif username == 'salesman' and password == '1234':
        session['user_role'] = 'salesman'
        return redirect(url_for('salesman_dashboard'))
    else:
        return "Invalid Username or Password! <a href='/'>Try Again</a>"

# ওনার ড্যাশবোর্ড (মেনু ও সেটিংস ট্যাবসহ)
@app.route('/owner')
def owner_dashboard():
    if 'user_role' in session and session['user_role'] == 'owner':
        tab = request.args.get('tab', 'menu') # ডিফল্টভাবে মেনু ট্যাব দেখাবে
        return render_template('owner.html', cars=cars_db, active_tab=tab)
    return redirect(url_for('home'))

# সেলসম্যান ড্যাশবোর্ড
@app.route('/salesman')
def salesman_dashboard():
    if 'user_role' in session and session['user_role'] == 'salesman':
        return render_template('salesman.html', cars=cars_db)
    return redirect(url_for('home'))

# ইউজারনেম ও পাসওয়ার্ড পরিবর্তনের রাউট
@app.route('/update_credentials', methods=['POST'])
def update_credentials():
    if 'user_role' in session and session['user_role'] == 'owner':
        new_username = request.form.get('new_username')
        current_password = request.form.get('current_password')
        new_password = request.form.get('new_password')
        
        # বর্তমান পাসওয়ার্ড সঠিক কি না যাচাই করা
        if current_password == USER_CREDENTIALS['password']:
            if new_username:
                USER_CREDENTIALS['username'] = new_username
            if new_password:
                USER_CREDENTIALS['password'] = new_password
            return redirect(url_for('owner_dashboard', tab='settings'))
        else:
            return "Incorrect Current Password! <a href='/owner?tab=settings'>Go Back</a>"
    return redirect(url_for('home'))

# নতুন গাড়ি যোগ করার রাউট
@app.route('/add_car', methods=['POST'])
def add_car():
    if 'user_role' in session and session['user_role'] == 'owner':
        new_car = {
            'car_name': request.form.get('car_name'),
            'model': request.form.get('model'),
            'cc': request.form.get('cc'),
            'colour': request.form.get('colour'),
            'grade': request.form.get('grade'),
            'mileage': request.form.get('mileage'),
            'extra_feature': request.form.get('extra_feature'),
            'hybrid_status': request.form.get('hybrid_status')
        }
        cars_db.append(new_car)
        
    return redirect(url_for('owner_dashboard', tab='menu'))

# গাড়ি ডিলিট করার রাউট
@app.route('/delete_car/<int:car_id>', methods=['POST', 'GET'])
def delete_car(car_id):
    if 'user_role' in session and session['user_role'] == 'owner':
        if 0 <= car_id < len(cars_db):
            cars_db.pop(car_id)
            
    return redirect(url_for('owner_dashboard', tab='menu'))

# গাড়ি এডিট করার রাউট
@app.route('/edit_car/<int:car_id>', methods=['GET', 'POST'])
def edit_car(car_id):
    if 'user_role' in session and session['user_role'] == 'owner':
        if 0 <= car_id < len(cars_db):
            car = cars_db[car_id]
            if request.method == 'POST':
                cars_db[car_id] = {
                    'car_name': request.form.get('car_name'),
                    'model': request.form.get('model'),
                    'cc': request.form.get('cc'),
                    'colour': request.form.get('colour'),
                    'grade': request.form.get('grade'),
                    'mileage': request.form.get('mileage'),
                    'extra_feature': request.form.get('extra_feature'),
                    'hybrid_status': request.form.get('hybrid_status')
                }
                return redirect(url_for('owner_dashboard', tab='menu'))
            
            return render_template('edit_car.html', car=car, car_id=car_id)
    return redirect(url_for('home'))

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('home'))

if __name__ == '__main__':
    app.run(debug=True)
