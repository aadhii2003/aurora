from flask import render_template, request, redirect, url_for, session, flash, current_app
import json
from . import user_bp
from app import db
from app.utilities import queries

@user_bp.route('/login', methods=['GET', 'POST'])
def user_login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        # Check if user exists
        user = db.fetchone(queries.user_login, (email, password))
        if user:
            session['user'] = user['id']
            flash('Login successful!', 'success')
            return redirect(url_for('user.user_home'))
        else:
            # Insert new user
            try:
                db.execute(queries.user_register, (email, password, 'user'))
                user = db.fetchone(queries.user_login, (email, password))  # Fetch the newly created user
                if user:
                    session['user'] = user['id']
                    flash('Account created and logged in successfully!', 'success')
                    return redirect(url_for('user.user_home'))
                else:
                    flash('Failed to create account. Please try again.', 'error')
            except Exception as e:
                print(f"Error creating user: {e}")
                flash('An error occurred while creating the account.', 'error')
    return render_template('user/user-login.html')

@user_bp.route('/')
def user_home():
    query_categories = "SELECT * FROM tbl_category"
    query_products = """
        SELECT p.*, c.category_name, s.sub_category_name, MIN(ps.prize) as prize, MIN(ps.offer_prize) as offer_prize
        FROM tbl_product p 
        JOIN tbl_category c ON p.category_id = c.id 
        JOIN tbl_subcategory s ON p.sub_category_id = s.id 
        LEFT JOIN tbl_product_size ps ON p.id = ps.product_id
        WHERE p.status = 'active'
        GROUP BY p.id, c.category_name, s.sub_category_name
        LIMIT 6
    """
    categories = db.fetchall(query_categories)
    products = db.fetchall(query_products)
    for product in products:
        product['images_list'] = json.loads(product['images']) if product['images'] else []
    return render_template('user/base.html', categories=categories, products=products)

@user_bp.route('/products', methods=['GET'])
def products():
    category_id = request.args.get('category_id')
    subcategory_id = request.args.get('subcategory_id')
    
    query_categories = "SELECT * FROM tbl_category"
    query_subcategories = "SELECT * FROM tbl_subcategory"
    
    query_products = """
        SELECT p.*, c.category_name, s.sub_category_name, MIN(ps.prize) as prize, MIN(ps.offer_prize) as offer_prize
        FROM tbl_product p 
        JOIN tbl_category c ON p.category_id = c.id 
        JOIN tbl_subcategory s ON p.sub_category_id = s.id 
        LEFT JOIN tbl_product_size ps ON p.id = ps.product_id
        WHERE p.status = 'active'
    """
    params = []
    if category_id:
        query_products += " AND p.category_id = %s"
        params.append(category_id)
    if subcategory_id:
        query_products += " AND p.sub_category_id = %s"
        params.append(subcategory_id)
    
    query_products += " GROUP BY p.id, c.category_name, s.sub_category_name"
    
    categories = db.fetchall(query_categories)
    subcategories = db.fetchall(query_subcategories)
    products = db.fetchall(query_products, tuple(params))
    for product in products:
        product['images_list'] = json.loads(product['images']) if product['images'] else []
    
    return render_template('user/shop.html', categories=categories, subcategories=subcategories, products=products, selected_category=category_id, selected_subcategory=subcategory_id)

@user_bp.route('/product/<int:id>')
def product_detail(id):
    query_product = """
        SELECT p.*, c.category_name, s.sub_category_name 
        FROM tbl_product p 
        JOIN tbl_category c ON p.category_id = c.id 
        JOIN tbl_subcategory s ON p.sub_category_id = s.id 
        WHERE p.id = %s AND p.status = 'active'
    """
    query_sizes = """
        SELECT ps.*, s.stock_count, ps.prize as size_price
        FROM tbl_product_size ps 
        LEFT JOIN tbl_stock s ON ps.id = s.product_size_id 
        WHERE ps.product_id = %s
    """
    product = db.fetchone(query_product, (id,))
    if not product:
        flash('Product not found or inactive', 'error')
        return redirect(url_for('user.products'))
    
    product['images_list'] = json.loads(product['images']) if product['images'] else []
    sizes = db.fetchall(query_sizes, (id,))
    return render_template('user/product-detail.html', product=product, sizes=sizes)

@user_bp.route('/cart', methods=['GET', 'POST'])
def cart():
    if 'user' not in session:
        flash('Please login first', 'error')
        return redirect(url_for('user.user_login'))
    
    if request.method == 'POST':
        product_size_id = request.form.get('product_size_id')
        quantity = request.form.get('quantity', type=int)
        user_id = session['user']
        
        if not all([product_size_id, quantity]):
            flash('Invalid product or quantity', 'error')
            return redirect(url_for('user.cart'))
        
        try:
            # Check stock availability
            stock = db.fetchone("SELECT stock_count FROM tbl_stock WHERE product_size_id = %s", (product_size_id,))
            if not stock or stock['stock_count'] < quantity:
                flash('Insufficient stock', 'error')
                return redirect(url_for('user.cart'))
            
            # Check if item already in cart
            existing_item = db.fetchone(
                "SELECT * FROM tbl_cart WHERE user_id = %s AND product_size_id = %s",
                (user_id, product_size_id)
            )
            if existing_item:
                new_quantity = existing_item['quantity'] + quantity
                if stock['stock_count'] < new_quantity:
                    flash('Insufficient stock to increase quantity', 'error')
                    return redirect(url_for('user.cart'))
                db.execute(
                    "UPDATE tbl_cart SET quantity = %s, updated_at = NOW() WHERE id = %s",
                    (new_quantity, existing_item['id'])
                )
            else:
                db.execute(
                    "INSERT INTO tbl_cart (user_id, product_size_id, quantity, created_at, updated_at) VALUES (%s, %s, %s, NOW(), NOW())",
                    (user_id, product_size_id, quantity)
                )
            flash('Item added to cart', 'success')
        except Exception as e:
            flash(f'Error adding to cart: {str(e)}', 'error')
        return redirect(url_for('user.cart'))
    
    # Fetch cart items for GET request
    query_cart = """
        SELECT c.id, c.user_id, c.product_size_id, c.quantity, c.created_at, c.updated_at, 
               p.name, ps.size, ps.prize, ps.offer_prize, ps.discount, p.images 
        FROM tbl_cart c 
        JOIN tbl_product_size ps ON c.product_size_id = ps.id 
        JOIN tbl_product p ON ps.product_id = p.id 
        WHERE c.user_id = %s
    """
    cart_items = db.fetchall(query_cart, (session['user'],))
    for item in cart_items:
        item['images_list'] = json.loads(item['images']) if item['images'] else []
    
    return render_template('user/cart.html', cart_items=cart_items)

@user_bp.route('/cart/remove/<int:id>')
def remove_from_cart(id):
    if 'user' not in session:
        flash('Please login first', 'error')
        return redirect(url_for('user.user_login'))
    
    try:
        db.execute("DELETE FROM tbl_cart WHERE id = %s AND user_id = %s", (id, session['user']))
        flash('Item removed from cart', 'success')
    except Exception as e:
        flash(f'Error removing item: {str(e)}', 'error')
    return redirect(url_for('user.cart'))

@user_bp.route('/checkout', methods=['GET', 'POST'])
def checkout():
    if 'user' not in session:
        flash('Please login first', 'error')
        return redirect(url_for('user.user_login'))
    
    if request.method == 'POST':
        address = request.form.get('address')
        payment_method = request.form.get('payment_method')
        user_id = session['user']
        
        if not all([address, payment_method]):
            flash('All fields are required', 'error')
            return redirect(url_for('user.checkout'))
        
        try:
            # Get cart items
            cart_items = db.fetchall(
                """
                SELECT c.*, ps.prize, ps.offer_prize, ps.discount 
                FROM tbl_cart c 
                JOIN tbl_product_size ps ON c.product_size_id = ps.id 
                WHERE c.user_id = %s
                """,
                (user_id,)
            )
            
            if not cart_items:
                flash('Your cart is empty', 'error')
                return redirect(url_for('user.cart'))
            
            total_amount = 0
            for item in cart_items:
                price = item['offer_prize'] if item['offer_prize'] else item['prize']
                total_amount += price * item['quantity']
            
            # Insert into tbl_purchase_master
            query_purchase = """
                INSERT INTO tbl_purchase_master (user_id, total_amount, address, payment_method, status)
                VALUES (%s, %s, %s, %s, %s)
            """
            db.execute(query_purchase, (user_id, total_amount, address, payment_method, 'pending'))
            purchase_id = db.fetchone("SELECT LAST_INSERT_ID() as id")['id']
            
            # Insert into tbl_purchase_child and update stock
            for item in cart_items:
                db.execute(
                    """
                    INSERT INTO tbl_purchase_child (purchase_id, product_size_id, quantity, price)
                    VALUES (%s, %s, %s, %s)
                    """,
                    (purchase_id, item['product_size_id'], item['quantity'], item['offer_prize'] or item['prize'])
                )
                db.execute(
                    """
                    UPDATE tbl_stock 
                    SET stock_count = stock_count - %s, purchase_count = purchase_count + %s 
                    WHERE product_size_id = %s
                    """,
                    (item['quantity'], item['quantity'], item['product_size_id'])
                )
            
            # Clear cart
            db.execute("DELETE FROM tbl_cart WHERE user_id = %s", (user_id,))
            
            # Add initial tracking status
            db.execute(
                "INSERT INTO tbl_tracking (purchase_id, status) VALUES (%s, %s)",
                (purchase_id, 'Order Placed')
            )
            
            flash('Order placed successfully', 'success')
            return redirect(url_for('user.order_history'))
        except Exception as e:
            flash(f'Error processing order: {str(e)}', 'error')
            return redirect(url_for('user.checkout'))
    
    cart_items = db.fetchall(
        """
        SELECT c.*, p.name, ps.size, ps.prize, ps.offer_prize, ps.discount 
        FROM tbl_cart c 
        JOIN tbl_product_size ps ON c.product_size_id = ps.id 
        JOIN tbl_product p ON ps.product_id = p.id 
        WHERE c.user_id = %s
        """,
        (session['user'],)
    )
    total_amount = sum((item['offer_prize'] or item['prize']) * item['quantity'] for item in cart_items)
    return render_template('user/checkout.html', cart_items=cart_items, total_amount=total_amount)

@user_bp.route('/order-history')
def order_history():
    if 'user' not in session:
        flash('Please login first', 'error')
        return redirect(url_for('user.user_login'))
    
    query = """
        SELECT pm.*, u.first_name, u.last_name 
        FROM tbl_purchase_master pm 
        JOIN tbl_user u ON pm.user_id = u.id 
        WHERE pm.user_id = %s
        ORDER BY pm.created_at DESC
    """
    orders = db.fetchall(query, (session['user'],))
    return render_template('user/order-history.html', orders=orders)

@user_bp.route('/order-details/<int:id>')
def user_order_details(id):
    if 'user' not in session:
        flash('Please login first', 'error')
        return redirect(url_for('user.user_login'))
    
    query_order = """
        SELECT pm.*, u.first_name, u.last_name 
        FROM tbl_purchase_master pm 
        JOIN tbl_user u ON pm.user_id = u.id 
        WHERE pm.id = %s AND pm.user_id = %s
    """
    query_items = """
        SELECT pc.*, p.name, ps.size 
        FROM tbl_purchase_child pc 
        JOIN tbl_product_size ps ON pc.product_size_id = ps.id 
        JOIN tbl_product p ON ps.product_id = p.id 
        WHERE pc.purchase_id = %s
    """
    query_tracking = "SELECT * FROM tbl_tracking WHERE purchase_id = %s ORDER BY created_at DESC"
    order = db.fetchone(query_order, (id, session['user']))
    if not order:
        flash('Order not found', 'error')
        return redirect(url_for('user.order_history'))
    
    order_items = db.fetchall(query_items, (id,))
    tracking = db.fetchall(query_tracking, (id,))
    return render_template('user/order-details.html', order=order, order_items=order_items, tracking=tracking)

@user_bp.route('/logout')
def logout():
    session.pop('user', None)
    flash('Logged out successfully', 'success')
    return redirect(url_for('user.user_login'))