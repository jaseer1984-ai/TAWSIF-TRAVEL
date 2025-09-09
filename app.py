import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, date, timedelta
import numpy as np
from plotly.subplots import make_subplots

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
    
    .sidebar .sidebar-content {
        background: linear-gradient(180deg, #f8f9fa 0%, #e9ecef 100%);
    }
    
    .stSelectbox > div > div {
        background-color: #f8f9fa;
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

# Initialize sample data (in production, this would come from your database)
@st.cache_data
def load_sample_data():
    # Generate sample data based on the Excel template structure
    dates = pd.date_range(start='2025-01-01', end='2025-09-09', freq='D')
    
    # Daily Summary Data
    daily_data = []
    for i, d in enumerate(dates):
        daily_sales = np.random.normal(150000, 30000)
        cash_balance = np.random.normal(35000, 10000)
        bank_balance = daily_sales - cash_balance
        daily_data.append({
            'Date': d,
            'Daily_Sales': max(0, daily_sales),
            'Cash_Balance': max(0, cash_balance),
            'Bank_Balance': max(0, bank_balance)
        })
    daily_df = pd.DataFrame(daily_data)
    
    # Airlines data
    airlines = ['Saudi Airlines', 'Emirates', 'Qatar Airways', 'Etihad', 'Flynas', 'Flyadeal']
    branches = ['Main', 'Branch A', 'Branch B']
    
    tickets_data = []
    sales_data = []
    
    for d in dates:
        for branch in branches:
            for airline in airlines:
                tickets = np.random.poisson(25)
                sales_amount = tickets * np.random.normal(1200, 200)
                
                tickets_data.append({
                    'Date': d,
                    'Branch': branch,
                    'Airline': airline,
                    'Tickets_Issued': tickets
                })
                
                sales_data.append({
                    'Date': d,
                    'Branch': branch,
                    'Airline': airline,
                    'Sales': max(0, sales_amount)
                })
    
    tickets_df = pd.DataFrame(tickets_data)
    airline_sales_df = pd.DataFrame(sales_data)
    
    # Staff data
    staff_names = ['Ali Ahmed', 'Sara Al-Mahmoud', 'Ahmed Ibrahim', 'Lina Hassan', 
                   'Omar Al-Rashid', 'Fatima Al-Zahra', 'Khalid Al-Mansour', 'Nora Al-Sabbagh']
    
    staff_data = []
    for d in dates:
        for branch in branches:
            branch_staff = np.random.choice(staff_names, size=np.random.randint(3, 6), replace=False)
            for staff in branch_staff:
                tickets = np.random.poisson(20)
                sales_amount = tickets * np.random.normal(1100, 150)
                
                staff_data.append({
                    'Date': d,
                    'Branch': branch,
                    'Staff': staff,
                    'Tickets_Issued': tickets,
                    'Sales': max(0, sales_amount)
                })
    
    staff_df = pd.DataFrame(staff_data)
    
    # Bank balances
    banks = ['SNB', 'Al Rajhi', 'SAMBA', 'NCB', 'SAIB']
    bank_data = []
    
    for d in dates:
        for branch in branches:
            for bank in banks:
                balance = np.random.normal(50000, 15000)
                bank_data.append({
                    'Date': d,
                    'Branch': branch,
                    'Bank': bank,
                    'Balance': max(0, balance)
                })
    
    bank_df = pd.DataFrame(bank_data)
    
    return daily_df, tickets_df, airline_sales_df, staff_df, bank_df

# Load data
daily_df, tickets_df, airline_sales_df, staff_df, bank_df = load_sample_data()

# Sidebar filters
st.sidebar.header("📊 Dashboard Filters")

# Date range selector
date_range = st.sidebar.date_input(
    "Select Date Range",
    value=(date.today() - timedelta(days=30), date.today()),
    min_value=date(2025, 1, 1),
    max_value=date.today()
)

# Branch filter
branches = ['All'] + list(tickets_df['Branch'].unique())
selected_branch = st.sidebar.selectbox("Select Branch", branches)

# Filter data based on selections
if len(date_range) == 2:
    start_date, end_date = date_range
    daily_filtered = daily_df[(daily_df['Date'] >= pd.Timestamp(start_date)) & 
                             (daily_df['Date'] <= pd.Timestamp(end_date))]
    tickets_filtered = tickets_df[(tickets_df['Date'] >= pd.Timestamp(start_date)) & 
                                 (tickets_df['Date'] <= pd.Timestamp(end_date))]
    airline_sales_filtered = airline_sales_df[(airline_sales_df['Date'] >= pd.Timestamp(start_date)) & 
                                             (airline_sales_df['Date'] <= pd.Timestamp(end_date))]
    staff_filtered = staff_df[(staff_df['Date'] >= pd.Timestamp(start_date)) & 
                             (staff_df['Date'] <= pd.Timestamp(end_date))]
    bank_filtered = bank_df[(bank_df['Date'] >= pd.Timestamp(start_date)) & 
                           (bank_df['Date'] <= pd.Timestamp(end_date))]
else:
    daily_filtered = daily_df
    tickets_filtered = tickets_df
    airline_sales_filtered = airline_sales_df
    staff_filtered = staff_df
    bank_filtered = bank_df

# Apply branch filter
if selected_branch != 'All':
    tickets_filtered = tickets_filtered[tickets_filtered['Branch'] == selected_branch]
    airline_sales_filtered = airline_sales_filtered[airline_sales_filtered['Branch'] == selected_branch]
    staff_filtered = staff_filtered[staff_filtered['Branch'] == selected_branch]
    bank_filtered = bank_filtered[bank_filtered['Branch'] == selected_branch]

# Main dashboard content
col1, col2, col3, col4 = st.columns(4)

with col1:
    total_sales = daily_filtered['Daily_Sales'].sum()
    st.metric(
        label="💰 Total Sales",
        value=f"SAR {total_sales:,.0f}",
        delta=f"{(total_sales/len(daily_filtered)):.0f} avg/day"
    )

with col2:
    total_tickets = tickets_filtered['Tickets_Issued'].sum()
    st.metric(
        label="🎫 Total Tickets",
        value=f"{total_tickets:,}",
        delta=f"{(total_tickets/len(daily_filtered)):.0f} avg/day"
    )

with col3:
    avg_cash = daily_filtered['Cash_Balance'].mean()
    st.metric(
        label="💵 Avg Cash Balance",
        value=f"SAR {avg_cash:,.0f}",
        delta="Daily Average"
    )

with col4:
    total_bank_balance = bank_filtered['Balance'].sum()
    st.metric(
        label="🏦 Total Bank Balance",
        value=f"SAR {total_bank_balance:,.0f}",
        delta="All Banks"
    )

# Charts section
st.markdown("---")

# Row 1: Sales trends and airline performance
col1, col2 = st.columns(2)

with col1:
    st.subheader("📈 Daily Sales Trend")
    fig_sales = px.line(daily_filtered, x='Date', y='Daily_Sales', 
                       title="Daily Sales Over Time",
                       labels={'Daily_Sales': 'Sales (SAR)', 'Date': 'Date'})
    fig_sales.update_layout(showlegend=False)
    fig_sales.update_traces(line_color='#2a5298', line_width=3)
    st.plotly_chart(fig_sales, use_container_width=True)

with col2:
    st.subheader("✈️ Airline Performance")
    airline_summary = airline_sales_filtered.groupby('Airline')['Sales'].sum().reset_index()
    fig_airline = px.bar(airline_summary, x='Airline', y='Sales',
                        title="Sales by Airline",
                        labels={'Sales': 'Total Sales (SAR)', 'Airline': 'Airline'},
                        color='Sales',
                        color_continuous_scale='Blues')
    fig_airline.update_layout(showlegend=False, xaxis_tickangle=-45)
    st.plotly_chart(fig_airline, use_container_width=True)

# Row 2: Staff performance and ticket distribution
col1, col2 = st.columns(2)

with col1:
    st.subheader("👥 Top Performing Staff")
    staff_summary = staff_filtered.groupby('Staff').agg({
        'Sales': 'sum',
        'Tickets_Issued': 'sum'
    }).reset_index().sort_values('Sales', ascending=False).head(8)
    
    fig_staff = px.bar(staff_summary, x='Staff', y='Sales',
                      title="Sales by Staff Member",
                      labels={'Sales': 'Total Sales (SAR)', 'Staff': 'Staff Member'},
                      color='Sales',
                      color_continuous_scale='Greens')
    fig_staff.update_layout(showlegend=False, xaxis_tickangle=-45)
    st.plotly_chart(fig_staff, use_container_width=True)

with col2:
    st.subheader("🎯 Ticket Distribution by Airline")
    ticket_summary = tickets_filtered.groupby('Airline')['Tickets_Issued'].sum().reset_index()
    fig_tickets = px.pie(ticket_summary, values='Tickets_Issued', names='Airline',
                        title="Ticket Distribution",
                        color_discrete_sequence=px.colors.qualitative.Set3)
    st.plotly_chart(fig_tickets, use_container_width=True)

# Row 3: Financial overview
st.subheader("💳 Financial Overview")
col1, col2 = st.columns(2)

with col1:
    st.write("**Cash vs Bank Balance Trend**")
    fig_balance = make_subplots(specs=[[{"secondary_y": True}]])
    
    fig_balance.add_trace(
        go.Scatter(x=daily_filtered['Date'], y=daily_filtered['Cash_Balance'], 
                  name="Cash Balance", line=dict(color='green', width=2)),
        secondary_y=False,
    )
    
    fig_balance.add_trace(
        go.Scatter(x=daily_filtered['Date'], y=daily_filtered['Bank_Balance'], 
                  name="Bank Balance", line=dict(color='blue', width=2)),
        secondary_y=True,
    )
    
    fig_balance.update_xaxes(title_text="Date")
    fig_balance.update_yaxes(title_text="Cash Balance (SAR)", secondary_y=False)
    fig_balance.update_yaxes(title_text="Bank Balance (SAR)", secondary_y=True)
    fig_balance.update_layout(height=400, showlegend=True)
    
    st.plotly_chart(fig_balance, use_container_width=True)

with col2:
    st.write("**Bank Balances Distribution**")
    bank_summary = bank_filtered.groupby('Bank')['Balance'].sum().reset_index()
    fig_banks = px.bar(bank_summary, x='Bank', y='Balance',
                      title="Balance by Bank",
                      labels={'Balance': 'Total Balance (SAR)', 'Bank': 'Bank'},
                      color='Balance',
                      color_continuous_scale='Oranges')
    fig_banks.update_layout(showlegend=False)
    st.plotly_chart(fig_banks, use_container_width=True)

# Data tables section
st.markdown("---")
st.subheader("📋 Detailed Data Tables")

tab1, tab2, tab3, tab4 = st.tabs(["Daily Summary", "Airline Sales", "Staff Performance", "Bank Balances"])

with tab1:
    st.dataframe(daily_filtered.style.format({
        'Daily_Sales': 'SAR {:,.0f}',
        'Cash_Balance': 'SAR {:,.0f}',
        'Bank_Balance': 'SAR {:,.0f}'
    }), use_container_width=True)

with tab2:
    airline_display = airline_sales_filtered.groupby(['Date', 'Airline']).agg({
        'Sales': 'sum'
    }).reset_index()
    st.dataframe(airline_display.style.format({
        'Sales': 'SAR {:,.0f}'
    }), use_container_width=True)

with tab3:
    staff_display = staff_filtered.groupby(['Date', 'Staff']).agg({
        'Tickets_Issued': 'sum',
        'Sales': 'sum'
    }).reset_index()
    st.dataframe(staff_display.style.format({
        'Sales': 'SAR {:,.0f}',
        'Tickets_Issued': '{:,}'
    }), use_container_width=True)

with tab4:
    bank_display = bank_filtered.groupby(['Date', 'Bank']).agg({
        'Balance': 'sum'
    }).reset_index()
    st.dataframe(bank_display.style.format({
        'Balance': 'SAR {:,.0f}'
    }), use_container_width=True)

# Footer
st.markdown("---")
st.markdown("""
<div style='text-align: center; color: #666; padding: 20px;'>
    <p>© 2025 Tawsif Travel & Tourism Company - Business Intelligence Dashboard</p>
    <p>Last Updated: {} | Data Range: {} to {}</p>
</div>
""".format(
    datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
    date_range[0] if len(date_range) == 2 else "All Time",
    date_range[1] if len(date_range) == 2 else "All Time"
), unsafe_allow_html=True)