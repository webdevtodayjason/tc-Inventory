from flask import Blueprint, render_template, request, flash, redirect, url_for, jsonify
from flask_login import login_required
from app.models.config import Configuration
from app.models.inventory import Tag
from app.routes.inventory import admin_required
from app import db

bp = Blueprint('admin', __name__)

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