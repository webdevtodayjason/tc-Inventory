import os
from datetime import datetime, timedelta
from flask import current_app

def get_recent_logs(max_lines=100):
    """
    Get the most recent log entries from the application logs.
    
    Args:
        max_lines (int): Maximum number of log lines to return
        
    Returns:
        list: List of log entries, most recent first
    """
    try:
        # Get log entries from Flask's default logger
        logs = []
        for handler in current_app.logger.handlers:
            if isinstance(handler.formatter, logging.Formatter):
                # Get records from the handler
                if hasattr(handler, 'stream'):
                    # For StreamHandler
                    logs.extend(handler.stream.getvalue().splitlines())
                elif hasattr(handler, 'baseFilename'):
                    # For FileHandler
                    with open(handler.baseFilename, 'r') as f:
                        logs.extend(f.readlines())
        
        # If no logs found in handlers, try reading from app.log
        if not logs:
            log_file = os.path.join(current_app.root_path, 'logs', 'app.log')
            if os.path.exists(log_file):
                with open(log_file, 'r') as f:
                    logs = f.readlines()
        
        # Clean and format logs
        logs = [log.strip() for log in logs if log.strip()]
        
        # Return most recent logs first
        return list(reversed(logs[-max_lines:]))
    except Exception as e:
        current_app.logger.error(f"Error reading logs: {str(e)}")
        return [] 