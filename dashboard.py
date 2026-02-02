import streamlit as st
import pandas as pd
import psycopg2
import os
import plotly.express as px
import plotly.graph_objects as go
import plotly.io as pio 
from dotenv import load_dotenv
import time

load_dotenv()

# 1. Configuración de la página
st.set_page_config(page_title="Energy IoT Dashboard", layout="wide")

# 2. IMPORTAR FUENTE Y APLICAR CSS (ACTUALIZADO PARA CENTRAR)
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Lexend:wght@300;400;500;600;700;800;900&family=Inter:wght@400;500;600;700&display=swap');

    html, body, [class*="css"], .stMetric, .stMarkdown, p, div {
        font-family: 'Lexend', sans-serif !important;
    }
    
    /* Título principal gordito */
    .main-header {
        font-family: 'Lexend', sans-serif !important;
        font-weight: 650 !important;
        text-align: center !important;
        font-size: 3rem !important;
        background: linear-gradient(135deg, #9CB92E 0%, #9CB92E 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
        margin-bottom: 0.5rem;
        letter-spacing: -1px !important;
    }
    
    /* Títulos de gráficas en mayúsculas */
    h3 {
        font-family: 'Inter', sans-serif !important;
        font-weight: 600 !important;
        text-align: center !important;
        font-size: 0.9rem !important;
        letter-spacing: 2px !important;
        color: #25619E !important;
        text-transform: uppercase !important;
    }

    /* Métricas */
    [data-testid="stMetricValue"] {
        text-align: center !important;
        font-family: 'Lexend', sans-serif !important;
        font-weight: 700 !important;
        font-size: 2rem !important;
        color: #5DB3B3 !important;
    }
    
    [data-testid="stMetricLabel"] {
        text-align: center !important;
        font-family: 'Inter', sans-serif !important;
        font-weight: 500 !important;
        color: #888 !important;
        text-transform: uppercase !important;
        letter-spacing: 1px !important;
        font-size: 0.75rem !important;
    }
    
    /* Tarjetas de métricas con efecto */
    [data-testid="metric-container"] {
        background: linear-gradient(135deg, rgba(93, 179, 179, 0.08) 0%, rgba(156, 185, 46, 0.08) 100%);
        border-radius: 12px;
        padding: 1.2rem 1rem;
        border: 1px solid rgba(93, 179, 179, 0.3);
        transition: all 0.3s ease;
    }
    
    [data-testid="metric-container"]:hover {
        transform: translateY(-3px);
        border-color: rgba(93, 179, 179, 0.6);
        box-shadow: 0 6px 20px rgba(93, 179, 179, 0.25);
    }
    </style>
    """, unsafe_allow_html=True)

# 3. CONFIGURACIÓN GLOBAL DE PLOTLY (Para que todas las gráficas usen Inter)
pio.templates.default = "plotly_white"
pio.templates[pio.templates.default].layout.update(
    font_family="Inter",
    title_font_family="Inter",
    title_font_size=10
)
@st.cache_data(ttl=10)
def get_data():
    conn = psycopg2.connect(
        host=os.getenv('PG_HOST'),
        database='energy_project',
        user=os.getenv('PG_USER'),
        password=os.getenv('PG_PASSWORD')
    )
    # Cambiamos JOIN por LEFT JOIN para no perder registros
    query = """
    SELECT c.date, c.appliances, c.lights, 
           a.t1, a.rh_1, a.t2, a.rh_2, a.t3, a.rh_3, a.t6,
           e.t_out, e.press_mm_hg, e.rh_out, e.windspeed, e.visibility
    FROM consumo_energia c
    LEFT JOIN ambiente_interno a ON c.date = a.date
    LEFT JOIN clima_externo e ON c.date = e.date
    ORDER BY c.date ASC
    """
    df = pd.read_sql(query, conn)
    conn.close()
    return df

# Auto-refresh configuration
st.sidebar.header("Data Stream Settings")
auto_refresh = st.sidebar.checkbox("Enable Live Monitoring", value=False)
refresh_interval = st.sidebar.selectbox(
    "Update Frequency",
    options=[5, 10, 30, 60, 300], # Añadimos 5 minutos (300s)    index=3
)

st.markdown("<h1 class='main-header'>Real-Time Energy Analysis Dashboard</h1>", unsafe_allow_html=True)
st.markdown("---")

try:
    df = get_data()
    df['date'] = pd.to_datetime(df['date'])
    
    # Display main metrics
    col_m1, col_m2, col_m3, col_m4 = st.columns(4)
    with col_m1:
        st.metric("Total Records", len(df))
    with col_m2:
        st.metric("Average Consumption", f"{df['appliances'].mean():.2f} Wh")
    with col_m3:
        st.metric("Current Temp (T1)", f"{df['t1'].iloc[-1]:.1f}°C")
    with col_m4:
        st.metric("Current Humidity", f"{df['rh_1'].iloc[-1]:.1f}%")
    

    st.markdown("---")
    
    # Filters
    st.sidebar.header("Visualization Filters")
    items = st.sidebar.slider("Time Window (Records)", 50, len(df), 500)
    df_plot = df.tail(items)

    col1, col2 = st.columns(2)

    with col1:
        # 1. Appliances Histogram - Using Teal
        st.subheader("CONSUMPTION DISTRIBUTION")
        fig1 = px.histogram(df_plot, x='appliances', nbins=30, 
                           labels={'appliances': 'Consumption (Wh)', 'count': 'Frequency'},
                           color_discrete_sequence=['#5DB3B3']) # TEAL
        fig1.update_traces(marker_line_color='white', marker_line_width=0.5)
        st.plotly_chart(fig1, use_container_width=True)

        # 2. Time Series - Using Orange
        st.subheader("CONSUMPTION OVER TIME")
        fig2 = px.line(df_plot, x='date', y='appliances',
                      labels={'date': 'Time', 'appliances': 'Consumption (Wh)'})
        fig2.update_traces(line_color='#E57A07', line_width=2) # ORANGE
        st.plotly_chart(fig2, use_container_width=True)

        # 3. Correlation Heatmap - Using Teal-Red-Blue scale
        st.subheader("CORRELATION MAP")
        correlation_data = df_plot[['appliances', 't1', 't_out', 'rh_1', 'windspeed']].corr()
        fig3 = go.Figure(data=go.Heatmap(
            z=correlation_data.values,
            x=correlation_data.columns,
            y=correlation_data.columns,
            colorscale=[[0, '#1F568D'], [0.5, '#F4F4F4'], [1, '#A8201A']], # BLUE to RED
            zmin=-1, zmax=1,
            text=correlation_data.values.round(2),
            texttemplate='%{text}',
            textfont={"size": 10}
        ))
        fig3.update_layout(height=400)
        st.plotly_chart(fig3, use_container_width=True)

    with col2:
        # 4. Temperature Comparison 
        st.subheader("INTERNAL VS EXTERNAL TEMPERATURE")
        fig4 = go.Figure()
        fig4.add_trace(go.Scatter(x=df_plot['date'], y=df_plot['t1'],
                                 mode='lines', name='Internal (T1)',
                                 line=dict(color='#5DB3B3', width=2))) # TEAL
        fig4.add_trace(go.Scatter(x=df_plot['date'], y=df_plot['t_out'],
                                 mode='lines', name='External',
                                 line=dict(color='#1F568D', width=2))) # BLUE
        fig4.update_layout(xaxis_title='Time', yaxis_title='Temperature (°C)',
                          hovermode='x unified')
        st.plotly_chart(fig4, use_container_width=True)

        # 5. Humidity Boxplot 
        st.subheader("HUMIDITY VARIABILITY")
        humidity_df = df_plot[['rh_1', 'rh_2', 'rh_3']].melt(var_name='Sensor', value_name='Humidity')
        fig5 = px.box(humidity_df, x='Sensor', y='Humidity', 
                     color='Sensor',
                     color_discrete_sequence=['#5DB3B3', '#A8201A', '#1F568D'], # Teal, Red, Blue
                     labels={'Humidity': 'Relative Humidity (%)'})
        st.plotly_chart(fig5, use_container_width=True)

        # 6. Scatter Plot: Temp vs Consumption
        st.subheader("TEMPERATURE VS CONSUMPTION")
        fig6 = px.scatter(df_plot, x='t1', y='appliances',
                         labels={'t1': 'Internal Temperature (°C)', 
                                'appliances': 'Consumption (Wh)'},
                         opacity=0.6,
                         color_discrete_sequence=['#9CB92E']) 
        st.plotly_chart(fig6, use_container_width=True)
    
    # Display last records
    st.markdown("---")
    st.subheader("Last 10 Records")
    st.dataframe(df.tail(10)[['date', 'appliances', 'lights', 't1', 't_out', 'rh_1']], use_container_width=True)
    
    # Auto-refresh logic
    if auto_refresh:
        time.sleep(refresh_interval)
        st.rerun()

except Exception as e:
    st.error(f"Error loading data: {e}")
    st.info("Verify that the subscriber is running and the database is accessible.")