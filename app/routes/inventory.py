from flask import Blueprint, render_template, request, jsonify, flash, redirect, url_for, current_app, send_file, session
from flask_login import login_required, current_user
from flask_wtf import FlaskForm
from app.models.inventory import (
    InventoryItem, ComputerSystem, Category, 
    Transaction, ComputerModel, CPU, Tag, item_tags,
    WikiPage, WikiCategory, PurchaseLink
)
from app.models.config import Configuration
from app.utils.email import send_stock_alert
from app.forms import (
    ComputerModelForm, CPUForm, GeneralItemForm, InventoryItemForm,
    ComputerSystemForm, MANUFACTURER_CHOICES, 
    COMPUTER_TYPES, CategoryForm
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
from app.utils.activity_logger import log_inventory_activity, log_system_activity
from datetime import datetime
from sqlalchemy import or_

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
    # Get active tab from query parameters
    active_tab = request.args.get('active_tab', 'items')
    
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
                InventoryItem.tracking_id.ilike(f'%{search}%'),
                InventoryItem.barcode.ilike(f'%{search}%')
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
    
    # Computer Systems query with eager loading of tags
    systems_query = ComputerSystem.query.options(db.joinedload(ComputerSystem.tags))
    
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
    
    # Get all systems for DataTables with eager loading
    systems = systems_query.all()
    
    # Get categories and models for filter dropdowns
    categories = Category.get_ordered_categories()
    computer_models = ComputerModel.query.order_by(ComputerModel.manufacturer, ComputerModel.model_name).all()
    
    # Get Wiki pages
    wiki_search = request.args.get('wiki_search', '')
    wiki_category = request.args.get('wiki_category', type=int)
    
    wiki_query = WikiPage.query
    if wiki_search:
        wiki_query = wiki_query.filter(
            db.or_(
                WikiPage.title.ilike(f'%{wiki_search}%'),
                WikiPage.content.ilike(f'%{wiki_search}%')
            )
        )
    if wiki_category:
        wiki_query = wiki_query.filter_by(category_id=wiki_category)
    
    wiki_pages = wiki_query.order_by(WikiPage.updated_at.desc()).limit(10).all()
    wiki_categories = WikiCategory.query.order_by(WikiCategory.name).all()
    
    form = FlaskForm()  # For CSRF protection
    
    return render_template('inventory/dashboard.html',
                         items=items,
                         systems=systems,
                         categories=categories,
                         computer_models=computer_models,
                         wiki_pages=wiki_pages,
                         wiki_categories=wiki_categories,
                         form=form,
                         active_tab=active_tab)

@bp.route('/item/add', methods=['GET', 'POST'])
@login_required
def add_item():
    form = InventoryItemForm()
    form.category.choices = [(c.id, c.get_display_name()) for c in Category.get_ordered_categories()]
    form.tags.choices = [(t.id, t.name) for t in Tag.query.order_by(Tag.name).all()]
    
    if request.method == 'POST':
        try:
            # Create the item
            item = InventoryItem(
                tracking_id=generate_tracking_id(),
                name=form.name.data,
                description=form.description.data,
                quantity=form.quantity.data,
                min_quantity=form.min_quantity.data,
                reorder_threshold=form.reorder_threshold.data,
                location=form.location.data,
                storage_location=form.storage_location.data,
                manufacturer=form.manufacturer.data,
                mpn=form.mpn.data,
                image_url=form.image_url.data,
                cost=form.cost.data,
                sell_price=form.sell_price.data,
                category_id=form.category.data,
                creator_id=current_user.id
            )
            
            # Add purchase links
            purchase_link_urls = request.form.getlist('purchase_link_urls[]')
            purchase_link_titles = request.form.getlist('purchase_link_titles[]')
            
            for url, title in zip(purchase_link_urls, purchase_link_titles):
                if url.strip():  # Only add non-empty URLs
                    link = PurchaseLink(
                        url=url.strip(),
                        title=title.strip() if title else None,
                        created_by=current_user.id
                    )
                    item.purchase_links.append(link)
            
            # Handle tags
            tag_ids = request.form.get('tags', '').split(',')
            for tag_id in tag_ids:
                if tag_id.strip():
                    try:
                        tag = Tag.query.get(int(tag_id))
                        if tag:
                            item.tags.append(tag)
                    except (ValueError, TypeError) as e:
                        print(f"Invalid tag ID {tag_id}: {str(e)}")
            
            db.session.add(item)
            db.session.commit()
            
            flash('Item added successfully', 'success')
            return redirect(url_for('inventory.view_item', id=item.id))
            
        except Exception as e:
            db.session.rollback()
            flash(f'Error adding item: {str(e)}', 'error')
            return render_template('inventory/add_item.html', form=form)
    
    return render_template('inventory/add_item.html', form=form)

@bp.route('/item/<int:id>/view')
@login_required
def view_item(id):
    # Get item with transactions eager loaded
    item = InventoryItem.query.options(
        db.joinedload(InventoryItem.transactions).joinedload(Transaction.user)
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
    form = InventoryItemForm(obj=item)
    form.category.choices = [(c.id, c.get_display_name()) for c in Category.get_ordered_categories()]
    form.tags.choices = [(t.id, t.name) for t in Tag.query.order_by(Tag.name).all()]
    
    if request.method == 'POST':
        try:
            # Store original values for logging
            original_quantity = item.quantity
            original_location = item.storage_location
            original_values = {
                'location': item.storage_location,
                'name': item.name,
                'description': item.description,
                'manufacturer': item.manufacturer,
                'mpn': item.mpn,
                'category': item.category.name if item.category else None
            }
            
            # Update basic fields individually
            item.name = form.name.data
            item.description = form.description.data
            item.quantity = form.quantity.data
            item.min_quantity = form.min_quantity.data
            item.reorder_threshold = form.reorder_threshold.data
            item.location = form.location.data
            item.storage_location = form.storage_location.data
            item.manufacturer = form.manufacturer.data.strip() if form.manufacturer.data else None
            item.mpn = form.mpn.data.strip() if form.mpn.data else None
            item.barcode = form.barcode.data.strip() if form.barcode.data else None
            item.upc = form.upc.data.strip() if form.upc.data else None
            item.image_url = form.image_url.data.strip() if form.image_url.data else None
            item.cost = form.cost.data
            item.sell_price = form.sell_price.data
            item.category_id = form.category.data
            
            # If quantity changed, create a transaction record
            if item.quantity != original_quantity:
                quantity_change = item.quantity - original_quantity
                transaction = Transaction(
                    item_id=item.id,
                    user_id=current_user.id,
                    quantity_changed=quantity_change,
                    transaction_type='adjustment',
                    notes=f'Quantity adjusted from {original_quantity} to {item.quantity}'
                )
                db.session.add(transaction)
                
                # Log the quantity change
                log_inventory_activity('adjustment', item, {
                    'old_quantity': original_quantity,
                    'new_quantity': item.quantity,
                    'tracking_id': item.tracking_id
                })
            
            # Check if any other fields changed
            new_values = {
                'location': item.storage_location,
                'name': item.name,
                'description': item.description,
                'manufacturer': item.manufacturer,
                'mpn': item.mpn,
                'category': item.category.name if item.category else None
            }
            
            # Log item update if any fields changed
            if any(original_values[k] != new_values[k] for k in original_values):
                changes = {k: {'old': original_values[k], 'new': new_values[k]} 
                          for k in original_values if original_values[k] != new_values[k]}
                log_inventory_activity('update_item', item, {
                    'changes': changes,
                    'tracking_id': item.tracking_id
                })
            
            # Update purchase links
            purchase_link_urls = request.form.getlist('purchase_link_urls[]')
            purchase_link_titles = request.form.getlist('purchase_link_titles[]')
            
            # Remove all existing links
            item.purchase_links = []
            
            # Add new links
            for url, title in zip(purchase_link_urls, purchase_link_titles):
                if url.strip():  # Only add non-empty URLs
                    link = PurchaseLink(
                        url=url.strip(),
                        title=title.strip() if title else None,
                        created_by=current_user.id
                    )
                    item.purchase_links.append(link)
            
            # Handle tags
            raw_tags = request.form.get('tags', '').split(',')
            tag_ids = []
            for tag_id in raw_tags:
                if tag_id.strip():
                    try:
                        tag_ids.append(int(tag_id))
                    except (ValueError, TypeError) as e:
                        print(f"Invalid tag ID {tag_id}: {str(e)}")
            
            # Clear existing tags and add new ones
            item.tags = []
            if tag_ids:
                tags = Tag.query.filter(Tag.id.in_(tag_ids)).all()
                for tag in tags:
                    item.tags.append(tag)
            
            db.session.commit()
            
            flash('Item updated successfully!', 'success')
            return redirect(url_for('inventory.dashboard'))
            
        except Exception as e:
            db.session.rollback()
            flash(f'Error updating item: {str(e)}', 'danger')
            current_app.logger.error(f'Error updating item: {str(e)}')
    else:
        # For GET request, explicitly set the category and tags
        form.category.data = item.category_id
        form.tags.data = [str(tag.id) for tag in item.tags]
    
    return render_template('inventory/edit_item.html', form=form, item=item)

@bp.route('/item/<int:id>/delete', methods=['POST'])
@login_required
def delete_item(id):
    item = InventoryItem.query.get_or_404(id)
    try:
        # Log the activity before deletion
        log_inventory_activity('delete', item, {
            'name': item.name,
            'category': item.category.name if item.category else None
        })
        
        db.session.delete(item)
        db.session.commit()
        flash('Item deleted successfully!', 'success')
        
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Error deleting item: {str(e)}")
        flash('Error deleting item', 'error')
        
    return redirect(url_for('inventory.dashboard'))

@bp.route('/manage/models')
@login_required
def manage_models():
    """
    Route for managing computer models.
    Returns all models ordered by manufacturer and model name.
    """
    # Create a form instance for CSRF token
    form = ComputerModelForm()
    
    # Get all models ordered by manufacturer and model name
    models = ComputerModel.query.order_by(ComputerModel.manufacturer, ComputerModel.model_name).all()
    
    return render_template('inventory/manage/models.html', models=models, form=form)

@bp.route('/manage/cpus')
@login_required
def manage_cpus():
    # Create a form instance for CSRF token
    form = CPUForm()
    # Get all CPUs ordered by manufacturer and model
    cpus = CPU.query.order_by(CPU.manufacturer, CPU.model).all()
    return render_template('inventory/manage/cpus.html', cpus=cpus, form=form)

@bp.route('/manage/cpus/add', methods=['GET', 'POST'])
@login_required
def add_cpu():
    form = CPUForm()
    if request.method == 'POST':
        print("\n=== Debug: Add CPU POST Request ===")
        print(f"Form Data: {request.form.to_dict()}")
        
        if form.validate_on_submit():
            print("Form validation successful")
            try:
                # Speed is already formatted as "X.XX GHz" by form validation
                cpu = CPU(
                    manufacturer=form.manufacturer.data,
                    model=form.model.data,
                    speed=form.speed.data,
                    cores=form.cores.data,
                    benchmark=form.benchmark.data
                )
                db.session.add(cpu)
                db.session.commit()
                print(f"CPU added successfully: {cpu.manufacturer} {cpu.model}")
                flash('CPU added successfully!', 'success')
                return redirect(url_for('inventory.manage_cpus'))
            except Exception as e:
                db.session.rollback()
                print(f"Error adding CPU: {str(e)}")
                flash(f'Error adding CPU: {str(e)}', 'danger')
        else:
            print("Form validation failed")
            print(f"Form errors: {form.errors}")
            for field, errors in form.errors.items():
                for error in errors:
                    flash(f'{field}: {error}', 'danger')
    
    return render_template('inventory/manage/add_cpu.html', form=form)

@bp.route('/manage/cpus/<int:id>/edit', methods=['GET', 'POST'])
@login_required
def edit_cpu(id):
    cpu = CPU.query.get_or_404(id)
    form = CPUForm(obj=cpu)
    
    if request.method == 'GET':
        # Speed is already in the correct format from database
        form.speed.data = cpu.speed
    
    if form.validate_on_submit():
        try:
            # Store original values for logging
            original_values = {
                'manufacturer': cpu.manufacturer,
                'model': cpu.model,
                'speed': cpu.speed,
                'cores': cpu.cores,
                'benchmark': cpu.benchmark
            }
            
            # Update CPU fields
            cpu.manufacturer = form.manufacturer.data
            cpu.model = form.model.data
            cpu.speed = form.speed.data  # Speed is already formatted by form validation
            cpu.cores = form.cores.data
            cpu.benchmark = form.benchmark.data
            
            db.session.commit()
            
            # Log the update
            changes = {k: {'old': original_values[k], 'new': getattr(cpu, k)} 
                      for k in original_values 
                      if original_values[k] != getattr(cpu, k)}
            
            if changes:
                log_inventory_activity('update_cpu', cpu, {
                    'changes': changes
                })
            
            flash('CPU updated successfully!', 'success')
            return redirect(url_for('inventory.manage_cpus'))
            
        except Exception as e:
            db.session.rollback()
            flash(f'Error updating CPU: {str(e)}', 'danger')
            current_app.logger.error(f'Error updating CPU: {str(e)}')
    else:
        for field, errors in form.errors.items():
            for error in errors:
                flash(f'{field}: {error}', 'danger')
    
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
        recent_transactions = Transaction.query\
            .filter_by(transaction_type='check_out')\
            .order_by(Transaction.created_at.desc())\
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
    
    if not pin:
        flash('Please enter a PIN', 'danger')
        return redirect(url_for('inventory.checkout'))
    
    # Find all users and check their PINs
    users = User.query.all()
    tech = None
    for user in users:
        if user.check_pin(pin):
            tech = user
            break
    
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
        transaction = Transaction(
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
        
        # Log the activity
        log_inventory_activity('checkout', item, {
            'quantity': quantity,
            'remaining': item.quantity
        })
        
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

def create_or_get_category_hierarchy(category_path):
    """
    Create or get categories from a hierarchical path string.
    Example: "Electronics > Networking > Bridges & Routers > Wireless Access Points"
    Returns the most specific (leaf) category.
    """
    if not category_path:
        return None
        
    categories = [cat.strip() for cat in category_path.split('>')]
    parent_id = None
    last_category = None
    
    for category_name in categories:
        # Look for existing category at this level
        category = Category.query.filter_by(
            name=category_name,
            parent_id=parent_id
        ).first()
        
        # Create if it doesn't exist
        if not category:
            category = Category(
                name=category_name,
                parent_id=parent_id,
                category_metadata={'full_path': category_path}
            )
            db.session.add(category)
            db.session.commit()  # Commit to get the ID for next iteration
            
        parent_id = category.id
        last_category = category
    
    return last_category

@bp.route('/scan_barcode', methods=['POST'])
@login_required
def scan_barcode():
    try:
        current_app.logger.debug('Barcode scan request received')
        data = request.get_json()
        current_app.logger.debug(f'Request data: {data}')
        
        if not data or 'barcode' not in data:
            return jsonify({
                'success': False,
                'message': 'No barcode provided'
            }), 400
            
        barcode = data['barcode']
        current_app.logger.debug(f'Barcode to lookup: {barcode}')
        
        # Get API key from environment
        api_key = current_app.config.get('UPCITEMDB_API_KEY')
        if not api_key:
            return jsonify({
                'success': False,
                'message': 'API key not configured'
            }), 500
            
        # UPCItemDB API endpoint
        url = f'https://api.upcitemdb.com/prod/v1/lookup?upc={barcode}'
        headers = {
            'user_key': api_key,
            'key_type': '3scale'
        }
        
        current_app.logger.debug(f'Making request to UPCItemDB with headers: {headers}')
        
        # Make the API request
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        
        # Parse the response
        result = response.json()
        
        if not result.get('items'):
            return jsonify({
                'success': False,
                'message': 'No product found for this barcode'
            }), 404
            
        # Get the first item from the results
        item_data = result['items'][0]
        
        # Create category hierarchy if category exists
        category = None
        if item_data.get('category'):
            category = create_or_get_category_hierarchy(item_data['category'])
            current_app.logger.debug(f'Created/found category: {category.name if category else None}')
        
        # Prepare the response data
        # Use model as name, fallback to title if model is not available
        name = item_data.get('model')
        if not name:
            name = item_data.get('title')
        if item_data.get('brand'):
            name = f"{item_data['brand']} {name}"
            
        response_data = {
            'success': True,
            'name': name,
            'description': item_data.get('description', ''),
            'manufacturer': item_data.get('brand', ''),
            'mpn': item_data.get('model', ''),
            'category_id': category.id if category else None,
            'category_name': category.get_full_path() if category else None,
            'image_url': item_data.get('images', [''])[0] if item_data.get('images') else '',
            'upc': item_data.get('upc', '')
        }
        
        return jsonify(response_data)
        
    except requests.exceptions.RequestException as e:
        current_app.logger.error(f'UPCItemDB API error: {str(e)}')
        return jsonify({
            'success': False,
            'message': 'Error connecting to UPC database'
        }), 500
        
    except Exception as e:
        current_app.logger.error(f'Unexpected error in scan_barcode: {str(e)}')
        return jsonify({
            'success': False,
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
        print("\n=== Debug: Add System POST Request ===")
        print(f"Form Data: {request.form.to_dict()}")
        print(f"Serial Number from form: {form.serial_tag.data}")
        
        if form.validate():
            try:
                # Get the model and CPU for naming
                model = ComputerModel.query.get(form.model_id.data)
                cpu = CPU.query.get(form.cpu_id.data)
                
                # Create Computer System without tags first
                system = ComputerSystem(
                    tracking_id=generate_tracking_id(),
                    serial_tag=form.serial_tag.data,
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
                
                print(f"Debug: Created system with serial_tag: {system.serial_tag}")
                
                # Add tags
                if form.tags.data:
                    tags = Tag.query.filter(Tag.id.in_(form.tags.data)).all()
                    system.tags.extend(tags)
                
                db.session.add(system)
                db.session.commit()
                
                print(f"Debug: After commit, system serial_tag: {system.serial_tag}")
                
                # Log the activity
                log_system_activity('add', system)
                
                flash('Computer system added successfully!', 'success')
                return redirect(url_for('inventory.dashboard', active_tab='systems'))
                
            except Exception as e:
                db.session.rollback()
                print(f"Debug: Error occurred: {str(e)}")
                current_app.logger.error(f'Error adding computer system: {str(e)}')
                flash(f'Error adding computer system: {str(e)}', 'danger')
        else:
            print("Debug: Form validation failed")
            print(f"Form errors: {form.errors}")
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
    try:
        system = ComputerSystem.query.get_or_404(id)
        form = ComputerSystemForm(obj=system)
        
        # Set up computer model and CPU choices
        computer_models = ComputerModel.query.order_by(ComputerModel.manufacturer, ComputerModel.model_name).all()
        form.model_id.choices = [(m.id, f"{m.manufacturer} {m.model_name}") for m in computer_models]
        
        cpus = CPU.query.order_by(CPU.manufacturer, CPU.model).all()
        form.cpu_id.choices = [(c.id, f"{c.manufacturer} {c.model}") for c in cpus]
        
        if request.method == 'POST':
            if form.validate():
                try:
                    # Store original values for logging
                    original_model = ComputerModel.query.get(system.model_id)
                    original_cpu = CPU.query.get(system.cpu_id)
                    original_values = {
                        'model': f"{original_model.manufacturer} {original_model.model_name}",
                        'cpu': f"{original_cpu.manufacturer} {original_cpu.model}",
                        'ram': system.ram,
                        'storage': system.storage,
                        'location': system.storage_location,
                        'os': system.os,
                        'cpu_benchmark': system.cpu_benchmark,
                        'usb_ports_status': system.usb_ports_status,
                        'video_status': system.video_status,
                        'network_status': system.network_status
                    }
                    
                    # Update system fields
                    system.serial_tag = form.serial_tag.data
                    system.model_id = form.model_id.data
                    system.cpu_id = form.cpu_id.data
                    system.ram = form.ram.data
                    system.storage = form.storage.data
                    system.os = form.os.data
                    system.storage_location = form.storage_location.data
                    system.cpu_benchmark = form.cpu_benchmark.data
                    system.usb_ports_status = form.usb_ports_status.data
                    system.usb_ports_notes = form.usb_ports_notes.data
                    system.video_status = form.video_status.data
                    system.video_notes = form.video_notes.data
                    system.network_status = form.network_status.data
                    system.network_notes = form.network_notes.data
                    system.general_notes = form.general_notes.data
                    
                    # Handle tags
                    raw_tags = request.form.get('tags', '').split(',')
                    tag_ids = []
                    for tag_id in raw_tags:
                        if tag_id.strip():
                            try:
                                tag_ids.append(int(tag_id))
                            except (ValueError, TypeError) as e:
                                print(f"Invalid tag ID {tag_id}: {str(e)}")
                    
                    # Clear existing tags
                    system.tags = []
                    
                    if tag_ids:
                        # Fetch and validate tags
                        tags = Tag.query.filter(Tag.id.in_(tag_ids)).all()
                        found_ids = [t.id for t in tags]
                        
                        # Check if all requested tags were found
                        missing = set(tag_ids) - set(found_ids)
                        if missing:
                            raise ValueError(f"Some tags were not found: {missing}")
                        
                        # Add tags one by one
                        for tag in tags:
                            system.tags.append(tag)
                    
                    db.session.commit()
                    
                    # Get new values for logging
                    new_model = ComputerModel.query.get(system.model_id)
                    new_cpu = CPU.query.get(system.cpu_id)
                    new_values = {
                        'model': f"{new_model.manufacturer} {new_model.model_name}",
                        'cpu': f"{new_cpu.manufacturer} {new_cpu.model}",
                        'ram': system.ram,
                        'storage': system.storage,
                        'location': system.storage_location,
                        'os': system.os,
                        'cpu_benchmark': system.cpu_benchmark,
                        'usb_ports_status': system.usb_ports_status,
                        'video_status': system.video_status,
                        'network_status': system.network_status
                    }
                    
                    # Create details for logging
                    changes = []
                    for key in original_values:
                        if original_values[key] != new_values[key]:
                            changes.append(f"{key}:\nOld Value: {original_values[key]}\nNew Value: {new_values[key]}")
                    
                    if changes:
                        log_system_activity('update', system, {
                            'system': f"{new_model.manufacturer} {new_model.model_name}",
                            'changes': changes
                        })
                    
                    flash('Computer system updated successfully!', 'success')
                    return redirect(url_for('inventory.dashboard', active_tab='systems'))
                    
                except Exception as e:
                    db.session.rollback()
                    flash(f'Error updating computer system: {str(e)}', 'danger')
                    current_app.logger.error(f'Error updating computer system: {str(e)}')
            else:
                for field, errors in form.errors.items():
                    for error in errors:
                        flash(f'{field}: {error}', 'danger')
        
        # GET request - populate form
        form.tags.data = [str(tag.id) for tag in system.tags]
        
        return render_template('inventory/edit_system.html', form=form, system=system)
        
    except Exception as e:
        flash(f'An unexpected error occurred: {str(e)}', 'danger')
        current_app.logger.error(f'Unexpected error in edit_system: {str(e)}')
        return redirect(url_for('inventory.dashboard', active_tab='systems'))

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

@bp.route('/manage/tags')
@login_required
@admin_required
def manage_tags():
    tags = Tag.query.order_by(Tag.name).all()
    
    # Count items for each tag
    tag_counts = {}
    for tag in tags:
        count = db.session.query(item_tags).filter_by(tag_id=tag.id).count()
        tag_counts[tag.id] = count
    
    return render_template('inventory/manage/tags.html', 
                         tags=tags,
                         tag_counts=tag_counts)

@bp.route('/manage/tags/add', methods=['POST'])
@login_required
@admin_required
def add_tag():
    name = request.form.get('name')
    color = request.form.get('color', '#6c757d')  # Get color from form, default to secondary
    
    if not name:
        flash('Tag name is required', 'error')
        return redirect(url_for('inventory.manage_tags'))
    
    if Tag.query.filter_by(name=name).first():
        flash('Tag already exists', 'error')
        return redirect(url_for('inventory.manage_tags'))
    
    tag = Tag(name=name, color=color)
    db.session.add(tag)
    db.session.commit()
    flash('Tag added successfully', 'success')
    return redirect(url_for('inventory.manage_tags'))

@bp.route('/manage/tags/<int:id>/edit', methods=['POST'])
@login_required
@admin_required
def edit_tag(id):
    tag = Tag.query.get_or_404(id)
    name = request.form.get('name')
    color = request.form.get('color', tag.color)  # Get new color or keep existing
    
    if not name:
        flash('Tag name is required', 'error')
        return redirect(url_for('inventory.manage_tags'))
    
    existing = Tag.query.filter_by(name=name).first()
    if existing and existing.id != id:
        flash('Tag name already exists', 'error')
        return redirect(url_for('inventory.manage_tags'))
    
    tag.name = name
    tag.color = color
    db.session.commit()
    flash('Tag updated successfully', 'success')
    return redirect(url_for('inventory.manage_tags'))

@bp.route('/manage/tags/<int:id>/delete', methods=['POST'])
@login_required
@admin_required
def delete_tag(id):
    tag = Tag.query.get_or_404(id)
    db.session.delete(tag)
    db.session.commit()
    flash('Tag deleted successfully', 'success')
    return redirect(url_for('inventory.manage_tags'))

@bp.route('/test_upc', methods=['GET'])
@login_required
def test_upc():
    """Test endpoint for UPC lookups"""
    api_key = current_app.config.get('UPCITEMDB_API_KEY')
    if not api_key:
        return jsonify({'error': 'API key not configured'}), 500
        
    # Test UPC code
    test_upc = "190199267039"  # Example UPC for testing
    
    # UPCItemDB API endpoint
    url = "https://api.upcitemdb.com/prod/trial/lookup"
    headers = {
        'user_key': api_key,
        'Content-Type': 'application/json'
    }
    params = {'upc': test_upc}
    
    try:
        response = requests.get(url, headers=headers, params=params)
        response.raise_for_status()
        return jsonify(response.json())
    except requests.exceptions.RequestException as e:
        current_app.logger.error(f"UPC lookup error: {str(e)}")
        return jsonify({'error': str(e)}), 500

@bp.route('/categories/add', methods=['GET', 'POST'])
@login_required
@admin_required
def add_category():
    form = CategoryForm()
    # Always populate parent choices with top-level categories
    parent_categories = Category.query.filter_by(parent_id=None).order_by(Category.name).all()
    form.parent_id.choices = [(c.id, c.name) for c in parent_categories]
    form.parent_id.choices.insert(0, ('', 'None'))  # Add None option for parent categories
    
    if request.method == 'POST':
        category_type = request.form.get('category_type')
        
        # If it's a parent category, set parent_id to None and skip validation
        if category_type == 'parent':
            form.parent_id.data = None
            # Remove parent_id from form validation
            delattr(form.parent_id, 'validators')
        
        if form.validate_on_submit():
            try:
                category = Category(
                    name=form.name.data,
                    parent_id=form.parent_id.data if category_type == 'child' else None
                )
                db.session.add(category)
                db.session.commit()
                flash('Category added successfully!', 'success')
                return redirect(url_for('inventory.manage_categories'))
            except Exception as e:
                db.session.rollback()
                flash(f'Error adding category: {str(e)}', 'danger')
        else:
            if form.errors:
                for field, errors in form.errors.items():
                    for error in errors:
                        flash(f'{field}: {error}', 'danger')
    
    return render_template('inventory/add_category.html', form=form)

@bp.route('/categories')
@login_required
@admin_required
def manage_categories():
    page = request.args.get('page', 1, type=int)
    per_page = current_app.config.get('CATEGORIES_PER_PAGE', 10)
    parent_filter = request.args.get('parent_filter', type=int)
    
    # Get all parent categories for the dropdown
    parent_categories = Category.query.filter_by(parent_id=None).order_by(Category.name).all()
    
    # Base query for categories
    query = Category.query
    
    # Apply parent filter if selected
    if parent_filter:
        # Get the parent category and its children
        parent = Category.query.get(parent_filter)
        if parent:
            categories = [parent]  # Start with the parent
            children = Category.query.filter_by(parent_id=parent_filter).order_by(Category.name).all()
            categories.extend(children)  # Add all children
    else:
        categories = Category.get_ordered_categories()
    
    # Pagination
    paginated_categories = categories[(page-1)*per_page:page*per_page]
    total_pages = (len(categories) + per_page - 1) // per_page
    
    return render_template('inventory/manage_categories.html', 
                         categories=paginated_categories,
                         parent_categories=parent_categories,
                         selected_parent=parent_filter,
                         page=page,
                         total_pages=total_pages)

@bp.route('/category/<int:id>/edit', methods=['GET', 'POST'])
@login_required
@admin_required
def edit_category(id):
    category = Category.query.get_or_404(id)
    form = CategoryForm(obj=category)
    if form.validate_on_submit():
        category.name = form.name.data
        category.parent_id = form.parent_id.data if form.category_type.data == 'child' else None
        db.session.commit()
        flash('Category updated successfully!', 'success')
        return redirect(url_for('inventory.manage_categories'))
    categories = Category.get_ordered_categories()
    form.parent_id.choices = [(c.id, c.get_display_name()) for c in categories if c.id != category.id]
    return render_template('inventory/edit_category.html', form=form, category=category)

@bp.route('/category/<int:id>/delete', methods=['POST'])
@login_required
@admin_required
def delete_category(id):
    category = Category.query.get_or_404(id)
    
    # Check if category has children
    if Category.query.filter_by(parent_id=category.id).first():
        flash('Cannot delete category that has child categories. Please delete or reassign child categories first.', 'danger')
        return redirect(url_for('inventory.manage_categories'))
    
    try:
        db.session.delete(category)
        db.session.commit()
        flash('Category deleted successfully!', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'Error deleting category: {str(e)}', 'danger')
    return redirect(url_for('inventory.manage_categories'))

@bp.route('/api/cpu/<int:id>/benchmark')
@login_required
def get_cpu_benchmark(id):
    cpu = CPU.query.get_or_404(id)
    return jsonify({'benchmark': cpu.benchmark})