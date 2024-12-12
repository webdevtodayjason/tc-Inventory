from flask import current_app
from flask_login import current_user
from datetime import datetime

def log_activity(action, item_type, item_id, details=None):
    """
    Log database activity with user information.
    
    Args:
        action (str): The action performed (e.g., 'add', 'update', 'delete', 'checkout')
        item_type (str): Type of item affected (e.g., 'inventory_item', 'computer_system')
        item_id: Identifier of the affected item
        details (dict, optional): Additional details about the action
    """
    try:
        # Get user info
        user_id = current_user.id if not current_user.is_anonymous else None
        username = current_user.username if not current_user.is_anonymous else 'Anonymous'
        
        # Format the log message
        timestamp = datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S UTC')
        message = f"[DATABASE] {timestamp} - User {username} (ID: {user_id}) performed {action} on {item_type} (ID: {item_id})"
        
        # Add details if provided
        if details:
            message += f" - Details: {details}"
        
        # Log the activity
        current_app.logger.info(message)
        
    except Exception as e:
        current_app.logger.error(f"Error logging activity: {str(e)}")

def log_inventory_activity(action, item, details=None):
    """Convenience function for logging inventory item activities"""
    log_activity(action, 'inventory_item', item.id, details)

def log_system_activity(action, system, details=None):
    """Convenience function for logging computer system activities"""
    log_activity(action, 'computer_system', system.id, details)

def log_user_activity(action, user, details=None):
    """Convenience function for logging user-related activities"""
    log_activity(action, 'user', user.id, details) 