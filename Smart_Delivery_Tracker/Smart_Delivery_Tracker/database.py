import sqlite3
import pandas as pd
from datetime import datetime
import os

DB_NAME = "delivery_tracker.db"

def get_connection():
    """Create and return database connection"""
    return sqlite3.connect(DB_NAME)

def init_database():
    """Initialize database with required tables (FR-03)"""
    conn = get_connection()
    cursor = conn.cursor()
    
    # Create deliveries table with all required fields (FR-01)
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS deliveries (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            order_id TEXT UNIQUE NOT NULL,
            customer_name TEXT NOT NULL,
            phone TEXT,
            delivery_area TEXT NOT NULL,
            driver_name TEXT NOT NULL,
            order_date TEXT NOT NULL,
            expected_time TEXT NOT NULL,
            actual_time TEXT,
            status TEXT DEFAULT 'PENDING',
            delay_minutes INTEGER DEFAULT 0,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP,
            updated_at TEXT DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # Create indexes for performance
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_order_id ON deliveries(order_id)')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_customer ON deliveries(customer_name)')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_status ON deliveries(status)')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_driver ON deliveries(driver_name)')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_area ON deliveries(delivery_area)')
    
    conn.commit()
    conn.close()
    print("✅ Database initialized successfully!")

def add_delivery_db(order_id, customer_name, phone, delivery_area, driver_name, 
                    order_date, expected_time):
    """Add a new delivery to database (FR-01, FR-02)"""
    conn = get_connection()
    cursor = conn.cursor()
    
    try:
        cursor.execute('''
            INSERT INTO deliveries 
            (order_id, customer_name, phone, delivery_area, driver_name, 
             order_date, expected_time, status)
            VALUES (?, ?, ?, ?, ?, ?, ?, 'PENDING')
        ''', (order_id, customer_name, phone, delivery_area, driver_name, 
              order_date, expected_time))
        
        conn.commit()
        return True, "Delivery added successfully"
    except sqlite3.IntegrityError:
        return False, f"❌ Order ID '{order_id}' already exists! Please use a unique ID."  # FR-02
    except Exception as e:
        return False, f"Error: {str(e)}"
    finally:
        conn.close()

def get_all_deliveries_db():
    """Get all deliveries (FR-07)"""
    conn = get_connection()
    query = "SELECT * FROM deliveries ORDER BY created_at DESC"
    df = pd.read_sql_query(query, conn)
    conn.close()
    return df

def get_delivery_by_id_db(order_id):
    """Get delivery by order_id"""
    conn = get_connection()
    query = "SELECT * FROM deliveries WHERE order_id = ?"
    df = pd.read_sql_query(query, conn, params=(order_id,))
    conn.close()
    return df.iloc[0] if not df.empty else None

def complete_delivery_db(order_id, actual_time, status, delay_minutes):
    """Complete a delivery with actual time (FR-06)"""
    conn = get_connection()
    cursor = conn.cursor()
    
    cursor.execute('''
        UPDATE deliveries 
        SET actual_time = ?, status = ?, delay_minutes = ?, updated_at = CURRENT_TIMESTAMP
        WHERE order_id = ?
    ''', (actual_time, status, delay_minutes, order_id))
    
    conn.commit()
    conn.close()
    return True

def update_delivery_status_db(order_id, status, delay_minutes):
    """Update delivery status and delay (FR-04)"""
    conn = get_connection()
    cursor = conn.cursor()
    
    cursor.execute('''
        UPDATE deliveries 
        SET status = ?, delay_minutes = ?, updated_at = CURRENT_TIMESTAMP
        WHERE order_id = ?
    ''', (status, delay_minutes, order_id))
    
    conn.commit()
    conn.close()
    return True

def search_deliveries_db(search_term):
    """Search deliveries by Order ID or Customer Name (FR-08)"""
    conn = get_connection()
    query = '''
        SELECT * FROM deliveries 
        WHERE order_id LIKE ? OR customer_name LIKE ? OR driver_name LIKE ? OR delivery_area LIKE ?
        ORDER BY created_at DESC
    '''
    search_pattern = f"%{search_term}%"
    df = pd.read_sql_query(query, conn, params=(search_pattern, search_pattern, search_pattern, search_pattern))
    conn.close()
    return df

def filter_deliveries_db(status=None, driver=None, area=None):
    """Filter deliveries by Status, Driver, Area (FR-09)"""
    conditions = []
    params = []
    
    if status and status != "All":
        conditions.append("status = ?")
        params.append(status)
    if driver and driver != "All":
        conditions.append("driver_name = ?")
        params.append(driver)
    if area and area != "All":
        conditions.append("delivery_area = ?")
        params.append(area)
    
    where_clause = " WHERE " + " AND ".join(conditions) if conditions else ""
    query = f"SELECT * FROM deliveries{where_clause} ORDER BY created_at DESC"
    
    conn = get_connection()
    df = pd.read_sql_query(query, conn, params=params)
    conn.close()
    return df

def get_unique_drivers_db():
    """Get list of unique drivers"""
    conn = get_connection()
    df = pd.read_sql_query("SELECT DISTINCT driver_name FROM deliveries", conn)
    conn.close()
    return df['driver_name'].tolist()

def get_unique_areas_db():
    """Get list of unique areas"""
    conn = get_connection()
    df = pd.read_sql_query("SELECT DISTINCT delivery_area FROM deliveries", conn)
    conn.close()
    return df['delivery_area'].tolist()

def delete_all_deliveries_db():
    """Delete all deliveries (for testing)"""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM deliveries")
    conn.commit()
    conn.close()
    return True

def insert_sample_data_db(sample_data):
    """Insert sample data for testing"""
    query = '''
        INSERT OR IGNORE INTO deliveries 
        (order_id, customer_name, phone, delivery_area, driver_name, 
         order_date, expected_time, actual_time, status, delay_minutes)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    '''
    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.executemany(query, sample_data)
        conn.commit()
        return True
    except Exception as e:
        print(f"Error inserting sample data: {e}")
        return False
    finally:
        conn.close()

def get_db_stats():
    """Get database statistics"""
    conn = get_connection()
    query = '''
        SELECT 
            COUNT(*) as total,
            SUM(CASE WHEN status = 'ON TIME' THEN 1 ELSE 0 END) as on_time,
            SUM(CASE WHEN status = 'LATE' THEN 1 ELSE 0 END) as late,
            SUM(CASE WHEN status = 'PENDING' THEN 1 ELSE 0 END) as pending,
            SUM(CASE WHEN status = 'OVERDUE' THEN 1 ELSE 0 END) as overdue
        FROM deliveries
    '''
    df = pd.read_sql_query(query, conn)
    conn.close()
    return df.iloc[0].to_dict() if not df.empty else {}

if __name__ == "__main__":
    init_database()
    print("✅ Database setup complete!")