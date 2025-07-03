from flask import render_template, request, redirect, url_for, session, flash,current_app
from werkzeug.utils import secure_filename
import json
import os
import uuid
from . import admin_bp
from app import db
from app.utilities import queries



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

@admin_bp.route('/admin-home')
def admin_home():
    return render_template('admin/admin-home.html')

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
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}

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
    
    print("Request method:", request.method)
    print("Form data:", request.form)
    
    if request.method == 'POST':
        if 'add_product' in request.form:
            print("Processing add_product form")
            name = request.form.get('name')
            description = request.form.get('description')
            style = request.form.get('style')
            sub_category_id = request.form.get('sub_category_id')
            category_id = request.form.get('category_id')
            status = request.form.get('status')
            updated_by = session['admin_id']
            
            image_paths = []
            if 'images' in request.files:
                files = request.files.getlist('images')
                for file in files:
                    if file and allowed_file(file.filename):
                        filename = secure_filename(file.filename)
                        unique_filename = f"{uuid.uuid4().hex}_{filename}"
                        file_path = os.path.join(UPLOAD_FOLDER, unique_filename)
                        file.save(file_path)
                        image_paths.append(f"admin/img/{unique_filename}")
            
            images_json = json.dumps(image_paths)

            if all([name, description, style, sub_category_id, category_id, status]):
                try:
                    query_product = """
                        INSERT INTO tbl_product (name, description, style, images, sub_category_id, status, category_id, updated_by)
                        VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                    """
                    db.execute(query_product, (name, description, style, images_json, sub_category_id, status, category_id, updated_by))
                    product_id = db.fetchone("SELECT LAST_INSERT_ID() as id")['id'] if hasattr(db, 'fetchone') else None
                    
                    if product_id:
                        flash('Product added successfully.', 'success')
                    else:
                        flash('Failed to retrieve product ID after insertion.', 'error')
                except Exception as e:
                    flash(f'Error adding product: {str(e)}', 'error')
                    print(f"Exception: {str(e)}")
            else:
                flash('All product fields are required.', 'error')
            return redirect(url_for('admin.admin_product'))
        
        elif 'add_size' in request.form:
            print("Processing add_size form")
            product_id = request.form.get('product_id')
            size = request.form.get('size')
            prize = request.form.get('prize')
            discount = request.form.get('discount', '0')
            offer_prize = request.form.get('offer_prize')
            updated_by = session['admin_id']
            
            if not all([product_id, size, prize]):
                flash('Product ID, Size, and Prize are required.', 'error')
                return redirect(url_for('admin.admin_product'))
            
            if size and not size.endswith(' cm'):
                size = f"{size} cm"
            
            try:
                query_size = """
                    INSERT INTO tbl_product_size (product_id, size, prize, offer_prize, discount, updated_by)
                    VALUES (%s, %s, %s, %s, %s, %s)
                """
                db.execute(query_size, (product_id, size, prize, offer_prize, discount, updated_by))
                flash('Product size added successfully', 'success')
            except Exception as e:
                flash(f'Error adding product size: {str(e)}', 'error')
                print(f"Exception: {str(e)}")
            return redirect(url_for('admin.admin_product'))
    
    query_categories = "SELECT * FROM tbl_category"
    query_subcategories = "SELECT * FROM tbl_subcategory"
    query_products = "SELECT id, name FROM tbl_product ORDER BY name"
    categories = db.fetchall(query_categories)
    subcategories = db.fetchall(query_subcategories)
    products = db.fetchall(query_products)
    return render_template('admin/admin-product.html', categories=categories, subcategories=subcategories, products=products)

@admin_bp.route('/admin-manage-product', methods=['GET', 'POST'])
def admin_manage_product():
    if 'admin_id' not in session:
        flash('Please login first', 'error')
        return redirect(url_for('admin.admin_login'))
    
    if request.method == 'POST':
        product_id = request.form.get('product_id')
        name = request.form.get('name')
        description = request.form.get('description')
        style = request.form.get('style')
        sub_category_id = request.form.get('sub_category_id')
        category_id = request.form.get('category_id')
        status = request.form.get('status')
        updated_by = session['admin_id']
        
        image_paths = []
        if 'images' in request.files:
            files = request.files.getlist('images')
            for file in files:
                if file and allowed_file(file.filename):
                    filename = secure_filename(file.filename)
                    unique_filename = f"{uuid.uuid4().hex}_{filename}"
                    file_path = os.path.join(UPLOAD_FOLDER, unique_filename)
                    file.save(file_path)
                    image_paths.append(f"admin/img/{unique_filename}")
        
        if not image_paths:
            existing_product = db.fetchone("SELECT images FROM tbl_product WHERE id = %s", (product_id,))
            image_paths = json.loads(existing_product['images']) if existing_product and existing_product['images'] else []
        
        images_json = json.dumps(image_paths)

        if all([product_id, name, description, style, sub_category_id, category_id, status]):
            try:
                query = """
                    UPDATE tbl_product 
                    SET name = %s, description = %s, style = %s, images = %s, 
                        sub_category_id = %s, status = %s, category_id = %s, updated_by = %s
                    WHERE id = %s
                """
                db.execute(query, (name, description, style, images_json, sub_category_id, status, category_id, updated_by, product_id))
                flash('Product updated successfully', 'success')
            except Exception as e:
                flash(f'Error updating product: {str(e)}', 'error')
                print(f"Product update exception: {str(e)}")

        # Handle size updates and additions
        sizes = {}
        for key, value in request.form.items():
            if key.startswith('sizes[') and key.endswith('][size]'):
                size_id = key.split('[')[1].split(']')[0]
                sizes[size_id] = sizes.get(size_id, {})
                sizes[size_id]['size'] = value if not value.endswith(' cm') else value
                sizes[size_id]['id'] = request.form.get(f'sizes[{size_id}][id]')
                sizes[size_id]['prize'] = request.form.get(f'sizes[{size_id}][prize]')
                sizes[size_id]['discount'] = request.form.get(f'sizes[{size_id}][discount]', '0')
                sizes[size_id]['offer_prize'] = request.form.get(f'sizes[{size_id}][offer_prize]')

        print("Received sizes data:", sizes)

        for size_id, size_data in sizes.items():
            size = size_data['size']
            prize = size_data['prize']
            discount = size_data['discount']
            offer_prize = size_data['offer_prize']
            size_id = size_data['id']

            if size and not size.endswith(' cm'):
                size = f"{size} cm"

            if size_id:  # Update existing size
                try:
                    query_size = """
                        UPDATE tbl_product_size 
                        SET size = %s, prize = %s, offer_prize = %s, discount = %s, updated_by = %s
                        WHERE id = %s AND product_id = %s
                    """
                    db.execute(query_size, (size, prize, offer_prize, discount, updated_by, size_id, product_id))
                    flash('Product size updated successfully', 'success')
                except Exception as e:
                    flash(f'Error updating product size: {str(e)}', 'error')
                    print(f"Size update exception: {str(e)}")
            else:  # Add new size
                try:
                    query_size = """
                        INSERT INTO tbl_product_size (product_id, size, prize, offer_prize, discount, updated_by)
                        VALUES (%s, %s, %s, %s, %s, %s)
                    """
                    db.execute(query_size, (product_id, size, prize, offer_prize, discount, updated_by))
                    flash('New product size added successfully', 'success')
                except Exception as e:
                    flash(f'Error adding new product size: {str(e)}', 'error')
                    print(f"Size add exception: {str(e)}")

        return redirect(url_for('admin.admin_manage_product'))
    
    query_products = """
        SELECT p.*, c.category_name, s.sub_category_name 
        FROM tbl_product p 
        JOIN tbl_category c ON p.category_id = c.id 
        JOIN tbl_subcategory s ON p.sub_category_id = s.id
    """
    query_categories = "SELECT * FROM tbl_category"
    query_subcategories = "SELECT * FROM tbl_subcategory"
    query_sizes = """
        SELECT ps.*, p.name 
        FROM tbl_product_size ps 
        JOIN tbl_product p ON ps.product_id = p.id
    """
    query_stocks = """
        SELECT s.*, p.name, ps.size 
        FROM tbl_stock s 
        JOIN tbl_product_size ps ON s.product_size_id = ps.id 
        JOIN tbl_product p ON ps.product_id = p.id
    """
    products = db.fetchall(query_products)
    categories = db.fetchall(query_categories)
    subcategories = db.fetchall(query_subcategories)
    product_sizes = db.fetchall(query_sizes)
    stocks = db.fetchall(query_stocks)
    
    for product in products:
        product['images_list'] = json.loads(product['images']) if product['images'] else []
    
    return render_template('admin/admin-manage-product.html', products=products, categories=categories, subcategories=subcategories, product_sizes=product_sizes, stocks=stocks)

@admin_bp.route('/admin-product/delete/<int:id>')
def delete_product(id):
    if 'admin_id' not in session:
        flash('Please login first', 'error')
        return redirect(url_for('admin.admin_login'))
    
    try:
        product = db.fetchone("SELECT images FROM tbl_product WHERE id = %s", (id,))
        if product and product['images']:
            for image_path in json.loads(product['images']):
                file_path = os.path.join('static', image_path)
                if os.path.exists(file_path):
                    os.remove(file_path)
        
        db.execute("DELETE FROM tbl_stock WHERE product_size_id IN (SELECT id FROM tbl_product_size WHERE product_id = %s)", (id,))
        db.execute("DELETE FROM tbl_product_size WHERE product_id = %s", (id,))
        query = "DELETE FROM tbl_product WHERE id = %s"
        db.execute(query, (id,))
        flash('Product deleted successfully', 'success')
    except Exception as e:
        flash(f'Error deleting product: {str(e)}', 'error')
    return redirect(url_for('admin.admin_manage_product'))

@admin_bp.route('/admin-product-size', methods=['GET', 'POST'])
def admin_product_size():
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
            INSERT INTO tbl_product_size (product_id, size, prize, offer_prize, discount, updated_by)
            VALUES (%s, %s, %s, %s, %s, %s)
        """
        try:
            db.execute(query, (product_id, size, prize, offer_prize, discount, updated_by))
            flash('Product size added successfully', 'success')
        except Exception as e:
            flash(f'Error adding product size: {str(e)}', 'error')
        return redirect(url_for('admin.admin_manage_product'))
    
    query_product_sizes = """
        SELECT ps.*, p.name 
        FROM tbl_product_size ps 
        JOIN tbl_product p ON ps.product_id = p.id
    """
    query_products = "SELECT * FROM tbl_product"
    product_sizes = db.fetchall(query_product_sizes)
    products = db.fetchall(query_products)
    return render_template('admin/admin-product-size.html', product_sizes=product_sizes, products=products)

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

@admin_bp.route('/admin-stock', methods=['GET', 'POST'])
def admin_stock():
    if 'admin_id' not in session:
        flash('Please login first', 'error')
        return redirect(url_for('admin.admin_login'))
    
    if request.method == 'POST':
        product_id = request.form.get('product_id')
        product_size_id = request.form.get('product_size_id')
        stock_count = request.form.get('stock_count')
        purchase_count = request.form.get('purchase_count')
        updated_by = session['admin_id']
        
        if not all([product_id, product_size_id, stock_count, purchase_count]):
            flash('Product ID, Product Size ID, Stock Count, and Purchase Count are required.', 'error')
            return redirect(url_for('admin.admin_stock'))
        
        try:
            query_stock = """
                INSERT INTO tbl_stock (product_size_id, stock_count, purchase_count, updated_by)
                VALUES (%s, %s, %s, %s)
            """
            db.execute(query_stock, (product_size_id, stock_count, purchase_count, updated_by))
            flash('Stock added successfully', 'success')
        except Exception as e:
            flash(f'Error adding stock: {str(e)}', 'error')
            print(f"Exception: {str(e)}")
        return redirect(url_for('admin.admin_stock', product_id=product_id))
    
    product_id = request.args.get('product_id')
    query_product_sizes = """
        SELECT ps.*, p.name 
        FROM tbl_product_size ps 
        JOIN tbl_product p ON ps.product_id = p.id
        WHERE ps.product_id = %s
    """
    query_stocks = """
        SELECT s.*, p.name, ps.size 
        FROM tbl_stock s 
        JOIN tbl_product_size ps ON s.product_size_id = ps.id 
        JOIN tbl_product p ON ps.product_id = p.id
        WHERE ps.product_id = %s
    """
    product_sizes = db.fetchall(query_product_sizes, (product_id,)) if product_id else []
    stocks = db.fetchall(query_stocks, (product_id,)) if product_id else []
    products = db.fetchall("SELECT id, name FROM tbl_product")
    
    return render_template('admin/admin-stock.html', product_sizes=product_sizes, stocks=stocks, products=products, selected_product_id=product_id)

@admin_bp.route('/admin-stock/edit/<int:id>', methods=['GET', 'POST'])
def edit_stock(id):
    if 'admin_id' not in session:
        flash('Please login first', 'error')
        return redirect(url_for('admin.admin_login'))
    
    if request.method == 'POST':
        product_size_id = request.form['product_size_id']
        stock_count = request.form['stock_count']
        purchase_count = request.form['purchase_count']
        updated_by = session['admin_id']
        query = """
            UPDATE tbl_stock 
            SET product_size_id = %s, stock_count = %s, purchase_count = %s, updated_by = %s
            WHERE id = %s
        """
        try:
            db.execute(query, (product_size_id, stock_count, purchase_count, updated_by, id))
            flash('Stock updated successfully', 'success')
        except Exception as e:
            flash(f'Error updating stock: {str(e)}', 'error')
        product_id = db.fetchone("SELECT product_size_id FROM tbl_stock WHERE id = %s", (id,))['product_size_id']
        product_id = db.fetchone("SELECT product_id FROM tbl_product_size WHERE id = %s", (product_id,))['product_id']
        return redirect(url_for('admin.admin_stock', product_id=product_id))
    
    query_stock = "SELECT * FROM tbl_stock WHERE id = %s"
    query_product_sizes = "SELECT ps.id, p.name, ps.size FROM tbl_product_size ps JOIN tbl_product p ON ps.product_id = p.id"
    stock = db.fetchone(query_stock, (id,))
    product_sizes = db.fetchall(query_product_sizes)
    return render_template('admin/edit-stock.html', stock=stock, product_sizes=product_sizes)

@admin_bp.route('/admin-stock/delete/<int:id>')
def delete_stock(id):
    if 'admin_id' not in session:
        flash('Please login first', 'error')
        return redirect(url_for('admin.admin_login'))
    
    try:
        product_id = db.fetchone("SELECT product_size_id FROM tbl_stock WHERE id = %s", (id,))['product_size_id']
        product_id = db.fetchone("SELECT product_id FROM tbl_product_size WHERE id = %s", (product_id,))['product_id']
        query = "DELETE FROM tbl_stock WHERE id = %s"
        db.execute(query, (id,))
        flash('Stock deleted successfully', 'success')
    except Exception as e:
        flash(f'Error deleting stock: {str(e)}', 'error')
    return redirect(url_for('admin.admin_stock', product_id=product_id))

# Order Management
@admin_bp.route('/admin-orders', methods=['GET', 'POST'])
def admin_orders():
    if 'admin_id' not in session:
        flash('Please login first', 'error')
        return redirect(url_for('admin.admin_login'))
    
    if request.method == 'POST':
        purchase_id = request.form['purchase_id']
        status = request.form['status']
        query = "UPDATE tbl_purchase_master SET status = %s WHERE id = %s"
        try:
            db.execute(query, (status, purchase_id))
            flash('Order status updated successfully', 'success')
        except Exception as e:
            flash(f'Error updating order status: {str(e)}', 'error')
        return redirect(url_for('admin.admin_orders'))
    
    query = """
        SELECT pm.*, u.first_name, u.last_name 
        FROM tbl_purchase_master pm 
        JOIN tbl_user u ON pm.user_id = u.id
    """
    orders = db.fetchall(query)
    return render_template('admin/admin-orders.html', orders=orders)

@admin_bp.route('/admin-order-details/<int:id>')
def order_details(id):
    if 'admin_id' not in session:
        flash('Please login first', 'error')
        return redirect(url_for('admin.admin_login'))
    
    query_order = """
        SELECT pm.*, u.first_name, u.last_name 
        FROM tbl_purchase_master pm 
        JOIN tbl_user u ON pm.user_id = u.id 
        WHERE pm.id = %s
    """
    query_items = """
        SELECT pc.*, p.name, ps.size 
        FROM tbl_purchase_child pc 
        JOIN tbl_product_size ps ON pc.product_size_id = ps.id 
        JOIN tbl_product p ON ps.product_id = p.id 
        WHERE pc.purchase_id = %s
    """
    query_tracking = "SELECT * FROM tbl_tracking WHERE purchase_id = %s"
    order = db.fetchone(query_order, (id,))
    order_items = db.fetchall(query_items, (id,))
    tracking = db.fetchall(query_tracking, (id,))
    return render_template('admin/order-details.html', order=order, order_items=order_items, tracking=tracking)

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