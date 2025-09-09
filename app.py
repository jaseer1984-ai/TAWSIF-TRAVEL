import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, date, timedelta
import numpy as np
from plotly.subplots import make_subplots
import io

# Page configuration
st.set_page_config(
    page_title="Tawsif Travel & Tourism Dashboard",
    page_icon="✈️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for better styling
st.markdown("""
<style>
    .main-header {
        background: linear-gradient(90deg, #1e3c72 0%, #2a5298 100%);
        padding: 20px;
        border-radius: 10px;
        margin-bottom: 30px;
        color: white;
        text-align: center;
    }
    
    .metric-card {
        background: white;
        padding: 20px;
        border-radius: 10px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        border-left: 4px solid #2a5298;
        margin-bottom: 20px;
    }
    
    .upload-section {
        background: #f8f9fa;
        padding: 20px;
        border-radius: 10px;
        margin-bottom: 20px;
        border: 2px dashed #2a5298;
    }
    
    .sidebar .sidebar-content {
        background: linear-gradient(180deg, #f8f9fa 0%, #e9ecef 100%);
    }
    
    .stSelectbox > div > div {
        background-color: #f8f9fa;
    }
    
    .success-message {
        background: #d4edda;
        border: 1px solid #c3e6cb;
        border-radius: 5px;
        padding: 10px;
        margin: 10px 0;
        color: #155724;
    }
    
    .error-message {
        background: #f8d7da;
        border: 1px solid #f5c6cb;
        border-radius: 5px;
        padding: 10px;
        margin: 10px 0;
        color: #721c24;
    }
</style>
""", unsafe_allow_html=True)

# Header
st.markdown("""
<div class="main-header">
    <h1>✈️ Tawsif Travel & Tourism Company</h1>
    <h3>Business Intelligence Dashboard</h3>
</div>
""", unsafe_allow_html=True)

# Data loading functions
@st.cache_data
def load_excel_data(uploaded_file):
    """Load data from uploaded Excel file"""
    try:
        # Read Excel file with all sheets
        excel_data = pd.read_excel(uploaded_file, sheet_name=None)
        
        # Expected sheet names mapping
        sheet_mapping = {
            'Daily_Summary': ['Daily_Summary', 'Daily Summary', 'daily_summary', 'Summary'],
            'Tickets_By_Airline': ['Tickets_By_Airline', 'Tickets By Airline', 'tickets_by_airline', 'Tickets'],
            'Airline_Sales': ['Airline_Sales', 'Airline Sales', 'airline_sales', 'Sales'],
            'Staff_Sales': ['Staff_Sales', 'Staff Sales', 'staff_sales', 'Staff'],
            'Bank_Balances': ['Bank_Balances', 'Bank Balances', 'bank_balances', 'Banks']
        }
        
        # Find and map sheets
        mapped_data = {}
        available_sheets = list(excel_data.keys())
        
        for expected_name, possible_names in sheet_mapping.items():
            found_sheet = None
            for possible_name in possible_names:
                if possible_name in available_sheets:
                    found_sheet = possible_name
                    break
            
            if found_sheet:
                df = excel_data[found_sheet].copy()
                # Clean column names
                df.columns = df.columns.str.strip()
                # Convert Date columns
                if 'Date' in df.columns:
                    df['Date'] = pd.to_datetime(df['Date'], errors='coerce')
                mapped_data[expected_name] = df
        
        return mapped_data, available_sheets
        
    except Exception as e:
        st.error(f"Error reading Excel file: {str(e)}")
        return None, []

def validate_data_structure(data_dict):
    """Validate the structure of uploaded data"""
    validation_results = []
    is_valid = True
    
    # Required structure for each sheet
    required_structure = {
        'Daily_Summary': ['Date', 'Daily Sales', 'Cash Balance', 'Bank Balance'],
        'Tickets_By_Airline': ['Date', 'Branch', 'Airline', 'Tickets Issued'],
        'Airline_Sales': ['Date', 'Branch', 'Airline', 'Sales'],
        'Staff_Sales': ['Date', 'Branch', 'Staff', 'Tickets Issued', 'Sales'],
        'Bank_Balances': ['Date', 'Branch', 'Bank', 'Balance']
    }
    
    # Alternative column names that should be accepted
    column_alternatives = {
        'Daily Sales': ['Daily_Sales', 'daily_sales', 'Sales', 'Total Sales'],
        'Cash Balance': ['Cash_Balance', 'cash_balance', 'Cash'],
        'Bank Balance': ['Bank_Balance', 'bank_balance', 'Bank'],
        'Tickets Issued': ['Tickets_Issued', 'tickets_issued', 'Tickets'],
        'Balance': ['balance', 'Amount', 'amount']
    }
    
    for sheet_name, required_cols in required_structure.items():
        if sheet_name not in data_dict:
            validation_results.append(f"❌ Missing sheet: {sheet_name}")
            is_valid = False
            continue
            
        df = data_dict[sheet_name]
        if df.empty:
            validation_results.append(f"⚠️ Sheet '{sheet_name}' is empty")
            is_valid = False
            continue
            
        # Check columns with alternatives
        df_columns = [col.strip() for col in df.columns]
        missing_cols = []
        
        for req_col in required_cols:
            found = False
            # Check exact match first
            if req_col in df_columns:
                found = True
            else:
                # Check alternatives
                alternatives = column_alternatives.get(req_col, [req_col])
                for alt in alternatives:
                    if alt in df_columns:
                        found = True
                        break
            
            if not found:
                missing_cols.append(req_col)
        
        if missing_cols:
            validation_results.append(f"❌ Sheet '{sheet_name}' missing columns: {missing_cols}")
            validation_results.append(f"   Available columns: {df_columns}")
            is_valid = False
        else:
            validation_results.append(f"✅ Sheet '{sheet_name}': {len(df)} records")
    
    return is_valid, validation_results

def normalize_column_names(data_dict):
    """Normalize column names to match expected format"""
    column_mapping = {
        'Daily_Summary': {
            'Daily_Sales': 'Daily Sales',
            'daily_sales': 'Daily Sales',
            'Sales': 'Daily Sales',
            'Total Sales': 'Daily Sales',
            'Cash_Balance': 'Cash Balance',
            'cash_balance': 'Cash Balance',
            'Cash': 'Cash Balance',
            'Bank_Balance': 'Bank Balance',
            'bank_balance': 'Bank Balance',
            'Bank': 'Bank Balance'
        },
        'Tickets_By_Airline': {
            'Tickets_Issued': 'Tickets Issued',
            'tickets_issued': 'Tickets Issued',
            'Tickets': 'Tickets Issued'
        },
        'Staff_Sales': {
            'Tickets_Issued': 'Tickets Issued',
            'tickets_issued': 'Tickets Issued',
            'Tickets': 'Tickets Issued'
        },
        'Bank_Balances': {
            'balance': 'Balance',
            'Amount': 'Balance',
            'amount': 'Balance'
        }
    }
    
    normalized_data = {}
    for sheet_name, df in data_dict.items():
        df_copy = df.copy()
        if sheet_name in column_mapping:
            df_copy = df_copy.rename(columns=column_mapping[sheet_name])
        normalized_data[sheet_name] = df_copy
    
    return normalized_data

# File upload section
st.markdown("""
<div class="upload-section">
    <h3>📁 Upload Your Travel Agency Data</h3>
    <p>Please upload an Excel file (.xlsx) containing your travel agency data with the following sheets:</p>
    <ul>
        <li><strong>Daily_Summary</strong>: Date, Daily Sales, Cash Balance, Bank Balance</li>
        <li><strong>Tickets_By_Airline</strong>: Date, Branch, Airline, Tickets Issued</li>
        <li><strong>Airline_Sales</strong>: Date, Branch, Airline, Sales</li>
        <li><strong>Staff_Sales</strong>: Date, Branch, Staff, Tickets Issued, Sales</li>
        <li><strong>Bank_Balances</strong>: Date, Branch, Bank, Balance</li>
    </ul>
</div>
""", unsafe_allow_html=True)

# File uploader
uploaded_file = st.file_uploader(
    "Choose an Excel file",
    type=['xlsx', 'xls'],
    help="Upload your travel agency data Excel file. Make sure it contains all required sheets."
)

# Initialize session state for data
if 'data_loaded' not in st.session_state:
    st.session_state.data_loaded = False
    st.session_state.data_dict = {}

# Process uploaded file
if uploaded_file is not None:
    with st.spinner("📊 Processing your data..."):
        data_dict, available_sheets = load_excel_data(uploaded_file)
        
        if data_dict:
            # Validate data structure
            is_valid, validation_results = validate_data_structure(data_dict)
            
            # Display validation results
            st.subheader("📋 Data Validation Results")
            for result in validation_results:
                if result.startswith("✅"):
                    st.markdown(f'<div class="success-message">{result}</div>', unsafe_allow_html=True)
                elif result.startswith("❌"):
                    st.markdown(f'<div class="error-message">{result}</div>', unsafe_allow_html=True)
                else:
                    st.info(result)
            
            if is_valid:
                # Normalize column names
                normalized_data = normalize_column_names(data_dict)
                st.session_state.data_dict = normalized_data
                st.session_state.data_loaded = True
                st.success("🎉 Data loaded successfully! You can now view your dashboard below.")
            else:
                st.error("❌ Data validation failed. Please check your Excel file structure and try again.")
                st.info("💡 **Tip**: Download the sample template from the sidebar to see the expected format.")
        else:
            st.error("❌ Failed to load data from the Excel file. Please check the file format and try again.")

# Download sample template
st.sidebar.header("📥 Download Sample Template")
if st.sidebar.button("📄 Download Excel Template"):
    # Create sample template
    sample_data = {
        'Daily_Summary': pd.DataFrame({
            'Date': [date.today()],
            'Daily Sales': [150000],
            'Cash Balance': [35000],
            'Bank Balance': [115000]
        }),
        'Tickets_By_Airline': pd.DataFrame({
            'Date': [date.today()] * 4,
            'Branch': ['Main'] * 4,
            'Airline': ['Saudi Airlines', 'Emirates', 'Qatar Airways', 'Etihad'],
            'Tickets Issued': [40, 30, 20, 15]
        }),
        'Airline_Sales': pd.DataFrame({
            'Date': [date.today()] * 4,
            'Branch': ['Main'] * 4,
            'Airline': ['Saudi Airlines', 'Emirates', 'Qatar Airways', 'Etihad'],
            'Sales': [50000, 40000, 30000, 20000]
        }),
        'Staff_Sales': pd.DataFrame({
            'Date': [date.today()] * 4,
            'Branch': ['Main'] * 4,
            'Staff': ['Ali', 'Sara', 'Ahmed', 'Lina'],
            'Tickets Issued': [20, 30, 25, 25],
            'Sales': [25000, 35000, 30000, 30000]
        }),
        'Bank_Balances': pd.DataFrame({
            'Date': [date.today()] * 2,
            'Branch': ['Main'] * 2,
            'Bank': ['SNB', 'Al Rajhi'],
            'Balance': [55000, 30000]
        })
    }
    
    # Create Excel file in memory
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        for sheet_name, df in sample_data.items():
            df.to_excel(writer, sheet_name=sheet_name, index=False)
    
    st.sidebar.download_button(
        label="⬇️ Download Template",
        data=output.getvalue(),
        file_name="tawsif_travel_template.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )

# Only show dashboard if data is loaded
if st.session_state.data_loaded and st.session_state.data_dict:
    data_dict = st.session_state.data_dict
    
    # Sidebar filters
    st.sidebar.header("📊 Dashboard Filters")
    
    # --------- SAFE DATE PICKER (single date vs range) ----------
    all_dates = []
    for df in data_dict.values():
        if 'Date' in df.columns:
            dcol = pd.to_datetime(df['Date'], errors='coerce').dropna()
            all_dates.extend([d.date() for d in dcol.tolist()])

    if all_dates:
        min_date = min(all_dates)
        max_date = max(all_dates)

        default_start = max(min_date, max_date - timedelta(days=30))

        if min_date == max_date:
            sel = st.sidebar.date_input(
                "Select Date",
                value=max_date,
                min_value=min_date,
                max_value=max_date,
                key="single_date"
            )
        else:
            sel = st.sidebar.date_input(
                "Select Date Range",
                value=(default_start, max_date),
                min_value=min_date,
                max_value=max_date,
                key="range_date"
            )

        if isinstance(sel, tuple) and len(sel) == 2:
            start_date, end_date = sel
        else:
            start_date = end_date = sel
    else:
        # No valid dates found → fall back to last 30 days ending today
        end_date = date.today()
        start_date = end_date - timedelta(days=30)
    # -----------------------------------------------------------

    # Branch filter
    branches = ['All']
    if 'Tickets_By_Airline' in data_dict and 'Branch' in data_dict['Tickets_By_Airline'].columns:
        branches.extend(list(data_dict['Tickets_By_Airline']['Branch'].dropna().unique()))
    selected_branch = st.sidebar.selectbox("Select Branch", branches)

    # Filter data based on selections
    filtered_data = {}
    for sheet_name, df in data_dict.items():
        filtered_df = df.copy()

        if 'Date' in filtered_df.columns:
            filtered_df['Date'] = pd.to_datetime(filtered_df['Date'], errors='coerce')
            mask = (filtered_df['Date'] >= pd.Timestamp(start_date)) & (filtered_df['Date'] <= pd.Timestamp(end_date))
            filtered_df = filtered_df.loc[mask]

        # Apply branch filter
        if selected_branch != 'All' and 'Branch' in filtered_df.columns:
            filtered_df = filtered_df[filtered_df['Branch'] == selected_branch]

        filtered_data[sheet_name] = filtered_df
    
    # Main dashboard content
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        if 'Daily_Summary' in filtered_data and not filtered_data['Daily_Summary'].empty:
            total_sales = filtered_data['Daily_Summary']['Daily Sales'].sum()
            avg_daily = total_sales / len(filtered_data['Daily_Summary']) if len(filtered_data['Daily_Summary']) > 0 else 0
            st.metric(
                label="💰 Total Sales",
                value=f"SAR {total_sales:,.0f}",
                delta=f"{avg_daily:,.0f} avg/day"
            )
        else:
            st.metric("💰 Total Sales", "No data")
    
    with col2:
        if 'Tickets_By_Airline' in filtered_data and not filtered_data['Tickets_By_Airline'].empty:
            total_tickets = filtered_data['Tickets_By_Airline']['Tickets Issued'].sum()
            days_count = max((end_date - start_date).days + 1, 1)
            avg_daily_tickets = total_tickets / days_count
            st.metric(
                label="🎫 Total Tickets",
                value=f"{int(total_tickets):,}",
                delta=f"{avg_daily_tickets:,.0f} avg/day"
            )
        else:
            st.metric("🎫 Total Tickets", "No data")
    
    with col3:
        if 'Daily_Summary' in filtered_data and not filtered_data['Daily_Summary'].empty:
            avg_cash = filtered_data['Daily_Summary']['Cash Balance'].mean()
            st.metric(
                label="💵 Avg Cash Balance",
                value=f"SAR {avg_cash:,.0f}",
                delta="Daily Average"
            )
        else:
            st.metric("💵 Avg Cash Balance", "No data")
    
    with col4:
        if 'Bank_Balances' in filtered_data and not filtered_data['Bank_Balances'].empty:
            total_bank_balance = filtered_data['Bank_Balances']['Balance'].sum()
            st.metric(
                label="🏦 Total Bank Balance",
                value=f"SAR {total_bank_balance:,.0f}",
                delta="All Banks"
            )
        else:
            st.metric("🏦 Total Bank Balance", "No data")
    
    # Charts section
    st.markdown("---")
    
    # Row 1: Sales trends and airline performance
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("📈 Daily Sales Trend")
        if 'Daily_Summary' in filtered_data and not filtered_data['Daily_Summary'].empty:
            fig_sales = px.line(
                filtered_data['Daily_Summary'],
                x='Date', y='Daily Sales',
                title="Daily Sales Over Time",
                labels={'Daily Sales': 'Sales (SAR)', 'Date': 'Date'}
            )
            fig_sales.update_layout(showlegend=False)
            fig_sales.update_traces(line_color='#2a5298', line_width=3)
            st.plotly_chart(fig_sales, use_container_width=True)
        else:
            st.info("No daily sales data available")
    
    with col2:
        st.subheader("✈️ Airline Performance")
        if 'Airline_Sales' in filtered_data and not filtered_data['Airline_Sales'].empty:
            airline_summary = filtered_data['Airline_Sales'].groupby('Airline', dropna=True)['Sales'].sum().reset_index()
            fig_airline = px.bar(
                airline_summary, x='Airline', y='Sales',
                title="Sales by Airline",
                labels={'Sales': 'Total Sales (SAR)', 'Airline': 'Airline'},
                color='Sales',
                color_continuous_scale='Blues'
            )
            fig_airline.update_layout(showlegend=False, xaxis_tickangle=-45)
            st.plotly_chart(fig_airline, use_container_width=True)
        else:
            st.info("No airline sales data available")
    
    # Row 2: Staff performance and ticket distribution
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("👥 Top Performing Staff")
        if 'Staff_Sales' in filtered_data and not filtered_data['Staff_Sales'].empty:
            staff_summary = (
                filtered_data['Staff_Sales']
                .groupby('Staff', dropna=True)
                .agg({'Sales': 'sum', 'Tickets Issued': 'sum'})
                .reset_index()
                .sort_values('Sales', ascending=False)
                .head(8)
            )
            fig_staff = px.bar(
                staff_summary, x='Staff', y='Sales',
                title="Sales by Staff Member",
                labels={'Sales': 'Total Sales (SAR)', 'Staff': 'Staff Member'},
                color='Sales',
                color_continuous_scale='Greens'
            )
            fig_staff.update_layout(showlegend=False, xaxis_tickangle=-45)
            st.plotly_chart(fig_staff, use_container_width=True)
        else:
            st.info("No staff sales data available")
    
    with col2:
        st.subheader("🎯 Ticket Distribution by Airline")
        if 'Tickets_By_Airline' in filtered_data and not filtered_data['Tickets_By_Airline'].empty:
            ticket_summary = (
                filtered_data['Tickets_By_Airline']
                .groupby('Airline', dropna=True)['Tickets Issued']
                .sum()
                .reset_index()
            )
            fig_tickets = px.pie(
                ticket_summary, values='Tickets Issued', names='Airline',
                title="Ticket Distribution",
                color_discrete_sequence=px.colors.qualitative.Set3
            )
            st.plotly_chart(fig_tickets, use_container_width=True)
        else:
            st.info("No ticket data available")
    
    # Row 3: Financial overview
    st.subheader("💳 Financial Overview")
    col1, col2 = st.columns(2)
    
    with col1:
        st.write("**Cash vs Bank Balance Trend**")
        if 'Daily_Summary' in filtered_data and not filtered_data['Daily_Summary'].empty:
            fig_balance = make_subplots(specs=[[{"secondary_y": True}]])
            
            fig_balance.add_trace(
                go.Scatter(
                    x=filtered_data['Daily_Summary']['Date'], 
                    y=filtered_data['Daily_Summary']['Cash Balance'], 
                    name="Cash Balance", line=dict(color='green', width=2)
                ),
                secondary_y=False,
            )
            
            fig_balance.add_trace(
                go.Scatter(
                    x=filtered_data['Daily_Summary']['Date'], 
                    y=filtered_data['Daily_Summary']['Bank Balance'], 
                    name="Bank Balance", line=dict(color='blue', width=2)
                ),
                secondary_y=True,
            )
            
            fig_balance.update_xaxes(title_text="Date")
            fig_balance.update_yaxes(title_text="Cash Balance (SAR)", secondary_y=False)
            fig_balance.update_yaxes(title_text="Bank Balance (SAR)", secondary_y=True)
            fig_balance.update_layout(height=400, showlegend=True)
            
            st.plotly_chart(fig_balance, use_container_width=True)
        else:
            st.info("No financial balance data available")
    
    with col2:
        st.write("**Bank Balances Distribution**")
        if 'Bank_Balances' in filtered_data and not filtered_data['Bank_Balances'].empty:
            bank_summary = (
                filtered_data['Bank_Balances']
                .groupby('Bank', dropna=True)['Balance']
                .sum()
                .reset_index()
            )
            fig_banks = px.bar(
                bank_summary, x='Bank', y='Balance',
                title="Balance by Bank",
                labels={'Balance': 'Total Balance (SAR)', 'Bank': 'Bank'},
                color='Balance',
                color_continuous_scale='Oranges'
            )
            fig_banks.update_layout(showlegend=False)
            st.plotly_chart(fig_banks, use_container_width=True)
        else:
            st.info("No bank balance data available")
    
    # Data tables section
    st.markdown("---")
    st.subheader("📋 Detailed Data Tables")
    
    available_sheets = [name for name in ['Daily_Summary', 'Airline_Sales', 'Staff_Sales', 'Bank_Balances'] 
                       if name in filtered_data and not filtered_data[name].empty]
    
    if available_sheets:
        tabs = st.tabs([name.replace('_', ' ') for name in available_sheets])
        
        for i, sheet_name in enumerate(available_sheets):
            with tabs[i]:
                df_display = filtered_data[sheet_name].copy()
                
                # Format numeric columns
                numeric_cols = df_display.select_dtypes(include=[np.number]).columns
                format_dict = {}
                for col in numeric_cols:
                    if 'Sales' in col or 'Balance' in col:
                        # Show decimals where relevant? using 0 decimals here
                        format_dict[col] = 'SAR {:,.0f}'
                    elif 'Tickets' in col:
                        format_dict[col] = '{:,}'
                
                if format_dict:
                    st.dataframe(df_display.style.format(format_dict), use_container_width=True)
                else:
                    st.dataframe(df_display, use_container_width=True)
    else:
        st.info("No data tables available to display")
    
    # Footer
    st.markdown("---")
    st.markdown("""
    <div style='text-align: center; color: #666; padding: 20px;'>
        <p>© 2025 Tawsif Travel & Tourism Company - Business Intelligence Dashboard</p>
        <p>Last Updated: {} | Data Range: {} to {}</p>
    </div>
    """.format(
        datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        start_date.strftime("%Y-%m-%d"),
        end_date.strftime("%Y-%m-%d")
    ), unsafe_allow_html=True)

else:
    # Show instructions when no data is loaded
    st.markdown("""
    <div style='text-align: center; padding: 50px; color: #666;'>
        <h2>👆 Please upload your Excel file to get started</h2>
        <p>Upload your travel agency data file using the file uploader above to view your dashboard.</p>
        <p>Don't have a file? Download the sample template from the sidebar to see the expected format.</p>
    </div>
    """, unsafe_allow_html=True)
