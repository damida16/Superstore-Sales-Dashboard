import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

st.set_page_config(page_title="Superstore Sales Dashboard", layout="wide")

st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');
    * { font-family: 'Inter', sans-serif; }
    .stApp { background-color: #f8fafc; }
    section[data-testid="stSidebar"] { background-color: #ffffff !important; }
    section[data-testid="stSidebar"] > div { background-color: #ffffff !important; }
    .kpi-card {
        background: white;
        padding: 24px;
        border-radius: 12px;
        border: 1px solid #e2e8f0;
        text-align: center;
        box-shadow: 0 1px 3px rgba(0,0,0,0.05);
    }
    .kpi-value { font-size: 2rem; font-weight: 700; color: #1e293b; margin: 8px 0; }
    .kpi-label { font-size: 0.85rem; color: #64748b; text-transform: uppercase; letter-spacing: 0.5px; font-weight: 500; }
    .section-header { font-size: 1.1rem; font-weight: 600; color: #1e293b; margin: 24px 0 16px 0; padding-bottom: 8px; border-bottom: 2px solid #e2e8f0; }
    .main-title { text-align: center; padding: 20px 0 10px 0; }
    .main-title h1 { font-size: 1.8rem; font-weight: 700; color: #1e293b; margin: 0; }
    .main-title p { color: #64748b; font-size: 0.95rem; margin-top: 6px; }
    .alert-box {
        background: #fef2f2;
        border: 1px solid #fecaca;
        border-left: 4px solid #ef4444;
        border-radius: 8px;
        padding: 16px 20px;
        margin: 20px 0;
    }
    .alert-title { font-weight: 600; color: #991b1b; margin-bottom: 4px; }
    .alert-text { color: #7f1d1d; font-size: 0.9rem; }
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    .footer { text-align: center; padding: 30px 0; color: #94a3b8; font-size: 0.85rem; }
    .footer strong { color: #475569; }
</style>
""", unsafe_allow_html=True)

@st.cache_data
def load_data():
    df = pd.read_csv("Sample_-_Superstore.csv", encoding='latin1')
    df['Order Date'] = pd.to_datetime(df['Order Date'], format='%m/%d/%Y')
    df['Ship Date'] = pd.to_datetime(df['Ship Date'], format='%m/%d/%Y')
    df['Year'] = df['Order Date'].dt.year
    df['Month'] = df['Order Date'].dt.month
    df['Month_Year'] = df['Order Date'].dt.to_period('M').astype(str)
    return df

df = load_data()

st.sidebar.markdown("### Filters")
st.sidebar.markdown("---")
years = st.sidebar.multiselect("Year", options=sorted(df['Year'].unique()), default=sorted(df['Year'].unique()))
regions = st.sidebar.multiselect("Region", options=df['Region'].unique(), default=df['Region'].unique())
categories = st.sidebar.multiselect("Category", options=df['Category'].unique(), default=df['Category'].unique())

df_filtered = df[(df['Year'].isin(years)) & (df['Region'].isin(regions)) & (df['Category'].isin(categories))]

total_sales = df_filtered['Sales'].sum()
total_profit = df_filtered['Profit'].sum()
total_orders = df_filtered['Order ID'].nunique()
profit_margin = (total_profit / total_sales * 100) if total_sales > 0 else 0

loss_makers = df_filtered.groupby('Sub-Category')['Profit'].sum()
loss_makers = loss_makers[loss_makers < 0].sort_values()

st.markdown('<div class="main-title"><h1>Superstore Sales Dashboard</h1><p>Analyzing sales performance across regions, categories, and time periods</p></div>', unsafe_allow_html=True)
st.markdown("---")

col1, col2, col3, col4 = st.columns(4)
with col1:
    st.markdown(f'<div class="kpi-card"><div class="kpi-label">Total Sales</div><div class="kpi-value">${total_sales:,.0f}</div></div>', unsafe_allow_html=True)
with col2:
    st.markdown(f'<div class="kpi-card"><div class="kpi-label">Total Profit</div><div class="kpi-value">${total_profit:,.0f}</div></div>', unsafe_allow_html=True)
with col3:
    st.markdown(f'<div class="kpi-card"><div class="kpi-label">Total Orders</div><div class="kpi-value">{total_orders:,}</div></div>', unsafe_allow_html=True)
with col4:
    st.markdown(f'<div class="kpi-card"><div class="kpi-label">Profit Margin</div><div class="kpi-value">{profit_margin:.1f}%</div></div>', unsafe_allow_html=True)

if len(loss_makers) > 0:
    loss_items = ", ".join([f"{name} (${profit:,.0f})" for name, profit in loss_makers.items()])
    st.markdown(f'''
    <div class="alert-box">
        <div class="alert-title">Loss-Making Products Detected</div>
        <div class="alert-text">{loss_items} => Consider reviewing pricing or discontinuing these items.</div>
    </div>
    ''', unsafe_allow_html=True)

col1, col2 = st.columns([2, 1])
with col1:
    st.markdown('<p class="section-header">Monthly Sales Trend</p>', unsafe_allow_html=True)
    monthly_sales = df_filtered.groupby('Month_Year').agg({'Sales': 'sum', 'Profit': 'sum'}).reset_index().sort_values('Month_Year')
    fig_trend = go.Figure()
    fig_trend.add_trace(go.Scatter(x=monthly_sales['Month_Year'], y=monthly_sales['Sales'], name='Sales', line=dict(color='#3b82f6', width=2), mode='lines+markers', marker=dict(size=4)))
    fig_trend.add_trace(go.Scatter(x=monthly_sales['Month_Year'], y=monthly_sales['Profit'], name='Profit', line=dict(color='#22c55e', width=2), mode='lines+markers', marker=dict(size=4)))
    fig_trend.update_layout(plot_bgcolor='white', paper_bgcolor='white', xaxis=dict(showgrid=False, tickangle=-45), yaxis=dict(showgrid=True, gridcolor='#f1f5f9'), legend=dict(orientation='h', yanchor='bottom', y=1.02, xanchor='right', x=1), margin=dict(l=20, r=20, t=40, b=60), hovermode='x unified')
    st.plotly_chart(fig_trend, use_container_width=True)

with col2:
    st.markdown('<p class="section-header">Sales by Category</p>', unsafe_allow_html=True)
    category_sales = df_filtered.groupby('Category')['Sales'].sum().reset_index()
    fig_category = px.pie(category_sales, values='Sales', names='Category', color_discrete_sequence=['#3b82f6', '#22c55e', '#f59e0b'])
    fig_category.update_traces(textposition='inside', textinfo='percent+label', textfont_size=12)
    fig_category.update_layout(plot_bgcolor='white', paper_bgcolor='white', showlegend=False, margin=dict(l=20, r=20, t=20, b=20))
    st.plotly_chart(fig_category, use_container_width=True)

col1, col2 = st.columns(2)
with col1:
    st.markdown('<p class="section-header">Sales by Region</p>', unsafe_allow_html=True)
    region_sales = df_filtered.groupby('Region').agg({'Sales': 'sum'}).reset_index().sort_values('Sales', ascending=True)
    fig_region = px.bar(region_sales, x='Sales', y='Region', orientation='h', color_discrete_sequence=['#3b82f6'])
    fig_region.update_layout(plot_bgcolor='white', paper_bgcolor='white', xaxis=dict(showgrid=True, gridcolor='#f1f5f9'), yaxis=dict(showgrid=False), margin=dict(l=20, r=20, t=20, b=20), showlegend=False)
    st.plotly_chart(fig_region, use_container_width=True)

with col2:
    st.markdown('<p class="section-header">Top 10 Products</p>', unsafe_allow_html=True)
    top_products = df_filtered.groupby('Product Name')['Sales'].sum().nlargest(10).reset_index().sort_values('Sales', ascending=True)
    top_products['Short Name'] = top_products['Product Name'].str[:25] + '...'
    fig_products = px.bar(top_products, x='Sales', y='Short Name', orientation='h', color_discrete_sequence=['#64748b'])
    fig_products.update_layout(plot_bgcolor='white', paper_bgcolor='white', xaxis=dict(showgrid=True, gridcolor='#f1f5f9'), yaxis=dict(showgrid=False), margin=dict(l=20, r=20, t=20, b=20), showlegend=False)
    st.plotly_chart(fig_products, use_container_width=True)

col1, col2 = st.columns(2)
with col1:
    st.markdown('<p class="section-header">Sales by Segment</p>', unsafe_allow_html=True)
    segment_sales = df_filtered.groupby('Segment').agg({'Sales': 'sum', 'Profit': 'sum'}).reset_index()
    fig_segment = go.Figure()
    fig_segment.add_trace(go.Bar(x=segment_sales['Segment'], y=segment_sales['Sales'], name='Sales', marker_color='#3b82f6'))
    fig_segment.add_trace(go.Bar(x=segment_sales['Segment'], y=segment_sales['Profit'], name='Profit', marker_color='#22c55e'))
    fig_segment.update_layout(barmode='group', plot_bgcolor='white', paper_bgcolor='white', xaxis=dict(showgrid=False), yaxis=dict(showgrid=True, gridcolor='#f1f5f9'), legend=dict(orientation='h', yanchor='bottom', y=1.02, xanchor='right', x=1), margin=dict(l=20, r=20, t=40, b=20))
    st.plotly_chart(fig_segment, use_container_width=True)

with col2:
    st.markdown('<p class="section-header">Profit vs Sales by Sub-Category</p>', unsafe_allow_html=True)
    subcat_sales = df_filtered.groupby('Sub-Category').agg({'Sales': 'sum', 'Profit': 'sum'}).reset_index()
    fig_subcat = px.scatter(subcat_sales, x='Sales', y='Profit', size='Sales', hover_name='Sub-Category', color_discrete_sequence=['#3b82f6'])
    fig_subcat.update_layout(plot_bgcolor='white', paper_bgcolor='white', xaxis=dict(showgrid=True, gridcolor='#f1f5f9'), yaxis=dict(showgrid=True, gridcolor='#f1f5f9'), margin=dict(l=20, r=20, t=20, b=20))
    fig_subcat.add_hline(y=0, line_dash="dash", line_color="#ef4444", opacity=0.5)
    st.plotly_chart(fig_subcat, use_container_width=True)

st.markdown("---")
st.markdown('<div class="footer"><p><strong>Superstore Sales Dashboard</strong></p><p>Built with Python, Pandas, Plotly & Streamlit</p><p>Created by <strong>Damida Shu Mudita</strong></p></div>', unsafe_allow_html=True)