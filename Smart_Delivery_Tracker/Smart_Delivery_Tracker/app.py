import streamlit as st
import pandas as pd
from datetime import datetime, time
import plotly.express as px
import plotly.graph_objects as go

# Import all modules
from database import (
    init_database, add_delivery_db, get_all_deliveries_db,
    complete_delivery_db, search_deliveries_db, filter_deliveries_db,
    get_unique_drivers_db, get_unique_areas_db, insert_sample_data_db,
    delete_all_deliveries_db, get_db_stats, update_delivery_status_db
)
from delivery_service import (
    calculate_delivery_status, get_status_color, get_status_emoji,
    format_delay_display, validate_delivery_input, get_status_badge_html,
    generate_order_id
)
from analytics import (
    get_dashboard_metrics, get_driver_performance, get_area_performance,
    get_delay_distribution, generate_summary_report
)
from utils import format_phone, get_current_date_str, get_current_time_str

# ============================================
# PAGE CONFIGURATION
# ============================================
st.set_page_config(
    page_title="Smart Delivery Tracker Pro",
    page_icon="🚚",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ============================================
# CUSTOM CSS
# ============================================
st.markdown("""
<style>
    .main-header {
        background: linear-gradient(135deg, #0f0c29 0%, #302b63 50%, #24243e 100%);
        padding: 25px 30px;
        border-radius: 15px;
        margin-bottom: 25px;
        color: white;
    }
    .main-header h1 {
        font-size: 2.5rem;
        font-weight: 700;
        margin: 0;
    }
    .main-header p {
        opacity: 0.8;
        margin: 5px 0 0 0;
    }
    .metric-card {
        background: white;
        padding: 20px;
        border-radius: 12px;
        box-shadow: 0 2px 10px rgba(0,0,0,0.05);
        text-align: center;
        border-left: 4px solid #4facfe;
    }
    .metric-card .value {
        font-size: 2rem;
        font-weight: 700;
        color: #1a1a2e;
    }
    .metric-card .label {
        color: #6b7280;
        font-size: 0.85rem;
    }
    .metric-card .delta {
        font-size: 0.8rem;
        font-weight: 600;
    }
    .status-badge {
        display: inline-block;
        padding: 4px 12px;
        border-radius: 20px;
        font-weight: 600;
        font-size: 0.8rem;
    }
    .status-on-time { background: #10b981; color: white; }
    .status-late { background: #ef4444; color: white; }
    .status-pending { background: #f59e0b; color: white; }
    .status-overdue { background: #dc2626; color: white; }
    .stButton > button {
        border-radius: 10px;
        font-weight: 600;
    }
    .stForm {
        background: white;
        padding: 20px;
        border-radius: 12px;
        box-shadow: 0 2px 10px rgba(0,0,0,0.05);
    }
    .delivery-table {
        background: white;
        padding: 15px;
        border-radius: 12px;
        box-shadow: 0 2px 10px rgba(0,0,0,0.05);
    }
    .divider {
        border: none;
        height: 2px;
        background: linear-gradient(90deg, #4facfe 0%, #00f2fe 100%);
        margin: 25px 0;
    }
</style>
""", unsafe_allow_html=True)

# ============================================
# INITIALIZE DATABASE
# ============================================
init_database()

# ============================================
# SESSION STATE
# ============================================
if 'refresh' not in st.session_state:
    st.session_state.refresh = False

def load_data():
    return get_all_deliveries_db()

def refresh_data():
    st.session_state.refresh = not st.session_state.refresh

# ============================================
# MAIN APP
# ============================================

# HEADER
st.markdown("""
<div class="main-header">
    <h1>🚚 Smart Delivery Tracker Pro</h1>
    <p>Complete delivery management with real-time tracking & analytics</p>
</div>
""", unsafe_allow_html=True)

# ============================================
# SIDEBAR
# ============================================
with st.sidebar:
    st.markdown("### 📋 Navigation")
    page = st.radio(
        "Select Page",
        ["🏠 Dashboard", "➕ Add Delivery", "📋 All Deliveries", "📊 Analytics", "📈 Reports"],
        index=0
    )
    
    st.divider()
    
    # Quick Stats
    stats = get_db_stats()
    if stats and stats.get('total', 0) > 0:
        st.markdown("### 📊 Quick Stats")
        col1, col2 = st.columns(2)
        with col1:
            st.metric("Total", stats.get('total', 0))
            st.metric("✅ On Time", stats.get('on_time', 0))
        with col2:
            st.metric("⏰ Late", stats.get('late', 0))
            st.metric("⏳ Pending", stats.get('pending', 0))
    
    st.divider()
    st.caption("Built with ❤️ | Python Capstone")

# ============================================
# PAGE ROUTING
# ============================================

# ===== DASHBOARD (FR-10, FR-11, FR-12) =====
if page == "🏠 Dashboard":
    st.header("📊 Executive Dashboard")
    
    df = load_data()
    
    if df.empty:
        st.warning("No deliveries found! Load sample data or add your first delivery.")
        col1, col2 = st.columns(2)
        with col1:
            if st.button("📦 Load Sample Data", use_container_width=True):
                sample_data = [
                    ("DLV-1001", "Ahmed Khan", "0300-1234567", "Islamabad", "Ali", "2024-08-30", "10:00", "09:45", "ON TIME", 0),
                    ("DLV-1002", "Sara Malik", "0301-7654321", "Rawalpindi", "Hamza", "2024-08-30", "11:00", "12:15", "LATE", 75),
                    ("DLV-1003", "Usman Ali", "0302-9876543", "Wah Cantt", "Ali", "2024-08-30", "16:00", None, "PENDING", 0),
                    ("DLV-1004", "Hira Noor", "0303-4567890", "Islamabad", "Bilal", "2024-08-30", "13:30", "13:30", "ON TIME", 0),
                    ("DLV-1005", "Adeel Khan", "0304-7890123", "Rawalpindi", "Hamza", "2024-08-30", "15:00", "15:42", "LATE", 42),
                    ("DLV-1006", "Fatima Ahmed", "0305-3456789", "Islamabad", "Sohail", "2024-08-30", "09:00", "08:50", "ON TIME", 0),
                    ("DLV-1007", "Imran Shah", "0306-6789012", "Rawalpindi", "Bilal", "2024-08-30", "14:00", "14:30", "LATE", 30),
                    ("DLV-1008", "Zara Khan", "0307-9012345", "Wah Cantt", "Ali", "2024-08-30", "12:00", None, "OVERDUE", 0),
                    ("DLV-1009", "Hassan Ali", "0308-2345678", "Islamabad", "Hamza", "2024-08-30", "17:00", "17:10", "LATE", 10),
                    ("DLV-1010", "Ayesha Malik", "0309-5678901", "Rawalpindi", "Sohail", "2024-08-30", "08:00", "08:05", "LATE", 5),
                ]
                insert_sample_data_db(sample_data)
                st.rerun()
        with col2:
            if st.button("➕ Add First Delivery", use_container_width=True):
                st.switch_page("app.py")
    else:
        # Update statuses for pending deliveries
        for idx, row in df.iterrows():
            if row['status'] in ['PENDING', 'OVERDUE']:
                status, delay, display = calculate_delivery_status(row['expected_time'], row['actual_time'])
                if status != row['status'] or delay != row['delay_minutes']:
                    update_delivery_status_db(row['order_id'], status, delay)
        
        df = load_data()
        metrics = get_dashboard_metrics(df)
        
        # FR-10: Dashboard Counters
        col1, col2, col3, col4, col5, col6 = st.columns(6)
        
        with col1:
            st.metric("📦 Total", metrics['total'])
        with col2:
            st.metric("✅ Completed", metrics['completed'])
        with col3:
            st.metric("🟢 On Time", metrics['on_time'])
        with col4:
            st.metric("🔴 Late", metrics['late'])
        with col5:
            st.metric("⏳ Pending", metrics['pending'])
        with col6:
            st.metric("⚠️ Overdue", metrics['overdue'])
        
        # FR-11: On-Time Rate
        col1, col2 = st.columns(2)
        with col1:
            st.metric("📊 On-Time Rate", f"{metrics['on_time_rate']}%", 
                     help="Percentage of completed deliveries that were on time")
        with col2:
            # FR-12: Average Delay
            st.metric("⏱️ Avg Delay", f"{metrics['avg_delay']} min", 
                     help="Average delay for late deliveries only")
        
        st.markdown('<hr class="divider">', unsafe_allow_html=True)
        
        # Charts
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("📈 Status Distribution")
            status_counts = df['status'].value_counts().reset_index()
            status_counts.columns = ['Status', 'Count']
            
            fig = px.pie(status_counts, values='Count', names='Status',
                         color='Status',
                         color_discrete_map={
                             'ON TIME': '#10b981',
                             'LATE': '#ef4444',
                             'PENDING': '#f59e0b',
                             'OVERDUE': '#dc2626'
                         })
            fig.update_layout(height=350)
            st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            st.subheader("📊 Delay Distribution")
            delay_dist = get_delay_distribution(df)
            dist_df = pd.DataFrame({
                'Category': list(delay_dist.keys()),
                'Count': list(delay_dist.values())
            })
            fig = px.bar(dist_df, x='Category', y='Count', color='Category',
                        color_discrete_sequence=['#10b981', '#f59e0b', '#f97316', '#ef4444'])
            fig.update_layout(height=350, showlegend=False)
            st.plotly_chart(fig, use_container_width=True)

# ===== ADD DELIVERY (FR-01, FR-02, FR-16) =====
elif page == "➕ Add Delivery":
    st.header("➕ Add New Delivery")
    
    with st.form("delivery_form", clear_on_submit=True):
        col1, col2 = st.columns(2)
        
        with col1:
            order_id = st.text_input(
                "📋 Order ID*",
                value=generate_order_id(),
                help="Auto-generated unique ID",
                disabled=True
            )
            customer_name = st.text_input("👤 Customer Name*", placeholder="e.g., Ahmed Khan")
            phone = st.text_input("📞 Phone", placeholder="e.g., 0300-1234567")
            delivery_area = st.text_input("📍 Delivery Area*", placeholder="e.g., Islamabad")
        
        with col2:
            driver_name = st.text_input("🚗 Driver Name*", placeholder="e.g., Ali")
            order_date = st.date_input("📅 Order Date", value=datetime.now())
            expected_time = st.time_input("⏰ Expected Delivery Time*", value=datetime.now().time())
            expected_time_str = expected_time.strftime("%H:%M")
        
        st.markdown("*Required fields")
        
        submitted = st.form_submit_button("✅ Add Delivery", use_container_width=True)
        
        if submitted:
            # FR-16: Validation
            errors = validate_delivery_input(
                order_id, customer_name, delivery_area, driver_name, 
                expected_time_str, phone
            )
            
            if errors:
                for error in errors:
                    st.error(f"❌ {error}")
            else:
                # FR-02: Check duplicate
                from database import get_delivery_by_id_db
                existing = get_delivery_by_id_db(order_id)
                if existing is not None:
                    st.error(f"❌ Order ID '{order_id}' already exists! Please use a unique ID.")
                else:
                    success, message = add_delivery_db(
                        order_id, customer_name, phone, delivery_area, driver_name,
                        order_date.strftime("%Y-%m-%d"), expected_time_str
                    )
                    
                    if success:
                        st.success(f"✅ {message}")
                        st.balloons()
                        # FR-04: Show initial status
                        status, delay, display = calculate_delivery_status(expected_time_str)
                        st.info(f"📊 Initial Status: {get_status_emoji(status)} **{status}**")
                        if status == "LATE":
                            st.info(f"⏱️ Delay: {display}")
                        st.rerun()
                    else:
                        st.error(f"❌ {message}")
    
    # Show recent deliveries
    df = load_data()
    if not df.empty:
        st.divider()
        st.subheader("📋 Recent Deliveries")
        recent = df.head(3)
        for _, row in recent.iterrows():
            status_badge = get_status_badge_html(row['status'])
            st.markdown(f"""
            <div style="background:#f8f9fa;padding:10px;border-radius:8px;margin:5px 0;">
                <b>{row['order_id']}</b> - {row['customer_name']} 
                {status_badge}
                <span style="float:right;">🚗 {row['driver_name']} | 📍 {row['delivery_area']}</span>
            </div>
            """, unsafe_allow_html=True)

# ===== ALL DELIVERIES (FR-07, FR-08, FR-09, FR-15) =====
elif page == "📋 All Deliveries":
    st.header("📋 All Deliveries")
    
    # FR-08: Search and FR-09: Filters
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        search_term = st.text_input("🔍 Search", placeholder="ID / Customer / Driver / Area")
    with col2:
        status_options = ["All"] + list(load_data()['status'].unique()) if not load_data().empty else ["All"]
        status_filter = st.selectbox("📊 Status Filter", status_options)
    with col3:
        drivers = ["All"] + get_unique_drivers_db()
        driver_filter = st.selectbox("🚗 Driver Filter", drivers)
    with col4:
        areas = ["All"] + get_unique_areas_db()
        area_filter = st.selectbox("📍 Area Filter", areas)
    
    # Load data with filters
    if search_term:
        df = search_deliveries_db(search_term)  # FR-08
    else:
        df = filter_deliveries_db(status_filter, driver_filter, area_filter)  # FR-09
    
    if df.empty:
        st.info("No deliveries found matching the current filters.")
    else:
        # FR-07: View Deliveries in clear table
        display_df = df.copy()
        
        # Format status with badge
        display_df['Status'] = display_df['status'].apply(get_status_badge_html)
        
        # Format delay display (FR-05)
        def format_delay(row):
            if row['status'] == 'LATE' and row['delay_minutes'] > 0:
                return format_delay_display(row['delay_minutes'])
            return "-"
        display_df['Delay'] = df.apply(format_delay, axis=1)
        
        # Format phone
        display_df['Phone'] = display_df['phone'].apply(lambda x: format_phone(x) if x else "-")
        
        # Select columns
        columns_to_show = ['order_id', 'customer_name', 'Phone', 'delivery_area', 'driver_name',
                          'expected_time', 'actual_time', 'Status', 'Delay']
        
        display_df = display_df[columns_to_show].rename(columns={
            'order_id': 'Order ID',
            'customer_name': 'Customer',
            'delivery_area': 'Area',
            'driver_name': 'Driver',
            'expected_time': 'Expected',
            'actual_time': 'Actual'
        })
        
        st.markdown('<div class="delivery-table">', unsafe_allow_html=True)
        st.write(display_df.to_html(escape=False, index=False), unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)
        
        st.caption(f"Showing {len(df)} deliveries")
        
        # FR-15: CSV Export
        col1, col2 = st.columns(2)
        with col1:
            if st.button("📥 Export to CSV", use_container_width=True):
                csv = df.to_csv(index=False)
                st.download_button(
                    label="📥 Click to Download",
                    data=csv,
                    file_name=f"deliveries_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                    mime="text/csv"
                )
        with col2:
            if st.button("🗑️ Clear All Data", use_container_width=True):
                if delete_all_deliveries_db():
                    st.success("All data cleared!")
                    st.rerun()

# ===== ANALYTICS (FR-13, FR-14) =====
elif page == "📊 Analytics":
    st.header("📊 Performance Analytics")
    
    df = load_data()
    
    if df.empty:
        st.warning("No data available for analytics. Please add some deliveries first!")
    else:
        # FR-13: Driver Performance
        st.subheader("🚗 Driver Performance")
        driver_stats, best_driver = get_driver_performance(df)
        
        if not driver_stats.empty:
            # Display driver stats
            st.dataframe(driver_stats, use_container_width=True)
            
            # Highlight best driver
            if best_driver:
                st.success(f"🏆 Best Performing Driver: **{best_driver}**")
            
            # Driver chart
            fig = px.bar(driver_stats, x='Driver', y='On-Time Rate',
                         title='Driver On-Time Rate (%)',
                         color='On-Time Rate',
                         color_continuous_scale=['red', 'yellow', 'green'],
                         text='On-Time Rate')
            fig.update_traces(texttemplate='%{text:.1f}%', textposition='outside')
            fig.update_layout(height=350)
            st.plotly_chart(fig, use_container_width=True)
        
        st.markdown('<hr class="divider">', unsafe_allow_html=True)
        
        # FR-14: Area Performance
        st.subheader("📍 Area Performance")
        area_stats, worst_area = get_area_performance(df)
        
        if not area_stats.empty:
            st.dataframe(area_stats, use_container_width=True)
            
            # Highlight worst area
            if worst_area:
                st.warning(f"⚠️ Area with Highest Late Rate: **{worst_area}**")
            
            # Area chart
            fig = px.bar(area_stats, x='Area', y='Late Rate',
                         title='Area Late Rate (%)',
                         color='Late Rate',
                         color_continuous_scale=['green', 'yellow', 'red'],
                         text='Late Rate')
            fig.update_traces(texttemplate='%{text:.1f}%', textposition='outside')
            fig.update_layout(height=350)
            st.plotly_chart(fig, use_container_width=True)

# ===== REPORTS =====
elif page == "📈 Reports":
    st.header("📈 Summary Reports")
    
    df = load_data()
    
    if df.empty:
        st.warning("No data available for reports.")
    else:
        report = generate_summary_report(df)
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.subheader("📊 Overview")
            st.metric("Total Deliveries", report['total_deliveries'])
            st.metric("Completed", report['completed'])
            st.metric("On-Time Rate", f"{report['on_time_rate']}%")
        
        with col2:
            st.subheader("⏱️ Delay Metrics")
            st.metric("Late Deliveries", report['late'])
            st.metric("Average Delay", f"{report['avg_delay']} min")
            st.metric("Overdue", report['overdue'])
        
        with col3:
            st.subheader("🏆 Performance")
            st.metric("Best Driver", report['best_driver'] or "N/A")
            st.metric("Worst Area", report['worst_area'] or "N/A")
            st.metric("Completion Rate", f"{report['completion_rate']}%")
        
        st.markdown('<hr class="divider">', unsafe_allow_html=True)
        
        # Export report
        if st.button("📥 Export Full Report CSV", use_container_width=True):
            report_df = pd.DataFrame([report])
            csv = report_df.to_csv(index=False)
            st.download_button(
                label="📥 Download Report",
                data=csv,
                file_name=f"delivery_report_{datetime.now().strftime('%Y%m%d')}.csv",
                mime="text/csv"
            )

# ============================================
# FOOTER
# ============================================
st.divider()
st.markdown("""
<div style="text-align: center; padding: 15px 0; color: #6b7280; font-size: 0.85rem;">
    🚚 Smart Delivery Tracker Pro v2.0 | Built with ❤️ using Python & Streamlit
</div>
""", unsafe_allow_html=True)