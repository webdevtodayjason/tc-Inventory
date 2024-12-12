from flask import current_app
from flask_login import current_user
from datetime import datetime

def format_details(details):
    """Format details dictionary into a readable string"""
    if not details:
        return ""
    
    formatted = []
    for key, value in details.items():
        if key == 'name':
            formatted.append(f"'{value}'")
        elif key == 'category':
            formatted.append(f"in {value}" if value else "")
        elif key == 'quantity':
            formatted.append(f"(qty: {value})")
        elif key == 'location':
            formatted.append(f"at {value}" if value else "")
        elif key == 'remaining':
            formatted.append(f"({value} remaining)")
    
    return " ".join(s for s in formatted if s)

def log_activity(action, item_type, item_id, details=None):
    """
    Log database activity with user information in a human-readable format.
    """
    try:
        # Get user info
        username = current_user.username if not current_user.is_anonymous else 'Anonymous'
        
        # Make item type more readable
        item_type = item_type.replace('_', ' ').title()
        
        # Format the details
        details_str = format_details(details)
        
        # Create readable action phrase
        if action == 'add':
            action_phrase = 'added new'
        elif action == 'update':
            action_phrase = 'updated'
        elif action == 'delete':
            action_phrase = 'deleted'
        elif action == 'checkout':
            action_phrase = 'checked out'
        else:
            action_phrase = action
        
        # Format the log message
        message = f"User {username} {action_phrase} {item_type} {details_str}"
        
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