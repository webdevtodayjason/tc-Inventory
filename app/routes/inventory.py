from flask import Blueprint, render_template, request, jsonify, flash, redirect, url_for, current_app, send_file, session
from flask_login import login_required, current_user
from flask_wtf import FlaskForm
from app.models.inventory import (
    InventoryItem, ComputerSystem, Category, 
    InventoryTransaction, ComputerModel, CPU, Tag
)
from app.forms import (
    ComputerModelForm, CPUForm, ItemForm, 
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

bp = Blueprint('inventory', __name__)

@bp.route('/dashboard')
@login_required
def dashboard():
    page = request.args.get('page', 1, type=int)
    per_page = current_app.config['ITEMS_PER_PAGE']
    query = InventoryItem.query
    
    # Filter out removed computer systems by default
    query = query.filter(
        db.or_(
            InventoryItem.type != 'computer_system',  # Show all non-computer items
            db.and_(
                InventoryItem.type == 'computer_system',
                InventoryItem.status != 'removed'  # Only show non-removed computers
            )
        )
    )
    
    # Search functionality
    search = request.args.get('search', '')
    if search:
        query = query.filter(
            db.or_(
                InventoryItem.name.ilike(f'%{search}%'),
                InventoryItem.tracking_id.ilike(f'%{search}%')
            )
        )
    
    # Filter by type
    item_type = request.args.get('type')
    if item_type:
        query = query.filter(InventoryItem.type == item_type)
    
    # Filter by category
    category_id = request.args.get('category', type=int)
    if category_id:
        query = query.filter(InventoryItem.category_id == category_id)
    
    # Add status filter
    status = request.args.get('status')
    if status == 'restock':
        query = query.filter(
            db.and_(
                InventoryItem.quantity <= InventoryItem.reorder_threshold,
                InventoryItem.reorder_threshold != None
            )
        )
    elif status:
        query = query.filter(InventoryItem.status == status)
    
    # Show removed items if specifically requested
    show_removed = request.args.get('show_removed', type=bool)
    if not show_removed:
        query = query.filter(
            db.or_(
                InventoryItem.status != 'removed',
                InventoryItem.type != 'computer_system'
            )
        )
    
    # Sorting
    sort_by = request.args.get('sort', 'tracking_id')
    order = request.args.get('order', 'asc')
    
    if sort_by == 'tracking_id':
        query = query.order_by(InventoryItem.tracking_id.asc() if order == 'asc' else InventoryItem.tracking_id.desc())
    elif sort_by == 'name':
        query = query.order_by(InventoryItem.name.asc() if order == 'asc' else InventoryItem.name.desc())
    
    # Pagination
    items = query.paginate(page=page, per_page=per_page)
    
    # Get categories for filter dropdown
    categories = Category.query.order_by(Category.name).all()
    
    form = FlaskForm()  # For CSRF protection
    return render_template('inventory/dashboard.html',
                         items=items,
                         categories=categories,
                         form=form,
                         sort_by=sort_by,
                         order=order,
                         show_removed=show_removed)

@bp.route('/item/add', methods=['GET', 'POST'])
@login_required
def add_item():
    form = ItemForm()
    categories = Category.query.order_by(Category.name).all()
    computer_models = ComputerModel.query.order_by(ComputerModel.manufacturer, ComputerModel.model_name).all()
    cpus = CPU.query.order_by(CPU.manufacturer, CPU.model).all()
    
    if form.validate_on_submit():
        try:
            if form.type.data == 'computer':
                # Get the model and CPU for naming
                model = ComputerModel.query.get(form.model_id.data)
                cpu = CPU.query.get(form.cpu_id.data)
                
                # Get the Computer Systems category
                computer_systems_category = Category.query.filter_by(name='Computer Systems').first()
                if not computer_systems_category:
                    flash('Error: Computer Systems category not found', 'danger')
                    return redirect(url_for('inventory.dashboard'))
                
                # Create Computer System
                item = ComputerSystem(
                    tracking_id=generate_tracking_id(),
                    name=f"{model.manufacturer} {model.model_name} - {cpu.model}",
                    category_id=computer_systems_category.id,
                    model_id=form.model_id.data,
                    cpu_id=form.cpu_id.data,
                    ram=form.ram.data,
                    storage=form.storage.data,
                    os=form.os.data,
                    cpu_benchmark=form.cpu_benchmark.data,
                    usb_ports_status=form.usb_ports_status.data,
                    usb_ports_notes=form.usb_ports_notes.data,
                    video_status=form.video_status.data,
                    video_notes=form.video_notes.data,
                    network_status=form.network_status.data,
                    network_notes=form.network_notes.data,
                    general_notes=form.general_notes.data,
                    created_by=current_user.id,
                    tested_by=current_user.id,
                    cost=form.cost.data,
                    purchase_url=form.purchase_url.data,
                    sell_price=form.sell_price.data,
                    tags=[Tag.query.get(tag_id) for tag_id in form.tags.data] if form.tags.data else []
                )
            else:
                # Create General Item
                item = InventoryItem(
                    tracking_id=generate_tracking_id(),
                    name=form.name.data,
                    category_id=form.category.data,
                    quantity=form.quantity.data,
                    reorder_threshold=form.reorder_threshold.data,
                    created_by=current_user.id,
                    cost=form.cost.data,
                    purchase_url=form.purchase_url.data,
                    sell_price=form.sell_price.data,
                    tags=[Tag.query.get(tag_id) for tag_id in form.tags.data] if form.tags.data else []
                )
            
            db.session.add(item)
            db.session.commit()
            flash('Item added successfully!', 'success')
            return redirect(url_for('inventory.dashboard'))
            
        except Exception as e:
            db.session.rollback()
            flash(f'Error adding item: {str(e)}', 'danger')
            current_app.logger.error(f'Error adding item: {str(e)}')
    
    return render_template('inventory/add_item.html', 
                         form=form,
                         categories=categories,
                         computer_models=computer_models,
                         cpus=cpus)

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
    item = InventoryItem.query.get_or_404(id)
    
    # Generate PDF with ReportLab
    from reportlab.lib import colors
    from reportlab.lib.pagesizes import landscape
    from reportlab.lib.units import inch
    from reportlab.pdfgen import canvas
    from reportlab.graphics.barcode import code128
    
    # Create a BytesIO buffer for the PDF
    buffer = io.BytesIO()
    
    # Create the PDF canvas (2x4 inches)
    c = canvas.Canvas(buffer, pagesize=(4*inch, 2*inch))
    
    # Add item details
    c.setFont("Helvetica-Bold", 12)
    c.drawString(0.2*inch, 1.5*inch, item.name)
    
    if isinstance(item, ComputerSystem):
        c.setFont("Helvetica", 10)
        c.drawString(0.2*inch, 1.2*inch, f"Model: {item.model.manufacturer} {item.model.model_name}")
        c.drawString(0.2*inch, 1.0*inch, f"CPU: {item.cpu.manufacturer} {item.cpu.model}")
        c.drawString(0.2*inch, 0.8*inch, f"RAM: {item.ram}")
    
    # Add barcode
    barcode = code128.Code128(item.tracking_id, barHeight=0.4*inch)
    barcode.drawOn(c, 0.2*inch, 0.3*inch)
    
    # Add tracking ID below barcode
    c.setFont("Helvetica", 8)
    c.drawString(0.2*inch, 0.1*inch, item.tracking_id)
    
    c.save()
    buffer.seek(0)
    
    return send_file(
        buffer,
        as_attachment=True,
        download_name=f"label_{item.tracking_id}.pdf",
        mimetype='application/pdf'
    )

@bp.route('/item/<int:id>/edit', methods=['GET', 'POST'])
@login_required
def edit_item(id):
    item = InventoryItem.query.get_or_404(id)
    categories = Category.query.order_by(Category.name).all()
    
    if isinstance(item, ComputerSystem):
        form = ComputerSystemForm(obj=item)
        if form.validate_on_submit():
            try:
                # Manually update fields for computer system
                item.cost = request.form.get('cost', type=float)
                item.purchase_url = request.form.get('purchase_url')
                item.sell_price = request.form.get('sell_price', type=float)
                
                # Update computer-specific fields
                form.populate_obj(item)
                
                # Handle tags
                if request.form.getlist('tags'):
                    item.tags = [Tag.query.get(tag_id) for tag_id in request.form.getlist('tags')]
                
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
        form = ItemForm(obj=item)
        if request.method == 'POST':
            try:
                # Manually update fields
                item.name = request.form.get('name')
                item.category_id = request.form.get('category_id', type=int)
                item.quantity = int(request.form.get('quantity', 0))
                item.reorder_threshold = request.form.get('reorder_threshold', type=int)
                item.cost = request.form.get('cost', type=float)
                item.purchase_url = request.form.get('purchase_url')
                item.sell_price = request.form.get('sell_price', type=float)
                
                # Handle tags
                if request.form.getlist('tags'):
                    item.tags = [Tag.query.get(tag_id) for tag_id in request.form.getlist('tags')]
                
                # Log the values before commit
                current_app.logger.debug(f'Updating item {item.id}:')
                current_app.logger.debug(f'Name: {item.name}')
                current_app.logger.debug(f'Category: {item.category_id}')
                current_app.logger.debug(f'Quantity: {item.quantity}')
                current_app.logger.debug(f'Reorder Threshold: {item.reorder_threshold}')
                
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
                             categories=categories)

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

@bp.route('/checkout/process', methods=['POST'])
def process_checkout():
    """Process item checkout"""
    if 'tech_id' not in session:
        flash('Please log in first', 'danger')
        return redirect(url_for('inventory.checkout'))
    
    tech = User.query.get(session['tech_id'])
    tracking_id = request.form.get('tracking_id')
    reason = request.form.get('reason')
    quantity = int(request.form.get('quantity', 1))  # Get quantity from form
    
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
            quantity=quantity,  # Use the requested quantity
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

def generate_tracking_id():
    """Generate a unique tracking ID"""
    while True:
        tracking_id = f"TC-{uuid.uuid4().hex[:8].upper()}"
        if not InventoryItem.query.filter_by(tracking_id=tracking_id).first():
            return tracking_id