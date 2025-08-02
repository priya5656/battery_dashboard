import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import random
import time
import datetime
from io import StringIO
import numpy as np

# Page configuration
st.set_page_config(
    page_title="Battery Cell Monitoring Dashboard",
    page_icon="🔋",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for better styling
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        font-weight: bold;
        text-align: center;
        color: #2E86C1;
        margin-bottom: 2rem;
    }
    .metric-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 1rem;
        border-radius: 10px;
        color: white;
        text-align: center;
        margin: 0.5rem;
    }
    .status-good {
        background-color: #27AE60;
        color: white;
        padding: 0.3rem 0.8rem;
        border-radius: 15px;
        font-weight: bold;
    }
    .status-warning {
        background-color: #F39C12;
        color: white;
        padding: 0.3rem 0.8rem;
        border-radius: 15px;
        font-weight: bold;
    }
    .status-critical {
        background-color: #E74C3C;
        color: white;
        padding: 0.3rem 0.8rem;
        border-radius: 15px;
        font-weight: bold;
    }
    .sidebar .sidebar-content {
        background: linear-gradient(180deg, #2C3E50 0%, #34495E 100%);
    }
</style>
""", unsafe_allow_html=True)

# Initialize session state
if 'cells_data' not in st.session_state:
    st.session_state.cells_data = {}
if 'historical_data' not in st.session_state:
    st.session_state.historical_data = []
if 'bench_name' not in st.session_state:
    st.session_state.bench_name = ""
if 'group_num' not in st.session_state:
    st.session_state.group_num = 1

# Cell type configurations
CELL_CONFIGS = {
    "lfp": {
        "nominal_voltage": 3.2,
        "min_voltage": 2.8,
        "max_voltage": 3.6,
        "color": "#27AE60"
    },
    "nmc": {
        "nominal_voltage": 3.6,
        "min_voltage": 3.2,
        "max_voltage": 4.0,
        "color": "#3498DB"
    }
}

def get_cell_status(cell_data):
    """Determine cell status based on voltage and temperature"""
    voltage = cell_data['voltage']
    temp = cell_data['temp']
    min_v = cell_data['min_voltage']
    max_v = cell_data['max_voltage']
    
    if temp > 45 or voltage < min_v * 0.9 or voltage > max_v * 1.05:
        return "Critical"
    elif temp > 40 or voltage < min_v or voltage > max_v:
        return "Warning"
    else:
        return "Good"

def create_gauge_chart(value, title, min_val, max_val, color_ranges):
    """Create a gauge chart for metrics"""
    fig = go.Figure(go.Indicator(
        mode = "gauge+number+delta",
        value = value,
        domain = {'x': [0, 1], 'y': [0, 1]},
        title = {'text': title, 'font': {'size': 16}},
        gauge = {
            'axis': {'range': [None, max_val]},
            'bar': {'color': "darkblue"},
            'steps': color_ranges,
            'threshold': {
                'line': {'color': "red", 'width': 4},
                'thickness': 0.75,
                'value': max_val * 0.9
            }
        }
    ))
    fig.update_layout(height=250, margin={'l': 20, 'r': 20, 't': 40, 'b': 20})
    return fig

# Sidebar - Configuration Panel
st.sidebar.markdown("## ⚙️ Configuration Panel")

# Bench Configuration
with st.sidebar.expander("🏭 Bench Setup", expanded=True):
    bench_name = st.text_input("Bench Name", value=st.session_state.bench_name, key="bench_input")
    group_num = st.number_input("Group Number", min_value=1, max_value=100, value=st.session_state.group_num, key="group_input")
    
    if st.button("Update Bench Info"):
        st.session_state.bench_name = bench_name
        st.session_state.group_num = group_num
        st.success("Bench information updated!")

# Cell Configuration
with st.sidebar.expander("🔋 Cell Configuration", expanded=True):
    num_cells = st.slider("Number of Cells", min_value=1, max_value=16, value=8)
    
    if st.button("Initialize Cells"):
        st.session_state.cells_data = {}
        for i in range(1, num_cells + 1):
            cell_type = random.choice(["lfp", "nmc"])
            config = CELL_CONFIGS[cell_type]
            
            st.session_state.cells_data[f"cell_{i}"] = {
                "type": cell_type,
                "voltage": config["nominal_voltage"] + random.uniform(-0.1, 0.1),
                "current": random.uniform(0, 5),
                "temp": round(random.uniform(25, 40), 1),
                "min_voltage": config["min_voltage"],
                "max_voltage": config["max_voltage"],
                "capacity": 0,
                "cycle_count": random.randint(0, 1000),
                "health": random.uniform(80, 100)
            }
        
        # Calculate capacity
        for cell_id in st.session_state.cells_data:
            cell = st.session_state.cells_data[cell_id]
            cell["capacity"] = round(cell["voltage"] * cell["current"], 2)
        
        st.success(f"Initialized {num_cells} cells!")

# Control Panel
with st.sidebar.expander("🎛️ Control Panel", expanded=True):
    if st.button("🔄 Simulate Real-time Update"):
        for cell_id in st.session_state.cells_data:
            cell = st.session_state.cells_data[cell_id]
            # Simulate small variations
            cell["voltage"] += random.uniform(-0.05, 0.05)
            cell["current"] += random.uniform(-0.2, 0.2)
            cell["temp"] += random.uniform(-1, 1)
            cell["capacity"] = round(cell["voltage"] * cell["current"], 2)
            
            # Keep values within realistic bounds
            cell["voltage"] = max(cell["min_voltage"], min(cell["max_voltage"], cell["voltage"]))
            cell["current"] = max(0, cell["current"])
            cell["temp"] = max(20, min(50, cell["temp"]))
        
        # Add to historical data
        timestamp = datetime.datetime.now()
        for cell_id, cell_data in st.session_state.cells_data.items():
            st.session_state.historical_data.append({
                "timestamp": timestamp,
                "cell_id": cell_id,
                **cell_data
            })
        
        st.success("Data updated!")
    
    if st.button("🚨 Emergency Stop"):
        for cell_id in st.session_state.cells_data:
            st.session_state.cells_data[cell_id]["current"] = 0
        st.warning("Emergency stop activated - All currents set to 0")
    
    if st.button("🔄 Reset All Data"):
        st.session_state.cells_data = {}
        st.session_state.historical_data = []
        st.info("All data reset!")

# Data Export
with st.sidebar.expander("📊 Data Export", expanded=True):
    if st.session_state.cells_data:
        # Current data CSV
        df_current = pd.DataFrame.from_dict(st.session_state.cells_data, orient='index')
        df_current.index.name = 'cell_id'
        
        csv_current = df_current.to_csv()
        st.download_button(
            label="📥 Download Current Data (CSV)",
            data=csv_current,
            file_name=f"battery_data_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
            mime="text/csv"
        )
        
        # Historical data CSV
        if st.session_state.historical_data:
            df_historical = pd.DataFrame(st.session_state.historical_data)
            csv_historical = df_historical.to_csv(index=False)
            st.download_button(
                label="📈 Download Historical Data (CSV)",
                data=csv_historical,
                file_name=f"battery_historical_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                mime="text/csv"
            )

# Main Dashboard
st.markdown('<div class="main-header">🔋 Battery Cell Monitoring Dashboard</div>', unsafe_allow_html=True)

if st.session_state.bench_name:
    st.markdown(f"**Bench:** {st.session_state.bench_name} | **Group:** {st.session_state.group_num}")

if not st.session_state.cells_data:
    st.info("👈 Please configure and initialize cells using the sidebar panel.")
    st.stop()

# Overview Metrics
col1, col2, col3, col4 = st.columns(4)

total_cells = len(st.session_state.cells_data)
avg_voltage = sum(cell["voltage"] for cell in st.session_state.cells_data.values()) / total_cells
avg_temp = sum(cell["temp"] for cell in st.session_state.cells_data.values()) / total_cells
total_power = sum(cell["capacity"] for cell in st.session_state.cells_data.values())

with col1:
    st.metric("Total Cells", total_cells, delta=None)

with col2:
    st.metric("Avg Voltage", f"{avg_voltage:.2f}V", delta=f"{random.uniform(-0.1, 0.1):.2f}V")

with col3:
    st.metric("Avg Temperature", f"{avg_temp:.1f}°C", delta=f"{random.uniform(-1, 1):.1f}°C")

with col4:
    st.metric("Total Power", f"{total_power:.2f}W", delta=f"{random.uniform(-1, 1):.1f}W")

# Tabs for different views
tab1, tab2, tab3, tab4 = st.tabs(["📊 Real-time Dashboard", "📈 Data Analysis", "🔧 Cell Management", "📋 Reports"])

with tab1:
    # Real-time Dashboard
    col1, col2 = st.columns([2, 1])
    
    with col1:
        # Cell Status Grid
        st.subheader("Cell Status Overview")
        
        # Create grid layout for cells
        cells_per_row = 4
        rows = (len(st.session_state.cells_data) + cells_per_row - 1) // cells_per_row
        
        for row in range(rows):
            cols = st.columns(cells_per_row)
            for col_idx in range(cells_per_row):
                cell_idx = row * cells_per_row + col_idx
                if cell_idx < len(st.session_state.cells_data):
                    cell_id = list(st.session_state.cells_data.keys())[cell_idx]
                    cell_data = st.session_state.cells_data[cell_id]
                    status = get_cell_status(cell_data)
                    
                    with cols[col_idx]:
                        status_class = f"status-{status.lower()}" if status != "Good" else "status-good"
                        st.markdown(f"""
                        <div style="border: 2px solid {'#27AE60' if status=='Good' else '#F39C12' if status=='Warning' else '#E74C3C'}; 
                                    border-radius: 10px; padding: 10px; margin: 5px;">
                            <h4>{cell_id.replace('_', ' ').title()}</h4>
                            <p><span class="{status_class}">{status}</span></p>
                            <p><strong>Type:</strong> {cell_data['type'].upper()}</p>
                            <p><strong>Voltage:</strong> {cell_data['voltage']:.2f}V</p>
                            <p><strong>Current:</strong> {cell_data['current']:.2f}A</p>
                            <p><strong>Temp:</strong> {cell_data['temp']:.1f}°C</p>
                            <p><strong>Power:</strong> {cell_data['capacity']:.2f}W</p>
                        </div>
                        """, unsafe_allow_html=True)
    
    with col2:
        st.subheader("System Health")
        
        # Status distribution
        status_counts = {"Good": 0, "Warning": 0, "Critical": 0}
        for cell_data in st.session_state.cells_data.values():
            status = get_cell_status(cell_data)
            status_counts[status] += 1
        
        fig_status = px.pie(
            values=list(status_counts.values()),
            names=list(status_counts.keys()),
            title="Cell Status Distribution",
            color_discrete_map={"Good": "#27AE60", "Warning": "#F39C12", "Critical": "#E74C3C"}
        )
        st.plotly_chart(fig_status, use_container_width=True)
        
        # Health gauge
        avg_health = sum(cell["health"] for cell in st.session_state.cells_data.values()) / total_cells
        
        gauge_fig = create_gauge_chart(
            avg_health, 
            "System Health (%)", 
            0, 
            100,
            [
                {'range': [0, 60], 'color': "#E74C3C"},
                {'range': [60, 80], 'color': "#F39C12"},
                {'range': [80, 100], 'color': "#27AE60"}
            ]
        )
        st.plotly_chart(gauge_fig, use_container_width=True)

with tab2:
    # Data Analysis
    st.subheader("📈 Performance Analysis")
    
    if st.session_state.historical_data:
        df_hist = pd.DataFrame(st.session_state.historical_data)
        
        # Time series plots
        col1, col2 = st.columns(2)
        
        with col1:
            fig_voltage = px.line(
                df_hist, 
                x='timestamp', 
                y='voltage', 
                color='cell_id',
                title='Voltage Over Time'
            )
            st.plotly_chart(fig_voltage, use_container_width=True)
        
        with col2:
            fig_temp = px.line(
                df_hist, 
                x='timestamp', 
                y='temp', 
                color='cell_id',
                title='Temperature Over Time'
            )
            st.plotly_chart(fig_temp, use_container_width=True)
        
        # Correlation analysis
        st.subheader("Correlation Analysis")
        numeric_cols = ['voltage', 'current', 'temp', 'capacity', 'health']
        corr_matrix = df_hist[numeric_cols].corr()
        
        fig_corr = px.imshow(
            corr_matrix,
            text_auto=True,
            aspect="auto",
            title="Parameter Correlation Matrix"
        )
        st.plotly_chart(fig_corr, use_container_width=True)
        
    else:
        st.info("No historical data available. Use 'Simulate Real-time Update' to generate data.")

with tab3:
    # Cell Management
    st.subheader("🔧 Individual Cell Management")
    
    selected_cell = st.selectbox("Select Cell", list(st.session_state.cells_data.keys()))
    
    if selected_cell:
        cell_data = st.session_state.cells_data[selected_cell]
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.write("**Current Values**")
            st.write(f"Type: {cell_data['type'].upper()}")
            st.write(f"Voltage: {cell_data['voltage']:.2f}V")
            st.write(f"Current: {cell_data['current']:.2f}A")
            st.write(f"Temperature: {cell_data['temp']:.1f}°C")
            st.write(f"Capacity: {cell_data['capacity']:.2f}W")
            st.write(f"Health: {cell_data['health']:.1f}%")
            st.write(f"Cycles: {cell_data['cycle_count']}")
        
        with col2:
            st.write("**Manual Controls**")
            new_current = st.number_input(
                "Set Current (A)", 
                min_value=0.0, 
                max_value=10.0, 
                value=cell_data['current'], 
                step=0.1,
                key=f"current_{selected_cell}"
            )
            
            if st.button("Update Current", key=f"update_{selected_cell}"):
                st.session_state.cells_data[selected_cell]['current'] = new_current
                st.session_state.cells_data[selected_cell]['capacity'] = round(
                    cell_data['voltage'] * new_current, 2
                )
                st.success(f"Current updated for {selected_cell}")
                st.rerun()
        
        with col3:
            st.write("**Cell Diagnostics**")
            status = get_cell_status(cell_data)
            st.write(f"Status: {status}")
            
            # Performance metrics
            voltage_efficiency = (cell_data['voltage'] / cell_data['max_voltage']) * 100
            temp_status = "Normal" if cell_data['temp'] < 40 else "High"
            
            st.write(f"Voltage Efficiency: {voltage_efficiency:.1f}%")
            st.write(f"Temperature Status: {temp_status}")

with tab4:
    # Reports
    st.subheader("📋 System Reports")
    
    if st.session_state.cells_data:
        # Summary report
        df = pd.DataFrame.from_dict(st.session_state.cells_data, orient='index')
        
        st.write("### Summary Statistics")
        st.dataframe(df.describe(), use_container_width=True)
        
        # Performance ranking
        st.write("### Cell Performance Ranking")
        df_ranking = df.copy()
        df_ranking['performance_score'] = (
            df_ranking['health'] * 0.4 + 
            (df_ranking['voltage'] / df_ranking['max_voltage']) * 30 +
            (100 - (df_ranking['temp'] - 25) * 2).clip(0, 30) * 0.3
        )
        df_ranking = df_ranking.sort_values('performance_score', ascending=False)
        
        st.dataframe(
            df_ranking[['type', 'voltage', 'current', 'temp', 'health', 'performance_score']],
            use_container_width=True
        )
        
        # Alerts and recommendations
        st.write("### System Alerts & Recommendations")
        
        alerts = []
        for cell_id, cell_data in st.session_state.cells_data.items():
            if cell_data['temp'] > 45:
                alerts.append(f"🚨 {cell_id}: Critical temperature ({cell_data['temp']:.1f}°C)")
            elif cell_data['temp'] > 40:
                alerts.append(f"⚠️ {cell_id}: High temperature ({cell_data['temp']:.1f}°C)")
            
            if cell_data['health'] < 70:
                alerts.append(f"🔋 {cell_id}: Low health ({cell_data['health']:.1f}%)")
            
            if cell_data['voltage'] < cell_data['min_voltage']:
                alerts.append(f"⚡ {cell_id}: Low voltage ({cell_data['voltage']:.2f}V)")
        
        if alerts:
            for alert in alerts:
                st.warning(alert)
        else:
            st.success("✅ All systems operating normally")

# Auto-refresh option
if st.sidebar.checkbox("🔄 Auto-refresh (every 5 seconds)"):
    time.sleep(5)
    st.rerun()

# Footer
st.markdown("---")
st.markdown("**Battery Cell Monitoring Dashboard** | Built with Streamlit & Plotly")