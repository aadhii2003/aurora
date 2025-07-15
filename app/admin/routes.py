from flask import render_template, request, redirect, url_for, session, flash,current_app
from werkzeug.utils import secure_filename
import json
import os
import uuid
from . import admin_bp
from app import db
from app.utilities import queries
import time
import traceback
import pymysql



@admin_bp.route('/', methods=['GET', 'POST'])
def admin_login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        admin=db.fetchone(queries.ADMIN_LOGIN, (email, password))
        if admin:
            session['admin_id'] = admin['id']
            return redirect(url_for('admin.admin_home'))
        flash('Invalid credentials', 'error')
    return render_template('admin/admin-login.html')

# In your admin blueprint file, replace the existing admin_home function

from datetime import datetime, timedelta
import traceback # Import traceback to get detailed error info

@admin_bp.route('/admin-home', methods=['GET'])
def admin_home():
    if 'admin_id' not in session:
        flash('Please login first', 'error')
        return redirect(url_for('admin.admin_login'))

    print("\n--- LOADING ADMIN DASHBOARD (With Correct Schema) ---")

    try:
        # --- 1. KPI Cards Data ---
        print("1. Fetching KPI data...")
        query_revenue = "SELECT SUM(taxed_subtotal) as total FROM tbl_purchase_master "
        revenue_result = db.fetchone(query_revenue)
        total_revenue = revenue_result['total'] if revenue_result and revenue_result['total'] is not None else 0
        print(f"   - Total Revenue: {total_revenue}")

        query_orders = "SELECT COUNT(id) as count FROM tbl_purchase_master"
        orders_result = db.fetchone(query_orders)
        total_orders = orders_result['count'] if orders_result else 0
        print(f"   - Total Orders: {total_orders}")
        
        query_users = "SELECT COUNT(id) as count FROM tbl_user"
        users_result = db.fetchone(query_users)
        total_users = users_result['count'] if users_result else 0
        print(f"   - Total Users: {total_users}")
        
        query_products = "SELECT COUNT(id) as count FROM tbl_product WHERE status = 'active'"
        products_result = db.fetchone(query_products)
        total_products = products_result['count'] if products_result else 0
        print(f"   - Total Products: {total_products}")

        # --- 2. Recent Orders Data (Using the new 'purchase_date' column) ---
        print("2. Fetching recent orders...")
        query_recent_orders = """
            SELECT 
                pm.id, 
                pm.taxed_subtotal, 
                pm.status, 
                pm.purchase_date,  -- This will now work
                u.first_name, 
                u.last_name
            FROM tbl_purchase_master pm
            JOIN tbl_user u ON pm.user_id = u.id
            ORDER BY pm.id DESC 
            LIMIT 5
        """
        recent_orders_result = db.fetchall(query_recent_orders)
        
        if isinstance(recent_orders_result, Exception):
            raise recent_orders_result
        
        recent_orders = recent_orders_result
        print(f"   - Found {len(recent_orders)} recent orders.")

        # --- 3. Chart Data (Using the new 'purchase_date' column) ---
        print("3. Fetching chart data...")
        
        sales_labels = []
        sales_values = []
        today = datetime.utcnow().date()
        for i in range(29, -1, -1):
            day = today - timedelta(days=i)
            query_daily_sales = "SELECT SUM(taxed_subtotal) as daily_total FROM tbl_purchase_master WHERE DATE(purchase_date) = %s AND status = 'Delivered'"
            result = db.fetchone(query_daily_sales, (day,))
            if isinstance(result, Exception): raise result
            
            daily_sales = result['daily_total'] if result and result['daily_total'] is not None else 0
            sales_labels.append(day.strftime('%b %d'))
            sales_values.append(float(daily_sales))

        sales_chart_data = {"labels": sales_labels, "values": sales_values}
        print(f"   - Sales Chart Data: {len(sales_chart_data['labels'])} labels.")

        query_status_counts = "SELECT status, COUNT(id) as count FROM tbl_purchase_master GROUP BY status"
        status_results = db.fetchall(query_status_counts)
        if isinstance(status_results, Exception): raise status_results

        order_status_data = {
            "labels": [row['status'] for row in status_results],
            "values": [row['count'] for row in status_results]
        }
        print(f"   - Order Status Data: {order_status_data}")
        
        print("--- DASHBOARD DATA FETCHED SUCCESSFULLY ---\n")

        # The HTML template already uses `order.purchase_date` from my last full code example.
        return render_template(
            'admin/admin-home.html',
            title='Admin Dashboard',
            total_revenue=total_revenue,
            total_orders=total_orders,
            total_users=total_users,
            total_products=total_products,
            recent_orders=recent_orders,
            sales_chart_data=sales_chart_data,
            order_status_data=order_status_data
        )

    except Exception as e:
        print("\n!!! EXCEPTION CAUGHT IN ADMIN DASHBOARD ROUTE !!!")
        print(traceback.format_exc())
        print("!!! END OF EXCEPTION !!!\n")
        
        flash(f"A critical error occurred while loading the dashboard. Please check server logs. Error: {e}", 'error')
        return render_template(
            'admin/admin-home.html',
            title='Admin Dashboard - Error',
            total_revenue=0, total_orders=0, total_users=0, total_products=0,
            recent_orders=[],
            sales_chart_data={"labels": [], "values": []},
            order_status_data={"labels": [], "values": []}
        )

BANNER_UPLOAD_FOLDER = 'app/static/uploads/banners'

# Ensure the banner upload folder exists
if not os.path.exists(BANNER_UPLOAD_FOLDER):
    os.makedirs(BANNER_UPLOAD_FOLDER)

# --- 2. REUSE YOUR HELPER FUNCTION ---
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


@admin_bp.route('/banners', methods=['GET', 'POST'])
def manage_banners():
    if 'admin_id' not in session:
        flash('Please login first', 'error')
        return redirect(url_for('admin.admin_login'))

    # Handle the form submission to ADD a new banner
    if request.method == 'POST':
        title = request.form.get('title')
        content = request.form.get('content')
        is_active = 1 if 'is_active' in request.form else 0
        sort_order = request.form.get('sort_order', 0)
        image = request.files.get('image')

        # --- Validation (following your product route's pattern) ---
        if not title:
            flash('Title is required.', 'danger')
            return redirect(url_for('admin.manage_banners'))
        
        if not image or image.filename == '':
            flash('Image file is required.', 'danger')
            return redirect(url_for('admin.manage_banners'))

        if image and allowed_file(image.filename):
            # Create a unique filename, just like in your product route
            filename = secure_filename(image.filename)
            unique_filename = f"{uuid.uuid4().hex}_{filename}"
            
            # Save the file to the BANNER_UPLOAD_FOLDER
            file_path = os.path.join(BANNER_UPLOAD_FOLDER, unique_filename)
            image.save(file_path)
            
            # Create the relative URL to store in the database
            image_url = f'/static/uploads/banners/{unique_filename}'

            # Insert into database
            try:
                query = """
                    INSERT INTO tbl_banner (title, content, image_url, is_active, sort_order) 
                    VALUES (%s, %s, %s, %s, %s)
                """
                db.execute(query, (title, content, image_url, is_active, sort_order))
                flash('Banner added successfully!', 'success')
            except Exception as e:
                flash(f'Database error: Could not add banner. Error: {e}', 'danger')
                # Clean up the saved file if the database insert fails
                if os.path.exists(file_path):
                    os.remove(file_path)
        else:
            flash('Invalid image file type. Allowed types are: png, jpg, jpeg, gif, webp', 'danger')
        
        return redirect(url_for('admin.manage_banners'))

    # For a GET request, fetch and display all existing banners
    banners = []
    try:
        query_all_banners = "SELECT * FROM tbl_banner ORDER BY sort_order ASC, id DESC"
        banners = db.fetchall(query_all_banners)
    except Exception as e:
        flash(f'Database error: Could not fetch banners. Error: {e}', 'danger')

    return render_template('admin/banners.html', banners=banners)


# --- 4. REFACTORED BANNER DELETE ROUTE (more robust) ---
@admin_bp.route('/banners/delete/<int:banner_id>', methods=['POST'])
def delete_banner(banner_id):
    if 'admin_id' not in session:
        flash('Please login first', 'error')
        return redirect(url_for('admin.admin_login'))

    try:
        # First, get the image_url to delete the file from the server
        query_get_banner = "SELECT image_url FROM tbl_banner WHERE id = %s"
        banner = db.fetchone(query_get_banner, (banner_id,))

        if banner and banner.get('image_url'):
            # Extract just the filename from the URL
            filename_only = os.path.basename(banner['image_url'])
            # Construct the full server path using our reliable folder variable
            image_server_path = os.path.join(BANNER_UPLOAD_FOLDER, filename_only)
            
            if os.path.exists(image_server_path):
                os.remove(image_server_path)

        # Delete the banner record from the database
        query_delete = "DELETE FROM tbl_banner WHERE id = %s"
        db.execute(query_delete, (banner_id,))
        
        flash('Banner deleted successfully!', 'success')
    except Exception as e:
        flash(f'Could not delete banner. A database error occurred: {e}', 'danger')

    return redirect(url_for('admin.manage_banners'))

# Category Management
@admin_bp.route('/admin-category', methods=['GET', 'POST'])
def admin_category():
    # if 'admin_id' not in session:
    #     flash('Please login first', 'error')
    #     return redirect(url_for('admin.admin_login'))
    
    # Handle both add and edit in the same route
    if request.method == 'POST':
        category_name = request.form['category_name']
        category_id = request.form.get('category_id')  # Get category_id if editing
        
        if category_id:  # Update existing category
            query = "UPDATE tbl_category SET category_name = %s WHERE id = %s"
            try:
                db.execute(query, (category_name, category_id))
                flash('Category updated successfully', 'success')
            except Exception as e:
                flash(f'Error updating category: {str(e)}', 'error')
        else:  # Add new category
            query = "INSERT INTO tbl_category (category_name) VALUES (%s)"
            try:
                db.execute(query, (category_name,))
                flash('Category added successfully', 'success')
            except Exception as e:
                flash(f'Error adding category: {str(e)}', 'error')
        return redirect(url_for('admin.admin_category'))
    
    query = "SELECT * FROM tbl_category"
    categories = db.fetchall(query)
    return render_template('admin/admin-category.html', categories=categories)

@admin_bp.route('/admin-category/delete/<int:id>')
def delete_category(id):
    if 'admin_id' not in session:
        flash('Please login first', 'error')
        return redirect(url_for('admin.admin_login'))
    
    query = "DELETE FROM tbl_category WHERE id = %s"
    try:
        db.execute(query, (id,))
        flash('Category deleted successfully', 'success')
    except Exception as e:
        flash(f'Error deleting category: {str(e)}', 'error')
    return redirect(url_for('admin.admin_category'))

# Subcategory Management
@admin_bp.route('/admin-subcategory', methods=['GET', 'POST'])
def admin_subcategory():
    # if 'admin_id' not in session:
    #     flash('Please login first', 'error')
    #     return redirect(url_for('admin.admin_login'))
    
    if request.method == 'POST':
        category_id = request.form['category_id']
        sub_category_name = request.form['sub_category_name']
        subcategory_id = request.form.get('subcategory_id')  # Get subcategory_id if editing
        
        if subcategory_id:  # Update existing subcategory
            query = "UPDATE tbl_subcategory SET category_id = %s, sub_category_name = %s WHERE id = %s"
            try:
                db.execute(query, (category_id, sub_category_name, subcategory_id))
                flash('Subcategory updated successfully', 'success')
            except Exception as e:
                flash(f'Error updating subcategory: {str(e)}', 'error')
        else:  # Add new subcategory
            query = "INSERT INTO tbl_subcategory (category_id, sub_category_name) VALUES (%s, %s)"
            try:
                db.execute(query, (category_id, sub_category_name))
                flash('Subcategory added successfully', 'success')
            except Exception as e:
                flash(f'Error adding subcategory: {str(e)}', 'error')
        return redirect(url_for('admin.admin_subcategory'))
    
    query_categories = "SELECT * FROM tbl_category"
    query_subcategories = """
        SELECT s.*, c.category_name 
        FROM tbl_subcategory s 
        JOIN tbl_category c ON s.category_id = c.id
    """
    categories = db.fetchall(query_categories)
    subcategories = db.fetchall(query_subcategories)
    return render_template('admin/admin-subcategory.html', categories=categories, subcategories=subcategories)

@admin_bp.route('/admin-subcategory/delete/<int:id>')
def delete_subcategory(id):
    if 'admin_id' not in session:
        flash('Please login first', 'error')
        return redirect(url_for('admin.admin_login'))
    
    query = "DELETE FROM tbl_subcategory WHERE id = %s"
    try:
        db.execute(query, (id,))
        flash('Subcategory deleted successfully', 'success')
    except Exception as e:
        flash(f'Error deleting subcategory: {str(e)}', 'error')
    return redirect(url_for('admin.admin_subcategory'))

# Product Management
# Configure upload folder
UPLOAD_FOLDER = 'app/static/admin/img'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'webp'}

# Ensure the upload folder exists
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@admin_bp.route('/admin-product', methods=['GET', 'POST'])
def admin_product():
    if 'admin_id' not in session:
        flash('Please login first', 'error')
        return redirect(url_for('admin.admin_login'))
    
    # --- HANDLE FORM SUBMISSION (POST REQUEST) ---
    if request.method == 'POST':
        # Retrieve all form data, including new fields
        name = request.form.get('name')
        description = request.form.get('description')
        style = request.form.get('style')
        category_id = request.form.get('category_id')
        sub_category_id = request.form.get('sub_category_id')
        status = request.form.get('status')
        updated_by = session['admin_id']
        color_id = request.form.get('color_id')
        shape_id = request.form.get('shape_id')
        
        # --- Handle the three separate image file inputs ---
        image_paths = []
        for i in range(1, 4):  # Loop to check for image1, image2, image3
            input_name = f'image{i}'
            if input_name in request.files:
                file = request.files[input_name]
                if file and allowed_file(file.filename):
                    filename = secure_filename(file.filename)
                    unique_filename = f"{uuid.uuid4().hex}_{filename}"
                    file_path = os.path.join(UPLOAD_FOLDER, unique_filename)
                    file.save(file_path)
                    image_paths.append(f"admin/img/{unique_filename}")
        
        images_json = json.dumps(image_paths)

        # --- Updated validation to include new required fields ---
        if not all([name, description, style, sub_category_id, category_id, status, color_id, shape_id]):
            flash('All product fields, including Color and Shape, are required.', 'error')
            return redirect(url_for('admin.admin_product'))
        
        try:
            # --- Updated INSERT query with new columns ---
            query_product = """
                INSERT INTO tbl_product (name, description, style, images, sub_category_id, status, category_id, color_id, shape_id, updated_by)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            """
            # --- Pass all values, including new ones, in the correct order ---
            db.execute(query_product, (name, description, style, images_json, sub_category_id, status, category_id, color_id, shape_id, updated_by))
            flash('Product added successfully!', 'success')
            return redirect(url_for('admin.admin_manage_product'))

        except Exception as e:
            print(f"!!! DATABASE ERROR: {str(e)} !!!") # Log the error for debugging
            flash(f'Error adding product. A database error occurred: {str(e)}', 'error')
            return redirect(url_for('admin.admin_product'))

    # --- DISPLAY THE FORM (GET REQUEST) ---
    # Fetch data for all dropdowns, including the new master tables
    query_categories = "SELECT * FROM tbl_category ORDER BY category_name"
    query_subcategories = "SELECT * FROM tbl_subcategory ORDER BY sub_category_name"
    query_colors = "SELECT * FROM master_color ORDER BY color_name"
    query_shapes = "SELECT * FROM master_shape ORDER BY shape_name"
    
    # Execute all queries
    categories = db.fetchall(query_categories)
    subcategories = db.fetchall(query_subcategories)
    colors = db.fetchall(query_colors)
    shapes = db.fetchall(query_shapes)
    
    # Pass all data to the template
    return render_template(
        'admin/admin-product.html', 
        categories=categories, 
        subcategories=subcategories,
        colors=colors,
        shapes=shapes
    )
@admin_bp.route('/admin-product/delete/<int:id>')
def delete_product(id):
    if 'admin_id' not in session:
        flash('Please login first', 'error')
        return redirect(url_for('admin.admin_login'))
    
    try:
        print(f"Attempting to delete product ID: {id}")
        product = db.fetchone("SELECT images FROM tbl_product WHERE id = %s", (id,))
        print(f"Product fetched: {product}")
        if product and product['images']:
            try:
                image_paths = json.loads(product['images'])
                print(f"Images to delete: {image_paths}")
                for image_path in image_paths:
                    file_path = os.path.join('static', image_path)
                    if os.path.exists(file_path):
                        print(f"Deleting image: {file_path}")
                        os.remove(file_path)
                    else:
                        print(f"Image not found: {file_path}")
            except json.JSONDecodeError as e:
                print(f"JSON decode error for images: {e}")
                flash(f"Warning: Invalid image data for product ID {id}. Continuing with deletion.", 'warning')
        
        print("Deleting purchase child records...")
        result = db.execute("DELETE FROM tbl_purchase_child WHERE product_size_id IN (SELECT id FROM tbl_product_size WHERE product_id = %s)", (id,))
        if result and isinstance(result, pymysql.Error):
            raise result
        print("Deleting stock records...")
        result = db.execute("DELETE FROM tbl_stock WHERE product_size_id IN (SELECT id FROM tbl_product_size WHERE product_id = %s)", (id,))
        if result and isinstance(result, pymysql.Error):
            raise result
        print("Deleting product size records...")
        result = db.execute("DELETE FROM tbl_product_size WHERE product_id = %s", (id,))
        if result and isinstance(result, pymysql.Error):
            raise result
        print("Deleting product...")
        result = db.execute("DELETE FROM tbl_product WHERE id = %s", (id,))
        if result and isinstance(result, pymysql.Error):
            raise result
        flash('Product deleted successfully', 'success')
    except pymysql.Error as e:
        error_message = f"Database error: {str(e)}"
        print(f"!!! DATABASE ERROR: {error_message} !!!")
        flash(error_message, 'error')
    except Exception as e:
        error_message = f"Unexpected error: {str(e)}"
        print(f"!!! UNEXPECTED ERROR: {error_message} !!!")
        flash(error_message, 'error')
    return redirect(url_for('admin.admin_manage_product'))

# @admin_bp.route('/admin-product-size', methods=['GET', 'POST'])
# def admin_product_size():
#     if 'admin_id' not in session:
#         flash('Please login first', 'error')
#         return redirect(url_for('admin.admin_login'))
    
#     if request.method == 'POST':
#         product_id = request.form.get('product_id')
#         size = request.form.get('size')
#         prize = request.form.get('prize')
#         discount = request.form.get('discount', '0')
#         offer_prize = request.form.get('offer_prize')
#         updated_by = session['admin_id']
        
#         if not all([product_id, size, prize]):
#             flash('Product ID, Size, and Prize are required.', 'error')
#             return redirect(url_for('admin.admin_product_size'))
        
#         if size and not size.endswith(' cm'):
#             size = f"{size} cm"
        
#         try:
#             query_size = """
#                 INSERT INTO tbl_product_size (product_id, size, prize, offer_prize, discount, updated_by)
#                 VALUES (%s, %s, %s, %s, %s, %s)
#             """
#             db.execute(query_size, (product_id, size, prize, offer_prize, discount, updated_by))
#             flash('Product size added successfully', 'success')
#         except Exception as e:
#             flash(f'Error adding product size: {str(e)}', 'error')
#         return redirect(url_for('admin.admin_product_size'))
    
#     query_products = "SELECT id, name FROM tbl_product ORDER BY name"
#     products = db.fetchall(query_products)
#     return render_template('admin/admin-product-size.html', products=products)

# @admin_bp.route('/admin-manage-product', methods=['GET', 'POST'])
# def admin_manage_product():
#     if 'admin_id' not in session:
#         flash('Please login first', 'error')
#         return redirect(url_for('admin.admin_login'))
    
#     if request.method == 'POST':
#         product_id = request.form.get('product_id')
#         name = request.form.get('name')
#         description = request.form.get('description')
#         style = request.form.get('style')
#         sub_category_id = request.form.get('sub_category_id')
#         category_id = request.form.get('category_id')
#         status = request.form.get('status')
#         updated_by = session['admin_id']
        
#         image_paths = []
#         if 'images' in request.files:
#             files = request.files.getlist('images')
#             for file in files:
#                 if file and allowed_file(file.filename):
#                     filename = secure_filename(file.filename)
#                     unique_filename = f"{uuid.uuid4().hex}_{filename}"
#                     file_path = os.path.join(UPLOAD_FOLDER, unique_filename)
#                     file.save(file_path)
#                     image_paths.append(f"admin/img/{unique_filename}")
        
#         if not image_paths:
#             existing_product = db.fetchone("SELECT images FROM tbl_product WHERE id = %s", (product_id,))
#             image_paths = json.loads(existing_product['images']) if existing_product and existing_product['images'] else []
        
#         images_json = json.dumps(image_paths)

#         if all([product_id, name, description, style, sub_category_id, category_id, status]):
#             try:
#                 query = """
#                     UPDATE tbl_product 
#                     SET name = %s, description = %s, style = %s, images = %s, 
#                         sub_category_id = %s, status = %s, category_id = %s, updated_by = %s
#                     WHERE id = %s
#                 """
#                 db.execute(query, (name, description, style, images_json, sub_category_id, status, category_id, updated_by, product_id))
#                 flash('Product updated successfully', 'success')
#             except Exception as e:
#                 flash(f'Error updating product: {str(e)}', 'error')
#                 print(f"Product update exception: {str(e)}")

#         # Handle size updates and additions
#         sizes = {}
#         for key, value in request.form.items():
#             if key.startswith('sizes[') and key.endswith('][size]'):
#                 size_id = key.split('[')[1].split(']')[0]
#                 sizes[size_id] = sizes.get(size_id, {})
#                 sizes[size_id]['size'] = value if not value.endswith(' cm') else value
#                 sizes[size_id]['id'] = request.form.get(f'sizes[{size_id}][id]')
#                 sizes[size_id]['prize'] = request.form.get(f'sizes[{size_id}][prize]')
#                 sizes[size_id]['discount'] = request.form.get(f'sizes[{size_id}][discount]', '0')
#                 sizes[size_id]['offer_prize'] = request.form.get(f'sizes[{size_id}][offer_prize]')

#         print("Received sizes data:", sizes)

#         for size_id, size_data in sizes.items():
#             size = size_data['size']
#             prize = size_data['prize']
#             discount = size_data['discount']
#             offer_prize = size_data['offer_prize']
#             size_id = size_data['id']

#             if size and not size.endswith(' cm'):
#                 size = f"{size} cm"

#             if size_id:  # Update existing size
#                 try:
#                     query_size = """
#                         UPDATE tbl_product_size 
#                         SET size = %s, prize = %s, offer_prize = %s, discount = %s, updated_by = %s
#                         WHERE id = %s AND product_id = %s
#                     """
#                     db.execute(query_size, (size, prize, offer_prize, discount, updated_by, size_id, product_id))
#                     flash('Product size updated successfully', 'success')
#                 except Exception as e:
#                     flash(f'Error updating product size: {str(e)}', 'error')
#                     print(f"Size update exception: {str(e)}")
#             else:  # Add new size
#                 try:
#                     query_size = """
#                         INSERT INTO tbl_product_size (product_id, size, prize, offer_prize, discount, updated_by)
#                         VALUES (%s, %s, %s, %s, %s, %s)
#                     """
#                     db.execute(query_size, (product_id, size, prize, offer_prize, discount, updated_by))
#                     flash('New product size added successfully', 'success')
#                 except Exception as e:
#                     flash(f'Error adding new product size: {str(e)}', 'error')
#                     print(f"Size add exception: {str(e)}")

#         return redirect(url_for('admin.admin_manage_product'))
    
#     query_products = """
#         SELECT p.*, c.category_name, s.sub_category_name 
#         FROM tbl_product p 
#         JOIN tbl_category c ON p.category_id = c.id 
#         JOIN tbl_subcategory s ON p.sub_category_id = s.id
#     """
#     query_categories = "SELECT * FROM tbl_category"
#     query_subcategories = "SELECT * FROM tbl_subcategory"
#     query_sizes = """
#         SELECT ps.*, p.name 
#         FROM tbl_product_size ps 
#         JOIN tbl_product p ON ps.product_id = p.id
#     """
#     query_stocks = """
#         SELECT s.*, p.name, ps.size 
#         FROM tbl_stock s 
#         JOIN tbl_product_size ps ON s.product_size_id = ps.id 
#         JOIN tbl_product p ON ps.product_id = p.id
#     """
#     products = db.fetchall(query_products)
#     categories = db.fetchall(query_categories)
#     subcategories = db.fetchall(query_subcategories)
#     product_sizes = db.fetchall(query_sizes)
#     stocks = db.fetchall(query_stocks)
    
#     for product in products:
#         product['images_list'] = json.loads(product['images']) if product['images'] else []
    
#     return render_template('admin/admin-manage-product.html', products=products, categories=categories, subcategories=subcategories, product_sizes=product_sizes, stocks=stocks)



@admin_bp.route('/admin-product-size', methods=['GET', 'POST'])
def admin_product_size():
    if 'admin_id' not in session:
        flash('Please login first', 'error')
        return redirect(url_for('admin.admin_login'))
    
    if request.method == 'POST':
        product_id = request.form.get('product_id')
        size = request.form.get('size')  # <-- FIX 1: Changed from 'size_value' to 'size'
        weight = request.form.get('weight')
        weight_unit_id = request.form.get('weight_unit_id')
        prize = request.form.get('prize')
        discount = request.form.get('discount', 0, type=float)
        updated_by = session['admin_id']

        if not all([product_id, size, weight, weight_unit_id, prize]):
            flash('All fields are required to add a size.', 'error')
            return redirect(url_for('admin.admin_product_size'))

        # Use the logic from the previous step to handle the database interaction correctly
        prize_float = float(prize)
        offer_prize = prize_float - (prize_float * (discount / 100))

        # --- FIX 2: Updated SQL INSERT query to use 'size' ---
        query = """
            INSERT INTO tbl_product_size (product_id, size, weight, weight_unit_id, prize, offer_prize, discount, updated_by)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
        """
        # --- FIX 3: Pass the 'size' variable in the parameters ---
        params = (product_id, size, weight, weight_unit_id, prize, offer_prize, discount, updated_by)
        
        # This logic correctly checks the return value from your custom db.execute method
        result = db.execute(query, params)

        if isinstance(result, Exception):
            print(f"!!! DATABASE ERROR (Add Size): {str(result)} !!!")
            flash(f'Error adding product size: {str(result)}', 'error')
        else:
            flash('Product size added successfully!', 'success')
        
        return redirect(url_for('admin.admin_manage_product'))

    # --- DISPLAY THE FORM (GET REQUEST) ---
    query_products = "SELECT id, name FROM tbl_product WHERE status='active' ORDER BY name ASC"
    query_weight_units = "SELECT * FROM master_weight_unit ORDER BY unit_name"
    
    products = db.fetchall(query_products)
    weight_units = db.fetchall(query_weight_units)
    
    return render_template(
        'admin/admin-product-size.html', 
        products=products,
        weight_units=weight_units
    )

@admin_bp.route('/admin-product-size/edit/<int:id>', methods=['GET', 'POST'])
def edit_product_size(id):
    if 'admin_id' not in session:
        flash('Please login first', 'error')
        return redirect(url_for('admin.admin_login'))
    
    if request.method == 'POST':
        product_id = request.form['product_id']
        size = request.form['size']
        prize = request.form['prize']
        offer_prize = request.form.get('offer_prize')
        discount = request.form.get('discount')
        updated_by = session['admin_id']
        if size and not size.endswith(' cm'):
            size = f"{size} cm"
        query = """
            UPDATE tbl_product_size 
            SET product_id = %s, size = %s, prize = %s, offer_prize = %s, discount = %s, updated_by = %s
            WHERE id = %s
        """
        try:
            db.execute(query, (product_id, size, prize, offer_prize, discount, updated_by, id))
            flash('Product size updated successfully', 'success')
        except Exception as e:
            flash(f'Error updating product size: {str(e)}', 'error')
        return redirect(url_for('admin.admin_manage_product'))
    
    query_product_size = "SELECT * FROM tbl_product_size WHERE id = %s"
    query_products = "SELECT * FROM tbl_product"
    product_size = db.fetchone(query_product_size, (id,))
    products = db.fetchall(query_products)
    return render_template('admin/edit-product-size.html', product_size=product_size, products=products)

@admin_bp.route('/admin-product-size/delete/<int:id>')
def delete_product_size(id):
    if 'admin_id' not in session:
        flash('Please login first', 'error')
        return redirect(url_for('admin.admin_login'))
    
    query = "DELETE FROM tbl_product_size WHERE id = %s"
    try:
        db.execute(query, (id,))
        flash('Product size deleted successfully', 'success')
    except Exception as e:
        flash(f'Error deleting product size: {str(e)}', 'error')
    return redirect(url_for('admin.admin_manage_product'))

# @admin_bp.route('/admin-stock', methods=['GET', 'POST'])
# def admin_stock():
#     if 'admin_id' not in session:
#         flash('Please login first', 'error')
#         return redirect(url_for('admin.admin_login'))
    
#     if request.method == 'POST':
#         product_id = request.form.get('product_id')
#         product_size_id = request.form.get('product_size_id')
#         stock_count = request.form.get('stock_count')
#         purchase_count = request.form.get('purchase_count')
#         updated_by = session['admin_id']
        
#         if not all([product_id, product_size_id, stock_count, purchase_count]):
#             flash('Product ID, Product Size ID, Stock Count, and Purchase Count are required.', 'error')
#             return redirect(url_for('admin.admin_stock'))
        
#         try:
#             query_stock = """
#                 INSERT INTO tbl_stock (product_size_id, stock_count, purchase_count, updated_by)
#                 VALUES (%s, %s, %s, %s)
#             """
#             db.execute(query_stock, (product_size_id, stock_count, purchase_count, updated_by))
#             flash('Stock added successfully', 'success')
#         except Exception as e:
#             flash(f'Error adding stock: {str(e)}', 'error')
#             print(f"Exception: {str(e)}")
#         return redirect(url_for('admin.admin_stock', product_id=product_id))
    
#     product_id = request.args.get('product_id')
#     query_product_sizes = """
#         SELECT ps.*, p.name 
#         FROM tbl_product_size ps 
#         JOIN tbl_product p ON ps.product_id = p.id
#         WHERE ps.product_id = %s
#     """
#     query_stocks = """
#         SELECT s.*, p.name, ps.size 
#         FROM tbl_stock s 
#         JOIN tbl_product_size ps ON s.product_size_id = ps.id 
#         JOIN tbl_product p ON ps.product_id = p.id
#         WHERE ps.product_id = %s
#     """
#     product_sizes = db.fetchall(query_product_sizes, (product_id,)) if product_id else []
#     stocks = db.fetchall(query_stocks, (product_id,)) if product_id else []
#     products = db.fetchall("SELECT id, name FROM tbl_product")
    
#     return render_template('admin/admin-stock.html', product_sizes=product_sizes, stocks=stocks, products=products, selected_product_id=product_id)

# @admin_bp.route('/admin-stock/edit/<int:id>', methods=['GET', 'POST'])
# def edit_stock(id):
#     if 'admin_id' not in session:
#         flash('Please login first', 'error')
#         return redirect(url_for('admin.admin_login'))
    
#     if request.method == 'POST':
#         product_size_id = request.form['product_size_id']
#         stock_count = request.form['stock_count']
#         purchase_count = request.form['purchase_count']
#         updated_by = session['admin_id']
#         query = """
#             UPDATE tbl_stock 
#             SET product_size_id = %s, stock_count = %s, purchase_count = %s, updated_by = %s
#             WHERE id = %s
#         """
#         try:
#             db.execute(query, (product_size_id, stock_count, purchase_count, updated_by, id))
#             flash('Stock updated successfully', 'success')
#         except Exception as e:
#             flash(f'Error updating stock: {str(e)}', 'error')
#         product_id = db.fetchone("SELECT product_size_id FROM tbl_stock WHERE id = %s", (id,))['product_size_id']
#         product_id = db.fetchone("SELECT product_id FROM tbl_product_size WHERE id = %s", (product_id,))['product_id']
#         return redirect(url_for('admin.admin_stock', product_id=product_id))
    
#     query_stock = "SELECT * FROM tbl_stock WHERE id = %s"
#     query_product_sizes = "SELECT ps.id, p.name, ps.size FROM tbl_product_size ps JOIN tbl_product p ON ps.product_id = p.id"
#     stock = db.fetchone(query_stock, (id,))
#     product_sizes = db.fetchall(query_product_sizes)
#     return render_template('admin/edit-stock.html', stock=stock, product_sizes=product_sizes)

# @admin_bp.route('/admin-stock/delete/<int:id>')
# def delete_stock(id):
#     if 'admin_id' not in session:
#         flash('Please login first', 'error')
#         return redirect(url_for('admin.admin_login'))
    
#     try:
#         product_id = db.fetchone("SELECT product_size_id FROM tbl_stock WHERE id = %s", (id,))['product_size_id']
#         product_id = db.fetchone("SELECT product_id FROM tbl_product_size WHERE id = %s", (product_id,))['product_id']
#         query = "DELETE FROM tbl_stock WHERE id = %s"
#         db.execute(query, (id,))
#         flash('Stock deleted successfully', 'success')
#     except Exception as e:
#         flash(f'Error deleting stock: {str(e)}', 'error')
#     return redirect(url_for('admin.admin_stock', product_id=product_id))

# Order Management
# @admin_bp.route('/admin-orders', methods=['GET', 'POST'])
# def admin_orders():
#     if 'admin_id' not in session:
#         flash('Please login first', 'error')
#         return redirect(url_for('admin.admin_login'))
    
#     if request.method == 'POST':
#         purchase_id = request.form['purchase_id']
#         status = request.form['status']
#         query = "UPDATE tbl_purchase_master SET status = %s WHERE id = %s"
#         try:
#             db.execute(query, (status, purchase_id))
#             flash('Order status updated successfully', 'success')
#         except Exception as e:
#             flash(f'Error updating order status: {str(e)}', 'error')
#         return redirect(url_for('admin.admin_orders'))
    
#     query = """
#         SELECT pm.*, u.first_name, u.last_name 
#         FROM tbl_purchase_master pm 
#         JOIN tbl_user u ON pm.user_id = u.id
#     """
#     orders = db.fetchall(query)
#     return render_template('admin/admin-orders.html', orders=orders)

# @admin_bp.route('/admin-order-details/<int:id>')
# def order_details(id):
#     if 'admin_id' not in session:
#         flash('Please login first', 'error')
#         return redirect(url_for('admin.admin_login'))
    
#     query_order = """
#         SELECT pm.*, u.first_name, u.last_name 
#         FROM tbl_purchase_master pm 
#         JOIN tbl_user u ON pm.user_id = u.id 
#         WHERE pm.id = %s
#     """
#     query_items = """
#         SELECT pc.*, p.name, ps.size 
#         FROM tbl_purchase_child pc 
#         JOIN tbl_product_size ps ON pc.product_size_id = ps.id 
#         JOIN tbl_product p ON ps.product_id = p.id 
#         WHERE pc.purchase_id = %s
#     """
#     query_tracking = "SELECT * FROM tbl_tracking WHERE purchase_id = %s"
#     order = db.fetchone(query_order, (id,))
#     order_items = db.fetchall(query_items, (id,))
#     tracking = db.fetchall(query_tracking, (id,))
#     return render_template('admin/order-details.html', order=order, order_items=order_items, tracking=tracking)

@admin_bp.route('/admin-order-tracking/<int:purchase_id>', methods=['GET', 'POST'])
def order_tracking(purchase_id):
    if 'admin_id' not in session:
        flash('Please login first', 'error')
        return redirect(url_for('admin.admin_login'))
    
    if request.method == 'POST':
        status = request.form['status']
        query = "INSERT INTO tbl_tracking (purchase_id, status) VALUES (%s, %s)"
        try:
            db.execute(query, (purchase_id, status))
            flash('Tracking status added successfully', 'success')
        except Exception as e:
            flash(f'Error adding tracking status: {str(e)}', 'error')
        return redirect(url_for('admin.order_details', id=purchase_id))
    
    query = "SELECT * FROM tbl_tracking WHERE purchase_id = %s"
    tracking = db.fetchall(query, (purchase_id,))
    return render_template('admin/order-tracking.html', purchase_id=purchase_id, tracking=tracking)

# User Management
@admin_bp.route('/admin-users')
def admin_users():
    if 'admin_id' not in session:
        flash('Please login first', 'error')
        return redirect(url_for('admin.admin_login'))
    
    query = """
        SELECT u.*, l.email 
        FROM tbl_user u 
        JOIN tbl_login l ON u.login_id = l.id
    """
    users = db.fetchall(query)
    return render_template('admin/admin-users.html', users=users)

@admin_bp.route('/admin-orders')
def admin_orders():
    if 'admin_id' not in session:
        flash('Please login first', 'error')
        return redirect(url_for('admin.admin_login'))
    
    # Updated query to include the payment_verify status
    query = """
        SELECT 
            pm.id, 
            pm.taxed_subtotal, 
            pm.status, 
            pm.payment_verify,  -- Fetch the verification status
            u.first_name, 
            u.last_name 
        FROM tbl_purchase_master pm 
        JOIN tbl_user u ON pm.user_id = u.id
        ORDER BY pm.payment_verify, pm.id DESC
    """
    orders = db.fetchall(query)
    return render_template('admin/admin-orders.html', orders=orders)


# MODIFIED ROUTE: /admin-order-details remains mostly the same, it just needs to render the new template
@admin_bp.route('/admin-order-details/<int:id>')
def order_details(id):
    if 'admin_id' not in session:
        flash('Please login first', 'error')
        return redirect(url_for('admin.admin_login'))
    
    query_order = """
        SELECT pm.*, u.first_name, u.last_name, l.email 
        FROM tbl_purchase_master pm 
        JOIN tbl_user u ON pm.user_id = u.id 
        JOIN tbl_login l ON u.login_id = l.id
        WHERE pm.id = %s
    """
    query_items = """
        SELECT pc.*, p.name, ps.size 
        FROM tbl_purchase_child pc 
        JOIN tbl_product_size ps ON pc.product_size_id = ps.id 
        JOIN tbl_product p ON ps.product_id = p.id 
        WHERE pc.purchase_id = %s
    """
    query_tracking = "SELECT * FROM tbl_tracking WHERE purchase_id = %s ORDER BY date DESC"
    
    order = db.fetchone(query_order, (id,))
    if not order:
        flash('Order not found.', 'error')
        return redirect(url_for('admin.admin_orders'))
        
    order_items = db.fetchall(query_items, (id,))
    tracking = db.fetchall(query_tracking, (id,))
    
    # This route will now render the detailed view with verification options
    return render_template('admin/order-details.html', order=order, order_items=order_items, tracking=tracking)

@admin_bp.route('/admin-manage-product', methods=['GET', 'POST'])
def admin_manage_product():
    if 'admin_id' not in session:
        flash('Please login first', 'error')
        return redirect(url_for('admin.admin_login'))
    
    # --- POST LOGIC: SAVING PRODUCT, SIZES, AND INITIAL STOCK ---
    if request.method == 'POST':
        try:
            product_id = request.form.get('product_id')
            name = request.form.get('name')
            description = request.form.get('description')
            style = request.form.get('style')
            sub_category_id = request.form.get('sub_category_id')
            category_id = request.form.get('category_id')
            status = request.form.get('status')
            updated_by = session['admin_id']

            # Image handling logic
            image_paths = []
            if 'images' in request.files:
                files = request.files.getlist('images')
                if files and files[0].filename: # Check if new files were actually uploaded
                    for file in files:
                        if file and allowed_file(file.filename):
                            filename = secure_filename(file.filename)
                            unique_filename = f"{uuid.uuid4().hex}_{filename}"
                            file_path = os.path.join(UPLOAD_FOLDER, unique_filename)
                            file.save(file_path)
                            image_paths.append(f"admin/img/{unique_filename}")

            if not image_paths and product_id:
                existing_product = db.fetchone("SELECT images FROM tbl_product WHERE id = %s", (product_id,))
                if existing_product and existing_product.get('images'):
                    image_paths = json.loads(existing_product['images'])
            
            images_json = json.dumps(image_paths)

            # Update the main product details
            if all([product_id, name, description, style, sub_category_id, category_id, status]):
                query_update_product = """
                    UPDATE tbl_product 
                    SET name = %s, description = %s, style = %s, images = %s, 
                        sub_category_id = %s, status = %s, category_id = %s, updated_by = %s
                    WHERE id = %s
                """
                db.execute(query_update_product, (name, description, style, images_json, sub_category_id, status, category_id, updated_by, product_id))
                flash('Product updated successfully', 'success')
            else:
                 flash('Missing required product details.', 'error')
                 return redirect(url_for('admin.admin_manage_product'))


            # Combined size and stock logic
            sizes = {}
            for key, value in request.form.items():
                if key.startswith('sizes['):
                    size_id_str = key.split('[')[1].split(']')[0]
                    field_name = key.split('[')[2].split(']')[0]
                    if size_id_str not in sizes:
                        sizes[size_id_str] = {}
                    sizes[size_id_str][field_name] = value

            for size_id_str, size_data in sizes.items():
                size = size_data.get('size')
                prize = size_data.get('prize')
                discount = size_data.get('discount', '0')
                offer_prize = size_data.get('offer_prize')
                existing_size_id = size_data.get('id') # This is the ID of an *existing* product_size record
                
                if size and not size.endswith(' cm'):
                    size = f"{size} cm"

                if existing_size_id:  # Update existing size
                    query_update_size = """
                        UPDATE tbl_product_size 
                        SET size = %s, prize = %s, offer_prize = %s, discount = %s, updated_by = %s
                        WHERE id = %s AND product_id = %s
                    """
                    db.execute(query_update_size, (size, prize, offer_prize, discount, updated_by, existing_size_id, product_id))
                
                else:  # This is a NEW size, so add it and create its initial stock record.
                    initial_stock = size_data.get('initial_stock')
                    
                    query_insert_size = """
                        INSERT INTO tbl_product_size (product_id, size, prize, offer_prize, discount, updated_by)
                        VALUES (%s, %s, %s, %s, %s, %s)
                    """
                    new_size_id = db.executeAndReturnId(query_insert_size, (product_id, size, prize, offer_prize, discount, updated_by))
                    
                    if new_size_id:
                        stock_count = int(initial_stock) if initial_stock else 0
                        query_insert_stock = """
                            INSERT INTO tbl_stock (product_size_id, stock_count, purchase_count, updated_by)
                            VALUES (%s, %s, 0, %s)
                        """
                        db.execute(query_insert_stock, (new_size_id, stock_count, updated_by))
                        flash(f'New size "{size}" added with an initial stock of {stock_count}.', 'success')
                    else:
                        flash('Failed to create new product size.', 'error')

        except Exception as e:
            flash(f'An error occurred while saving: {str(e)}', 'error')
            print(traceback.format_exc())

        return redirect(url_for('admin.admin_manage_product'))
    
    # --- GET LOGIC: FETCHING DATA FOR THE PAGE (WITH ERROR HANDLING) ---
    try:
        query_products = """
            SELECT p.*, c.category_name, s.sub_category_name 
            FROM tbl_product p 
            JOIN tbl_category c ON p.category_id = c.id 
            JOIN tbl_subcategory s ON p.sub_category_id = s.id
            ORDER BY p.id DESC
        """
        query_categories = "SELECT * FROM tbl_category ORDER BY category_name"
        query_subcategories = "SELECT * FROM tbl_subcategory ORDER BY sub_category_name"
        query_sizes = "SELECT * FROM tbl_product_size"
        query_stocks = "SELECT * FROM tbl_stock"

        products = db.fetchall(query_products)
        if isinstance(products, Exception): raise products

        categories = db.fetchall(query_categories)
        if isinstance(categories, Exception): raise categories

        subcategories = db.fetchall(query_subcategories)
        if isinstance(subcategories, Exception): raise subcategories

        product_sizes = db.fetchall(query_sizes)
        if isinstance(product_sizes, Exception): raise product_sizes

        stocks = db.fetchall(query_stocks)
        if isinstance(stocks, Exception): raise stocks
        
        for product in products:
            product['images_list'] = json.loads(product['images']) if product.get('images') else []
        
        return render_template('admin/admin-manage-product.html', 
                               products=products, 
                               categories=categories, 
                               subcategories=subcategories, 
                               product_sizes=product_sizes, 
                               stocks=stocks)

    except Exception as e:
        flash(f'A critical database error occurred while loading the page: {str(e)}', 'error')
        print("--- DATABASE ERROR IN admin_manage_product (GET) ---")
        print("---------------------------------------------")
        
        # Render the page with EMPTY lists to prevent crashing
        return render_template('admin/admin-manage-product.html', 
                               products=[], 
                               categories=[], 
                               subcategories=[], 
                               product_sizes=[], 
                               stocks=[])
@admin_bp.route('/admin-update-stock', methods=['GET', 'POST'])
def admin_update_stock():
    if 'admin_id' not in session:
        flash('Please login first', 'error')
        return redirect(url_for('admin.admin_login'))

    if request.method == 'POST':
        product_id_for_redirect = request.form.get('product_id_for_redirect')
        try:
            product_size_id = request.form.get('product_size_id')
            quantity_to_add = request.form.get('quantity_to_add', type=int)
            updated_by = session['admin_id']

            if not product_size_id or quantity_to_add is None or quantity_to_add <= 0:
                flash('Please enter a valid, positive quantity.', 'error')
            else:
                # --- NEW, MORE ROBUST LOGIC ---

                # 1. First, check if a stock record for this size already exists.
                check_query = "SELECT id FROM tbl_stock WHERE product_size_id = %s"
                existing_record = db.fetchone(check_query, (product_size_id,))

                if existing_record:
                    # If it exists, UPDATE it.
                    update_query = """
                        UPDATE tbl_stock SET stock_count = stock_count + %s, updated_by = %s
                        WHERE product_size_id = %s
                    """
                    db.execute(update_query, (quantity_to_add, updated_by, product_size_id))
                    action_taken = "updated"
                else:
                    # If it does NOT exist, INSERT a new record.
                    insert_query = """
                        INSERT INTO tbl_stock (product_size_id, stock_count, purchase_count, updated_by)
                        VALUES (%s, %s, 0, %s)
                    """
                    db.execute(insert_query, (product_size_id, quantity_to_add, updated_by))
                    action_taken = "created"
                
                # 2. Commit the transaction to save the changes.
                db.commit() 
                
                flash(f'Successfully {action_taken} stock record. Added {quantity_to_add} units.', 'success')

        except Exception as e:
            # Log the error for debugging, but show a user-friendly message.
            print(f"--- ERROR during stock update: {e} ---")
            flash(f'An unexpected error occurred. Please contact support.', 'error')
        
        # 3. Redirect back to the page.
        return redirect(url_for('admin.admin_update_stock', product_id=product_id_for_redirect))

    # --- GET request logic (remains the same) ---
    selected_product_id = request.args.get('product_id')
    products = db.fetchall("SELECT id, name FROM tbl_product ORDER BY name")
    product_sizes = []
    if selected_product_id:
        query_sizes = """
            SELECT ps.id, ps.size, p.name, 
                   COALESCE(s.stock_count, 0) as stock_count, 
                   COALESCE(s.purchase_count, 0) as purchase_count
            FROM tbl_product_size ps
            JOIN tbl_product p ON ps.product_id = p.id
            LEFT JOIN tbl_stock s ON ps.id = s.product_size_id
            WHERE ps.product_id = %s ORDER BY ps.size
        """
        product_sizes = db.fetchall(query_sizes, (selected_product_id,))
    return render_template('admin/admin-update-stock.html', products=products, product_sizes=product_sizes, selected_product_id=selected_product_id)
# NEW ROUTE: To handle the approve/reject form submission
@admin_bp.route('/verify-payment', methods=['POST'])
def verify_payment():
    if 'admin_id' not in session:
        flash('Unauthorized access', 'error')
        return redirect(url_for('admin.admin_login'))

    purchase_id = request.form.get('purchase_id')
    action = request.form.get('action') # This will be 'approve' or 'reject'

    if not all([purchase_id, action]):
        flash('Invalid request. Missing data.', 'error')
        return redirect(url_for('admin.admin_orders'))

    if action == 'approve':
        new_status = 'true'
        message = 'Payment approved successfully.'
    elif action == 'reject':
        new_status = 'false'
        message = 'Payment rejected.'
    else:
        flash('Invalid action.', 'error')
        return redirect(url_for('admin.order_details', id=purchase_id))

    try:
        query = "UPDATE tbl_purchase_master SET payment_verify = %s WHERE id = %s"
        db.execute(query, (new_status, purchase_id))
        flash(message, 'success')
    except Exception as e:
        flash(f'An error occurred: {str(e)}', 'error')

    return redirect(url_for('admin.order_details', id=purchase_id))

# In app/admin/routes.py

@admin_bp.route('/admin-color-shape-weight', methods=['GET', 'POST'])
def admin_color_shape_weight():
    if 'admin_id' not in session:
        flash('Please login first', 'error')
        return redirect(url_for('admin.admin_login'))

    # --- Handle POST requests for adding new items ---
    if request.method == 'POST':
        form_type = request.form.get('form_type')

        # --- Logic for adding a new COLOR ---
        if form_type == 'color':
            color_name = request.form.get('color_name')
            color_hex = request.form.get('color_hex_code')
            if color_name and color_hex:
                try:
                    query = "INSERT INTO master_color (color_name, color_hex_code) VALUES (%s, %s)"
                    db.execute(query, (color_name, color_hex))
                    flash(f'Color "{color_name}" added successfully!', 'success')
                except Exception as e:
                    flash(f'Error adding color: {e}', 'danger')
            else:
                flash('Color Name and Hex Code are required.', 'warning')

        # --- Logic for adding a new WEIGHT UNIT ---
        elif form_type == 'weight':
            unit_name = request.form.get('unit_name')
            if unit_name:
                try:
                    query = "INSERT INTO master_weight_unit (unit_name) VALUES (%s)"
                    db.execute(query, (unit_name,))
                    flash(f'Weight Unit "{unit_name}" added successfully!', 'success')
                except Exception as e:
                    flash(f'Error adding weight unit: {e}', 'danger')
            else:
                flash('Unit Name is required.', 'warning')

        # --- Logic for adding a new SHAPE ---
        elif form_type == 'shape':
            shape_name = request.form.get('shape_name')
            if shape_name:
                try:
                    query = "INSERT INTO master_shape (shape_name) VALUES (%s)"
                    db.execute(query, (shape_name,))
                    flash(f'Shape "{shape_name}" added successfully!', 'success')
                except Exception as e:
                    flash(f'Error adding shape: {e}', 'danger')
            else:
                flash('Shape Name is required.', 'warning')
        
        return redirect(url_for('admin.admin_color_shape_weight'))

    # --- For GET request, fetch all existing data to display ---
    try:
        colors = db.fetchall("SELECT * FROM master_color ORDER BY color_name ASC")
        weights = db.fetchall("SELECT * FROM master_weight_unit ORDER BY unit_name ASC")
        shapes = db.fetchall("SELECT * FROM master_shape ORDER BY shape_name ASC")
    except Exception as e:
        flash(f"Could not load master data. Error: {e}", 'danger')
        colors, weights, shapes = [], [], []

    return render_template(
        'admin/admin-color-shape-weight.html',
        colors=colors,
        weights=weights,
        shapes=shapes
    )

# --- Routes for Deleting Items ---

@admin_bp.route('/admin-masters/delete_color/<int:id>')
def delete_color(id):
    if 'admin_id' not in session:
        return redirect(url_for('admin.admin_login'))
    try:
        db.execute("DELETE FROM master_color WHERE id = %s", (id,))
        flash('Color deleted successfully.', 'success')
    except Exception as e:
        flash(f'Error deleting color: {e}', 'danger')
    return redirect(url_for('admin.admin_color_shape_weight'))

@admin_bp.route('/admin-masters/delete_weight/<int:id>')
def delete_weight(id):
    if 'admin_id' not in session:
        return redirect(url_for('admin.admin_login'))
    try:
        db.execute("DELETE FROM master_weight_unit WHERE id = %s", (id,))
        flash('Weight unit deleted successfully.', 'success')
    except Exception as e:
        flash(f'Error deleting weight unit: {e}', 'danger')
    return redirect(url_for('admin.admin_color_shape_weight'))

@admin_bp.route('/admin-masters/delete_shape/<int:id>')
def delete_shape(id):
    if 'admin_id' not in session:
        return redirect(url_for('admin.admin_login'))
    try:
        db.execute("DELETE FROM master_shape WHERE id = %s", (id,))
        flash('Shape deleted successfully.', 'success')
    except Exception as e:
        flash(f'Error deleting shape: {e}', 'danger')
    return redirect(url_for('admin.admin_color_shape_weight'))