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
    # --- Existing Queries ---
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
    
    # --- 1. Add the query to fetch active banners ---
    # This query selects all banners that are marked as active and orders them by the sort_order column.
    # Note: Ensure your banner table is named 'tbl_banner' or update the name here.
    query_banners = """
        SELECT * FROM tbl_banner 
        WHERE is_active = 1 
        ORDER BY sort_order ASC
    """

    # --- 2. Execute all queries ---
    categories = db.fetchall(query_categories)
    products = db.fetchall(query_products)
    banners = db.fetchall(query_banners) # Fetch the banner data

    # Process product images (your existing logic)
    for product in products:
        product['images_list'] = json.loads(product['images']) if product['images'] else []
        
    # --- 3. Pass the new 'banners' list to the template ---
    return render_template(
        'user/base.html', 
        categories=categories, 
        products=products, 
        banners=banners  # The 'banners' variable is now available in your HTML
    )

@user_bp.route('/products', methods=['GET'])
def products():
    # --- Get all filter parameters from the request URL ---
    category_id = request.args.get('category_id')
    subcategory_id = request.args.get('subcategory_id')
    color_id = request.args.get('color_id')
    shape_id = request.args.get('shape_id')
    sort_by = request.args.get('sort', 'default')
    per_page = request.args.get('per_page', 9, type=int)

    # --- Get price filter parameters ---
    min_price = request.args.get('min_price', type=float)
    max_price = request.args.get('max_price', type=float)

    # --- Fetch data for the filter options ---
    query_categories = "SELECT * FROM tbl_category"
    query_subcategories = "SELECT * FROM tbl_subcategory"
    query_colors = "SELECT id, color_name, color_hex_code FROM master_color"
    query_shapes = "SELECT * FROM master_shape"
    
    # --- Get the absolute maximum price for the slider's range ---
    max_price_query = "SELECT CEIL(MAX(COALESCE(offer_prize, prize))) as max_p FROM tbl_product_size"
    max_price_result = db.fetchone(max_price_query)
    # Use the fetched max price, or default to a high number if no products/prices exist.
    slider_max_price = max_price_result['max_p'] if max_price_result and max_price_result['max_p'] else 300000

    # --- Build the base query for fetching products ---
    query_products_base = """
        SELECT p.*, c.category_name, s.sub_category_name, 
               COALESCE(ps.offer_prize, ps.prize) as effective_price,
               ps.prize, ps.offer_prize,
               mc.color_name, mc.color_hex_code
        FROM tbl_product p 
        JOIN tbl_category c ON p.category_id = c.id 
        JOIN tbl_subcategory s ON p.sub_category_id = s.id 
        LEFT JOIN (
            SELECT product_id, MIN(prize) as prize, MIN(offer_prize) as offer_prize
            FROM tbl_product_size
            GROUP BY product_id
        ) ps ON p.id = ps.product_id
        LEFT JOIN master_color mc ON p.color_id = mc.id
        WHERE p.status = 'active'
    """
    
    # --- Build filter conditions and parameters ---
    conditions = []
    params = []

    if category_id:
        conditions.append("p.category_id = %s")
        params.append(category_id)
    if subcategory_id:
        conditions.append("p.sub_category_id = %s")
        params.append(subcategory_id)
    if color_id:
        conditions.append("p.color_id = %s")
        params.append(color_id)
    if shape_id:
        conditions.append("p.shape_id = %s")
        params.append(shape_id)
    
    if conditions:
        query_products_base += " AND " + " AND ".join(conditions)

    # --- Create final query by wrapping the base to filter by price ---
    final_query = f"SELECT * FROM ({query_products_base}) AS filtered_products WHERE 1=1"
    
    if min_price is not None:
        final_query += " AND effective_price >= %s"
        params.append(min_price)
    if max_price is not None:
        final_query += " AND effective_price <= %s"
        params.append(max_price)

    # --- Total Products Count (must use the final filtered query) ---
    total_products_query = f"SELECT COUNT(*) as total FROM ({final_query}) as subquery"
    total_products = db.fetchone(total_products_query, tuple(params))['total']

    # --- Sorting Logic ---
    if sort_by == 'price_asc':
        final_query += " ORDER BY effective_price ASC, id DESC"
    elif sort_by == 'price_desc':
        final_query += " ORDER BY effective_price DESC, id DESC"
    else:
        final_query += " ORDER BY id DESC"
        
    # --- Execute final queries ---
    products = db.fetchall(final_query, tuple(params))
    categories = db.fetchall(query_categories)
    subcategories = db.fetchall(query_subcategories)
    colors = db.fetchall(query_colors)
    shapes = db.fetchall(query_shapes)

    for product in products:
        product['images_list'] = json.loads(product['images']) if product['images'] and product['images'].strip() else []

    # --- Render the template with all the necessary data ---
    return render_template(
        'user/shop.html', 
        products=products, 
        total_products=total_products,
        categories=categories, 
        subcategories=subcategories,
        colors=colors,
        shapes=shapes,
        selected_category=category_id,
        selected_subcategory=subcategory_id,
        selected_color=color_id,
        selected_shape=shape_id,
        slider_max_price=slider_max_price,
        selected_min_price=min_price,
        selected_max_price=max_price,
        selected_sort=sort_by,
        selected_per_page=per_page
    )
@user_bp.route('/product/<int:id>')
def product_detail(id):
    query_product = """
       SELECT
            p.*,
            c.category_name,
            s.sub_category_name,
            mc.color_name,mc.color_hex_code,
            ms.shape_name
        FROM tbl_product        AS p
        JOIN tbl_category        AS c  ON p.category_id     = c.id
        JOIN tbl_subcategory     AS s  ON p.sub_category_id = s.id
        LEFT JOIN master_color   AS mc ON p.color_id        = mc.id
        LEFT JOIN master_shape   AS ms ON p.shape_id        = ms.id
        WHERE p.id = %s             -- <-- put a real ID here
        AND p.status = 'active';


            """
    # *** MODIFIED QUERY ***
    # Fetch stock_count and purchase_count from tbl_stock
    query_sizes = """
        SELECT 
            ps.*, 
            s.stock_count,
            s.purchase_count,
            ps.prize AS size_price,
            mwu.unit_name AS weight_unit_name
        FROM tbl_product_size ps
        LEFT JOIN tbl_stock s ON ps.id = s.product_size_id
        LEFT JOIN master_weight_unit mwu ON ps.weight_unit_id = mwu.id
        WHERE ps.product_id = %s

            """
    product = db.fetchone(query_product, (id,))
    if not product:
        flash('Product not found or inactive', 'error')
        return redirect(url_for('user.products'))
    
    product['images_list'] = json.loads(product['images']) if product['images'] else []
    sizes = db.fetchall(query_sizes, (id,))
    return render_template('user/product-detail.html', product=product, sizes=sizes)
    

@user_bp.route('/cart/remove/<int:id>', methods=['POST'])
def remove_from_cart(id):
    if 'user' not in session:
        flash('Please login first', 'danger') # 'danger' is a better category for Bootstrap alerts
        return redirect(url_for('user.user_login'))
    
    try:
        # The login_id check is great for security!
        # This execute command works and autocommits.
        db.execute("DELETE FROM tbl_cart WHERE id = %s AND login_id = %s", (id, session['user']))
        
        # REMOVED: db.commit() <-- This line was causing the error and is not needed.
        
        flash('Item removed from cart', 'success')

    except Exception as e:
        # This block will now only catch genuine database errors (e.g., connection lost)
        flash(f'An unexpected error occurred: {str(e)}', 'danger')
        
    return redirect(url_for('user.cart'))


@user_bp.route('/cart', methods=['GET', 'POST'])
def cart():
    if not session.get('user'):
        flash('Please log in to add items to cart.', 'error')
        return redirect(url_for('user.user_login'))
    
    if request.method == 'POST':
        product_id = request.form.get('product_id')
        product_size_id = request.form.get('product_size_id')
        quantity = request.form.get('quantity', 1, type=int)

        # *** NEW: SERVER-SIDE STOCK VALIDATION ***
        try:
            # 1. Check current stock level for the selected size
            stock_query = "SELECT stock_count, purchase_count FROM tbl_stock WHERE product_size_id = %s"
            stock = db.fetchone(stock_query, (product_size_id,))
            
            if not stock:
                flash('This item is not available for purchase (stock not managed).', 'error')
                return redirect(url_for('user.product_detail', id=product_id))

            available_stock = stock['stock_count'] - stock['purchase_count']

            # 2. Check if item is already in cart to calculate total needed
            check_query = "SELECT quantity FROM tbl_cart WHERE login_id = %s AND product_size_id = %s"
            existing_item = db.fetchone(check_query, (session.get('user'), product_size_id))
            
            current_cart_qty = existing_item['quantity'] if existing_item else 0
            total_quantity_needed = current_cart_qty + quantity

            # 3. The final check
            if available_stock < total_quantity_needed:
                flash(f'Not enough stock available. Only {available_stock} items left.', 'error')
                return redirect(url_for('user.product_detail', id=product_id))

            # --- If stock is sufficient, proceed with original logic ---

            if existing_item:
                new_quantity = existing_item['quantity'] + quantity
                update_query = "UPDATE tbl_cart SET quantity = %s, updated_at = CURRENT_TIMESTAMP WHERE id = %s"
                db.execute(update_query, (new_quantity, existing_item['id']))
            else:
                price_query = "SELECT prize FROM tbl_product_size WHERE id = %s"
                price_result = db.fetchone(price_query, (product_size_id,))
                if not price_result or price_result['prize'] is None:
                    flash('Invalid product size selected.', 'error')
                    return redirect(url_for('user.product_detail', id=product_id))
                insert_query = """
                    INSERT INTO tbl_cart (login_id, product_id, product_size_id, quantity, created_at, updated_at, prize)
                    VALUES (%s, %s, %s, %s, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP, %s)
                """
                db.execute(insert_query, (session.get('user'), product_id, product_size_id, quantity, price_result['prize']))

            flash('Item added to cart successfully!', 'success')
            return redirect(url_for('user.cart'))

        except Exception as e:
            flash(f'Error adding to cart: {str(e)}', 'error')
            return redirect(url_for('user.product_detail', id=product_id))

    # ... (the rest of the GET logic for the cart remains the same) ...
    try:
        cart_query = """
            SELECT c.*, ps.size, ps.prize as size_price, p.name as product_name, p.images as product_images
            FROM tbl_cart c
            JOIN tbl_product_size ps ON c.product_size_id = ps.id
            JOIN tbl_product p ON c.product_id = p.id
            WHERE c.login_id = %s
        """
        cart_items = db.fetchall(cart_query, (session.get('user'),))
        for item in cart_items:
            item['images_list'] = json.loads(item['product_images']) if item['product_images'] else []
        
        total_amount = sum(item['size_price'] * item['quantity'] for item in cart_items)
        return render_template('user/cart.html', cart_items=cart_items, total_amount=total_amount)
    except Exception as e:
        flash(f'Error loading cart: {str(e)}', 'error')
        return render_template('user/cart.html', cart_items=[], total_amount=0)
    
@user_bp.route('/checkout', methods=['GET'])
def checkout():
    if 'user' not in session:
        flash('Please login first', 'error')
        return redirect(url_for('user.user_login'))
    
    try:
        cart_items = db.fetchall(
            """
            SELECT c.*, p.name as product_name, ps.size, ps.prize as size_price, p.images as product_images
            FROM tbl_cart c 
            JOIN tbl_product_size ps ON c.product_size_id = ps.id 
            JOIN tbl_product p ON c.product_id = p.id 
            WHERE c.login_id = %s
            """,
            (session['user'],)
        )
        for item in cart_items:
            item['images_list'] = json.loads(item['product_images']) if item['product_images'] else []
        
        total_amount = sum(item['size_price'] * item['quantity'] for item in cart_items)
        
        if not cart_items:
            flash('Your cart is empty', 'error')
            return redirect(url_for('user.cart'))
        
        return render_template('user/checkout.html', cart_items=cart_items, total_amount=total_amount)
    except Exception as e:
        flash(f'Error loading checkout: {str(e)}', 'error')
        return redirect(url_for('user.cart'))
    
import traceback

@user_bp.route('/user-details', methods=['GET', 'POST'])
def user_details():
    if 'user' not in session:
        flash('Please login first', 'error')
        return redirect(url_for('user.user_login'))
    
    user_id = session['user']
    
    if request.method == 'POST':
        # ... (form data retrieval code is fine) ...
        first_name = request.form.get('first_name')
        last_name = request.form.get('last_name')
        shipping_address = request.form.get('shipping_address')
        phone_number = request.form.get('phone_number')
        
        if not all([first_name, last_name, shipping_address, phone_number]):
            flash('All fields are required', 'error')
            return redirect(url_for('user.user_details'))
        
        try:
            # Check if user details already exist
            existing_user = db.fetchone("SELECT * FROM tbl_user WHERE login_id = %s", (user_id,))
            
            if existing_user:
                # Update existing details
                query_update_user = """
                    UPDATE tbl_user 
                    SET first_name = %s, last_name = %s, shipping_address = %s, phone_number = %s
                    WHERE login_id = %s
                """
                db.execute(query_update_user, (first_name, last_name, shipping_address, phone_number, user_id))
                flash('Details updated successfully', 'success')
            else:
                # Insert new details
                query_insert_user = """
                    INSERT INTO tbl_user (login_id, first_name, last_name, shipping_address, phone_number)
                    VALUES (%s, %s, %s, %s, %s)
                """
                db.execute(query_insert_user, (user_id, first_name, last_name, shipping_address, phone_number))
                flash('Details added successfully', 'success')

            # Also use .connection.commit() for consistency
            if hasattr(db, 'connection') and hasattr(db.connection, 'commit'):
                db.connection.commit()

            return redirect(url_for('user.checkout')) # Redirect to checkout after saving details
        
        except Exception as e:
            # *** THE FIX IS HERE ***
            # Call rollback() on the underlying connection object
            try:
                if hasattr(db, 'connection') and hasattr(db.connection, 'rollback'):
                    db.connection.rollback()
                    print("Rollback successful in user_details")
            except Exception as rb_e:
                print(f"Could not perform rollback: {rb_e}")
            
            flash(f'Error saving details: {str(e)}', 'error')
            print(f"Database error: {str(e)}")
            print(traceback.format_exc())
            return redirect(url_for('user.user_details'))
    
    # GET Request Logic...
    try:
        user = db.fetchone("SELECT * FROM tbl_user WHERE login_id = %s", (user_id,))
        if not user:
            user = {'login_id': user_id}
        return render_template('user/user_details.html', user=user)
    except Exception as e:
        flash(f'Error loading user details: {str(e)}', 'error')
        print(f"Error loading user details: {str(e)}")
        print(traceback.format_exc())
        return render_template('user/user_details.html', user={'login_id': user_id})

@user_bp.route('/delete-user-details', methods=['POST'])
def delete_user_details():
    if 'user' not in session:
        flash('Please login first', 'error')
        return redirect(url_for('user.user_login'))
    
    user_id = session['user']
    
    try:
        query_delete_user = """
            DELETE FROM tbl_user WHERE login_id = %s
        """
        print(f"Executing DELETE query: {query_delete_user} with params: {(user_id,)}")
        db.execute(query_delete_user, (user_id,))
        db.connection.commit()
        print("Commit successful")
        flash('Details deleted successfully', 'success')
        return redirect(url_for('user.user_details'))
    except Exception as e:
        print(f"Error deleting user details: {str(e)}")
        print(traceback.format_exc())
        try:
            db.connection.rollback()
            print("Rollback successful")
        except AttributeError:
            print("Warning: No connection.rollback() method available")
        flash(f'Error deleting details: {str(e)}', 'error')
        return redirect(url_for('user.user_details'))


# Helper function to avoid repeating code
def _get_cart_data(user_id):
    """Fetches cart items and calculates total amount for a given user."""
    cart_query = """
        SELECT c.*, p.name as product_name, ps.size, ps.prize as size_price, p.images as product_images
        FROM tbl_cart c 
        JOIN tbl_product_size ps ON c.product_size_id = ps.id 
        JOIN tbl_product p ON c.product_id = p.id 
        WHERE c.login_id = %s
    """
    cart_items = db.fetchall(cart_query, (user_id,))
    
    for item in cart_items:
        item['images_list'] = json.loads(item['product_images']) if item['product_images'] else []
        
    total_amount = sum(item['size_price'] * item['quantity'] for item in cart_items)
    
    return cart_items, total_amount

from decimal import Decimal # Import Decimal for accurate price calculations
from werkzeug.utils import secure_filename
import os

# Configuration
UPLOAD_FOLDER = 'app/static/uploads'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg'}

# Ensure the upload directory exists when the app starts
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# Assuming this is part of a blueprint named user_bp
@user_bp.route('/place-order', methods=['GET', 'POST'])
def place_order():
    if 'user' not in session:
        flash('Please login first', 'error')
        return redirect(url_for('user.user_login'))
    
    user_id = session['user']
    
    try:
        # ... (Your existing code to fetch cart items, user, etc. is fine)
        cart_items_query = """
            SELECT c.*, p.name as product_name, ps.size, ps.prize as size_price, p.images as product_images
            FROM tbl_cart c 
            JOIN tbl_product_size ps ON c.product_size_id = ps.id 
            JOIN tbl_product p ON c.product_id = p.id 
            WHERE c.login_id = %s
        """
        cart_items = db.fetchall(cart_items_query, (user_id,))
        if not cart_items:
            flash('Your cart is empty. Cannot place an order.', 'error')
            return redirect(url_for('user.cart'))

        for item in cart_items:
            item['images_list'] = json.loads(item['product_images']) if item['product_images'] else []
        
        total_amount = sum(Decimal(item['size_price']) * item['quantity'] for item in cart_items)
        
        user = db.fetchone("SELECT * FROM tbl_user WHERE login_id = %s", (user_id,))
        if not user or not all([user.get('id'), user.get('shipping_address')]):
            flash('Please complete your shipping details before placing an order.', 'error')
            return redirect(url_for('user.user_details'))

        bank_details = { 'account_number': '1234567890', 'bank_name': 'Example Bank', 'ifsc_code': 'EXMP0001234', 'account_holder': 'Admin Name' }
        
        if request.method == 'POST':
            query_master = """
                INSERT INTO tbl_purchase_master (user_id, shipping_address, sub_total, tax, taxed_subtotal, status)
                VALUES (%s, %s, %s, %s, %s, %s)
            """
            params_master = (user['id'], user['shipping_address'], total_amount, 0, total_amount, 'ordered')
            purchase_id = db.executeAndReturnId(query_master, params_master)

            if not purchase_id or isinstance(purchase_id, Exception):
                flash('A critical error occurred while creating your order. Please try again.', 'error')
                return redirect(url_for('user.place_order'))
                
            try:
                if 'payment_screenshot' in request.files:
                    file = request.files['payment_screenshot']
                    if file and allowed_file(file.filename):
                        filename = secure_filename(f"{user_id}_{purchase_id}_{file.filename}")
                        # This saves to the correct physical path: 'app/static/uploads/...'
                        file.save(os.path.join(UPLOAD_FOLDER, filename))
                        
                        # <<< THE FIX IS HERE >>>
                        # We create the URL path, which should start from '/static/', not '/app/static/'
                        screenshot_path = f"/static/uploads/{filename}"
                        
                        # Now, the correct URL path is saved to the database
                        db.execute("UPDATE tbl_purchase_master SET payment_image = %s WHERE id = %s", (screenshot_path, purchase_id))
                    elif file:
                        raise ValueError("Invalid file format. Please upload a PNG, JPG, or JPEG.")

                # ... (The rest of your code for inserting child records and updating stock is correct)
                for item in cart_items:
                    unit_prize = Decimal(item['size_price'])
                    quantity = item['quantity']
                    total_prize = unit_prize * quantity
                    query_child = """
                        INSERT INTO tbl_purchase_child (purchase_id, product_size_id, quantity, unit_prize, total_prize, taxed_prize)
                        VALUES (%s, %s, %s, %s, %s, %s)
                    """
                    params_child = (purchase_id, item['product_size_id'], quantity, unit_prize, total_prize, total_prize)
                    db.execute(query_child, params_child)
                    db.execute("UPDATE tbl_stock SET stock_count = stock_count - %s, purchase_count = purchase_count + %s WHERE product_size_id = %s",
                               (quantity, quantity, item['product_size_id']))
                
                initial_tracking_query = "INSERT INTO tbl_tracking (purchase_id, status, date) VALUES (%s, %s, NOW())"
                db.execute(initial_tracking_query, (purchase_id, 'Order Placed'))
                
                db.execute("DELETE FROM tbl_cart WHERE login_id = %s", (user_id,))
                
                flash('Order placed successfully! It will appear in your history after payment verification.', 'success')
                return redirect(url_for('user.order_history'))

            except Exception as e:
                # Rollback logic is fine
                db.execute("DELETE FROM tbl_tracking WHERE purchase_id = %s", (purchase_id,))
                db.execute("DELETE FROM tbl_purchase_child WHERE purchase_id = %s", (purchase_id,))
                db.execute("DELETE FROM tbl_purchase_master WHERE id = %s", (purchase_id,))
                flash(f'An error occurred. Your order was cancelled. Error: {e}', 'error')
                print(traceback.format_exc())
                return redirect(url_for('user.cart'))
        
        return render_template('user/place_order.html', cart_items=cart_items, total_amount=total_amount, user=user, bank_details=bank_details)
    
    except Exception as e:
        flash(f'Error loading the page: {str(e)}', 'error')
        print(traceback.format_exc())
        return redirect(url_for('user.cart'))

@user_bp.route('/order-success/<int:purchase_id>')
def order_success(purchase_id):
    if 'user' not in session:
        flash('Please login first', 'error')
        return redirect(url_for('user.user_login'))
    
    login_id = session['user']

    try:
        # *** FIX: Added security check to ensure the user owns this order ***
        order_query = """
            SELECT pm.*
            FROM tbl_purchase_master pm
            JOIN tbl_user u ON pm.user_id = u.id
            WHERE pm.id = %s AND u.login_id = %s
        """
        order = db.fetchone(order_query, (purchase_id, login_id))

        if not order:
            flash('Order confirmation not found.', 'error')
            return redirect(url_for('user.order_history'))

        order_items_query = """
            SELECT pc.*, p.name as product_name
            FROM tbl_purchase_child pc
            JOIN tbl_product_size ps ON pc.product_size_id = ps.id
            JOIN tbl_product p ON ps.product_id = p.id
            WHERE pc.purchase_id = %s
        """
        order_items = db.fetchall(order_items_query, (purchase_id,))
        
        return render_template('user/order_success.html', order=order, order_items=order_items)

    except Exception as e:
        flash(f'Error loading order confirmation: {str(e)}', 'error')
        return redirect(url_for('user.order_history'))


@user_bp.route('/order-history')
def order_history():
    if 'user' not in session:
        flash('Please login to view your order history.', 'info') # Changed to 'info' for better UX
        return redirect(url_for('user.user_login'))
    
    login_id = session['user']

    try:
        # I have added pm.payment_verify to your existing query.
        orders_query = """
            SELECT 
                pm.id as purchase_id, 
                pm.taxed_subtotal, 
                pm.status,
                pm.payment_verify, -- << THIS IS THE ONLY LINE ADDED
                p.name as product_name,
                p.images as product_images
            FROM 
                tbl_purchase_master pm
            JOIN 
                (
                    SELECT 
                        purchase_id, 
                        MIN(id) as first_child_id
                    FROM 
                        tbl_purchase_child
                    GROUP BY 
                        purchase_id
                ) first_items ON pm.id = first_items.purchase_id
            JOIN 
                tbl_purchase_child pc ON pc.id = first_items.first_child_id
            JOIN 
                tbl_product_size ps ON pc.product_size_id = ps.id
            JOIN 
                tbl_product p ON ps.product_id = p.id
            JOIN 
                tbl_user u ON pm.user_id = u.id
            WHERE 
                u.login_id = %s
            ORDER BY 
                pm.id DESC;
        """
        orders = db.fetchall(orders_query, (login_id,))
        
        # Check for database errors
        if isinstance(orders, Exception):
            flash('Could not retrieve order history due to a database error.', 'error')
            print(f"Database error in order_history: {orders}")
            orders = []

        # Process the images for each order's representative item
        for order in orders:
            order['images_list'] = json.loads(order['product_images']) if order['product_images'] else []
        
        # Now 'orders' contains the payment_verify status for each order,
        # which can be used by the Jinja2 template.
        return render_template('user/order_history.html', orders=orders)

    except Exception as e:
        flash(f'An unexpected error occurred: {str(e)}', 'error')
        print(traceback.format_exc())
        return render_template('user/order_history.html', orders=[])


@user_bp.route('/order-details/<int:id>')
def user_order_details(id):
    if 'user' not in session:
        flash('Please login first', 'error')
        return redirect(url_for('user.user_login'))
    
    login_id = session['user']
    
    try:
        # Security check to ensure the user owns the order
        query_order = """
            SELECT pm.*, u.first_name, u.last_name 
            FROM tbl_purchase_master pm 
            JOIN tbl_user u ON pm.user_id = u.id 
            WHERE pm.id = %s AND u.login_id = %s
        """
        order = db.fetchone(query_order, (id, login_id))
        
        if not order:
            flash('Order not found or you do not have permission to view it.', 'error')
            return redirect(url_for('user.order_history'))
        
        # Fetch order items
        query_items = """
            SELECT pc.*, p.name as product_name, p.images as product_images, ps.size as product_size
            FROM tbl_purchase_child pc 
            JOIN tbl_product_size ps ON pc.product_size_id = ps.id 
            JOIN tbl_product p ON ps.product_id = p.id 
            WHERE pc.purchase_id = %s
        """
        order_items = db.fetchall(query_items, (id,))
        if isinstance(order_items, Exception):
            flash('Error fetching order items.', 'error')
            print(f"DB Error fetching order items: {order_items}")
            order_items = []

        for item in order_items:
            item['images_list'] = json.loads(item['product_images']) if item['product_images'] else []
        
        # *** THE FIX IS HERE ***
        # 1. Changed ORDER BY to use `id` instead of `created_at`.
        # 2. Added robust error checking.
        query_tracking = "SELECT * FROM tbl_tracking WHERE purchase_id = %s ORDER BY id DESC"
        tracking_info = db.fetchall(query_tracking, (id,))
        
        if isinstance(tracking_info, Exception):
            flash('Error fetching tracking information.', 'error')
            print(f"DB Error fetching tracking info: {tracking_info}")
            tracking_info = [] # Set to empty list on error
            
        return render_template('user/order_details.html', order=order, order_items=order_items, tracking_info=tracking_info)
    
    except Exception as e:
        flash(f'An unexpected error occurred while loading order details: {str(e)}', 'error')
        print(traceback.format_exc())
        return redirect(url_for('user.order_history'))
    
@user_bp.route('/logout')
def logout():
    session.pop('user', None)
    flash('Logged out successfully', 'success')
    return redirect(url_for('user.user_login'))