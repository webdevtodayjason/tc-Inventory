from flask import current_app
from app.models.config import Configuration
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

def send_stock_alert(items):
    """
    Send a low stock alert email for the given items.
    
    Args:
        items: List of InventoryItem objects that are low in stock
    """
    if not items:
        return
    
    # Get email settings
    smtp_server = Configuration.get_setting('smtp_server')
    smtp_port = int(Configuration.get_setting('smtp_port', '587'))
    smtp_username = Configuration.get_setting('smtp_username')
    smtp_password = Configuration.get_setting('smtp_password')
    
    # Get alert email address (use stock alert email if set, otherwise use general notification email)
    to_email = (Configuration.get_setting('stock_alert_email') or 
               Configuration.get_setting('notification_email'))
    
    if not all([smtp_server, smtp_port, smtp_username, smtp_password, to_email]):
        current_app.logger.error('Email settings not properly configured')
        return
    
    # Create message
    msg = MIMEMultipart('alternative')
    msg['Subject'] = 'Low Stock Alert - Action Required'
    msg['From'] = smtp_username
    msg['To'] = to_email
    
    # Create HTML content
    html_content = """
    <html>
    <head>
        <style>
            table { border-collapse: collapse; width: 100%; }
            th, td { padding: 8px; text-align: left; border: 1px solid #ddd; }
            th { background-color: #f2f2f2; }
            .low { color: #ff6b6b; }
            .critical { color: #dc3545; font-weight: bold; }
        </style>
    </head>
    <body>
        <h2>Low Stock Alert</h2>
        <p>The following items need attention:</p>
        <table>
            <tr>
                <th>Item Name</th>
                <th>Current Stock</th>
                <th>Reorder Point</th>
                <th>Status</th>
            </tr>
    """
    
    for item in items:
        status_class = 'critical' if item.quantity == 0 else 'low'
        status_text = 'Out of Stock' if item.quantity == 0 else 'Low Stock'
        
        html_content += f"""
            <tr>
                <td>{item.name}</td>
                <td class="{status_class}">{item.quantity}</td>
                <td>{item.reorder_threshold}</td>
                <td class="{status_class}">{status_text}</td>
            </tr>
        """
    
    html_content += """
        </table>
        <p>Please review and reorder these items as needed.</p>
    </body>
    </html>
    """
    
    msg.attach(MIMEText(html_content, 'html'))
    
    try:
        # Send email
        with smtplib.SMTP(smtp_server, smtp_port) as server:
            server.starttls()
            server.login(smtp_username, smtp_password)
            server.send_message(msg)
            
        current_app.logger.info(f'Stock alert email sent to {to_email}')
        return True
        
    except Exception as e:
        current_app.logger.error(f'Failed to send stock alert email: {str(e)}')
        return False 