from flask import Blueprint, render_template, request, jsonify, flash, redirect, url_for, current_app, send_file, session
from flask_login import login_required, current_user
from flask_wtf import FlaskForm
from app.models.inventory import (
    InventoryItem, ComputerSystem, Category, 
    InventoryTransaction, ComputerModel, CPU, Tag
)
from app.models.config import Configuration
from app.utils.email import send_stock_alert
from app.forms import (
    ComputerModelForm, CPUForm, GeneralItemForm, 
    ComputerSystemForm, MANUFACTURER_CHOICES, 
    COMPUTER_TYPES
)
from app import db
import uuid
from barcode import Code128
from barcode.writer import ImageWriter
import qrcode
import io
import base64
from reportlab.lib import colors
from reportlab.lib.pagesizes import landscape
from reportlab.lib.units import inch
from reportlab.pdfgen import canvas
from reportlab.graphics.barcode import code128
from app.models.user import User
import requests
from bs4 import BeautifulSoup
from flask_wtf.csrf import validate_csrf
from werkzeug.exceptions import BadRequest
import os
import random
import time
from werkzeug.security import generate_password_hash
from functools import wraps

bp = Blueprint('inventory', __name__)

def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated or current_user.role != 'admin':
            flash('You need to be an admin to access this page.', 'danger')
            return redirect(url_for('inventory.dashboard'))
        return f(*args, **kwargs)
    return decorated_function

@bp.route('/dashboard')
@login_required
def dashboard():
    # General Items pagination
    page = request.args.get('page', 1, type=int)
    per_page = current_app.config['ITEMS_PER_PAGE']
    
    # Items query
    items_query = InventoryItem.query
    
    # Items search
    search = request.args.get('search', '')
    if search:
        items_query = items_query.filter(
            db.or_(
                InventoryItem.name.ilike(f'%{search}%'),
                InventoryItem.tracking_id.ilike(f'%{search}%')
            )
        )
    
    # Items category filter
    category_id = request.args.get('category', type=int)
    if category_id:
        items_query = items_query.filter(InventoryItem.category_id == category_id)
    
    # Items status filter
    status = request.args.get('status')
    if status == 'restock':
        items_query = items_query.filter(
            db.and_(
                InventoryItem.quantity <= InventoryItem.min_quantity,
                InventoryItem.min_quantity != None
            )
        )
    elif status:
        items_query = items_query.filter(InventoryItem.status == status)
    
    # Items pagination
    items = items_query.paginate(page=page, per_page=per_page)
    
    # Computer Systems pagination
    systems_page = request.args.get('systems_page', 1, type=int)
    systems_query = ComputerSystem.query
    
    # Systems search
    systems_search = request.args.get('search_systems', '')
    if systems_search:
        systems_query = systems_query.filter(
            db.or_(
                ComputerSystem.tracking_id.ilike(f'%{systems_search}%'),
                ComputerSystem.serial_tag.ilike(f'%{systems_search}%')
            )
        )
    
    # Systems model filter
    model_id = request.args.get('model', type=int)
    if model_id:
        systems_query = systems_query.filter(ComputerSystem.model_id == model_id)
    
    # Systems status filter
    system_status = request.args.get('system_status')
    if system_status:
        systems_query = systems_query.filter(ComputerSystem.status == system_status)
    
    # Systems pagination
    systems = systems_query.paginate(page=systems_page, per_page=per_page)
    
    # Get categories and models for filter dropdowns
    categories = Category.query.order_by(Category.name).all()
    computer_models = ComputerModel.query.order_by(ComputerModel.manufacturer, ComputerModel.model_name).all()
    
    form = FlaskForm()  # For CSRF protection
    
    return render_template('inventory/dashboard.html',
                         items=items,
                         systems=systems,
                         categories=categories,
                         computer_models=computer_models,
                         form=form)

@bp.route('/item/add', methods=['GET', 'POST'])
@login_required
def add_item():
    form = GeneralItemForm()
    
    if request.method == 'POST':
        if form.validate():
            try:
                # Create General Item
                item = InventoryItem(
                    tracking_id=generate_tracking_id(),
                    name=form.name.data,
                    category_id=form.category.data,
                    quantity=form.quantity.data,
                    reorder_threshold=form.reorder_threshold.data,
                    created_by=current_user.id,
                    cost=form.cost.data if form.cost.data else None,
                    purchase_url=form.purchase_url.data,
                    sell_price=form.sell_price.data if form.sell_price.data else None,
                    barcode=form.barcode.data,
                    description=form.description.data,
                    manufacturer=form.manufacturer.data,
                    mpn=form.mpn.data,
                    image_url=form.image_url.data,
                    storage_location=form.storage_location.data,
                    tags=[Tag.query.get(tag_id) for tag_id in form.tags.data] if form.tags.data else []
                )
                
                db.session.add(item)
                db.session.commit()
                
                flash('Item added successfully!', 'success')
                return redirect(url_for('inventory.dashboard'))
                
            except Exception as e:
                db.session.rollback()
                current_app.logger.error(f'Error adding item: {str(e)}')
                flash(f'Error adding item: {str(e)}', 'danger')
        else:
            for field, errors in form.errors.items():
                for error in errors:
                    flash(f'{field}: {error}', 'danger')
    
    return render_template('inventory/add_item.html', form=form)

@bp.route('/item/<int:id>/view')
@login_required
def view_item(id):
    # Get item with transactions eager loaded
    item = InventoryItem.query.options(
        db.joinedload(InventoryItem.transactions).joinedload(InventoryTransaction.user)
    ).get_or_404(id)
    
    # Generate barcode
    barcode_io = io.BytesIO()
    Code128(item.tracking_id, writer=ImageWriter()).write(barcode_io)
    barcode_base64 = base64.b64encode(barcode_io.getvalue()).decode()
    
    # Generate QR code
    qr = qrcode.QRCode(version=1, box_size=10, border=5)
    qr.add_data(f"http://127.0.0.1:5001/item/{item.id}/view")
    qr.make(fit=True)
    qr_img = qr.make_image(fill_color="black", back_color="white")
    
    qr_io = io.BytesIO()
    qr_img.save(qr_io)
    qr_base64 = base64.b64encode(qr_io.getvalue()).decode()
    
    return render_template('inventory/view_item.html', 
                         item=item,
                         barcode=barcode_base64,
                         qr_code=qr_base64)

@bp.route('/item/<int:id>/label')
@login_required
def print_label(id):
    # Try to find item in both tables
    item = InventoryItem.query.get(id)
    if not item:
        item = ComputerSystem.query.get_or_404(id)
        item.type = 'computer_system'  # Add type attribute for template
    
    # Generate barcode image
    barcode_io = io.BytesIO()
    Code128(item.tracking_id, writer=ImageWriter()).write(barcode_io)
    barcode_base64 = base64.b64encode(barcode_io.getvalue()).decode()
    
    # Return the print template
    return render_template('inventory/print_label.html',
                         item=item,
                         barcode=barcode_base64)

@bp.route('/item/<int:id>/edit', methods=['GET', 'POST'])
@login_required
def edit_item(id):
    item = InventoryItem.query.get_or_404(id)
    categories = Category.query.order_by(Category.name).all()
    tags = Tag.query.order_by(Tag.name).all()
    
    if isinstance(item, ComputerSystem):
        form = ComputerSystemForm(obj=item)
        if form.validate_on_submit():
            try:
                # Manually update fields for computer system
                item.cost = form.cost.data
                item.purchase_url = form.purchase_url.data
                item.sell_price = form.sell_price.data
                
                # Update computer-specific fields
                form.populate_obj(item)
                
                # Handle tags
                if request.form.getlist('tags'):
                    tag_ids = [int(tag_id) for tag_id in request.form.getlist('tags')]
                    item.tags = [Tag.query.get(tag_id) for tag_id in tag_ids]
                else:
                    item.tags = []  # Clear tags if none selected
                
                db.session.commit()
                flash('Computer system updated successfully!', 'success')
                return redirect(url_for('inventory.dashboard'))
            except Exception as e:
                db.session.rollback()
                flash(f'Error updating computer system: {str(e)}', 'danger')
                current_app.logger.error(f'Error updating computer system: {str(e)}')
        else:
            # Log form validation errors
            current_app.logger.error(f'Form validation errors: {form.errors}')
            flash('Please check the form for errors', 'danger')
            
        return render_template('inventory/edit_computer_system.html', form=form, item=item)
    else:
        form = GeneralItemForm(obj=item)
        if form.validate_on_submit():
            try:
                # Update fields using form data
                form.populate_obj(item)
                
                # Handle tags
                if request.form.getlist('tags'):
                    tag_ids = [int(tag_id) for tag_id in request.form.getlist('tags')]
                    item.tags = [Tag.query.get(tag_id) for tag_id in tag_ids]
                else:
                    item.tags = []  # Clear tags if none selected
                
                # Log the values before commit
                current_app.logger.debug(f'Updating item {item.id}:')
                current_app.logger.debug(f'Name: {item.name}')
                current_app.logger.debug(f'Category: {item.category_id}')
                current_app.logger.debug(f'Quantity: {item.quantity}')
                current_app.logger.debug(f'Reorder Threshold: {item.reorder_threshold}')
                current_app.logger.debug(f'Tags: {[tag.name for tag in item.tags]}')
                
                db.session.commit()
                flash('Item updated successfully!', 'success')
                return redirect(url_for('inventory.dashboard'))
            except Exception as e:
                db.session.rollback()
                flash(f'Error updating item: {str(e)}', 'danger')
                current_app.logger.error(f'Error updating item: {str(e)}')
        
        return render_template('inventory/edit_item.html', 
                             form=form, 
                             item=item,
                             categories=categories,
                             tags=tags)

@bp.route('/item/<int:id>/delete', methods=['POST'])
@login_required
def delete_item(id):
    item = InventoryItem.query.get_or_404(id)
    try:
        db.session.delete(item)
        db.session.commit()
        flash('Item deleted successfully!', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'Error deleting item: {str(e)}', 'danger')
    return redirect(url_for('inventory.dashboard'))

@bp.route('/manage/models')
@login_required
def manage_models():
    page = request.args.get('page', 1, type=int)
    per_page = current_app.config['ITEMS_PER_PAGE']
    query = ComputerModel.query
    
    # Search by name or manufacturer
    search = request.args.get('search', '')
    if search:
        query = query.filter(
            db.or_(
                ComputerModel.model_name.ilike(f'%{search}%'),
                ComputerModel.manufacturer.ilike(f'%{search}%')
            )
        )
    
    # Filter by type
    model_type = request.args.get('type')
    if model_type:
        query = query.filter(ComputerModel.model_type == model_type)
    
    # Filter by manufacturer
    manufacturer = request.args.get('manufacturer')
    if manufacturer:
        query = query.filter(ComputerModel.manufacturer == manufacturer)
    
    # Order results
    sort_by = request.args.get('sort', 'manufacturer')
    order = request.args.get('order', 'asc')
    
    if sort_by == 'manufacturer':
        query = query.order_by(ComputerModel.manufacturer.asc() if order == 'asc' else ComputerModel.manufacturer.desc())
    elif sort_by == 'model_name':
        query = query.order_by(ComputerModel.model_name.asc() if order == 'asc' else ComputerModel.model_name.desc())
    elif sort_by == 'type':
        query = query.order_by(ComputerModel.model_type.asc() if order == 'asc' else ComputerModel.model_type.desc())
    
    models = query.paginate(page=page, per_page=per_page)
    
    return render_template('inventory/manage/models.html', 
                         models=models,
                         manufacturers=MANUFACTURER_CHOICES,
                         computer_types=COMPUTER_TYPES,
                         sort_by=sort_by,
                         order=order)

@bp.route('/manage/cpus')
@login_required
def manage_cpus():
    page = request.args.get('page', 1, type=int)
    per_page = current_app.config['ITEMS_PER_PAGE']
    query = CPU.query
    
    # Search and filter
    search = request.args.get('search', '')
    manufacturer = request.args.get('manufacturer')
    cores = request.args.get('cores', type=int)
    
    if search:
        query = query.filter(CPU.model.ilike(f'%{search}%'))
    if manufacturer:
        query = query.filter(CPU.manufacturer == manufacturer)
    if cores:
        query = query.filter(CPU.cores == cores)
    
    cpus = query.paginate(page=page, per_page=per_page)
    return render_template('inventory/manage/cpus.html', cpus=cpus)

@bp.route('/manage/cpus/add', methods=['GET', 'POST'])
@login_required
def add_cpu():
    form = CPUForm()
    if form.validate_on_submit():
        cpu = CPU(
            manufacturer=form.manufacturer.data,
            model=form.model.data,
            speed=form.speed.data,
            cores=form.cores.data
        )
        db.session.add(cpu)
        db.session.commit()
        flash('CPU added successfully!', 'success')
        return redirect(url_for('inventory.manage_cpus'))
    return render_template('inventory/manage/add_cpu.html', form=form)

@bp.route('/manage/cpus/<int:id>/edit', methods=['GET', 'POST'])
@login_required
def edit_cpu(id):
    cpu = CPU.query.get_or_404(id)
    form = CPUForm(obj=cpu)
    if form.validate_on_submit():
        form.populate_obj(cpu)
        db.session.commit()
        flash('CPU updated successfully!', 'success')
        return redirect(url_for('inventory.manage_cpus'))
    return render_template('inventory/manage/edit_cpu.html', form=form, cpu=cpu)

@bp.route('/manage/cpus/<int:id>/delete', methods=['POST'])
@login_required
def delete_cpu(id):
    cpu = CPU.query.get_or_404(id)
    try:
        db.session.delete(cpu)
        db.session.commit()
        flash('CPU deleted successfully!', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'Error deleting CPU: {str(e)}', 'danger')
    return redirect(url_for('inventory.manage_cpus'))

@bp.route('/manage/models/add', methods=['GET', 'POST'])
@login_required
def add_model():
    form = ComputerModelForm()
    if form.validate_on_submit():
        model = ComputerModel(
            manufacturer=form.manufacturer.data,
            model_name=form.model_name.data,
            model_type=form.model_type.data
        )
        db.session.add(model)
        db.session.commit()
        flash('Computer model added successfully!', 'success')
        return redirect(url_for('inventory.manage_models'))
    return render_template('inventory/manage/add_model.html', form=form)

@bp.route('/manage/models/<int:id>/edit', methods=['GET', 'POST'])
@login_required
def edit_model(id):
    model = ComputerModel.query.get_or_404(id)
    form = ComputerModelForm(obj=model)
    if form.validate_on_submit():
        form.populate_obj(model)
        db.session.commit()
        flash('Computer model updated successfully!', 'success')
        return redirect(url_for('inventory.manage_models'))
    return render_template('inventory/manage/edit_model.html', form=form, model=model)

@bp.route('/manage/models/<int:id>/delete', methods=['POST'])
@login_required
def delete_model(id):
    model = ComputerModel.query.get_or_404(id)
    try:
        db.session.delete(model)
        db.session.commit()
        flash('Computer model deleted successfully!', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'Error deleting model: {str(e)}', 'danger')
    return redirect(url_for('inventory.manage_models'))

@bp.route('/checkout', methods=['GET'])
def checkout():
    """Tablet-friendly checkout view"""
    # Create form for CSRF protection
    form = FlaskForm()
    
    # Get current tech from session if they're logged in
    current_tech = None
    if 'tech_id' in session:
        current_tech = User.query.get(session['tech_id'])
    
    # Get recent transactions if tech is logged in
    recent_transactions = []
    if current_tech:
        recent_transactions = InventoryTransaction.query\
            .filter_by(transaction_type='check_out')\
            .order_by(InventoryTransaction.timestamp.desc())\
            .limit(5)\
            .all()
    
    return render_template('inventory/checkout.html',
                         current_tech=current_tech,
                         recent_transactions=recent_transactions,
                         form=form)  # Pass form to template

@bp.route('/checkout/verify-pin', methods=['POST'])
def verify_pin():
    """Verify tech PIN and start checkout session"""
    pin = request.form.get('pin')
    
    # Find user by PIN
    tech = User.query.filter_by(pin_code=pin).first()
    if not tech:
        flash('Invalid PIN code', 'danger')
        return redirect(url_for('inventory.checkout'))
    
    # Store tech ID in session
    session['tech_id'] = tech.id
    flash(f'Welcome, {tech.username}!', 'success')
    return redirect(url_for('inventory.checkout'))

def check_low_stock(item):
    """Check if an item needs a stock alert and send if enabled"""
    if not Configuration.get_setting('enable_low_stock_alerts', 'false') == 'true':
        return
        
    if item.needs_restock:
        # Get all items that need restocking
        low_stock_items = InventoryItem.query.filter(
            InventoryItem.quantity <= InventoryItem.reorder_threshold,
            InventoryItem.reorder_threshold != None,
            InventoryItem.type != 'computer_system'  # Exclude computer systems
        ).all()
        
        if low_stock_items:
            send_stock_alert(low_stock_items)

@bp.route('/checkout/process', methods=['POST'])
def process_checkout():
    """Process item checkout"""
    if 'tech_id' not in session:
        flash('Please log in first', 'danger')
        return redirect(url_for('inventory.checkout'))
    
    tech = User.query.get(session['tech_id'])
    tracking_id = request.form.get('tracking_id')
    reason = request.form.get('reason')
    quantity = int(request.form.get('quantity', 1))
    
    # Find item
    item = InventoryItem.query.filter_by(tracking_id=tracking_id).first()
    if not item:
        flash('Item not found', 'danger')
        return redirect(url_for('inventory.checkout'))
    
    try:
        # Validate quantity for general items
        if not isinstance(item, ComputerSystem):
            if quantity > item.quantity:
                flash(f'Not enough items in stock. Available: {item.quantity}', 'danger')
                return redirect(url_for('inventory.checkout'))
        else:
            # Force quantity to 1 for computer systems
            quantity = 1
        
        # Create transaction record
        transaction = InventoryTransaction(
            item_id=item.id,
            transaction_type='check_out',
            quantity=quantity,
            user_id=tech.id,
            notes=reason
        )
        
        # Update item based on type
        if isinstance(item, ComputerSystem):
            item.status = 'removed'
        else:
            # Update quantity for general items
            item.quantity -= quantity
            
            # Update status based on remaining quantity
            if item.quantity == 0:
                item.status = 'out_of_stock'
            elif item.quantity <= item.reorder_threshold:
                item.status = 'restock'
                
            # Check if we need to send a stock alert
            check_low_stock(item)
        
        db.session.add(transaction)
        db.session.commit()
        
        flash(f'Successfully checked out {quantity} {item.name}', 'success')
        return redirect(url_for('inventory.checkout'))
        
    except Exception as e:
        db.session.rollback()
        flash(f'Error checking out item: {str(e)}', 'danger')
        current_app.logger.error(f'Checkout error: {str(e)}')
        return redirect(url_for('inventory.checkout'))

@bp.route('/checkout/logout', methods=['GET'])
def checkout_logout():
    """End checkout session"""
    session.pop('tech_id', None)
    flash('Logged out successfully', 'success')
    return redirect(url_for('inventory.checkout'))  # This will force a full page refresh

# List of common Chrome user agents
CHROME_USER_AGENTS = [
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
]

@bp.route('/api/scan_barcode', methods=['POST'])
@login_required
def scan_barcode():
    try:
        current_app.logger.debug('Barcode scan request received')
        current_app.logger.debug(f'Request data: {request.get_json()}')
        current_app.logger.debug(f'Request headers: {dict(request.headers)}')
        
        # Validate CSRF token from X-CSRFToken header
        csrf_token = request.headers.get('X-CSRFToken')
        current_app.logger.debug(f'CSRF Token from header: {csrf_token}')
        
        if not csrf_token:
            current_app.logger.error('Missing CSRF token')
            return jsonify({
                'error': 'Missing CSRF token',
                'message': 'Security token missing. Please refresh the page and try again.'
            }), 400
            
        try:
            validate_csrf(csrf_token)
        except Exception as e:
            current_app.logger.error(f'CSRF validation failed: {str(e)}')
            return jsonify({
                'error': 'Invalid CSRF token',
                'message': 'Security token invalid. Please refresh the page and try again.'
            }), 400
        
        data = request.get_json()
        if not data:
            current_app.logger.error('No JSON data in request')
            return jsonify({
                'error': 'Invalid request',
                'message': 'No data provided'
            }), 400
            
        barcode = data.get('barcode')
        current_app.logger.debug(f'Barcode to lookup: {barcode}')
        
        if not barcode:
            current_app.logger.error('No barcode provided')
            return jsonify({
                'error': 'No barcode provided',
                'message': 'Please enter a barcode'
            }), 400
        
        try:
            # UPCItemDB API endpoint
            url = f'https://api.upcitemdb.com/prod/trial/lookup?upc={barcode}'
            headers = {
                'User-Agent': random.choice(CHROME_USER_AGENTS),
                'Accept': 'application/json'
            }
            
            current_app.logger.debug(f'Making request to UPCItemDB: {url}')
            response = requests.get(url, headers=headers, timeout=10)
            current_app.logger.debug(f'UPCItemDB response status: {response.status_code}')
            
            try:
                response_data = response.json()
                current_app.logger.debug(f'UPCItemDB response data: {response_data}')
            except ValueError:
                current_app.logger.error(f'Invalid JSON in UPCItemDB response: {response.text}')
                return jsonify({
                    'error': 'Invalid response from UPC database',
                    'message': 'The UPC database returned an invalid response'
                }), 500
            
            # Initialize product info
            product_info = {
                'success': False,
                'message': 'No product information found',
                'name': None,
                'description': None,
                'manufacturer': None,
                'mpn': None,
                'image_url': None
            }
            
            # Extract information from the response
            if response_data.get('items') and len(response_data['items']) > 0:
                item = response_data['items'][0]  # Get the first item
                current_app.logger.debug(f'Found product: {item.get("title")}')
                
                # Extract basic information
                product_info.update({
                    'success': True,
                    'message': 'Product information found successfully',
                    'name': item.get('title'),
                    'description': item.get('description'),
                    'manufacturer': item.get('brand'),
                    'mpn': item.get('model'),
                    'image_url': item.get('images', [None])[0] if item.get('images') else None
                })
            
            return jsonify(product_info)
            
        except requests.exceptions.RequestException as e:
            current_app.logger.error(f'UPCItemDB API error: {str(e)}')
            return jsonify({
                'error': 'Failed to fetch product information',
                'message': f'API Error: {str(e)}'
            }), 500
        except Exception as e:
            current_app.logger.error(f'Error processing barcode lookup: {str(e)}')
            return jsonify({
                'error': 'Error processing barcode',
                'message': str(e)
            }), 500
            
    except Exception as e:
        current_app.logger.error(f'Unexpected error in scan_barcode: {str(e)}')
        return jsonify({
            'error': 'Server error',
            'message': 'An unexpected error occurred'
        }), 500

def generate_tracking_id():
    """Generate a unique tracking ID"""
    while True:
        tracking_id = f"TC-{uuid.uuid4().hex[:8].upper()}"
        if not InventoryItem.query.filter_by(tracking_id=tracking_id).first():
            return tracking_id

# User Management Routes
@bp.route('/users')
@login_required
@admin_required
def manage_users():
    users = User.query.all()
    return render_template('inventory/manage/users.html', users=users)

@bp.route('/users/add', methods=['GET', 'POST'])
@login_required
@admin_required
def add_user():
    if request.method == 'POST':
        username = request.form.get('username')
        email = request.form.get('email')
        password = request.form.get('password')
        role = request.form.get('role', 'user')
        pin = request.form.get('pin')

        if User.query.filter_by(username=username).first():
            flash('Username already exists', 'danger')
            return redirect(url_for('inventory.add_user'))

        if User.query.filter_by(email=email).first():
            flash('Email already exists', 'danger')
            return redirect(url_for('inventory.add_user'))

        user = User(username=username, email=email, role=role)
        user.set_password(password)
        if pin:
            try:
                user.set_pin(pin)
            except ValueError as e:
                flash(str(e), 'danger')
                return redirect(url_for('inventory.add_user'))

        db.session.add(user)
        db.session.commit()
        flash('User added successfully', 'success')
        return redirect(url_for('inventory.manage_users'))

    return render_template('inventory/manage/add_user.html')

@bp.route('/users/<int:id>/edit', methods=['GET', 'POST'])
@login_required
@admin_required
def edit_user(id):
    user = User.query.get_or_404(id)
    
    if request.method == 'POST':
        username = request.form.get('username')
        email = request.form.get('email')
        role = request.form.get('role')
        new_password = request.form.get('password')
        new_pin = request.form.get('pin')

        # Check if username is being changed and is unique
        if username != user.username and User.query.filter_by(username=username).first():
            flash('Username already exists', 'danger')
            return redirect(url_for('inventory.edit_user', id=id))

        # Check if email is being changed and is unique
        if email != user.email and User.query.filter_by(email=email).first():
            flash('Email already exists', 'danger')
            return redirect(url_for('inventory.edit_user', id=id))

        user.username = username
        user.email = email
        user.role = role

        if new_password:
            user.set_password(new_password)

        if new_pin:
            try:
                user.set_pin(new_pin)
            except ValueError as e:
                flash(str(e), 'danger')
                return redirect(url_for('inventory.edit_user', id=id))

        db.session.commit()
        flash('User updated successfully', 'success')
        return redirect(url_for('inventory.manage_users'))

    return render_template('inventory/manage/edit_user.html', user=user)

@bp.route('/users/<int:id>/delete', methods=['POST'])
@login_required
@admin_required
def delete_user(id):
    if current_user.id == id:
        flash('You cannot delete your own account', 'danger')
        return redirect(url_for('inventory.manage_users'))

    user = User.query.get_or_404(id)
    db.session.delete(user)
    db.session.commit()
    flash('User deleted successfully', 'success')
    return redirect(url_for('inventory.manage_users'))

@bp.route('/system/add', methods=['GET', 'POST'])
@login_required
def add_system():
    form = ComputerSystemForm()
    
    # Set up computer model and CPU choices
    computer_models = ComputerModel.query.order_by(ComputerModel.manufacturer, ComputerModel.model_name).all()
    form.model_id.choices = [(m.id, f"{m.manufacturer} {m.model_name}") for m in computer_models]
    
    cpus = CPU.query.order_by(CPU.manufacturer, CPU.model).all()
    form.cpu_id.choices = [(c.id, f"{c.manufacturer} {c.model}") for c in cpus]
    
    if request.method == 'POST':
        if form.validate():
            try:
                # Get the model and CPU for naming
                model = ComputerModel.query.get(form.model_id.data)
                cpu = CPU.query.get(form.cpu_id.data)
                
                # Create Computer System
                system = ComputerSystem(
                    tracking_id=generate_tracking_id(),
                    model_id=form.model_id.data,
                    cpu_id=form.cpu_id.data,
                    ram=form.ram.data,
                    storage=form.storage.data,
                    os=form.os.data,
                    storage_location=form.storage_location.data,
                    cpu_benchmark=form.cpu_benchmark.data,
                    usb_ports_status=form.usb_ports_status.data,
                    usb_ports_notes=form.usb_ports_notes.data,
                    video_status=form.video_status.data,
                    video_notes=form.video_notes.data,
                    network_status=form.network_status.data,
                    network_notes=form.network_notes.data,
                    general_notes=form.general_notes.data,
                    creator_id=current_user.id,
                    tested_by=current_user.id
                )
                
                db.session.add(system)
                db.session.commit()
                
                flash('Computer system added successfully!', 'success')
                return redirect(url_for('inventory.dashboard'))
                
            except Exception as e:
                db.session.rollback()
                current_app.logger.error(f'Error adding computer system: {str(e)}')
                flash(f'Error adding computer system: {str(e)}', 'danger')
        else:
            for field, errors in form.errors.items():
                for error in errors:
                    flash(f'{field}: {error}', 'danger')
    
    return render_template('inventory/add_system.html', 
                         form=form,
                         computer_models=computer_models,
                         cpus=cpus)

@bp.route('/system/<int:id>/view')
@login_required
def view_system(id):
    system = ComputerSystem.query.get_or_404(id)
    
    # Generate barcode
    barcode_io = io.BytesIO()
    Code128(system.tracking_id, writer=ImageWriter()).write(barcode_io)
    barcode_base64 = base64.b64encode(barcode_io.getvalue()).decode()
    
    return render_template('inventory/view_system.html', 
                         system=system,
                         barcode=barcode_base64)

@bp.route('/system/<int:id>/edit', methods=['GET', 'POST'])
@login_required
def edit_system(id):
    system = ComputerSystem.query.get_or_404(id)
    form = ComputerSystemForm(obj=system)
    
    if form.validate_on_submit():
        try:
            form.populate_obj(system)
            db.session.commit()
            flash('Computer system updated successfully!', 'success')
            return redirect(url_for('inventory.dashboard'))
        except Exception as e:
            db.session.rollback()
            flash(f'Error updating computer system: {str(e)}', 'danger')
            current_app.logger.error(f'Error updating computer system: {str(e)}')
    
    return render_template('inventory/edit_system.html', form=form, system=system)

@bp.route('/system/<int:id>/delete', methods=['POST'])
@login_required
def delete_system(id):
    system = ComputerSystem.query.get_or_404(id)
    try:
        db.session.delete(system)
        db.session.commit()
        flash('Computer system deleted successfully!', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'Error deleting computer system: {str(e)}', 'danger')
        current_app.logger.error(f'Error deleting computer system: {str(e)}')
    
    return redirect(url_for('inventory.dashboard'))

@bp.route('/system/<int:id>/label')
@login_required
def print_system_label(id):
    system = ComputerSystem.query.get_or_404(id)
    system.type = 'computer_system'  # Add type attribute for template
    
    # Generate barcode image
    barcode_io = io.BytesIO()
    Code128(system.tracking_id, writer=ImageWriter()).write(barcode_io)
    barcode_base64 = base64.b64encode(barcode_io.getvalue()).decode()
    
    # Return the print template
    return render_template('inventory/print_label.html',
                         item=system,
                         barcode=barcode_base64)