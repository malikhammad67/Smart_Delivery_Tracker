from datetime import datetime  # ✅ IMPORT ADDED
import pandas as pd
from delivery_service import calculate_delivery_status, format_delay_display

def get_dashboard_metrics(deliveries_df):
    """
    Calculate all dashboard metrics (FR-10, FR-11, FR-12)
    
    Returns:
    - total: Total deliveries
    - completed: Completed deliveries
    - on_time: On-time deliveries
    - late: Late deliveries
    - pending: Pending deliveries
    - overdue: Overdue deliveries
    - on_time_rate: On-time rate (FR-11)
    - avg_delay: Average delay for late deliveries (FR-12)
    """
    if deliveries_df.empty:
        return {
            'total': 0,
            'completed': 0,
            'on_time': 0,
            'late': 0,
            'pending': 0,
            'overdue': 0,
            'on_time_rate': 0.0,
            'avg_delay': 0.0,
            'completion_rate': 0.0
        }
    
    total = len(deliveries_df)
    on_time = len(deliveries_df[deliveries_df['status'] == 'ON TIME'])
    late = len(deliveries_df[deliveries_df['status'] == 'LATE'])
    pending = len(deliveries_df[deliveries_df['status'] == 'PENDING'])
    overdue = len(deliveries_df[deliveries_df['status'] == 'OVERDUE'])
    
    completed = on_time + late
    
    # FR-11: On-time rate (completed deliveries only)
    on_time_rate = round((on_time / completed * 100), 2) if completed > 0 else 0.0
    
    # FR-12: Average delay for late deliveries
    if late > 0:
        avg_delay = round(deliveries_df[deliveries_df['status'] == 'LATE']['delay_minutes'].mean(), 2)
    else:
        avg_delay = 0.0
    
    completion_rate = round((completed / total * 100), 2) if total > 0 else 0.0
    
    return {
        'total': total,
        'completed': completed,
        'on_time': on_time,
        'late': late,
        'pending': pending,
        'overdue': overdue,
        'on_time_rate': on_time_rate,
        'avg_delay': avg_delay,
        'completion_rate': completion_rate
    }

def get_driver_performance(deliveries_df):
    """
    Calculate driver performance metrics (FR-13)
    
    Returns:
    - DataFrame with: Driver, Total, On Time, Late, On-Time Rate
    - Best performing driver
    """
    if deliveries_df.empty:
        return pd.DataFrame(), None
    
    driver_stats = []
    
    for driver in deliveries_df['driver_name'].unique():
        driver_data = deliveries_df[deliveries_df['driver_name'] == driver]
        
        total = len(driver_data)
        on_time = len(driver_data[driver_data['status'] == 'ON TIME'])
        late = len(driver_data[driver_data['status'] == 'LATE'])
        
        completed = on_time + late
        on_time_rate = round((on_time / completed * 100), 2) if completed > 0 else 0.0
        
        driver_stats.append({
            'Driver': driver,
            'Total Deliveries': total,
            'On Time': on_time,
            'Late': late,
            'On-Time Rate': on_time_rate,
            'Rating': get_rating(on_time_rate)
        })
    
    driver_df = pd.DataFrame(driver_stats)
    driver_df = driver_df.sort_values('On-Time Rate', ascending=False)
    
    # Find best performing driver (FR-13)
    best_driver = driver_df.iloc[0]['Driver'] if not driver_df.empty else None
    
    return driver_df, best_driver

def get_area_performance(deliveries_df):
    """
    Calculate area performance metrics (FR-14)
    
    Returns:
    - DataFrame with: Area, Total, Late Count, Late Rate
    - Area with highest late rate
    """
    if deliveries_df.empty:
        return pd.DataFrame(), None
    
    area_stats = []
    
    for area in deliveries_df['delivery_area'].unique():
        area_data = deliveries_df[deliveries_df['delivery_area'] == area]
        
        total = len(area_data)
        late = len(area_data[area_data['status'] == 'LATE'])
        overdue = len(area_data[area_data['status'] == 'OVERDUE'])
        
        late_rate = round((late / total * 100), 2) if total > 0 else 0.0
        
        area_stats.append({
            'Area': area,
            'Total Deliveries': total,
            'Late Count': late,
            'Overdue Count': overdue,
            'Late Rate': late_rate
        })
    
    area_df = pd.DataFrame(area_stats)
    area_df = area_df.sort_values('Late Rate', ascending=False)
    
    # FR-14: Area with highest late rate
    worst_area = area_df.iloc[0]['Area'] if not area_df.empty else None
    
    return area_df, worst_area

def get_rating(on_time_rate):
    """Get rating based on on-time rate"""
    if on_time_rate >= 95:
        return "⭐ Exceptional"
    elif on_time_rate >= 85:
        return "⭐ Excellent"
    elif on_time_rate >= 70:
        return "⭐ Good"
    elif on_time_rate >= 50:
        return "⭐ Average"
    else:
        return "⭐ Needs Improvement"

def get_delay_distribution(deliveries_df):
    """Get distribution of delay severity"""
    if deliveries_df.empty:
        return {'No Delay': 0, 'Slight (1-15min)': 0, 'Moderate (16-60min)': 0, 'Severe (60+ min)': 0}
    
    distribution = {'No Delay': 0, 'Slight (1-15min)': 0, 'Moderate (16-60min)': 0, 'Severe (60+ min)': 0}
    
    for _, row in deliveries_df.iterrows():
        if row['status'] == 'LATE' and row['delay_minutes'] > 0:
            if row['delay_minutes'] <= 15:
                distribution['Slight (1-15min)'] += 1
            elif row['delay_minutes'] <= 60:
                distribution['Moderate (16-60min)'] += 1
            else:
                distribution['Severe (60+ min)'] += 1
        else:
            distribution['No Delay'] += 1
    
    return distribution

def generate_summary_report(deliveries_df):
    """Generate comprehensive summary report"""
    if deliveries_df.empty:
        return {'error': 'No data available'}
    
    metrics = get_dashboard_metrics(deliveries_df)
    driver_df, best_driver = get_driver_performance(deliveries_df)
    area_df, worst_area = get_area_performance(deliveries_df)
    
    return {
        'generated_at': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),  # ✅ NOW WORKS
        'total_deliveries': metrics['total'],
        'completed': metrics['completed'],
        'on_time': metrics['on_time'],
        'late': metrics['late'],
        'pending': metrics['pending'],
        'overdue': metrics['overdue'],
        'on_time_rate': metrics['on_time_rate'],
        'avg_delay': metrics['avg_delay'],
        'completion_rate': metrics['completion_rate'],
        'best_driver': best_driver,
        'worst_area': worst_area
    }

if __name__ == "__main__":
    print("Analytics module ready!")