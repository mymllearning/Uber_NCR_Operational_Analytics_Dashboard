import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime

# Page configuration
st.set_page_config(
    page_title="Uber NCR Operational Analytics",
    page_icon="🚗",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- Clean Light UI Styling ---
st.markdown("""
    <style>
    /* Main background */
    .main {
        background-color: #f8f9fa;
    }
    
    /* Sidebar styling */
    [data-testid="stSidebar"] {
        background-color: #ffffff;
        border-right: 1px solid #e9ecef;
    }
    
    /* KPI Card styling */
    .kpi-card {
        background: linear-gradient(135deg, #ffffff 0%, #f8f9fa 100%);
        padding: 1.5rem;
        border-radius: 12px;
        border: 1px solid #dee2e6;
        box-shadow: 0 2px 8px rgba(0,0,0,0.04);
        transition: all 0.3s ease;
    }
    
    .kpi-card:hover {
        transform: translateY(-2px);
        box-shadow: 0 4px 12px rgba(0,0,0,0.08);
    }
    
    .kpi-title {
        font-size: 0.85rem;
        color: #6c757d;
        font-weight: 500;
        text-transform: uppercase;
        letter-spacing: 0.5px;
        margin-bottom: 0.5rem;
    }
    
    .kpi-value {
        font-size: 2rem;
        font-weight: 700;
        color: #212529;
        margin: 0.25rem 0;
    }
    
    .kpi-delta {
        font-size: 0.875rem;
        color: #28a745;
        font-weight: 500;
    }
    
    /* Remove padding */
    .block-container {
        padding-top: 2rem;
    }
    
    /* Headings */
    h1, h2, h3 {
        color: #212529;
        font-weight: 600;
    }
    
    /* Tabs */
    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
        background-color: transparent;
    }
    
    .stTabs [data-baseweb="tab"] {
        background-color: #ffffff;
        border: 1px solid #dee2e6;
        border-radius: 8px;
        padding: 0.75rem 1.5rem;
        font-weight: 500;
    }
    
    .stTabs [aria-selected="true"] {
        background-color: #212529;
        color: white;
        border-color: #212529;
    }
    
    /* Metrics */
    [data-testid="stMetricValue"] {
        font-size: 1.75rem;
        font-weight: 600;
    }
    
    /* Dataframe */
    .dataframe {
        font-size: 0.9rem;
    }
    
    /* Buttons */
    .stButton > button {
        background-color: #212529;
        color: white;
        border: none;
        border-radius: 8px;
        padding: 0.5rem 1.5rem;
        font-weight: 500;
        transition: all 0.3s ease;
    }
    
    .stButton > button:hover {
        background-color: #495057;
        transform: translateY(-1px);
    }
    
    /* Multiselect */
    .stMultiSelect [data-baseweb="tag"] {
        background-color: #212529;
    }
    </style>
""", unsafe_allow_html=True)

# --- Helper Functions ---
@st.cache_data
def load_data():
    """Load and preprocess the Uber NCR data"""
    file_path = "ncr_ride_bookings.csv"
    
    try:
        df = pd.read_csv(file_path)
        
        # Datetime conversion
        df['Date'] = pd.to_datetime(df['Date'], errors='coerce')
        df['DateTime'] = pd.to_datetime(
            df['Date'].astype(str) + ' ' + df['Time'].astype(str), 
            errors='coerce'
        )
        
        # Feature Engineering
        df['Hour'] = df['DateTime'].dt.hour
        df['DayOfWeek'] = df['DateTime'].dt.day_name()
        df['Month'] = df['DateTime'].dt.month_name()
        df['is_weekend'] = df['DateTime'].dt.dayofweek >= 5
        
        # Numeric cleanup
        numeric_cols = [
            'Booking Value', 'Ride Distance', 'Driver Ratings', 
            'Customer Rating', 'Avg VTAT', 'Avg CTAT'
        ]
        for col in numeric_cols:
            if col in df.columns:
                df[col] = pd.to_numeric(df[col], errors='coerce')
        
        return df
    
    except FileNotFoundError:
        st.error(f"❌ File not found: {file_path}")
        st.info("Please update the file path in the code to match your data location.")
        return None
    except Exception as e:
        st.error(f"❌ Error loading data: {str(e)}")
        return None

def kpi_card(title, value, delta=None):
    """Create a clean KPI card"""
    delta_html = f'<div class="kpi-delta">▲ {delta}</div>' if delta else ""
    return f"""
    <div class="kpi-card">
        <div class="kpi-title">{title}</div>
        <div class="kpi-value">{value}</div>
        {delta_html}
    </div>
    """

# --- Load Data ---
df = load_data()

if df is not None:
    # --- Sidebar Filters ---
    st.sidebar.image("https://via.placeholder.com/200x60/000000/FFFFFF?text=UBER", use_container_width=True)
    st.sidebar.title("🎯 Filters")
    st.sidebar.markdown("---")
    
    # Date Filter
    min_date = df['Date'].min().date()
    max_date = df['Date'].max().date()
    date_range = st.sidebar.date_input(
        "📅 Analysis Period",
        [min_date, max_date],
        min_value=min_date,
        max_value=max_date
    )
    
    # Vehicle Type Filter
    vehicle_types = sorted(df['Vehicle Type'].dropna().unique().tolist())
    selected_vehicles = st.sidebar.multiselect(
        "🚗 Vehicle Segments",
        vehicle_types,
        default=vehicle_types
    )
    
    # Booking Status Filter
    booking_statuses = sorted(df['Booking Status'].dropna().unique().tolist())
    status_filter = st.sidebar.multiselect(
        "📊 Booking Status",
        booking_statuses,
        default=booking_statuses
    )
    
    st.sidebar.markdown("---")
    st.sidebar.caption("💡 Use filters to refine your analysis")
    
    # Apply Filters
    mask = (
        (df['Date'] >= pd.to_datetime(date_range[0])) &
        (df['Date'] <= pd.to_datetime(date_range[1])) &
        (df['Vehicle Type'].isin(selected_vehicles)) &
        (df['Booking Status'].isin(status_filter))
    )
    filtered_df = df[mask]
    
    # --- Header ---
    col1, col2 = st.columns([3, 1])
    with col1:
        st.title("🚗 Uber NCR Operational Analytics")
        st.markdown(
            f"**Period:** {date_range[0].strftime('%b %d, %Y')} - {date_range[1].strftime('%b %d, %Y')} "
            f"| **Records:** {len(filtered_df):,}"
        )
    with col2:
        st.metric("Data Quality", f"{(1 - filtered_df.isnull().sum().sum() / filtered_df.size) * 100:.1f}%")
    
    st.markdown("---")
    
    # --- KPI Section ---
    total_rev = filtered_df['Booking Value'].sum()
    avg_order_value = filtered_df['Booking Value'].mean()
    total_rides = len(filtered_df)
    completed_rides = filtered_df[filtered_df['Booking Status'] == 'Completed']
    completion_rate = (len(completed_rides) / total_rides * 100) if total_rides > 0 else 0
    avg_vtat = filtered_df['Avg VTAT'].mean()
    
    col1, col2, col3, col4, col5 = st.columns(5)
    
    with col1:
        st.markdown(
            kpi_card("Total Revenue", f"₹{total_rev/1e6:.1f}M"),
            unsafe_allow_html=True
        )
    
    with col2:
        st.markdown(
            kpi_card("Total Bookings", f"{total_rides:,}"),
            unsafe_allow_html=True
        )
    
    with col3:
        st.markdown(
            kpi_card("Completion Rate", f"{completion_rate:.1f}%"),
            unsafe_allow_html=True
        )
    
    with col4:
        st.markdown(
            kpi_card("Avg Order Value", f"₹{avg_order_value:.0f}"),
            unsafe_allow_html=True
        )
    
    with col5:
        st.markdown(
            kpi_card("Avg Arrival Time", f"{avg_vtat:.1f} min"),
            unsafe_allow_html=True
        )
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    # --- Tabs ---
    tab1, tab2, tab3 = st.tabs(["📈 Demand & Revenue", "🗓️ Operational Patterns", "⚠️ Cancellation Insights"])
    
    # --- Tab 1: Demand & Revenue ---
    with tab1:
        col1, col2 = st.columns([2, 1])
        
        with col1:
            st.markdown("### 📊 Revenue Trends")
            daily_data = filtered_df.groupby('Date').agg({
                'Booking Value': 'sum',
                'Booking ID': 'count'
            }).reset_index()
            daily_data.columns = ['Date', 'Revenue', 'Bookings']
            
            # 7-day rolling average
            daily_data['Revenue_7d'] = daily_data['Revenue'].rolling(window=7, min_periods=1).mean()
            
            fig_trend = go.Figure()
            
            # Actual revenue (light line)
            fig_trend.add_trace(go.Scatter(
                x=daily_data['Date'],
                y=daily_data['Revenue'],
                mode='lines',
                name='Daily Revenue',
                line=dict(color='#dee2e6', width=1.5),
                opacity=0.5
            ))
            
            # 7-day trend (bold line)
            fig_trend.add_trace(go.Scatter(
                x=daily_data['Date'],
                y=daily_data['Revenue_7d'],
                mode='lines',
                name='7-Day Average',
                line=dict(color='#212529', width=3)
            ))
            
            fig_trend.update_layout(
                template="plotly_white",
                xaxis_title="Date",
                yaxis_title="Revenue (₹)",
                height=400,
                hovermode='x unified',
                legend=dict(
                    orientation="h",
                    yanchor="bottom",
                    y=1.02,
                    xanchor="right",
                    x=1
                )
            )
            
            st.plotly_chart(fig_trend, use_container_width=True)
        
        with col2:
            st.markdown("### 🚙 Revenue by Vehicle Type")
            veh_metrics = filtered_df.groupby('Vehicle Type').agg(
                Revenue=('Booking Value', 'sum'),
                Rides=('Booking ID', 'count')
            ).reset_index().sort_values('Revenue', ascending=True)
            
            fig_mix = px.bar(
                veh_metrics,
                y='Vehicle Type',
                x='Revenue',
                orientation='h',
                text_auto='.2s',
                color_discrete_sequence=['#495057']
            )
            
            fig_mix.update_layout(
                template="plotly_white",
                height=400,
                xaxis_title="Revenue (₹)",
                yaxis_title="",
                showlegend=False
            )
            
            fig_mix.update_traces(
                textfont_size=11,
                textangle=0,
                textposition="outside",
                cliponaxis=False
            )
            
            st.plotly_chart(fig_mix, use_container_width=True)
        
        # Additional metrics
        st.markdown("### 📈 Key Metrics Breakdown")
        
        metric_col1, metric_col2, metric_col3, metric_col4 = st.columns(4)
        
        with metric_col1:
            avg_distance = filtered_df['Ride Distance'].mean()
            st.metric("Avg Trip Distance", f"{avg_distance:.1f} km")
        
        with metric_col2:
            avg_driver_rating = filtered_df['Driver Ratings'].mean()
            st.metric("Avg Driver Rating", f"{avg_driver_rating:.2f} ⭐")
        
        with metric_col3:
            avg_customer_rating = filtered_df['Customer Rating'].mean()
            st.metric("Avg Customer Rating", f"{avg_customer_rating:.2f} ⭐")
        
        with metric_col4:
            avg_ctat = filtered_df['Avg CTAT'].mean()
            st.metric("Avg Customer Wait", f"{avg_ctat:.1f} min")
    
    # --- Tab 2: Operational Patterns ---
    with tab2:
        st.markdown("### 🔥 Demand Heatmap: Day vs Hour")
        st.caption("Identify peak hours to optimize driver allocation and surge pricing")
        
        # Heatmap data
        heatmap_data = filtered_df.groupby(['DayOfWeek', 'Hour']).size().reset_index(name='Bookings')
        day_order = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
        heatmap_pivot = heatmap_data.pivot(index='DayOfWeek', columns='Hour', values='Bookings')
        heatmap_pivot = heatmap_pivot.reindex(day_order)
        
        fig_heat = px.imshow(
            heatmap_pivot,
            labels=dict(x="Hour of Day", y="Day of Week", color="Bookings"),
            x=heatmap_pivot.columns,
            y=heatmap_pivot.index,
            aspect="auto",
            color_continuous_scale="Blues",
            text_auto=True
        )
        
        fig_heat.update_layout(
            height=450,
            xaxis_title="Hour of Day (24h)",
            yaxis_title=""
        )
        
        fig_heat.update_traces(textfont_size=9)
        
        st.plotly_chart(fig_heat, use_container_width=True)
        
        # Hourly profile
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("### ⏰ Hourly Demand Profile")
            hourly_profile = filtered_df.groupby('Hour').size().reset_index(name='Bookings')
            
            fig_profile = px.area(
                hourly_profile,
                x='Hour',
                y='Bookings',
                line_shape='spline',
                color_discrete_sequence=['#6c757d']
            )
            
            fig_profile.update_layout(
                template="plotly_white",
                height=300,
                xaxis_title="Hour of Day",
                yaxis_title="Average Bookings"
            )
            
            st.plotly_chart(fig_profile, use_container_width=True)
        
        with col2:
            st.markdown("### 📅 Weekday vs Weekend")
            weekend_data = filtered_df.groupby('is_weekend').agg({
                'Booking ID': 'count',
                'Booking Value': 'sum'
            }).reset_index()
            weekend_data['Day Type'] = weekend_data['is_weekend'].map({True: 'Weekend', False: 'Weekday'})
            
            fig_weekend = px.pie(
                weekend_data,
                values='Booking ID',
                names='Day Type',
                color_discrete_sequence=['#495057', '#adb5bd']
            )
            
            fig_weekend.update_layout(
                height=300,
                showlegend=True
            )
            
            fig_weekend.update_traces(textposition='inside', textinfo='percent+label')
            
            st.plotly_chart(fig_weekend, use_container_width=True)
    
    # --- Tab 3: Cancellation Analysis ---
    with tab3:
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("### ❌ Top Cancellation Reasons")
            cancel_df = filtered_df[filtered_df['Booking Status'].str.contains('Cancel', case=False, na=False)]
            
            # Combine cancellation reasons
            all_reasons = pd.concat([
                cancel_df['Reason for cancelling by Customer'].dropna(),
                cancel_df['Driver Cancellation Reason'].dropna()
            ])
            
            reasons = all_reasons.value_counts().head(8)
            
            fig_pareto = go.Figure(go.Bar(
                x=reasons.values,
                y=reasons.index,
                orientation='h',
                marker_color='#dc3545',
                text=reasons.values,
                textposition='outside'
            ))
            
            fig_pareto.update_layout(
                template="plotly_white",
                height=400,
                xaxis_title="Number of Cancellations",
                yaxis_title="",
                showlegend=False
            )
            
            st.plotly_chart(fig_pareto, use_container_width=True)
        
        with col2:
            st.markdown("### 📏 Trip Distance Distribution")
            
            fig_dist = px.histogram(
                filtered_df,
                x="Ride Distance",
                nbins=50,
                color_discrete_sequence=['#0d6efd'],
                marginal="box"
            )
            
            fig_dist.update_layout(
                template="plotly_white",
                height=400,
                xaxis_title="Distance (km)",
                yaxis_title="Frequency",
                bargap=0.05,
                showlegend=False
            )
            
            st.plotly_chart(fig_dist, use_container_width=True)
        
        # Cancellation rate by vehicle type
        st.markdown("### 🚗 Cancellation Rate by Vehicle Type")
        
        cancel_by_vehicle = filtered_df.groupby('Vehicle Type').agg(
            Total=('Booking ID', 'count'),
            Cancelled=('Booking Status', lambda x: (x.str.contains('Cancel', case=False, na=False)).sum())
        ).reset_index()
        
        cancel_by_vehicle['Cancellation Rate (%)'] = (
            cancel_by_vehicle['Cancelled'] / cancel_by_vehicle['Total'] * 100
        )
        
        fig_cancel_rate = px.bar(
            cancel_by_vehicle.sort_values('Cancellation Rate (%)', ascending=True),
            x='Cancellation Rate (%)',
            y='Vehicle Type',
            orientation='h',
            text_auto='.1f',
            color_discrete_sequence=['#fd7e14']
        )
        
        fig_cancel_rate.update_layout(
            template="plotly_white",
            height=300,
            xaxis_title="Cancellation Rate (%)",
            yaxis_title=""
        )
        
        fig_cancel_rate.update_traces(textposition='outside')
        
        st.plotly_chart(fig_cancel_rate, use_container_width=True)
    
    # --- Footer ---
    st.markdown("---")
    st.markdown(
        """
        <div style='text-align: center; color: #6c757d; padding: 1rem;'>
            <p>🚗 <strong>Uber Technologies Inc.</strong> | Data Analytics Division</p>
            <p style='font-size: 0.85rem;'>Built with Streamlit • Last updated: {}</p>
        </div>
        """.format(datetime.now().strftime("%B %d, %Y")),
        unsafe_allow_html=True
    )

else:
    # Error state
    st.title("🚗 Uber NCR Operational Analytics")
    st.error("⚠️ Unable to load data. Please check the configuration.")
    st.info("💡 Update the file path in the `load_data()` function to point to your CSV file.")