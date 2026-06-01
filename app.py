import sqlite3
from flask import Flask, render_template, request, redirect, url_for, session, flash

app = Flask(__name__)
app.secret_key = 'super-secret-key'

def get_db_connection():
    conn = sqlite3.connect('database.db')
    conn.row_factory = sqlite3.Row
    return conn

@app.route('/', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        login = request.form['login']
        password = request.form['password']

        conn = get_db_connection()
        user = conn.execute('SELECT u.*, r.RoleName FROM Users u JOIN Roles r ON u.UserRole = r.RoleID WHERE UserLogin = ? AND UserPassword = ?',
                           (login, password)).fetchone()
        conn.close()

        if user:
            session['user_id'] = user['UserID']
            session['user_name'] = user['UserFullName']
            session['role_name'] = user['RoleName']
            return redirect(url_for('products'))
        else:
            flash('Неверный логин или пароль')

    return render_template('login.html')

@app.route('/guest')
def guest_login():
    session['user_id'] = 0
    session['user_name'] = 'Гость'
    session['role_name'] = 'Гость'
    return redirect(url_for('products'))

@app.route('/products')
def products():
    if 'role_name' not in session:
        return redirect(url_for('login'))

    conn = get_db_connection()
    products = conn.execute('SELECT * FROM Products').fetchall()
    conn.close()

    return render_template('products.html',
                           products=products,
                           user_name=session.get('user_name'),
                           role_name=session.get('role_name'))

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))

if __name__ == '__main__':
    app.run(port=5000, debug=True)
