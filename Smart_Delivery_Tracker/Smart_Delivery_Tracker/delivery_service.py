from datetime import datetime
import re

def calculate_delivery_status(expected_time, actual_time=None, current_time=None):
    """
    Calculate delivery status and delay minutes (FR-04, FR-05)
    
    Returns:
    - status: "ON TIME", "LATE", "PENDING", "OVERDUE"
    - delay_minutes: integer
    - delay_display: string like "1 hour 15 minutes" (FR-05)
    """
    if current_time is None:
        current_time = datetime.now()
    
    # Parse expected time
    try:
        expected_hour, expected_minute = map(int, expected_time.split(':'))
        expected_dt = current_time.replace(
            hour=expected_hour, 
            minute=expected_minute, 
            second=0, 
            microsecond=0
        )
    except (ValueError, AttributeError):
        return "INVALID", 0, "Invalid time format"
    
    # If actual time is provided (delivery completed)
    if actual_time:
        try:
            actual_hour, actual_minute = map(int, actual_time.split(':'))
            actual_dt = current_time.replace(
                hour=actual_hour, 
                minute=actual_minute, 
                second=0, 
                microsecond=0
            )
            
            # Calculate delay in minutes
            delay_minutes = int((actual_dt - expected_dt).total_seconds() / 60)
            
            if delay_minutes <= 0:
                return "ON TIME", 0, "On time"
            else:
                # Format delay for display (FR-05)
                delay_display = format_delay_display(delay_minutes)
                return "LATE", delay_minutes, delay_display
                
        except (ValueError, AttributeError):
            return "INVALID", 0, "Invalid time format"
    
    # Pending delivery (no actual time)
    else:
        if current_time < expected_dt:
            return "PENDING", 0, "Waiting for delivery"
        else:
            return "OVERDUE", 0, "Overdue - needs attention"

def format_delay_display(delay_minutes):
    """Format delay minutes to readable duration (FR-05)"""
    if delay_minutes == 0:
        return "On time"
    elif delay_minutes < 60:
        return f"{delay_minutes} minute{'s' if delay_minutes > 1 else ''}"
    else:
        hours = delay_minutes // 60
        minutes = delay_minutes % 60
        if minutes == 0:
            return f"{hours} hour{'s' if hours > 1 else ''}"
        else:
            return f"{hours} hour{'s' if hours > 1 else ''} {minutes} minute{'s' if minutes > 1 else ''}"

def get_status_color(status):
    """Return color for status display"""
    colors = {
        "ON TIME": "#10b981",
        "LATE": "#ef4444",
        "PENDING": "#f59e0b",
        "OVERDUE": "#dc2626",
        "INVALID": "#6b7280"
    }
    return colors.get(status, "#6b7280")

def get_status_emoji(status):
    """Return emoji for status"""
    emojis = {
        "ON TIME": "✅",
        "LATE": "⏰",
        "PENDING": "⏳",
        "OVERDUE": "⚠️",
        "INVALID": "❌"
    }
    return emojis.get(status, "❓")

def validate_delivery_input(order_id, customer_name, delivery_area, driver_name, 
                            expected_time, phone=None):
    """Validate delivery input (FR-16)"""
    errors = []
    
    # FR-02: Order ID validation
    if not order_id or not order_id.strip():
        errors.append("Order ID is required")
    elif not re.match(r'^[A-Za-z0-9\-_]{3,20}$', order_id):
        errors.append("Order ID must be 3-20 characters (letters, numbers, hyphens, underscores)")
    
    # Customer name validation
    if not customer_name or not customer_name.strip():
        errors.append("Customer Name is required")
    elif len(customer_name.strip()) < 2:
        errors.append("Customer Name must be at least 2 characters")
    
    # Delivery area validation
    if not delivery_area or not delivery_area.strip():
        errors.append("Delivery Area is required")
    
    # Driver name validation
    if not driver_name or not driver_name.strip():
        errors.append("Driver Name is required")
    
    # Expected time validation
    if not expected_time:
        errors.append("Expected Delivery Time is required")
    else:
        try:
            hour, minute = map(int, expected_time.split(':'))
            if not (0 <= hour <= 23 and 0 <= minute <= 59):
                errors.append("Invalid time format. Use HH:MM (24-hour format)")
        except:
            errors.append("Invalid time format. Use HH:MM (24-hour format)")
    
    # Phone validation (optional)
    if phone and phone.strip():
        phone_clean = re.sub(r'\D', '', phone)
        if len(phone_clean) < 10:
            errors.append("Phone number must be at least 10 digits")
    
    return errors

def get_status_badge_html(status):
    """Get HTML status badge"""
    badges = {
        "ON TIME": '<span style="background:#10b981;color:white;padding:4px 12px;border-radius:20px;font-weight:600;font-size:0.85rem;">✅ On Time</span>',
        "LATE": '<span style="background:#ef4444;color:white;padding:4px 12px;border-radius:20px;font-weight:600;font-size:0.85rem;">⏰ Late</span>',
        "PENDING": '<span style="background:#f59e0b;color:white;padding:4px 12px;border-radius:20px;font-weight:600;font-size:0.85rem;">⏳ Pending</span>',
        "OVERDUE": '<span style="background:#dc2626;color:white;padding:4px 12px;border-radius:20px;font-weight:600;font-size:0.85rem;">⚠️ Overdue</span>'
    }
    return badges.get(status, '<span style="background:#6b7280;color:white;padding:4px 12px;border-radius:20px;font-weight:600;font-size:0.85rem;">⏳ Pending</span>')

def generate_order_id():
    """Generate unique order ID"""
    from datetime import datetime
    import random
    timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
    random_suffix = ''.join(random.choices('ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789', k=4))
    return f"DLV-{timestamp[-6:]}{random_suffix}"

if __name__ == "__main__":
    print("Testing delivery_service.py")
    
    # Test FR-04: Status calculation
    status, delay, display = calculate_delivery_status("14:00", "13:45")
    print(f"On-time: {status}, {display}")
    
    status, delay, display = calculate_delivery_status("14:00", "15:15")
    print(f"Late: {status}, {delay} min, {display}")
    
    status, delay, display = calculate_delivery_status("16:00", None)
    print(f"Pending: {status}")
    
    # Test FR-16: Validation
    errors = validate_delivery_input("", "", "", "", "")
    print(f"Validation errors: {errors}")