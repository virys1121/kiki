import sqlite3
import os
from flask import Flask, render_template, request, redirect, url_for, session, flash, jsonify
from werkzeug.utils import secure_filename
from PIL import Image

app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY', 'dev-key-123')
app.config['UPLOAD_FOLDER'] = 'static/images'
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024

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
            session.clear()
            session['user_id'] = user['UserID']
            session['user_name'] = user['UserFullName']
            session['role_name'] = user['RoleName']
            return redirect(url_for('products'))
        else:
            flash('Неверный логин или пароль', 'error')

    return render_template('login.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        full_name = request.form['full_name']
        login = request.form['login']
        password = request.form['password']

        conn = get_db_connection()
        try:
            # All registered users are 'Клиент' by default (RoleID = 3)
            conn.execute('INSERT INTO Users (UserFullName, UserLogin, UserPassword, UserRole) VALUES (?, ?, ?, 3)',
                         (full_name, login, password))
            conn.commit()
            flash('Регистрация успешна! Теперь вы можете войти.', 'info')
            return redirect(url_for('login'))
        except sqlite3.IntegrityError:
            flash('Пользователь с таким логином уже существует', 'error')
        finally:
            conn.close()

    return render_template('register.html')

@app.route('/guest')
def guest_login():
    session.clear()
    session['user_id'] = 0
    session['user_name'] = 'Гость'
    session['role_name'] = 'Гость'
    return redirect(url_for('products'))

@app.route('/products')
def products():
    if 'role_name' not in session:
        return redirect(url_for('login'))

    search_query = request.args.get('search', '')
    sort_by = request.args.get('sort', '')
    filter_supplier = request.args.get('supplier', 'Все поставщики')

    conn = get_db_connection()
    query = 'SELECT * FROM Products WHERE 1=1'
    params = []

    # Restrictions: Filter and Sort only for Manager and Admin
    is_privileged = session['role_name'] in ['Менеджер', 'Администратор']

    if is_privileged:
        if filter_supplier != 'Все поставщики':
            query += ' AND ProductSupplier = ?'
            params.append(filter_supplier)

        if search_query:
            query += ' AND (ProductName LIKE ? OR ProductDescription LIKE ? OR ProductManufacturer LIKE ? OR ProductArticleNumber LIKE ?)'
            like_query = f'%{search_query}%'
            params.extend([like_query, like_query, like_query, like_query])

        if sort_by == 'price_asc':
            query += ' ORDER BY ProductPrice ASC'
        elif sort_by == 'price_desc':
            query += ' ORDER BY ProductPrice DESC'
        elif sort_by == 'stock_asc':
            query += ' ORDER BY ProductQuantityInStock ASC'
        elif sort_by == 'stock_desc':
            query += ' ORDER BY ProductQuantityInStock DESC'

    products = conn.execute(query, params).fetchall()
    suppliers = conn.execute('SELECT DISTINCT ProductSupplier FROM Products').fetchall()
    conn.close()

    # Reset edit lock when returning to product list
    session.pop('editing_product_id', None)

    return render_template('products.html',
                           products=products,
                           suppliers=[s['ProductSupplier'] for s in suppliers],
                           current_supplier=filter_supplier,
                           current_search=search_query,
                           current_sort=sort_by,
                           is_privileged=is_privileged,
                           user_name=session.get('user_name'),
                           role_name=session.get('role_name'))

@app.route('/products/add', methods=['GET', 'POST'])
def add_product():
    if session.get('role_name') != 'Администратор':
        flash('Доступ запрещен', 'error')
        return redirect(url_for('products'))

    if request.method == 'POST':
        article = request.form['article']
        name = request.form['name']
        category = request.form['category']
        description = request.form['description']
        manufacturer = request.form['manufacturer']
        supplier = request.form['supplier']
        price = float(request.form['price'])
        unit = request.form['unit']
        stock = int(request.form['stock'])
        discount = int(request.form['discount'])

        if price < 0 or stock < 0:
            flash('Цена и количество не могут быть отрицательными', 'error')
            return render_template('edit_product.html', mode='add')

        photo_filename = None
        if 'photo' in request.files:
            file = request.files['photo']
            if file and file.filename:
                filename = secure_filename(file.filename)
                photo_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
                file.save(photo_path)
                try:
                    img = Image.open(photo_path)
                    img = img.resize((300, 200))
                    img.save(photo_path)
                    photo_filename = filename
                except Exception as e:
                    flash(f'Ошибка обработки изображения: {e}', 'error')

        conn = get_db_connection()
        try:
            conn.execute('INSERT INTO Products (ProductArticleNumber, ProductName, ProductCategory, ProductDescription, ProductManufacturer, ProductSupplier, ProductPrice, ProductUnit, ProductQuantityInStock, ProductDiscount, ProductPhoto) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)',
                         (article, name, category, description, manufacturer, supplier, price, unit, stock, discount, photo_filename))
            conn.commit()
            flash('Товар успешно добавлен', 'info')
            return redirect(url_for('products'))
        except sqlite3.IntegrityError:
            flash('Товар с таким артикулом уже существует', 'error')
        finally:
            conn.close()

    return render_template('edit_product.html', mode='add')

@app.route('/products/edit/<int:product_id>', methods=['GET', 'POST'])
def edit_product(product_id):
    if session.get('role_name') != 'Администратор':
        flash('Доступ запрещен', 'error')
        return redirect(url_for('products'))

    # One-window editing logic
    current_editing = session.get('editing_product_id')
    if current_editing and current_editing != product_id:
        flash('Вы уже редактируете другой товар. Пожалуйста, завершите текущее редактирование.', 'error')
        return redirect(url_for('products'))

    session['editing_product_id'] = product_id

    conn = get_db_connection()
    product = conn.execute('SELECT * FROM Products WHERE ProductID = ?', (product_id,)).fetchone()

    if not product:
        session.pop('editing_product_id', None)
        conn.close()
        return "Товар не найден", 404

    if request.method == 'POST':
        name = request.form['name']
        category = request.form['category']
        description = request.form['description']
        manufacturer = request.form['manufacturer']
        supplier = request.form['supplier']
        price = float(request.form['price'])
        unit = request.form['unit']
        stock = int(request.form['stock'])
        discount = int(request.form['discount'])

        if price < 0 or stock < 0:
            flash('Цена и количество не могут быть отрицательными', 'error')
            return render_template('edit_product.html', mode='edit', product=product)

        photo_filename = product['ProductPhoto']
        if 'photo' in request.files:
            file = request.files['photo']
            if file and file.filename:
                if photo_filename:
                    old_path = os.path.join(app.config['UPLOAD_FOLDER'], photo_filename)
                    if os.path.exists(old_path):
                        os.remove(old_path)

                filename = secure_filename(file.filename)
                photo_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
                file.save(photo_path)

                try:
                    img = Image.open(photo_path)
                    img = img.resize((300, 200))
                    img.save(photo_path)
                    photo_filename = filename
                except Exception as e:
                    flash(f'Ошибка обработки изображения: {e}', 'error')

        conn.execute('UPDATE Products SET ProductName=?, ProductCategory=?, ProductDescription=?, ProductManufacturer=?, ProductSupplier=?, ProductPrice=?, ProductUnit=?, ProductQuantityInStock=?, ProductDiscount=?, ProductPhoto=? WHERE ProductID=?',
                     (name, category, description, manufacturer, supplier, price, unit, stock, discount, photo_filename, product_id))
        conn.commit()
        conn.close()
        session.pop('editing_product_id', None)
        flash('Товар успешно обновлен', 'info')
        return redirect(url_for('products'))

    conn.close()
    return render_template('edit_product.html', mode='edit', product=product)

@app.route('/products/delete/<int:product_id>', methods=['POST'])
def delete_product(product_id):
    if session.get('role_name') != 'Администратор':
        flash('Доступ запрещен', 'error')
        return redirect(url_for('products'))

    conn = get_db_connection()
    in_order = conn.execute('SELECT 1 FROM OrderItems WHERE ProductID = ?', (product_id,)).fetchone()

    if in_order:
        flash('Нельзя удалить товар, который присутствует в заказе', 'error')
    else:
        product = conn.execute('SELECT ProductPhoto FROM Products WHERE ProductID = ?', (product_id,)).fetchone()
        if product and product['ProductPhoto']:
            photo_path = os.path.join(app.config['UPLOAD_FOLDER'], product['ProductPhoto'])
            if os.path.exists(photo_path):
                os.remove(photo_path)

        conn.execute('DELETE FROM Products WHERE ProductID = ?', (product_id,))
        conn.commit()
        flash('Товар успешно удален', 'info')

    conn.close()
    session.pop('editing_product_id', None)
    return redirect(url_for('products'))

@app.route('/orders')
def view_orders():
    if session.get('role_name') not in ['Менеджер', 'Администратор']:
        flash('Доступ запрещен', 'error')
        return redirect(url_for('products'))

    conn = get_db_connection()
    # Join with users to get FIO
    orders = conn.execute('''
        SELECT o.*, u.UserFullName
        FROM Orders o
        JOIN Users u ON o.OrderUserID = u.UserID
        ORDER BY o.OrderDate DESC
    ''').fetchall()

    # For each order, get items
    order_list = []
    for order in orders:
        items = conn.execute('''
            SELECT oi.*, p.ProductName
            FROM OrderItems oi
            JOIN Products p ON oi.ProductID = p.ProductID
            WHERE oi.OrderID = ?
        ''', (order['OrderID'],)).fetchall()

        total_price = sum(item['ItemQuantity'] * item['ItemPrice'] for item in items)

        order_list.append({
            'data': order,
            'order_items': items,
            'total_price': total_price
        })

    conn.close()
    return render_template('orders.html', orders=order_list, role_name=session.get('role_name'), user_name=session.get('user_name'))

@app.route('/orders/add', methods=['GET', 'POST'])
def add_order():
    if session.get('role_name') != 'Администратор':
        flash('Доступ запрещен', 'error')
        return redirect(url_for('view_orders'))

    conn = get_db_connection()
    if request.method == 'POST':
        user_id = request.form['user_id']
        status = request.form['status']

        cursor = conn.cursor()
        cursor.execute('INSERT INTO Orders (OrderStatus, OrderUserID) VALUES (?, ?)', (status, user_id))
        order_id = cursor.lastrowid
        conn.commit()
        conn.close()
        return redirect(url_for('edit_order', order_id=order_id))

    users = conn.execute('SELECT UserID, UserFullName FROM Users WHERE UserRole = 3').fetchall() # Clients
    conn.close()
    return render_template('edit_order.html', mode='add', users=users)

@app.route('/orders/edit/<int:order_id>', methods=['GET', 'POST'])
def edit_order(order_id):
    if session.get('role_name') != 'Администратор':
        flash('Доступ запрещен', 'error')
        return redirect(url_for('view_orders'))

    conn = get_db_connection()
    if request.method == 'POST':
        if 'update_order' in request.form:
            status = request.form['status']
            conn.execute('UPDATE Orders SET OrderStatus = ? WHERE OrderID = ?', (status, order_id))
            conn.commit()
            flash('Заказ обновлен', 'info')
        elif 'add_item' in request.form:
            product_id = request.form['product_id']
            quantity = int(request.form['quantity'])

            product = conn.execute('SELECT ProductPrice FROM Products WHERE ProductID = ?', (product_id,)).fetchone()
            if product:
                try:
                    conn.execute('INSERT INTO OrderItems (OrderID, ProductID, ItemQuantity, ItemPrice) VALUES (?, ?, ?, ?)',
                                 (order_id, product_id, quantity, product['ProductPrice']))
                    conn.commit()
                except sqlite3.IntegrityError:
                    conn.execute('UPDATE OrderItems SET ItemQuantity = ItemQuantity + ? WHERE OrderID = ? AND ProductID = ?',
                                 (quantity, order_id, product_id))
                    conn.commit()
        elif 'remove_item' in request.form:
            product_id = request.form['product_id']
            conn.execute('DELETE FROM OrderItems WHERE OrderID = ? AND ProductID = ?', (order_id, product_id))
            conn.commit()

    order = conn.execute('SELECT o.*, u.UserFullName FROM Orders o JOIN Users u ON o.OrderUserID = u.UserID WHERE OrderID = ?', (order_id,)).fetchone()
    items = conn.execute('SELECT oi.*, p.ProductName FROM OrderItems oi JOIN Products p ON oi.ProductID = p.ProductID WHERE oi.OrderID = ?', (order_id,)).fetchall()
    products = conn.execute('SELECT ProductID, ProductName, ProductPrice FROM Products WHERE ProductQuantityInStock > 0').fetchall()

    conn.close()
    return render_template('edit_order.html', mode='edit', order=order, items=items, products=products)

@app.route('/orders/delete/<int:order_id>', methods=['POST'])
def delete_order(order_id):
    if session.get('role_name') != 'Администратор':
        flash('Доступ запрещен', 'error')
        return redirect(url_for('view_orders'))

    conn = get_db_connection()
    conn.execute('DELETE FROM OrderItems WHERE OrderID = ?', (order_id,))
    conn.execute('DELETE FROM Orders WHERE OrderID = ?', (order_id,))
    conn.commit()
    conn.close()
    flash('Заказ удален', 'info')
    return redirect(url_for('view_orders'))

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))

@app.errorhandler(404)
def page_not_found(e):
    return "<h1>Страница не найдена</h1><a href='/'>Вернуться на главную</a>", 404

@app.errorhandler(500)
def internal_server_error(e):
    return "<h1>Произошла внутренняя ошибка сервера</h1><a href='/'>Вернуться на главную</a>", 500

if __name__ == '__main__':
    app.run(port=5000, debug=True)
