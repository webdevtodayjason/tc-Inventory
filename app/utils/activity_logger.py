from flask import current_app
from flask_login import current_user
from datetime import datetime
import json
import logging
import os

# Configure activity logger
activity_logger = logging.getLogger('activity_logger')
activity_logger.setLevel(logging.INFO)

# Create logs directory if it doesn't exist
if not os.path.exists('logs'):
    os.makedirs('logs')

# Create file handler
file_handler = logging.FileHandler('logs/activity.log')
file_handler.setLevel(logging.INFO)

# Create formatter with just timestamp - we'll add tags in the message
formatter = logging.Formatter('%(asctime)s - %(message)s', datefmt='%Y-%m-%d %I:%M:%S %p')
file_handler.setFormatter(formatter)

# Add handler to logger
activity_logger.addHandler(file_handler)

# Action tags mapping
ACTION_TAGS = {
    'adjustment': '[QTY]',
    'add_system': '[SYSTEM-ADD]',
    'delete_system': '[SYSTEM-DEL]',
    'update_system': '[SYSTEM-UPD]',
    'add_item': '[ITEM-ADD]',
    'delete_item': '[ITEM-DEL]',
    'update_item': '[ITEM-UPD]',
    'add_cpu': '[CPU-ADD]',
    'delete_cpu': '[CPU-DEL]',
    'update_cpu': '[CPU-UPD]',
    'add_model': '[MOD-ADD]',
    'delete_model': '[MOD-DEL]',
    'update_model': '[MOD-UPD]'
}

def get_action_tag(action):
    """Get the appropriate tag for an action"""
    return ACTION_TAGS.get(action, '[INFO]')

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
    """Log activity with user information in a human-readable format."""
    try:
        # Get user info
        username = current_user.username if current_user else 'Unknown'
        
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
        activity_logger.info(log_message)
        
    except Exception as e:
        current_app.logger.error(f"Error logging activity: {str(e)}")

def log_inventory_activity(action, item, details=None):
    """Convenience function for logging inventory item activities"""
    try:
        username = current_user.username if current_user else 'Unknown'
        tag = get_action_tag(action)
        
        # Handle different item types
        if hasattr(item, 'tracking_id'):
            # For items and systems that have tracking_id
            identifier = details.get('tracking_id', item.tracking_id)
            item_name = item.name
        elif item.__class__.__name__ == 'CPU':
            # For CPUs, use manufacturer and model as identifier
            identifier = f"{item.manufacturer} {item.model}"
            item_name = identifier
        elif item.__class__.__name__ == 'ComputerModel':
            # For computer models, use manufacturer and model name
            identifier = f"{item.manufacturer} {item.model_name}"
            item_name = identifier
        else:
            identifier = str(item.id)
            item_name = str(item)
        
        if action == 'adjustment':
            old_qty = details.get('old_quantity', 0)
            new_qty = details.get('new_quantity', 0)
            qty_change = new_qty - old_qty
            sign = '+' if qty_change > 0 else ''
            message = f"{tag} - User {username} adjusted quantity of {item_name} ({identifier}) from {old_qty} to {new_qty} ({sign}{qty_change})"
        else:
            message = f"{tag} - User {username} {action} {item_name} ({identifier})"
            if details and 'changes' in details:
                detail_str = json.dumps(details['changes'])
                message += f" (changes={detail_str})"
        
        activity_logger.info(message)
        
    except Exception as e:
        current_app.logger.error(f"Error logging activity: {str(e)}")

def log_system_activity(action, system, details=None):
    """Log activity for computer systems"""
    try:
        username = current_user.username if current_user else 'Unknown'
        tag = get_action_tag(action)
        
        # Get system identifier (tracking ID or model info)
        system_identifier = system.tracking_id
        if hasattr(system, 'model'):
            model_info = f"{system.model.manufacturer} {system.model.model_name}"
            if system.serial_tag:
                system_identifier = f"{model_info} ({system.serial_tag})"
            else:
                system_identifier = f"{model_info} ({system.tracking_id})"

        # Format the log message
        action_phrase = action.replace('_', ' ').title()
        message = f"{tag} - User {username} {action_phrase} System {system_identifier}"
        
        if details:
            detail_str = json.dumps(details)
            message += f" - Details: {detail_str}"

        activity_logger.info(message)
        
    except Exception as e:
        current_app.logger.error(f"Error logging system activity: {str(e)}")

def log_user_activity(action, user, details=None):
    """Convenience function for logging user-related activities"""
    try:
        username = current_user.username if current_user else 'Unknown'
        tag = get_action_tag(action)
        message = f"{tag} - User {username} {action} {user.username}"
        if details:
            detail_str = ' '.join(f"{k}={v}" for k, v in details.items() if v is not None)
            if detail_str:
                message += f" ({detail_str})"
        activity_logger.info(message)
    except Exception as e:
        current_app.logger.error(f"Error logging user activity: {str(e)}") 