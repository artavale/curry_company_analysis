# ==================================
# ===    Libraries  =====
# ==================================
import folium
import pandas as pd

import streamlit as st
import plotly.express as px
import plotly.graph_objects as go

from PIL import Image
from haversine import haversine
from streamlit_folium import folium_static

st.set_page_config( page_title='Visão Empresa', page_icon="📈", layout='wide')

# ==================================
# ===    Help Functions    =====
# ==================================

def clean_code( df1 ):
    """
        Esta função realiza o data cleaning do dataset: 
            1. Elimina os NaN e converte os tipos das colunas Delivery person Age 
            2. Elimina os NaN e converte os tipos das colunas Delivery_person_Ratings
            3. Elimina os NaN da coluna City
            4. Converte a coluna Order Date
            5. Elimina os NaN e converte os tipos das colunas multiple deliveries
            6. Removendo os espaços de texto/string/objec com strip
            7. Limpa a coluna de Time taken
            
    """
    # 1. Convertendo a coluna Delivery person Age
    linhas_selecionadas = df1['Delivery_person_Age'] != 'NaN ' 
    df1 = df1.loc[ linhas_selecionadas, :].copy()
    df1['Delivery_person_Age'] = df1['Delivery_person_Age'].astype('int64')

    # 2. Convertendo a coluna Delivery person Ratings e eliminando os NaN
    linhas_selecionadas = df1['Road_traffic_density'] != 'NaN ' 
    df1 = df1.loc[ linhas_selecionadas, :].copy()
    df1['Delivery_person_Ratings'] = df1['Delivery_person_Ratings'].astype('float')

    # 3. Convertendo eliminando os NaN da coluna city
    linhas_selecionadas = df1['City'] != 'NaN ' 
    df1 = df1.loc[ linhas_selecionadas, :].copy()

    # 3. Convertendo eliminando os NaN da coluna city
    linhas_selecionadas = df1['Festival'] != 'NaN ' 
    df1 = df1.loc[ linhas_selecionadas, :].copy()

    # 4. Convertendo a coluna Order Date
    df1['Order_Date'] = pd.to_datetime( df1['Order_Date'], format='%d-%m-%Y')

    # 5. Convertendo a coluna multiple deliveries
    linhas_selecionadas = df1['multiple_deliveries'] != 'NaN '
    df1 = df1.loc[ linhas_selecionadas, :].copy()
    df1['multiple_deliveries'] = df1['multiple_deliveries'].astype('int')

    # 6. Removendo os espaços de texto/string/objec com strip
    df1.loc[:, 'ID'] = df1.loc[:, 'ID'].str.strip()
    df1.loc[:, 'Delivery_person_ID'] = df1.loc[:, 'Delivery_person_ID'].str.strip()
    df1.loc[:, 'Road_traffic_density'] = df1.loc[:, 'Road_traffic_density'].str.strip()
    df1.loc[:, 'Type_of_order'] = df1.loc[:, 'Type_of_order'].str.strip()
    df1.loc[:, 'Type_of_vehicle'] = df1.loc[:, 'Type_of_vehicle'].str.strip()
    df1.loc[:, 'Festival'] = df1.loc[:, 'Festival'].str.strip()
    df1.loc[:, 'City'] = df1.loc[:, 'City'].str.strip()

    # 7. Limpando a coluna de Time taken
    df1['Time_taken(min)'] = df1['Time_taken(min)'].apply( lambda x: x.split( ' ' )[1] )
    df1['Time_taken(min)'] = df1['Time_taken(min)'].astype( int )
    
    return df1

def order_metrics( df1 ):
    # Order Mertrics
    cols = [ 'ID', 'Order_Date'] 
    # Seleção de linhas
    df_aux = df1.loc[: , cols].groupby( 'Order_Date' ).count().reset_index()
    # Desenhar o gráfico de Barras
    fig = px.bar(df_aux, x='Order_Date', y='ID')
            
    return fig

def traffic_order_share( df1 ): 
    # Order Mertrics Share        
    df_aux = df1.loc[:, ['ID', 'Road_traffic_density']].groupby( 'Road_traffic_density').count().reset_index()
    # Criaçao. da metrica 
    df_aux['entregas_perc'] = df_aux['ID'] / df_aux['ID'].sum()
    # Desenhar o gráfico de pizza
    fig = px.pie( df_aux, values='entregas_perc', names='Road_traffic_density' )
                
    return fig

def traffic_order_city( df1 ):
    # Traffic Order by city            
    df_aux = df1.loc[:, ['ID', 'City', 'Road_traffic_density']].groupby(['City', 'Road_traffic_density']).count().reset_index()
    # Desenhar o gráfico de scatter
    fig  = px.scatter( df_aux, x='City', y= 'Road_traffic_density', size='ID', color='City')
                
    return fig

def orders_by_week( df1):
    # Criar a coluna da semana
    df1['week_of_year'] = df1['Order_Date'].dt.strftime( '%U' )
    # Agrupar pela semana
    df_aux = df1.loc[: ,['ID', 'week_of_year']].groupby( ['week_of_year']).count().reset_index()
    # Desenhar um gráfico de linhas 
    fig = px.line( df_aux, x='week_of_year', y='ID')
            
    return fig

def orders_share_by_week( df1 ):
    # Quantidade de pedidos por semana / numero unico de entregadores por semana 
    df_aux1 = df1.loc[: , [ 'ID', 'week_of_year']].groupby( 'week_of_year').count().reset_index()
    df_aux2 = df1.loc[:, ['Delivery_person_ID', 'week_of_year']].groupby( 'week_of_year').nunique().reset_index()
    # Merging os dois aux df criados 
    df_aux = pd.merge( df_aux1, df_aux2, how='inner')
    # Feature engeniering em df_aux
    df_aux['order_by_delivery'] = df_aux['ID'] / df_aux['Delivery_person_ID']
    # Desenhar um gráfico de linhas
    fig = px.line( df_aux, x= 'week_of_year', y='order_by_delivery')
            
    return fig
        
def county_maps( df1 ):
            
    df_aux = df1.loc[:, ['City', 'Road_traffic_density', 'Delivery_location_latitude', 'Delivery_location_longitude']].groupby( ['City', 'Road_traffic_density']).median().reset_index()
    # Desenhar o mapa
    map_ = folium.Map( zoom_start=11 )
    for index, location_info in df_aux.iterrows():
        folium.Marker( [location_info['Delivery_location_latitude'],
                       location_info['Delivery_location_longitude']], 
                       popup=location_info[['City', 'Road_traffic_density']] ).add_to( map_ )
    folium_static( map_, width=1400, height= 600 )
        
    return None 
    
# ==================================
# ===   Import dataset    =====
# ==================================
df = pd.read_csv('dataset/train.csv') 
df1 = df.copy()

# ==================================
# ===    Data Cleaning   =====
# ==================================

df1 = clean_code( df1 ) 

# ==================================
# ===    Barra Lateral    =====
# ==================================
st.header('Markeplace - Visão Empresa')

#image_path = '/Users/arthurvale/repos/FTC_python_analise_dados/logo.png'
image = Image.open( 'logo.png' )
st.sidebar.image( image, width=120 ) 

st.sidebar.markdown('# Cury Company')
st.sidebar.markdown('### Fastest Delivery in Town')

st.sidebar.markdown("""___""")

st.sidebar.markdown('## Selecione uma data limite')
date_slider = st.sidebar.slider(
    'Até qual data?',
    value=pd.datetime(2022,4,13),
    min_value=pd.datetime(2022,2,11), 
    max_value=pd.datetime(2022,4,6), 
    format='DD-MM-YYYY')

st.sidebar.markdown("""___""")

traffic_options= st.sidebar.multiselect(
    'Quais as condições do trânsito',
    ['Low', 'Medium', 'High', 'Jam'],
    default=['Low', 'Medium', 'High', 'Jam'])
st.sidebar.markdown("""___""")
st.sidebar.markdown("### Powered by Arthur Sousa")

# ===============
# Filtro de Data 
# ===============

linhas_selecionadas = df1['Order_Date'] < date_slider
df1 = df1.loc[linhas_selecionadas, :]

# ==================
# Filtro de Transito
# ==================

linhas_selecionadas = df1['Road_traffic_density'].isin( traffic_options )
df1 = df1.loc[linhas_selecionadas, :]
    
# ==================================
# ===    Layout no Streamlit   =====
# ==================================

tab1, tab2, tab3 = st.tabs( ['Visão Gerencial', 'Visão Estratégica', 'Visão Geográfica'] ) 

with tab1: 
    with st.container():
        
        st.markdown('# Orders by Day')
        fig = order_metrics( df1 )
        st.plotly_chart( fig, use_container_width=True)       
            
    
    with st.container():
        col1, col2 = st.columns( 2 )
        with col1:
                        
            st.markdown('### Traffic Order Share')
            fig = traffic_order_share( df1 )
            st.plotly_chart( fig, use_container_width=True )
            

        with col2:
            
            st.markdown('### Traffic Order City')
            fig = traffic_order_city( df1 )
            st.plotly_chart( fig, use_container_width=True )
            
    
with tab2:
    with st.container():
        
        st.markdown('## Orders by Week')
        fig = orders_by_week( df1 ) 
        st.plotly_chart( fig, use_container_width=True)
        
    
    with st.container():
        
        st.markdown('## Orders Share by Week')
        fig = orders_share_by_week( df1 ) 
        st.plotly_chart( fig, use_container_width=True)
    
    
with tab3: 
    st.markdown('# County Maps')
    fig = county_maps( df1 ) 
    


