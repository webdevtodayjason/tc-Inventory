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

def log_activity(user_id, action, message, details=None):
    """
    Log database activity with user information in a human-readable format.
    """
    try:
        # Get user info
        user = User.query.get(user_id)
        username = user.username if user else 'Unknown'
        
        # Format the log message based on action type
        if action == 'mobile_checkout':
            # For mobile checkouts, use the provided message directly
            log_message = message
            if details:
                # Add any additional details to the log
                detail_str = ' '.join(f"{k}={v}" for k, v in details.items() if v is not None)
                if detail_str:
                    log_message += f" ({detail_str})"
        else:
            # For other actions, use the standard format
            action_phrase = action.replace('_', ' ').title()
            log_message = f"User {username} {action_phrase} {message}"
            if details:
                detail_str = ' '.join(f"{k}={v}" for k, v in details.items() if v is not None)
                if detail_str:
                    log_message += f" ({detail_str})"
        
        # Log the activity
        current_app.logger.info(log_message)
        
    except Exception as e:
        current_app.logger.error(f"Error logging activity: {str(e)}")

def log_inventory_activity(action, item, details=None):
    """Convenience function for logging inventory item activities"""
    log_activity(item.id, action, item.name, details)

def log_system_activity(action, system, details=None):
    """Convenience function for logging computer system activities"""
    log_activity(system.id, action, system.name, details)

def log_user_activity(action, user, details=None):
    """Convenience function for logging user-related activities"""
    log_activity(user.id, action, user.username, details) 