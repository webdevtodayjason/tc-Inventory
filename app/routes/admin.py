from flask import (
    Blueprint, render_template, request, flash, redirect, 
    url_for, jsonify, send_file, make_response, current_app
)
from flask_login import login_required, current_user
from app.models.config import Configuration
from app.models.inventory import (
    InventoryItem, ComputerSystem, Category, 
    ComputerModel, CPU, Transaction
)
from app.routes.inventory import admin_required
from app import db
from app.models.user import User
import subprocess
from datetime import datetime, timedelta
import os
from urllib.parse import urlparse
import csv
import io
from sqlalchemy import create_engine
import uuid
from app.utils.logs import get_recent_logs

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

@bp.route('/admin/config', methods=['GET', 'POST'])
@login_required
@admin_required
def manage_config():
    if request.method == 'POST':
        try:
            # Debug: Log form data
            current_app.logger.debug(f"Form data: {request.form}")

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

            db.session.commit()

            # Return JSON response for AJAX request
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return jsonify({'success': True, 'message': 'Settings saved successfully'})
            
            flash('Configuration updated successfully', 'success')
            return redirect(url_for('admin.manage_config'))
            
        except Exception as e:
            db.session.rollback()
            current_app.logger.error(f"Error updating configuration: {str(e)}")
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
    try:
        logs = []
        log_start_date = None
        log_end_date = None
        
        # Read from both log files
        log_files = ['logs/app.log', 'logs/activity.log']
        
        for log_file in log_files:
            if os.path.exists(log_file):
                with open(log_file, 'r') as f:
                    file_logs = f.readlines()
                    logs.extend(file_logs)
        
        # Sort all logs by timestamp
        def get_log_timestamp(log):
            try:
                date_str = log.split('[')[0].strip()
                return datetime.strptime(date_str, '%Y-%m-%d %I:%M:%S %p')
            except:
                return datetime.min
        
        logs.sort(key=get_log_timestamp, reverse=True)
        
        # Get last 100 lines
        logs = logs[:100]
        
        # Get log date range
        if logs:
            # Parse dates from log entries
            for log in logs:
                try:
                    date_str = log.split('[')[0].strip()
                    date = datetime.strptime(date_str, '%Y-%m-%d %I:%M:%S %p')
                    if log_start_date is None or date < log_start_date:
                        log_start_date = date
                    if log_end_date is None or date > log_end_date:
                        log_end_date = date
                except:
                    continue
        
        # Format dates for template
        log_start_date = log_start_date.strftime('%Y-%m-%d') if log_start_date else datetime.now().strftime('%Y-%m-%d')
        log_end_date = log_end_date.strftime('%Y-%m-%d') if log_end_date else datetime.now().strftime('%Y-%m-%d')
        
        return render_template('admin/logs.html', logs=logs, log_start_date=log_start_date, log_end_date=log_end_date)
    except Exception as e:
        current_app.logger.error(f"Error viewing logs: {str(e)}")
        return render_template('admin/logs.html', logs=["Error loading logs"])

@bp.route('/admin/logs/download', methods=['POST'])
@login_required
@admin_required
def download_logs():
    try:
        start_date = datetime.strptime(request.form['start_date'], '%Y-%m-%d')
        end_date = datetime.strptime(request.form['end_date'], '%Y-%m-%d')
        # Add one day to end_date to include the entire day
        end_date = end_date + timedelta(days=1)
        
        filtered_logs = []
        log_files = ['logs/app.log', 'logs/activity.log']
        
        for log_file in log_files:
            if os.path.exists(log_file):
                with open(log_file, 'r') as f:
                    for line in f:
                        try:
                            date_str = line.split('[')[0].strip()
                            log_date = datetime.strptime(date_str, '%Y-%m-%d %I:%M:%S %p')
                            if start_date <= log_date <= end_date:
                                filtered_logs.append(line)
                        except:
                            continue
        
        # Sort filtered logs by timestamp
        def get_log_timestamp(log):
            try:
                date_str = log.split('[')[0].strip()
                return datetime.strptime(date_str, '%Y-%m-%d %I:%M:%S %p')
            except:
                return datetime.min
        
        filtered_logs.sort(key=get_log_timestamp, reverse=True)
        
        # Create in-memory file
        mem_file = io.StringIO()
        mem_file.write(''.join(filtered_logs))
        mem_file.seek(0)
        
        # Generate filename with date range
        filename = f"logs_{start_date.strftime('%Y%m%d')}_to_{end_date.strftime('%Y%m%d')}.log"
        
        return send_file(
            io.BytesIO(mem_file.getvalue().encode('utf-8')),
            mimetype='text/plain',
            as_attachment=True,
            download_name=filename
        )
        
    except Exception as e:
        current_app.logger.error(f"Error downloading logs: {str(e)}")
        return "Error downloading logs", 500

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
            'computer_models': ComputerModel,
            'cpus': CPU,
            'users': User,
            'transactions': Transaction
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

@bp.route('/admin/download-template', methods=['POST'])
@login_required
@admin_required
def download_template():
    try:
        table_name = request.form.get('table_name')
        if not table_name:
            flash('Please select a table', 'danger')
            return redirect(url_for('admin.backup'))
        
        # Define template fields for each table
        template_fields = {
            'items': [
                'name', 'category_id', 'quantity', 'reorder_threshold',
                'storage_location', 'barcode', 'manufacturer', 'mpn',
                'image_url', 'description', 'cost', 'sell_price',
                'purchase_url'
            ],
            'computer_systems': [
                'model_id', 'cpu_id', 'ram', 'storage', 'os',
                'storage_location', 'serial_tag', 'cpu_benchmark',
                'usb_ports_status', 'usb_ports_notes', 'video_status',
                'video_notes', 'network_status', 'network_notes',
                'general_notes'
            ],
            'categories': ['name'],
            'computer_models': ['manufacturer', 'model_name', 'model_type'],
            'cpus': ['manufacturer', 'model', 'speed', 'cores']
        }
        
        if table_name not in template_fields:
            flash('Invalid table selected', 'danger')
            return redirect(url_for('admin.backup'))
        
        # Create CSV in memory
        output = io.StringIO()
        writer = csv.writer(output)
        
        # Write headers
        writer.writerow(template_fields[table_name])
        
        # Add example row
        example_data = {
            'items': [
                'Example Item', '1', '10', '5', 'Shelf A1', '123456789',
                'Example Mfr', 'MPN123', '', 'Example description',
                '10.99', '15.99', ''
            ],
            'computer_systems': [
                '1', '1', '16GB', '512GB SSD', 'Windows 10 Pro',
                'Room 101', 'ABC123', '1000', 'PASSED', '',
                'PASSED', '', 'PASSED', '', 'Test notes'
            ],
            'categories': ['Example Category'],
            'computer_models': ['Dell', 'Latitude 5520', 'laptop'],
            'cpus': ['Intel', 'Core i7-11800H', '2.30 GHz', '8']
        }
        writer.writerow(example_data[table_name])
        
        # Create the response
        output.seek(0)
        response = make_response(output.getvalue())
        response.headers['Content-Type'] = 'text/csv'
        response.headers['Content-Disposition'] = f'attachment; filename={table_name}_template.csv'
        
        return response
        
    except Exception as e:
        error_msg = f'Error creating template: {str(e)}'
        current_app.logger.error(error_msg)
        flash(error_msg, 'danger')
        return redirect(url_for('admin.backup'))

@bp.route('/admin/import-table', methods=['POST'])
@login_required
@admin_required
def import_table():
    try:
        table_name = request.form.get('table_name')
        if not table_name:
            flash('Please select a table', 'danger')
            return redirect(url_for('admin.backup'))
        
        if 'csv_file' not in request.files:
            flash('No file uploaded', 'danger')
            return redirect(url_for('admin.backup'))
        
        file = request.files['csv_file']
        if file.filename == '':
            flash('No file selected', 'danger')
            return redirect(url_for('admin.backup'))
        
        if not file.filename.endswith('.csv'):
            flash('Please upload a CSV file', 'danger')
            return redirect(url_for('admin.backup'))
        
        # Define model mappings
        model_mappings = {
            'items': InventoryItem,
            'computer_systems': ComputerSystem,
            'categories': Category,
            'computer_models': ComputerModel,
            'cpus': CPU
        }
        
        if table_name not in model_mappings:
            flash('Invalid table selected', 'danger')
            return redirect(url_for('admin.backup'))
        
        # Get model class
        model = model_mappings[table_name]
        
        # Read CSV file
        stream = io.StringIO(file.stream.read().decode("UTF8"), newline=None)
        csv_reader = csv.DictReader(stream)
        
        # Start transaction
        try:
            # Track statistics
            rows_added = 0
            errors = []
            
            for row in csv_reader:
                try:
                    # Clean up the row data
                    data = {k: v.strip() if isinstance(v, str) else v for k, v in row.items()}
                    
                    # Handle special cases
                    if table_name == 'items':
                        # Generate tracking ID
                        data['tracking_id'] = f"TC-{str(uuid.uuid4())[:8].upper()}"
                        data['created_by'] = current_user.id
                        data['created_at'] = datetime.now()
                        
                        # Convert numeric fields
                        if data.get('cost'):
                            data['cost'] = float(data['cost']) if data['cost'] else None
                        if data.get('sell_price'):
                            data['sell_price'] = float(data['sell_price']) if data['sell_price'] else None
                        if data.get('quantity'):
                            data['quantity'] = int(data['quantity'])
                        if data.get('reorder_threshold'):
                            data['reorder_threshold'] = int(data['reorder_threshold'])
                    
                    # Create new record
                    record = model(**data)
                    db.session.add(record)
                    rows_added += 1
                    
                except Exception as row_error:
                    errors.append(f"Row {rows_added + 1}: {str(row_error)}")
            
            if errors:
                # Rollback if there were any errors
                db.session.rollback()
                error_list = "\n".join(errors)
                flash(f'Import failed with errors:\n{error_list}', 'danger')
            else:
                # Commit if all rows were successful
                db.session.commit()
                flash(f'Successfully imported {rows_added} records', 'success')
            
        except Exception as e:
            db.session.rollback()
            flash(f'Error during import: {str(e)}', 'danger')
        
        return redirect(url_for('admin.backup'))
        
    except Exception as e:
        error_msg = f'Error importing data: {str(e)}'
        current_app.logger.error(error_msg)
        flash(error_msg, 'danger')
        return redirect(url_for('admin.backup'))

@bp.route('/config/read_only_mode', methods=['POST'])
@login_required
@admin_required
def update_read_only_mode():
    """Update read-only mode setting"""
    read_only = request.form.get('read_only_mode', 'false')
    Configuration.set_value(
        'read_only_mode',
        'true' if read_only == 'on' else 'false',
        'When enabled, all create, edit, and delete operations are disabled'
    )
    flash('Read-only mode setting updated successfully', 'success')
    return redirect(url_for('admin.config'))

@bp.route('/logs/clear', methods=['POST'])
@login_required
@admin_required
def clear_logs():
    try:
        # Clear both log files
        log_files = ['logs/app.log', 'logs/activity.log']
        for log_file in log_files:
            if os.path.exists(log_file):
                # Open file in write mode to clear it
                with open(log_file, 'w') as f:
                    f.write('')  # Write empty string to clear file
                
        flash('Logs cleared successfully!', 'success')
    except Exception as e:
        current_app.logger.error(f"Error clearing logs: {str(e)}")
        flash('Error clearing logs', 'danger')
    
    return redirect(url_for('admin.view_logs'))