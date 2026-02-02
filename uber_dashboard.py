import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime

# Page configuration
st.set_page_config(
    page_title="Uber NCR Operational Analytics",
    page_icon="🏙️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- Professional Styling (Human Data Scientist Aesthetic) ---
st.markdown("""
    <style>
        /* Main background and font */
        .main {
            background-color: #f8f9fa;
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
        }
        h1, h2, h3 {
            color: #2c3e50;
            font-weight: 600;
        }
        h3 {
            font-size: 1.2rem;
            margin-top: 20px;
            margin-bottom: 15px;
        }
        
        /* Metric Cards */
        div.css-1r6slb0.e1tzin5v2 {
            background-color: white;
            border: 1px solid #e0e0e0;
            padding: 20px;
            border-radius: 8px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.05);
        }
        
        /* Custom KPI container */
        .kpi-card {
            background-color: white;
            padding: 20px;
            border-radius: 10px;
            border-left: 5px solid #000000;
            box-shadow: 0 4px 6px rgba(0,0,0,0.05);
            text-align: center;
            margin-bottom: 10px;
        }
        .kpi-title {
            color: #7f8c8d;
            font-size: 0.9rem;
            text-transform: uppercase;
            letter-spacing: 1px;
            margin-bottom: 5px;
        }
        .kpi-value {
            color: #2c3e50;
            font-size: 2rem;
            font-weight: 700;
        }
        .kpi-delta {
            font-size: 0.8rem;
            color: #27ae60;
            font-weight: 600;
        }

        /* Sidebar Styling */
        section[data-testid="stSidebar"] {
            background-color: #ffffff;
            border-right: 1px solid #e0e0e0;
        }
        
        /* Chart container */
        .chart-container {
            background-color: white;
            padding: 15px;
            border-radius: 8px;
            box-shadow: 0 1px 3px rgba(0,0,0,0.12);
            margin-bottom: 20px;
        }
    </style>
""", unsafe_allow_html=True)

# --- Helper Functions ---

@st.cache_data
def load_data():
    file_path = "/home/krutarth/D/machine_learning/uber/ncr_ride_bookings.csv"
    try:
        df = pd.read_csv(file_path)
        
        # Datetime conversion
        df['Date'] = pd.to_datetime(df['Date'], errors='coerce')
        # Combined datetime for granular analysis
        df['DateTime'] = pd.to_datetime(df['Date'].astype(str) + ' ' + df['Time'].astype(str), errors='coerce')
        
        # Feature Engineering for "Data Scientist" depth
        df['Hour'] = df['DateTime'].dt.hour
        df['DayOfWeek'] = df['DateTime'].dt.day_name()
        df['Month'] = df['DateTime'].dt.month_name()
        df['is_weekend'] = df['DateTime'].dt.dayofweek >= 5
        
        # Numeric cleanup
        numeric_cols = ['Booking Value', 'Ride Distance', 'Driver Ratings', 'Customer Rating', 'Avg VTAT', 'Avg CTAT']
        for col in numeric_cols:
            df[col] = pd.to_numeric(df[col], errors='coerce')

        return df
    except Exception as e:
        st.error(f"Error loading data: {e}")
        return None

def kpi_card(title, value, delta=None):
    delta_html = f"<div class='kpi-delta'>{delta}</div>" if delta else ""
    return f"""
    <div class="kpi-card">
        <div class="kpi-title">{title}</div>
        <div class="kpi-value">{value}</div>
        {delta_html}
    </div>
    """

df = load_data()

if df is not None:
    # --- Sidebar ---
    st.sidebar.title("Operational Filters")
    st.sidebar.markdown("Refine your analysis scope.")
    
    # Date Filter
    min_date = df['Date'].min()
    max_date = df['Date'].max()
    date_range = st.sidebar.date_input("Analysis Period", [min_date, max_date], min_value=min_date, max_value=max_date)
    
    # Advanced Filters
    vehicle_types = sorted(df['Vehicle Type'].dropna().unique().tolist())
    selected_vehicles = st.sidebar.multiselect("Vehicle Segments", vehicle_types, default=vehicle_types)
    
    booking_statuses = sorted(df['Booking Status'].dropna().unique().tolist())
    status_filter = st.sidebar.multiselect("Status Category", booking_statuses, default=booking_statuses)

    # Apply Filters
    mask = (
        (df['Date'] >= pd.to_datetime(date_range[0])) & 
        (df['Date'] <= pd.to_datetime(date_range[1])) &
        (df['Vehicle Type'].isin(selected_vehicles)) &
        (df['Booking Status'].isin(status_filter))
    )
    filtered_df = df[mask]
    
    # --- Main Content ---
    st.title("🏙️ NCR Region - Operations & Performance Overview")
    st.markdown(f"**Data Snapshot:** {date_range[0].strftime('%b %d, %Y')} - {date_range[1].strftime('%b %d, %Y')} | **Total Records:** {len(filtered_df):,}")
    
    st.markdown("---")

    # --- KPI Section (Custom HTML) ---
    col1, col2, col3, col4, col5 = st.columns(5)
    
    # Calculations
    total_rev = filtered_df['Booking Value'].sum()
    avg_order_value = filtered_df['Booking Value'].mean()
    total_rides = len(filtered_df)
    completed_rides = filtered_df[filtered_df['Booking Status'] == 'Completed']
    completion_rate = (len(completed_rides) / total_rides * 100) if total_rides > 0 else 0
    avg_vtat = filtered_df['Avg VTAT'].mean() # Vehicle Arrival Time

    with col1:
        st.markdown(kpi_card("Total Revenue", f"₹{total_rev/1e6:.1f}M"), unsafe_allow_html=True)
    with col2:
        st.markdown(kpi_card("Total Bookings", f"{total_rides:,}"), unsafe_allow_html=True)
    with col3:
        st.markdown(kpi_card("Completion Rate", f"{completion_rate:.1f}%"), unsafe_allow_html=True)
    with col4:
        st.markdown(kpi_card("Avg Order Value", f"₹{avg_order_value:.0f}"), unsafe_allow_html=True)
    with col5:
        st.markdown(kpi_card("Avg Arrival Time", f"{avg_vtat:.1f} min"), unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # --- Tabs Layout ---
    tab1, tab2, tab3 = st.tabs(["📉 Demand & Revenue", "📍 Operational Heatmaps", "⚙️ Cancellation Analysis"])

    # --- Tab 1: Demand & Revenue ---
    with tab1:
        c1, c2 = st.columns([2, 1])
        
        with c1:
            st.markdown("### Revenue & Booking Trends (Smoothed)")
            daily_data = filtered_df.groupby('Date').agg({'Booking Value': 'sum', 'Booking ID': 'count'}).reset_index()
            # 7-day rolling average for smoother "Data Scientist" look
            daily_data['Revenue (7d Avg)'] = daily_data['Booking Value'].rolling(window=7).mean()
            
            fig_trend = go.Figure()
            fig_trend.add_trace(go.Scatter(x=daily_data['Date'], y=daily_data['Booking Value'], mode='lines', name='Daily Revenue', line=dict(color='rgba(0,0,0,0.1)', width=1)))
            fig_trend.add_trace(go.Scatter(x=daily_data['Date'], y=daily_data['Revenue (7d Avg)'], mode='lines', name='7-Day Trend', line=dict(color='#000000', width=3)))
            
            fig_trend.update_layout(
                template="plotly_white",
                xaxis_title="Date",
                yaxis_title="Revenue (₹)",
                height=400,
                legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
            )
            st.plotly_chart(fig_trend, use_container_width=True)
            
        with c2:
            st.markdown("### Revenue Mix by Vehicle")
            # Aggregated metrics table aesthetic
            veh_metrics = filtered_df.groupby('Vehicle Type').agg(
                Revenue=('Booking Value', 'sum'),
                Rides=('Booking ID', 'count'),
                Avg_Price=('Booking Value', 'mean')
            ).reset_index().sort_values('Revenue', ascending=True)
            
            fig_mix = px.bar(veh_metrics, y='Vehicle Type', x='Revenue', text_auto='.2s', orientation='h',
                             color_discrete_sequence=['#2c3e50'])
            fig_mix.update_layout(template="plotly_white", height=400, xaxis_title="Total Revenue")
            fig_mix.update_traces(textfont_size=12, textangle=0, textposition="outside", cliponaxis=False)
            st.plotly_chart(fig_mix, use_container_width=True)

    # --- Tab 2: Demand Patterns (Heatmaps) ---
    with tab2:
        st.markdown("### Temporal Demand Patterns")
        st.caption("Identifying peak operational hours versus days of the week to optimize driver allocation.")
        
        # Prepare Heatmap Data
        heatmap_data = filtered_df.groupby(['DayOfWeek', 'Hour']).size().reset_index(name='Bookings')
        day_order = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
        
        # Pivot for heatmap format
        heatmap_pivot = heatmap_data.pivot(index='DayOfWeek', columns='Hour', values='Bookings').reindex(day_order)
        
        fig_heat = px.imshow(
            heatmap_pivot,
            labels=dict(x="Hour of Day", y="Day of Week", color="Booking Volume"),
            x=heatmap_pivot.columns,
            y=heatmap_pivot.index,
            aspect="auto",
            color_continuous_scale="Greys" # Professional/Scientific scale
        )
        fig_heat.update_layout(height=500)
        st.plotly_chart(fig_heat, use_container_width=True)
        
        # Hourly Distribution Line
        st.markdown("### Average Hourly Demand Profile")
        hourly_profile = filtered_df.groupby('Hour').size().reset_index(name='Average Bookings')
        fig_profile = px.area(hourly_profile, x='Hour', y='Average Bookings', line_shape='spline',
                              color_discrete_sequence=['#7f8c8d'])
        fig_profile.update_layout(template="plotly_white", height=300)
        st.plotly_chart(fig_profile, use_container_width=True)

    # --- Tab 3: Operational Efficiency ---
    with tab3:
        c1, c2 = st.columns(2)
        
        with c1:
            st.markdown("### Cancellation Reasons (Pareto Analysis)")
            # Focus on top reasons
            cancel_df = filtered_df[filtered_df['Booking Status'].str.contains('Cancel', case=False, na=False)]
            
            # Combine driver and customer reasons for a holistic view
            reasons = cancel_df['Reason for cancelling by Customer'].fillna(cancel_df['Driver Cancellation Reason']).value_counts()
            
            fig_pareto = go.Figure(go.Bar(
                x=reasons.values[:8], # Top 8 reasons
                y=reasons.index[:8],
                orientation='h',
                marker_color='#e74c3c'
            ))
            fig_pareto.update_layout(template="plotly_white", title="Top Friction Points", height=400)
            st.plotly_chart(fig_pareto, use_container_width=True)
            
        with c2:
            st.markdown("### Trip Distance Distribution")
            # Histogram for distance to understand short vs long haul
            fig_dist = px.histogram(filtered_df, x="Ride Distance", nbins=50, 
                                    title="Distribution of Trip Lengths (km)",
                                    color_discrete_sequence=['#3498db'])
            fig_dist.update_layout(template="plotly_white", height=400, bargap=0.1)
            st.plotly_chart(fig_dist, use_container_width=True)

    # --- Footer ---
    st.markdown("---")
    st.caption("© 2026 Uber Technologies Inc. | Internal Data Science Division | Report Generated via Streamlit")

else:
    st.error("Data unavailable. Please check the source path.")
