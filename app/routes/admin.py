from flask import Blueprint, render_template, request, flash, redirect, url_for, jsonify, send_file, make_response, current_app
from flask_login import login_required, current_user
from app.models.config import Configuration
from app.models.inventory import Tag
from app.routes.inventory import admin_required
from app import db
from app.models.user import User
import subprocess
from datetime import datetime
import os
from urllib.parse import urlparse
import csv
import io
from sqlalchemy import create_engine

bp = Blueprint('admin', __name__)

@bp.route('/admin/users')
@login_required
@admin_required
def manage_users():
    users = User.query.order_by(User.username).all()
    return render_template('admin/users/list.html', users=users)

@bp.route('/admin/users/add', methods=['GET', 'POST'])
@login_required
@admin_required
def add_user():
    if request.method == 'POST':
        username = request.form.get('username')
        email = request.form.get('email')
        password = request.form.get('password')
        pin = request.form.get('pin')
        role = request.form.get('role', 'user')

        if not all([username, email, password, pin]):
            flash('All fields are required', 'error')
            return redirect(url_for('admin.add_user'))

        if User.query.filter_by(username=username).first():
            flash('Username already exists', 'error')
            return redirect(url_for('admin.add_user'))

        if User.query.filter_by(email=email).first():
            flash('Email already registered', 'error')
            return redirect(url_for('admin.add_user'))

        try:
            user = User(username=username, email=email)
            user.set_password(password)
            user.set_pin(pin)
            user.role = role
            db.session.add(user)
            db.session.commit()
            flash('User created successfully', 'success')
            return redirect(url_for('admin.manage_users'))
        except Exception as e:
            db.session.rollback()
            flash(f'Error creating user: {str(e)}', 'error')
            return redirect(url_for('admin.add_user'))

    return render_template('admin/users/add.html')

@bp.route('/admin/users/<int:id>/edit', methods=['GET', 'POST'])
@login_required
@admin_required
def edit_user(id):
    user = User.query.get_or_404(id)
    
    if request.method == 'POST':
        username = request.form.get('username')
        email = request.form.get('email')
        password = request.form.get('password')
        pin = request.form.get('pin')
        role = request.form.get('role')

        if not all([username, email, role]):
            flash('Username, email and role are required', 'error')
            return redirect(url_for('admin.edit_user', id=id))

        try:
            # Check if username is taken by another user
            existing_user = User.query.filter_by(username=username).first()
            if existing_user and existing_user.id != id:
                flash('Username already exists', 'error')
                return redirect(url_for('admin.edit_user', id=id))

            # Check if email is taken by another user
            existing_user = User.query.filter_by(email=email).first()
            if existing_user and existing_user.id != id:
                flash('Email already registered', 'error')
                return redirect(url_for('admin.edit_user', id=id))

            user.username = username
            user.email = email
            user.role = role

            if password:
                user.set_password(password)
            if pin:
                user.set_pin(pin)

            db.session.commit()
            flash('User updated successfully', 'success')
            return redirect(url_for('admin.manage_users'))
        except Exception as e:
            db.session.rollback()
            flash(f'Error updating user: {str(e)}', 'error')
            return redirect(url_for('admin.edit_user', id=id))

    return render_template('admin/users/edit.html', user=user)

@bp.route('/admin/users/<int:id>/delete', methods=['POST'])
@login_required
@admin_required
def delete_user(id):
    if current_user.id == id:
        flash('You cannot delete your own account', 'error')
        return redirect(url_for('admin.manage_users'))

    user = User.query.get_or_404(id)
    try:
        db.session.delete(user)
        db.session.commit()
        flash('User deleted successfully', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'Error deleting user: {str(e)}', 'error')

    return redirect(url_for('admin.manage_users'))

@bp.route('/admin/tags')
@login_required
@admin_required
def manage_tags():
    tags = Tag.query.order_by(Tag.name).all()
    return render_template('admin/tags.html', tags=tags)

@bp.route('/admin/tags/add', methods=['POST'])
@login_required
@admin_required
def add_tag():
    name = request.form.get('name')
    if not name:
        flash('Tag name is required', 'error')
        return redirect(url_for('admin.manage_tags'))
    
    # Check if tag already exists
    if Tag.query.filter_by(name=name).first():
        flash('Tag already exists', 'error')
        return redirect(url_for('admin.manage_tags'))
    
    try:
        tag = Tag(name=name)
        db.session.add(tag)
        db.session.commit()
        flash('Tag added successfully', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'Error adding tag: {str(e)}', 'error')
    
    return redirect(url_for('admin.manage_tags'))

@bp.route('/admin/tags/<int:id>/edit', methods=['POST'])
@login_required
@admin_required
def edit_tag(id):
    tag = Tag.query.get_or_404(id)
    name = request.form.get('name')
    
    if not name:
        flash('Tag name is required', 'error')
        return redirect(url_for('admin.manage_tags'))
    
    # Check if new name already exists for a different tag
    existing_tag = Tag.query.filter_by(name=name).first()
    if existing_tag and existing_tag.id != id:
        flash('Tag name already exists', 'error')
        return redirect(url_for('admin.manage_tags'))
    
    try:
        tag.name = name
        db.session.commit()
        flash('Tag updated successfully', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'Error updating tag: {str(e)}', 'error')
    
    return redirect(url_for('admin.manage_tags'))

@bp.route('/admin/tags/<int:id>/delete', methods=['POST'])
@login_required
@admin_required
def delete_tag(id):
    tag = Tag.query.get_or_404(id)
    
    try:
        db.session.delete(tag)
        db.session.commit()
        flash('Tag deleted successfully', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'Error deleting tag: {str(e)}', 'error')
    
    return redirect(url_for('admin.manage_tags'))

@bp.route('/admin/config', methods=['GET', 'POST'])
@login_required
@admin_required
def manage_config():
    if request.method == 'POST':
        try:
            # User Management Settings
            Configuration.set_setting(
                'allow_public_registration',
                request.form.get('allow_registration', 'false'),
                'Allow public user registration'
            )
            Configuration.set_setting(
                'require_email_verification',
                request.form.get('require_email_verification', 'false'),
                'Require email verification for new users'
            )
            Configuration.set_setting(
                'allow_password_reset',
                request.form.get('allow_password_reset', 'false'),
                'Allow users to reset passwords via email'
            )

            # Inventory Settings
            Configuration.set_setting(
                'items_per_page',
                request.form.get('items_per_page', '20'),
                'Number of items to display per page'
            )
            Configuration.set_setting(
                'enable_barcode_scanner',
                request.form.get('enable_barcode_scanner', 'false'),
                'Enable barcode scanning functionality'
            )
            Configuration.set_setting(
                'enable_low_stock_alerts',
                request.form.get('enable_low_stock_alerts', 'false'),
                'Enable low stock alerts'
            )
            Configuration.set_setting(
                'stock_alert_email',
                request.form.get('stock_alert_email', ''),
                'Email address for low stock alerts'
            )

            # Email Settings
            Configuration.set_setting(
                'smtp_server',
                request.form.get('smtp_server', ''),
                'SMTP server address'
            )
            Configuration.set_setting(
                'smtp_port',
                request.form.get('smtp_port', '587'),
                'SMTP server port'
            )
            Configuration.set_setting(
                'smtp_username',
                request.form.get('smtp_username', ''),
                'SMTP username'
            )
            Configuration.set_setting(
                'smtp_password',
                request.form.get('smtp_password', ''),
                'SMTP password'
            )
            Configuration.set_setting(
                'notification_email',
                request.form.get('notification_email', ''),
                'Email address for system notifications'
            )

            # Return JSON response for AJAX request
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return jsonify({'success': True})
            
            flash('Configuration updated successfully', 'success')
            return redirect(url_for('admin.manage_config'))
            
        except Exception as e:
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return jsonify({'success': False, 'error': str(e)})
            flash(f'Error updating configuration: {str(e)}', 'error')
            return redirect(url_for('admin.manage_config'))

    # Get current settings
    settings = {
        'allow_registration': Configuration.get_setting('allow_public_registration', 'true'),
        'require_email_verification': Configuration.get_setting('require_email_verification', 'false'),
        'allow_password_reset': Configuration.get_setting('allow_password_reset', 'true'),
        'items_per_page': Configuration.get_setting('items_per_page', '20'),
        'enable_barcode_scanner': Configuration.get_setting('enable_barcode_scanner', 'true'),
        'enable_low_stock_alerts': Configuration.get_setting('enable_low_stock_alerts', 'true'),
        'stock_alert_email': Configuration.get_setting('stock_alert_email', ''),
        'smtp_server': Configuration.get_setting('smtp_server', ''),
        'smtp_port': Configuration.get_setting('smtp_port', '587'),
        'smtp_username': Configuration.get_setting('smtp_username', ''),
        'smtp_password': Configuration.get_setting('smtp_password', ''),
        'notification_email': Configuration.get_setting('notification_email', '')
    }

    return render_template('admin/config.html', **settings)

@bp.route('/admin/logs')
@login_required
@admin_required
def view_logs():
    # Get the last 100 log entries
    try:
        with open('app.log', 'r') as f:
            logs = f.readlines()[-100:]
        return render_template('admin/logs.html', logs=logs)
    except FileNotFoundError:
        flash('Log file not found', 'error')
        return render_template('admin/logs.html', logs=[])

@bp.route('/admin/backup', methods=['GET', 'POST'])
@login_required
@admin_required
def backup():
    if request.method == 'POST':
        try:
            # Create pg_dump command
            db_url = current_app.config['DATABASE_URL']
            parsed = urlparse(db_url)
            
            # Extract database connection info
            dbname = parsed.path[1:]  # Remove leading slash
            user = parsed.username
            password = parsed.password
            host = parsed.hostname
            port = parsed.port or 5432
            
            # Set environment variables for pg_dump
            env = os.environ.copy()
            env['PGPASSWORD'] = password
            
            # Generate timestamp for filename
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            filename = f'tc_inventory_backup_{timestamp}.sql'
            
            # Create pg_dump command
            command = [
                'pg_dump',
                '-h', host,
                '-p', str(port),
                '-U', user,
                '-F', 'p',  # Plain text format
                '-f', filename,
                dbname
            ]
            
            current_app.logger.info(f"Executing backup command: {' '.join(command)}")
            
            # Execute pg_dump
            result = subprocess.run(command, env=env, capture_output=True, text=True)
            
            if result.returncode == 0:
                current_app.logger.info("Backup file created successfully")
                # Read the backup file
                with open(filename, 'rb') as f:
                    backup_data = f.read()
                
                # Delete the temporary file
                os.remove(filename)
                current_app.logger.info("Temporary backup file deleted")
                
                # Create response with file download
                response = make_response(backup_data)
                response.headers['Content-Type'] = 'application/sql'
                response.headers['Content-Disposition'] = f'attachment; filename={filename}'
                
                flash('Backup created successfully!', 'success')
                return response
            else:
                error_msg = f'Backup failed: {result.stderr}'
                current_app.logger.error(error_msg)
                flash(error_msg, 'danger')
                
        except Exception as e:
            error_msg = f'Error creating backup: {str(e)}'
            current_app.logger.error(error_msg)
            flash(error_msg, 'danger')
    
    # Get backup settings from configuration
    backup_settings = {
        'auto_backup_enabled': Configuration.get_setting('auto_backup_enabled', 'false'),
        'backup_frequency': Configuration.get_setting('backup_frequency', 'daily'),
        'backup_retention_days': Configuration.get_setting('backup_retention_days', '30'),
        'backup_time': Configuration.get_setting('backup_time', '00:00'),
    }
    
    return render_template('admin/backup.html', settings=backup_settings)

@bp.route('/admin/backup/settings', methods=['POST'])
@login_required
@admin_required
def save_backup_settings():
    try:
        # Update configuration settings
        Configuration.query.filter_by(key='auto_backup_enabled').delete()
        Configuration.query.filter_by(key='backup_frequency').delete()
        Configuration.query.filter_by(key='backup_retention_days').delete()
        Configuration.query.filter_by(key='backup_time').delete()
        
        db.session.add(Configuration(
            key='auto_backup_enabled',
            value=request.form.get('auto_backup_enabled', 'false'),
            description='Enable automatic database backups'
        ))
        
        db.session.add(Configuration(
            key='backup_frequency',
            value=request.form.get('backup_frequency', 'daily'),
            description='Frequency of automatic backups'
        ))
        
        db.session.add(Configuration(
            key='backup_retention_days',
            value=request.form.get('backup_retention_days', '30'),
            description='Number of days to retain backups'
        ))
        
        db.session.add(Configuration(
            key='backup_time',
            value=request.form.get('backup_time', '00:00'),
            description='Time to run automatic backups'
        ))
        
        db.session.commit()
        flash('Backup settings updated successfully!', 'success')
        
    except Exception as e:
        db.session.rollback()
        flash(f'Error saving backup settings: {str(e)}', 'danger')
        current_app.logger.error(f'Backup settings error: {str(e)}')
    
    return redirect(url_for('admin.backup'))

@bp.route('/admin/export-table', methods=['POST'])
@login_required
@admin_required
def export_table():
    try:
        table_name = request.form.get('table_name')
        if not table_name:
            flash('Please select a table to export', 'danger')
            return redirect(url_for('admin.backup'))
        
        # Create database connection
        db_url = current_app.config['DATABASE_URL']
        engine = create_engine(db_url)
        
        # Define table mappings
        table_mappings = {
            'items': InventoryItem,
            'computer_systems': ComputerSystem,
            'categories': Category,
            'tags': Tag,
            'computer_models': ComputerModel,
            'cpus': CPU,
            'users': User,
            'inventory_transactions': InventoryTransaction
        }
        
        if table_name not in table_mappings:
            flash('Invalid table selected', 'danger')
            return redirect(url_for('admin.backup'))
        
        # Get model class
        model = table_mappings[table_name]
        
        # Query data
        data = model.query.all()
        
        if not data:
            flash('No data found in selected table', 'warning')
            return redirect(url_for('admin.backup'))
        
        # Create CSV in memory
        output = io.StringIO()
        writer = csv.writer(output)
        
        # Write headers
        headers = [column.name for column in model.__table__.columns]
        writer.writerow(headers)
        
        # Write data
        for row in data:
            csv_row = []
            for header in headers:
                value = getattr(row, header)
                # Handle relationships and complex types
                if hasattr(value, 'name'):  # For foreign key relations that have a name
                    value = value.name
                elif isinstance(value, datetime):  # Format datetime
                    value = value.strftime('%Y-%m-%d %H:%M:%S')
                csv_row.append(str(value) if value is not None else '')
            writer.writerow(csv_row)
        
        # Create the response
        output.seek(0)
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        response = make_response(output.getvalue())
        response.headers['Content-Type'] = 'text/csv'
        response.headers['Content-Disposition'] = f'attachment; filename={table_name}_{timestamp}.csv'
        
        return response
        
    except Exception as e:
        error_msg = f'Error exporting table: {str(e)}'
        current_app.logger.error(error_msg)
        flash(error_msg, 'danger')
        return redirect(url_for('admin.backup'))