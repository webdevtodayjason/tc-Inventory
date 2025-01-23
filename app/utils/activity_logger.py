from flask import current_app
from flask_login import current_user
from datetime import datetime
from app.models.user import User

def format_details(details):
    """Format details dictionary into a readable string."""
    if not details:
        return ""
        
    formatted = []
    for key, value in details.items():
        if key != 'changes':  # Skip changes as they'll be handled separately
            formatted.append(f"{value}")
            
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
        if action == 'update' and details and 'changes' in details:
            # Convert the changes list into a single line format
            changes = []
            for change in details['changes']:
                field, values = change.split(':\n', 1)
                old_val = values.split('\n')[0].replace('Old Value: ', '')
                new_val = values.split('\n')[1].replace('New Value: ', '')
                changes.append(f"change - {field} - {old_val} to {new_val}")
            
            changes_str = '; '.join(changes)
            message = f"User {username} {action_phrase} {item_type} '{details.get('name', '')}' {changes_str}"
        else:
            details_str = format_details(details)
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