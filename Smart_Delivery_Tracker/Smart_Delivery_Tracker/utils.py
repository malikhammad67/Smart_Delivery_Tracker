import re
import random
import string
from datetime import datetime

def generate_order_id(prefix="DLV"):
    """Generate a unique order ID"""
    timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
    random_suffix = ''.join(random.choices(string.digits, k=4))
    return f"{prefix}-{timestamp[-6:]}{random_suffix}"

def validate_order_id(order_id):
    """Validate order ID format"""
    pattern = r'^[A-Za-z0-9\-_]{3,20}$'
    return bool(re.match(pattern, order_id))

def validate_phone(phone):
    """Validate phone number"""
    if not phone:
        return True
    phone_clean = re.sub(r'\D', '', phone)
    return len(phone_clean) >= 10

def format_phone(phone):
    """Format phone number for display"""
    if not phone:
        return "-"
    digits = re.sub(r'\D', '', phone)
    if len(digits) == 11:
        return f"{digits[:4]}-{digits[4:7]}-{digits[7:]}"
    elif len(digits) == 10:
        return f"{digits[:3]}-{digits[3:6]}-{digits[6:]}"
    else:
        return phone

def validate_time(time_str):
    """Validate time in HH:MM format"""
    try:
        hour, minute = map(int, time_str.split(':'))
        return 0 <= hour <= 23 and 0 <= minute <= 59
    except:
        return False

def get_current_time_str():
    """Get current time as HH:MM string"""
    return datetime.now().strftime("%H:%M")

def get_current_date_str():
    """Get current date as YYYY-MM-DD string"""
    return datetime.now().strftime("%Y-%m-%d")

def format_duration(minutes):
    """Format minutes to human readable duration"""
    if minutes == 0:
        return "0 minutes"
    elif minutes < 60:
        return f"{minutes} minute{'s' if minutes > 1 else ''}"
    else:
        hours = minutes // 60
        mins = minutes % 60
        if mins == 0:
            return f"{hours} hour{'s' if hours > 1 else ''}"
        else:
            return f"{hours}h {mins}m"

def truncate_text(text, max_length=50):
    """Truncate text to max length"""
    if len(text) <= max_length:
        return text
    return text[:max_length] + "..."

def safe_divide(numerator, denominator):
    """Safe division returning 0 if denominator is 0"""
    try:
        return numerator / denominator if denominator != 0 else 0
    except:
        return 0

def get_status_icon(status):
    """Get icon for status"""
    icons = {
        "ON TIME": "✅",
        "LATE": "⏰",
        "PENDING": "⏳",
        "OVERDUE": "⚠️",
        "INVALID": "❌"
    }
    return icons.get(status, "❓")

def get_status_color_hex(status):
    """Get hex color for status"""
    colors = {
        "ON TIME": "#10b981",
        "LATE": "#ef4444",
        "PENDING": "#f59e0b",
        "OVERDUE": "#dc2626",
        "INVALID": "#6b7280"
    }
    return colors.get(status, "#6b7280")

if __name__ == "__main__":
    print("Utils module ready!")
    print(f"Generated Order ID: {generate_order_id()}")
    print(f"Formatted phone: {format_phone('03001234567')}")