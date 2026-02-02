# Uber NCR Operational Analytics Dashboard

A professional, data-science focused dashboard for analyzing Uber operational metrics in the NCR (National Capital Region). Built with [Streamlit](https://streamlit.io/) and [Plotly](https://plotly.com/), this application provides deep insights into revenue, demand patterns, and cancellation friction points.

## 📊 Features

- **Executive Summary Details**: Real-time KPIs for Total Revenue, Bookings, Completion Rate, and Average Arrival Times.
- **Demand & Revenue Analysis**: 
  - Smoothed 7-day rolling average trends.
  - Revenue mix breakdown by vehicle type (Auto, Moto, Prime, etc.).
- **Operational Heatmaps**:
  - Temporal demand patterns (Day of Week vs. Hour of Day).
  - Hourly demand profiling to identify peak operational windows.
- **Cancellation Intelligence**:
  - Pareto analysis of cancellation reasons (Driver vs. Customer).
  - Distribution of trip lengths.
- **Interactive Filtering**: Filter data by date range, vehicle segments, and booking status.

## 🛠️ Installation

1.  **Clone the repository** (or download usage files):
    ```bash
    git clone <repository-url>
    cd <repository-directory>
    ```

2.  **Create a Virtual Environment** (Recommended):
    ```bash
    python -m venv venv
    # Windows
    venv\Scripts\activate
    # macOS/Linux
    source venv/bin/activate
    ```

3.  **Install Dependencies**:
    ```bash
    pip install -r requirements.txt
    ```

## 🚀 Usage

1.  **Place the Dataset**:
    Ensure the `ncr_ride_bookings.csv` file is located in the root directory. 
    > **Note**: This file is excluded from version control (`.gitignore`) due to size/confidentiality. You must obtain this file separately.

2.  **Run the Dashboard**:
    ```bash
    streamlit run uber_dashboard.py
    ```

3.  **Explore**:
    Open your browser to the local URL provided (usually `http://localhost:8501`).

## 📁 Project Structure

```
├── uber_dashboard.py       # Main application entry point
├── requirements.txt        # Python dependencies
├── .gitignore             # Git exclusion rules
├── README.md              # Project documentation
└── ncr_ride_bookings.csv  # Data file (not in repo)
```

## 📦 Dependencies

- **Streamlit**: For the interactive web application framework.
- **Pandas**: For robust data manipulation and analysis.
- **Plotly**: For interactive, publication-quality visualizations.

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.
