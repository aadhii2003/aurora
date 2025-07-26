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

# In your user_routes.py file
# Make sure to import 'ceil' from the 'math' module at the top of your file
from math import ceil

@user_bp.route('/products', methods=['GET'])
def products():
    # --- Pagination & Per-Page Controls ---
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 9, type=int)
    
    # --- Get all other filter parameters ---
    category_id = request.args.get('category_id')
    subcategory_id = request.args.get('subcategory_id')
    color_id = request.args.get('color_id')
    shape_id = request.args.get('shape_id')
    sort_by = request.args.get('sort', 'default')
    weight_range = request.args.get('weight_range')
    max_price = request.args.get('max_price', type=float)

    # --- Fetch static data for filters ---
    categories = db.fetchall("SELECT * FROM tbl_category")
    subcategories = db.fetchall("SELECT * FROM tbl_subcategory")
    colors = db.fetchall("SELECT * FROM master_color ORDER BY color_name")
    shapes = db.fetchall("SELECT * FROM master_shape ORDER BY shape_name")
    weight_ranges_data = [
        {'value': '0-1', 'label': '0.00-1.00 CT'},
        {'value': '1-2', 'label': '1.00-2.00 CT'},
        {'value': '2-3', 'label': '2.00-3.00 CT'},
        {'value': '4-10', 'label': '4.00-10.00 CT'}
    ]
    per_page_options = [9, 12, 18, 24]
    
    max_price_result = db.fetchone("SELECT CEIL(MAX(COALESCE(offer_prize, prize))) as max_p FROM tbl_product_size")
    slider_max_price = max_price_result['max_p'] if max_price_result and max_price_result['max_p'] else 300000

    # --- Build the base query and filter conditions ---
    query_base = """
        FROM tbl_product p 
        JOIN tbl_category c ON p.category_id = c.id 
        JOIN tbl_subcategory s ON p.sub_category_id = s.id 
        LEFT JOIN tbl_product_size ps ON p.id = ps.product_id
        LEFT JOIN master_color mc ON p.color_id = mc.id
        WHERE p.status = 'active'
    """
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
    if max_price is not None:
        # This condition checks if ANY size of the product is below the max price
        conditions.append("(ps.prize <= %s OR ps.offer_prize <= %s)")
        params.extend([max_price, max_price])
    if weight_range and '-' in weight_range:
        try:
            min_weight, max_weight = map(float, weight_range.split('-'))
            # This condition checks if ANY size of the product is within the weight range
            conditions.append("ps.weight >= %s AND ps.weight <= %s")
            params.extend([min_weight, max_weight])
        except (ValueError, IndexError):
            pass

    if conditions:
        query_base += " AND " + " AND ".join(conditions)

    # --- Get Total Count for Pagination (This query is already correct) ---
    count_query = f"SELECT COUNT(DISTINCT p.id) as total {query_base}"
    total_products = db.fetchone(count_query, tuple(params))['total']

    # --- Build Final Query with GROUP BY to remove duplicates ---
    # MODIFIED: Use aggregate MIN() for price columns to get the "starting from" price
    query_select = """
        SELECT p.*, 
               MIN(COALESCE(ps.offer_prize, ps.prize)) as effective_price, 
               MIN(ps.prize) as prize, 
               MIN(ps.offer_prize) as offer_prize
    """
    
    # MODIFIED: Added GROUP BY p.id at the end of the query
    group_by_clause = " GROUP BY p.id"
    
    final_query = query_select + query_base + group_by_clause

    if sort_by == 'price_asc':
        final_query += " ORDER BY effective_price ASC, p.id DESC"
    elif sort_by == 'price_desc':
        final_query += " ORDER BY effective_price DESC, p.id DESC"
    else:
        final_query += " ORDER BY p.id DESC"
    
    offset = (page - 1) * per_page
    final_query += f" LIMIT {per_page} OFFSET {offset}"
    
    products = db.fetchall(final_query, tuple(params))
    for product in products:
        product['images_list'] = json.loads(product['images']) if product['images'] and product['images'].strip() else []

    # --- Create the Pagination Object Manually (No changes needed here) ---
    class SimplePagination:
        def __init__(self, page, per_page, total_count):
            self.page = page
            self.per_page = per_page
            self.total_count = total_count
            self.pages = int(ceil(total_count / float(per_page))) if per_page > 0 else 0
            self.has_prev = page > 1
            self.has_next = page < self.pages
            self.prev_num = page - 1 if self.has_prev else None
            self.next_num = page + 1 if self.has_next else None
            self.first = (page - 1) * per_page + 1 if total_count > 0 else 0
            self.last = min(page * per_page, total_count)
        
        def iter_pages(self, left_edge=2, left_current=2, right_current=3, right_edge=2):
            last = 0
            for num in range(1, self.pages + 1):
                if num <= left_edge or \
                   (num > self.page - left_current - 1 and num < self.page + right_current) or \
                   num > self.pages - right_edge:
                    if last + 1 != num:
                        yield None
                    yield num
                    last = num
    
    pagination = SimplePagination(page=page, per_page=per_page, total_count=total_products)

    return render_template(
        'user/shop.html', 
        products=products, 
        pagination=pagination,
        per_page_options=per_page_options,
        total_products=total_products,
        categories=categories, 
        subcategories=subcategories,
        colors=colors,
        shapes=shapes,
        weight_ranges=weight_ranges_data,
        selected_category=category_id,
        selected_subcategory=subcategory_id,
        selected_color=color_id,
        selected_shape=shape_id,
        selected_weight_range=weight_range,
        slider_max_price=slider_max_price,
        selected_max_price=max_price,
        selected_sort=sort_by,
        selected_per_page=per_page
    )

import re
def generate_tags(product, sizes):
    """
    Generates a list of relevant tags from product data.
    Uses a set to avoid duplicates automatically.
    """
    tags_set = set()

    # Add core attributes
    if product.get('name'):
        tags_set.add(product['name'].lower())
    if product.get('color_name'):
        tags_set.add(product['color_name'].lower())
        tags_set.add(f"{product['color_name'].lower()} gem")
    if product.get('shape_name'):
        tags_set.add(product['shape_name'].lower())
    if product.get('category_name'):
        tags_set.add(product['category_name'].lower())
    if product.get('sub_category_name'):
        tags_set.add(product['sub_category_name'].lower())
    if product.get('origin'):
        tags_set.add(f"{product['origin'].lower()} origin")
    if product.get('treatment'):
        tags_set.add(product['treatment'].lower())
    
    # Try to extract weight from the first available size option
    if sizes:
        first_size = sizes[0]
        if first_size.get('weight') and first_size.get('weight_unit_name'):
             # e.g., "0.95ct"
            tags_set.add(f"{first_size['weight']}{first_size['weight_unit_name'].lower()}")

    # Clean up tags: remove any empty strings that might have crept in
    # and split any multi-word names into individual tags
    final_tags = set()
    for tag in tags_set:
        # Split tags that might have spaces, e.g., "vivid red" becomes "vivid", "red"
        parts = re.split(r'[\s,]+', tag)
        for part in parts:
            if part: # ensure no empty parts are added
                final_tags.add(part.strip())

    return sorted(list(final_tags)) # Return as a sorted list

@user_bp.route('/product/<int:id>')
def product_detail(id):
    query_product = """
       SELECT
            p.*,
            c.category_name,
            s.sub_category_name,
            mc.color_name, mc.color_hex_code,
            ms.shape_name
        FROM tbl_product        AS p
        JOIN tbl_category        AS c  ON p.category_id     = c.id
        JOIN tbl_subcategory     AS s  ON p.sub_category_id = s.id
        LEFT JOIN master_color   AS mc ON p.color_id        = mc.id
        LEFT JOIN master_shape   AS ms ON p.shape_id        = ms.id
        WHERE p.id = %s
        AND p.status = 'active'
    """
    
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
    
    # --- MODIFIED SECTION ---
    product['images_list'] = json.loads(product['images']) if product['images'] else []
    product['videos_list'] = json.loads(product['videos']) if product['videos'] else []
    
    sizes = db.fetchall(query_sizes, (id,))
    
    # --- NEW: Generate and add tags to the product dictionary ---
    product['generated_tags'] = generate_tags(product, sizes)
    # --- END OF NEW SECTION ---
    
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
        flash('Please log in to manage your cart.', 'error')
        return redirect(url_for('user.user_login'))
    
    login_id = session['user']

    if request.method == 'POST':
        product_id = request.form.get('product_id')
        product_size_id = request.form.get('product_size_id')
        quantity = request.form.get('quantity', 1, type=int)

        try:
            stock_query = "SELECT stock_count, purchase_count FROM tbl_stock WHERE product_size_id = %s"
            stock = db.fetchone(stock_query, (product_size_id,))
            
            if not stock:
                flash('This item is not available for purchase.', 'error')
                return redirect(url_for('user.product_detail', id=product_id))

            available_stock = stock['stock_count'] - stock['purchase_count']

            check_query = "SELECT id, quantity, status FROM tbl_cart WHERE login_id = %s AND product_size_id = %s"
            existing_item = db.fetchone(check_query, (login_id, product_size_id))

            current_cart_qty = 0
            if existing_item and existing_item['status'] != 'rejected':
                current_cart_qty = existing_item['quantity']

            if available_stock < (current_cart_qty + quantity):
                flash(f'Not enough stock available. Only {available_stock} items left.', 'error')
                return redirect(url_for('user.product_detail', id=product_id))

            price_query = "SELECT prize FROM tbl_product_size WHERE id = %s"
            price_result = db.fetchone(price_query, (product_size_id,))
            if not price_result or price_result['prize'] is None:
                flash('Invalid product size selected.', 'error')
                return redirect(url_for('user.product_detail', id=product_id))

            if existing_item and existing_item['status'] != 'rejected':
                new_quantity = existing_item['quantity'] + quantity
                update_query = "UPDATE tbl_cart SET quantity = %s, status = 'pending', updated_at = CURRENT_TIMESTAMP WHERE id = %s"
                db.execute(update_query, (new_quantity, existing_item['id']))
            else:
                insert_query = """
                    INSERT INTO tbl_cart (login_id, product_id, product_size_id, quantity, prize, status, created_at, updated_at)
                    VALUES (%s, %s, %s, %s, %s, 'pending', CURRENT_TIMESTAMP, CURRENT_TIMESTAMP)
                """
                db.execute(insert_query, (login_id, product_id, product_size_id, quantity, price_result['prize']))

            # --- START: NEW ADMIN NOTIFICATION CODE ---
            try:
                user_info = db.fetchone("SELECT email FROM tbl_login WHERE id = %s", (login_id,))
                user_email = user_info['email'] if user_info else 'A user'

                notification_message = f"{user_email} added an item to their cart for approval."
                notification_link = url_for('admin.admin_carts')

                db.execute(
                    "INSERT INTO tbl_admin_notifications (message, link_url) VALUES (%s, %s)",
                    (notification_message, notification_link)
                )
            except Exception as e:
                print(f"--- FAILED TO CREATE ADMIN NOTIFICATION (CART): {e} ---")
            # --- END: NEW ADMIN NOTIFICATION CODE ---

            flash('Item added to cart. Awaiting admin confirmation.', 'info')
            return redirect(url_for('user.cart'))

        except Exception as e:
            flash(f'Error adding to cart: {str(e)}', 'error')
            return redirect(url_for('user.product_detail', id=product_id))

    # --- GET Request Logic (No changes needed here) ---
    try:
        cart_query = """
            SELECT 
                c.id, c.quantity, c.status, c.admin_message,
                ps.size, ps.prize as size_price, 
                p.name as product_name, p.images as product_images
            FROM tbl_cart c
            JOIN tbl_product_size ps ON c.product_size_id = ps.id
            JOIN tbl_product p ON c.product_id = p.id
            WHERE c.login_id = %s
        """
        cart_items = db.fetchall(cart_query, (login_id,))
        
        has_approved_items = False
        total_amount = 0

        for item in cart_items:
            item['images_list'] = json.loads(item['product_images']) if item['product_images'] else []
            if item['status'] == 'approved':
                total_amount += item['size_price'] * item['quantity']
                has_approved_items = True
        
        return render_template('user/cart.html', 
                               cart_items=cart_items, 
                               total_amount=total_amount, 
                               has_approved_items=has_approved_items)
    except Exception as e:
        flash(f'Error loading cart: {str(e)}', 'error')
        return render_template('user/cart.html', cart_items=[], total_amount=0, has_approved_items=False)
    
# @user_bp.route('/checkout', methods=['GET'])
# def checkout():
#     if 'user' not in session:
#         flash('Please login first', 'error')
#         return redirect(url_for('user.user_login'))
    
#     try:
#         cart_items = db.fetchall(
#             """
#             SELECT c.*, p.name as product_name, ps.size, ps.prize as size_price, p.images as product_images
#             FROM tbl_cart c 
#             JOIN tbl_product_size ps ON c.product_size_id = ps.id 
#             JOIN tbl_product p ON c.product_id = p.id 
#             WHERE c.login_id = %s
#             """,
#             (session['user'],)
#         )
#         for item in cart_items:
#             item['images_list'] = json.loads(item['product_images']) if item['product_images'] else []
        
#         total_amount = sum(item['size_price'] * item['quantity'] for item in cart_items)
        
#         if not cart_items:
#             flash('Your cart is empty', 'error')
#             return redirect(url_for('user.cart'))
        
#         return render_template('user/checkout.html', cart_items=cart_items, total_amount=total_amount)
#     except Exception as e:
#         flash(f'Error loading checkout: {str(e)}', 'error')
#         return redirect(url_for('user.cart'))
@user_bp.route('/checkout', methods=['GET', 'POST'])
def checkout():
    if 'user' not in session:
        flash('Please login first', 'error')
        return redirect(url_for('user.user_login'))
    
    user_id = session['user']

    # --- POST block remains the same ---
    if request.method == 'POST':
        # ... your existing POST logic ...
        # No changes needed here
        first_name = request.form.get('first_name')
        last_name = request.form.get('last_name')
        shipping_address = request.form.get('shipping_address')
        phone_number = request.form.get('phone_number')
        city = request.form.get('city')
        state = request.form.get('state')
        country = request.form.get('country')
        pincode = request.form.get('pincode')
        
        if not all([first_name, last_name, shipping_address, phone_number, city, state, country, pincode]):
            flash('All shipping details are required', 'error')
            return redirect(url_for('user.checkout'))

        try:
            existing_user = db.fetchone("SELECT * FROM tbl_user WHERE login_id = %s", (user_id,))
            
            if existing_user:
                query = """
                    UPDATE tbl_user 
                    SET first_name = %s, last_name = %s, shipping_address = %s, 
                        phone_number = %s, city = %s, state = %s, country = %s, pincode = %s
                    WHERE login_id = %s
                """
                params = (first_name, last_name, shipping_address, phone_number, city, state, country, pincode, user_id)
                db.execute(query, params)
                flash('Details updated successfully!', 'success')
            else:
                query = """
                    INSERT INTO tbl_user (
                        login_id, first_name, last_name, shipping_address, 
                        phone_number, city, state, country, pincode
                    ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
                """
                params = (user_id, first_name, last_name, shipping_address, phone_number, city, state, country, pincode)
                db.execute(query, params)
                flash('Details saved successfully!', 'success')
            
            return redirect(url_for('user.checkout'))
        except Exception as e:
            flash(f'Error saving details: {str(e)}', 'error')
            print(f"Database error in checkout POST: {str(e)}")
            print(traceback.format_exc())
            return redirect(url_for('user.checkout'))
    
    # --- GET: REVISED BLOCK WITH DEBUGGING ---
    try:
        # 1. Load country data with robust error checking
        countries_data = []
        resource_path = 'static/data/countries.json' # <-- DOUBLE CHECK THIS FILENAME!
        print(f"--- DEBUG: Attempting to load resource: {resource_path} ---")

        try:
            with current_app.open_resource(resource_path, 'r') as f:
                countries_data = json.load(f)
            
            print(f"--- DEBUG: Successfully loaded {len(countries_data)} countries. ---")
            if countries_data:
                # Print the first country to verify structure
                print(f"--- DEBUG: First country data: {countries_data[0]} ---")

        except FileNotFoundError:
            print(f"--- DEBUG: ERROR! File not found at path: {resource_path} ---")
            flash('Country data file not found. Please contact support.', 'error')
        except json.JSONDecodeError as e:
            print(f"--- DEBUG: ERROR! JSON is invalid in {resource_path}. Error: {e} ---")
            flash('Error reading country data. Please contact support.', 'error')
        
        # 2. Fetch cart items (No change)
        cart_items_query = """
            SELECT c.*, p.name as product_name, ps.size, ps.prize as size_price, p.images as product_images
            FROM tbl_cart c 
            JOIN tbl_product_size ps ON c.product_size_id = ps.id 
            JOIN tbl_product p ON c.product_id = p.id 
            WHERE c.login_id = %s AND c.status = 'approved'
        """
        cart_items = db.fetchall(cart_items_query, (user_id,))
        
        if not cart_items and request.method == 'GET':
            flash('You have no approved items to check out.', 'warning')
            return redirect(url_for('user.cart'))

        for item in cart_items:
            item['images_list'] = json.loads(item['product_images']) if item['product_images'] else []
        
        total_amount = sum(Decimal(item['size_price']) * item['quantity'] for item in cart_items)

        # 3. Fetch User Details (No change)
        user_details = db.fetchone("SELECT * FROM tbl_user WHERE login_id = %s", (user_id,))
        if not user_details:
            user_details = {'login_id': user_id}

        # 4. Render the page
        return render_template('user/checkout.html', 
                               cart_items=cart_items, 
                               total_amount=total_amount, 
                               user=user_details,
                               countries_data=countries_data)
                               
    except Exception as e:
        flash(f'Error loading checkout page: {str(e)}', 'error')
        print(f"Error loading checkout GET: {str(e)}")
        print(traceback.format_exc())
        return redirect(url_for('user.cart'))
    
import traceback

@user_bp.route('/user-details', methods=['GET', 'POST'])
def user_details():
    if 'user' not in session:
        flash('Please login first', 'error')
        return redirect(url_for('user.user_login'))
    
    user_id = session['user']
    
    if request.method == 'POST':
        # Retrieve form data
        first_name = request.form.get('first_name')
        last_name = request.form.get('last_name')
        shipping_address = request.form.get('shipping_address')
        phone_number = request.form.get('phone_number')
        city = request.form.get('city')
        state = request.form.get('state')
        country = request.form.get('country')
        pincode = request.form.get('pincode')
        
        # Validate all fields
        if not all([first_name, last_name, shipping_address, phone_number, city, state, country, pincode]):
            flash('All fields are required', 'error')
            return redirect(url_for('user.user_details'))
        
        try:
            # Check if user details already exist
            existing_user = db.fetchone("SELECT * FROM tbl_user WHERE login_id = %s", (user_id,))
            print(f"Existing user check: {existing_user}")
            
            if existing_user:
                # Update existing details
                query_update_user = """
                    UPDATE tbl_user 
                    SET first_name = %s, last_name = %s, shipping_address = %s, 
                        phone_number = %s, city = %s, state = %s, country = %s, pincode = %s
                    WHERE login_id = %s
                """
                print(f"Executing update: {query_update_user} with params: {(first_name, last_name, shipping_address, phone_number, city, state, country, pincode, user_id)}")
                db.execute(query_update_user, (
                    first_name, last_name, shipping_address, phone_number,
                    city, state, country, pincode, user_id
                ))
                flash('Details updated successfully', 'success')
            else:
                # Insert new details
                query_insert_user = """
                    INSERT INTO tbl_user (
                        login_id, first_name, last_name, shipping_address, 
                        phone_number, city, state, country, pincode
                    )
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
                """
                print(f"Executing insert: {query_insert_user} with params: {(user_id, first_name, last_name, shipping_address, phone_number, city, state, country, pincode)}")
                db.execute(query_insert_user, (
                    user_id, first_name, last_name, shipping_address,
                    phone_number, city, state, country, pincode
                ))
                flash('Details added successfully', 'success')

            # Attempt to commit (adjust based on your db library)
            try:
                if hasattr(db, 'commit'):  # Check if db has a commit method
                    db.commit()
                    print("Database commit successful")
                elif hasattr(db, 'session') and hasattr(db.session, 'commit'):  # For SQLAlchemy-like objects
                    db.session.commit()
                    print("Database session commit successful")
                else:
                    print("No commit method found, assuming autocommit")
            except Exception as commit_error:
                print(f"Commit failed: {commit_error}")
                raise

            return redirect(url_for('user.checkout'))
        
        except Exception as e:
            # Attempt to rollback if possible
            try:
                if hasattr(db, 'rollback'):  # Check if db has a rollback method
                    db.rollback()
                    print("Rollback successful in user_details")
                elif hasattr(db, 'session') and hasattr(db.session, 'rollback'):  # For SQLAlchemy-like objects
                    db.session.rollback()
                    print("Session rollback successful in user_details")
            except Exception as rb_e:
                print(f"Could not perform rollback: {rb_e}")
            
            flash(f'Error saving details: {str(e)}', 'error')
            print(f"Database error: {str(e)}")
            print(traceback.format_exc())
            return redirect(url_for('user.user_details'))
    
    # GET Request Logic
    try:
        user = db.fetchone("SELECT * FROM tbl_user WHERE login_id = %s", (user_id,))
        print(f"User data fetched: {user}")
        if not user:
            user = {'login_id': user_id}
        return render_template('user/user_details.html', user=user)
    except Exception as e:
        flash(f'Error loading user details: {str(e)}', 'error')
        print(f"Error loading user details: {str(e)}")
        print(traceback.format_exc())
        return render_template('user/user_details.html', user={'login_id': user_id})

# import traceback
# @user_bp.route('/checkout', methods=['GET', 'POST'])
# def checkout():
#     if 'user' not in session:
#         flash('Please login to proceed.', 'danger')
#         return redirect(url_for('user.user_login'))

#     user_id = session['user']

#     # --- HANDLE FORM SUBMISSION TO UPDATE/ADD USER DETAILS ---
#     if request.method == 'POST':
#         first_name = request.form.get('first_name')
#         last_name = request.form.get('last_name')
#         shipping_address = request.form.get('shipping_address')
#         phone_number = request.form.get('phone_number')
#         city = request.form.get('city')
#         state = request.form.get('state')
#         country = request.form.get('country')
#         pincode = request.form.get('pincode')

#         if not all([first_name, last_name, shipping_address, phone_number, city, state, country, pincode]):
#             flash('All shipping fields are required to proceed.', 'error')
#             # Fall through to the GET logic to re-render the page with an error
#         else:
#             try:
#                 existing_user = db.fetchone("SELECT id FROM tbl_user WHERE login_id = %s", (user_id,))
                
#                 if existing_user:
#                     query_update = """
#                         UPDATE tbl_user SET first_name=%s, last_name=%s, shipping_address=%s, 
#                                             phone_number=%s, city=%s, state=%s, country=%s, pincode=%s
#                         WHERE login_id = %s
#                     """
#                     db.execute(query_update, (first_name, last_name, shipping_address, phone_number, city, state, country, pincode, user_id))
#                     flash('Shipping details updated successfully!', 'success')
#                 else:
#                     query_insert = """
#                         INSERT INTO tbl_user (login_id, first_name, last_name, shipping_address, 
#                                               phone_number, city, state, country, pincode)
#                         VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
#                     """
#                     db.execute(query_insert, (user_id, first_name, last_name, shipping_address, phone_number, city, state, country, pincode))
#                     flash('Shipping details saved successfully!', 'success')
                
#                 # No commit needed as per your DB setup
#                 return redirect(url_for('user.checkout')) # Redirect to refresh the page with updated details
            
#             except Exception as e:
#                 flash(f'An error occurred while saving your details: {str(e)}', 'error')
#                 print(f"Checkout POST Error: {e}")

#     # --- GET REQUEST LOGIC (FETCH EVERYTHING FOR THE PAGE) ---
#     try:
#         # 1. Fetch APPROVED cart items for the order summary
#         cart_items = db.fetchall(
#             """
#             SELECT c.quantity, p.name as product_name, ps.size, ps.prize as size_price, p.images as product_images
#             FROM tbl_cart c 
#             JOIN tbl_product_size ps ON c.product_size_id = ps.id 
#             JOIN tbl_product p ON c.product_id = p.id 
#             WHERE c.login_id = %s AND c.status = 'approved'
#             """,
#             (user_id,)
#         )
        
#         # If no approved items, they can't check out
#         if not cart_items:
#             flash('You have no approved items in your cart. Please wait for admin approval or add items.', 'warning')
#             return redirect(url_for('user.cart'))
        
#         for item in cart_items:
#             item['images_list'] = json.loads(item['product_images']) if item['product_images'] else []
        
#         total_amount = sum(item['size_price'] * item.get('quantity', 0) for item in cart_items)
        
#         # 2. Fetch user's existing shipping details
#         user_details = db.fetchone("SELECT * FROM tbl_user WHERE login_id = %s", (user_id,))
#         if not user_details:
#             # Create a blank dictionary so the template doesn't error out
#             user_details = {}

#         # 3. Render the single, combined checkout page
#         return render_template(
#             'user/checkout_combined.html', 
#             cart_items=cart_items, 
#             total_amount=total_amount,
#             user=user_details
#         )
        
#     except Exception as e:
#         flash(f'Error loading checkout page: {str(e)}', 'error')
#         print(f"Checkout GET Error: {e}")
#         return redirect(url_for('user.cart'))

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
# /user/routes.py (or wherever your route is)

@user_bp.route('/place-order', methods=['GET', 'POST'])
def place_order():
    if 'user' not in session:
        flash('Please login first', 'error')
        return redirect(url_for('user.user_login'))
    
    user_id = session['user']
    
    try:
        cart_items_query = """
            SELECT c.*, p.name as product_name, ps.size, ps.prize as size_price, p.images as product_images
            FROM tbl_cart c 
            JOIN tbl_product_size ps ON c.product_size_id = ps.id 
            JOIN tbl_product p ON c.product_id = p.id 
            WHERE c.login_id = %s AND c.status = 'approved'
        """
        cart_items = db.fetchall(cart_items_query, (user_id,))
        
        if not cart_items:
            flash('You have no approved items to order. Cannot place an order.', 'error')
            return redirect(url_for('user.cart'))

        for item in cart_items:
            item['images_list'] = json.loads(item['product_images']) if item['product_images'] else []
        
        total_amount = sum(Decimal(item['size_price']) * item['quantity'] for item in cart_items)
        
        user = db.fetchone("SELECT * FROM tbl_user WHERE login_id = %s", (user_id,))

        if not user or not user.get('id') or not user.get('shipping_address'):
            flash('Please complete your shipping details before placing an order.', 'error')
            return redirect(url_for('user.checkout'))

        bank_details = {
            'account_number': '176-8-90907-1',
            'bank_name': 'KASIKORNBANK',
            'swift_code': 'KASITHBK',
            'account_name': 'Arunrat Changtongmadun',
            'bank_address': '919/1 ROOMJEWELRYTRADE CENTER BUILDINGSILOM ROAD SILOM. BANGRAKBANGKOK 10500 THAILAND',
            'wise_email': 'spinel.aurora@gmail.com'
        }
        
        if request.method == 'POST':
            query_master = """
                INSERT INTO tbl_purchase_master (user_id, shipping_address, sub_total, tax, taxed_subtotal, status)
                VALUES (%s, %s, %s, %s, %s, %s)
            """
            params_master = (user['id'], user['shipping_address'], total_amount, 0, total_amount, 'ordered')
            purchase_id = db.executeAndReturnId(query_master, params_master)

            if not purchase_id or isinstance(purchase_id, Exception):
                flash('A critical error occurred while creating your order. Please try again.', 'error')
                return redirect(url_for('user.checkout'))
                
            try:
                if 'payment_screenshot' in request.files:
                    file = request.files['payment_screenshot']
                    if file and allowed_file(file.filename):
                        filename = secure_filename(f"{user_id}_{purchase_id}_{file.filename}")
                        file.save(os.path.join(UPLOAD_FOLDER, filename))
                        screenshot_path = f"/static/uploads/{filename}"
                        db.execute("UPDATE tbl_purchase_master SET payment_image = %s WHERE id = %s", (screenshot_path, purchase_id))
                    elif file:
                        raise ValueError("Invalid file format. Please upload a PNG, JPG, or JPEG.")

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
                    
                    db.execute("UPDATE tbl_stock SET purchase_count = purchase_count + %s WHERE product_size_id = %s",
                              (quantity, item['product_size_id']))
                
                initial_tracking_query = "INSERT INTO tbl_tracking (purchase_id, status, date) VALUES (%s, %s, NOW())"
                db.execute(initial_tracking_query, (purchase_id, 'Order Placed'))
                
                db.execute("DELETE FROM tbl_cart WHERE login_id = %s AND status = 'approved'", (user_id,))
                
                # --- START: NEW ADMIN NOTIFICATION CODE ---
                try:
                    user_email = user.get('email', 'A user')
                    notification_message = f"New Order #{purchase_id} was placed by {user_email}."
                    notification_link = url_for('admin.order_details', id=purchase_id)
                    
                    db.execute(
                        "INSERT INTO tbl_admin_notifications (message, link_url) VALUES (%s, %s)",
                        (notification_message, notification_link)
                    )
                except Exception as e:
                    print(f"--- FAILED TO CREATE ADMIN NOTIFICATION (ORDER): {e} ---")
                # --- END: NEW ADMIN NOTIFICATION CODE ---

                flash('Order placed successfully! It will appear in your history after payment verification.', 'success')
                return redirect(url_for('user.order_history'))

            except Exception as e:
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

@user_bp.route('/about')
def about():
    return render_template('user/about.html')

@user_bp.route('/contact', methods=['GET', 'POST'])
def contact():
    if request.method == 'POST':
        try:
            # Get data from the contact form
            first_name = request.form.get('first_name')
            last_name = request.form.get('last_name')
            email = request.form.get('email')
            message = request.form.get('message')
            
            # Combine first and last name
            full_name = f"{first_name} {last_name}".strip()

            if not all([full_name, email, message]):
                flash('Please fill out all required fields.', 'error')
                return redirect(url_for('user.contact'))

            # Insert into the new inquiries table
            query = """
                INSERT INTO tbl_inquiries (type, name, email, message)
                VALUES (%s, %s, %s, %s)
            """
            db.execute(query, ('Contact', full_name, email, message))

            flash('Thank you for your message! We will get back to you soon.', 'success')
            return redirect(url_for('user.contact'))

        except Exception as e:
            flash(f'An error occurred: {str(e)}', 'error')
            return redirect(url_for('user.contact'))
    
    # This is the original GET request logic
    return render_template('user/contact.html')

@user_bp.route('/subscribe', methods=['POST'])
def subscribe():
    try:
        # Get data from the subscription form
        name = request.form.get('name')
        email = request.form.get('email')

        if not all([name, email]):
            flash('Please provide both name and email to subscribe.', 'error')
            # Redirect user back to the page they came from
            return redirect(request.referrer or url_for('user.user_home'))

        # Insert into the new inquiries table
        query = """
            INSERT INTO tbl_inquiries (type, name, email)
            VALUES (%s, %s, %s)
        """
        db.execute(query, ('Subscription', name, email))
        
        flash('Thank you for subscribing to our newsletter!', 'success')
        return redirect(request.referrer or url_for('user.user_home'))

    except Exception as e:
        flash(f'An error occurred during subscription: {str(e)}', 'error')
        return redirect(request.referrer or url_for('user.user_home'))
    
@user_bp.route('/notify-me', methods=['POST'])
def notify_admin_stock():
    # Ensure user is logged in to make a request
    if 'user' not in session:
        flash('Please log in to request a stock notification.', 'warning')
        return redirect(url_for('user.user_login'))

    try:
        login_id = session['user']
        product_size_id = request.form.get('product_size_id')

        if not product_size_id:
            flash('Invalid product selection for notification.', 'error')
            return redirect(request.referrer or url_for('user.products'))

        # Query to get user and product details for a clear notification message
        query = """
            SELECT u.email, p.name as product_name, ps.size
            FROM tbl_login u, tbl_product_size ps
            JOIN tbl_product p ON ps.product_id = p.id
            WHERE u.id = %s AND ps.id = %s
        """
        details = db.fetchone(query, (login_id, product_size_id))

        if not details:
            flash('Could not find details for the notification request.', 'error')
            return redirect(request.referrer)
        
        # Create a detailed message for the admin
        user_email = details['email']
        product_name = details['product_name']
        product_size_label = f"(Size: {details['size']})" if details['size'] else ""
        
        notification_message = f"User {user_email} requested a stock alert for: {product_name} {product_size_label}."
        
        # Link to the admin's general stock management page
        notification_link = url_for('admin.admin_update_stock', _external=True)

        # Insert the notification into the database
        db.execute(
            "INSERT INTO tbl_admin_notifications (message, link_url) VALUES (%s, %s)",
            (notification_message, notification_link)
        )

        flash('Thank you! The admin has been notified. We will contact you when the item is back in stock.', 'success')

    except Exception as e:
        print(f"--- ERROR in notify_admin_stock: {e} ---")
        flash('An error occurred while sending the notification.', 'error')

    return redirect(request.referrer or url_for('user.products'))