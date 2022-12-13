# Libraries

import folium
import pandas as pd
import numpy as np

import streamlit as st
import plotly.express as px
import plotly.graph_objects as go

from PIL import Image
from haversine import haversine
from streamlit_folium import folium_static

st.set_page_config( page_title='Visão Restaurantes', page_icon="🍽", layout='wide')

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


def distance( df1 ):

    cols = [ 'Restaurant_latitude', 'Restaurant_longitude' , 'Delivery_location_latitude', 'Delivery_location_longitude'  ]
    
    df1['distance'] = df1.loc[:, cols].apply( lambda x: 
                       haversine( 
                            (x['Restaurant_latitude'], x['Restaurant_longitude']), 
                            (x['Delivery_location_latitude'], x['Delivery_location_longitude']) ), axis=1 )

    avg_distance = np.round( df1['distance'].mean(), 2) 

    return avg_distance

def avg_std_time_delivery_festival( df1, festival, op):
    """"
        Esta funçao tem como objetivo calcular a distancia média e o desvio padrao das entregas com e sem festival
        Parametros: 
            Input:
                - df: Dataframe 
                - festival: 
                    'Yes': para dias em que há festivais 
                    'No': para dias em que nao há festivais
                - op
                    'avg_time': calcula a média da distancia
                    'std_time': calcula o desvio padrao da media
            Output:
                - df: Dataframe com uma linha e uma métrica
            
    """

    df_aux = ( df1.loc[:, [ 'Time_taken(min)', 'Festival' ]]
               .groupby( ['Festival'] )
               .agg( {'Time_taken(min)': ['mean', 'std']})
               .reset_index() )

    df_aux.columns = [ 'Festival', 'avg_time', 'std_time'] 
    df_aux = np.round( df_aux.loc[df_aux['Festival'] == festival, op], 2)

    return df_aux

def avg_std_time_by_city( df1 ):
    df_aux = df1.loc[:, ['City', 'Time_taken(min)']].groupby( 'City' ).agg( {'Time_taken(min)': ['mean', 'std']} )
    df_aux.columns = ['avg_time', 'std_time']
    df_aux = df_aux.reset_index()

    fig = go.Figure() 
    fig.add_trace( go.Bar( name='Control', x=df_aux['City'], y=df_aux['avg_time'], error_y=dict(type='data', array=df_aux['std_time']))) 
    fig.update_layout(barmode='group') 

    return fig 

def avg_time_by_city ( df1 ): 
    cols = ['Delivery_location_latitude', 'Delivery_location_longitude', 'Restaurant_latitude', 'Restaurant_longitude']
    df1['distance'] = df1.loc[:, cols].apply( lambda x: 
                                haversine(  (x['Restaurant_latitude'], x['Restaurant_longitude']), 
                                            (x['Delivery_location_latitude'], x['Delivery_location_longitude']) ), axis=1 )

    avg_distance = df1.loc[:, ['City', 'distance']].groupby( 'City' ).mean().reset_index()
    fig = go.Figure( data=[ go.Pie( labels=avg_distance['City'], values=avg_distance['distance'], pull=[0, 0.1, 0])])

    return fig

def avg_time_by_city_traffic( df1 ):

    df_aux = ( df1.loc[:, ['City', 'Time_taken(min)', 'Road_traffic_density']]
                  .groupby( ['City', 'Road_traffic_density'] )
                  .agg( {'Time_taken(min)': ['mean', 'std']} ) )

    df_aux.columns = ['avg_time', 'std_time']
    df_aux = df_aux.reset_index()

    fig = px.sunburst(df_aux, path=['City', 'Road_traffic_density'], values='avg_time',
                      color='std_time', color_continuous_scale='RdBu',
                      color_continuous_midpoint=np.average(df_aux['std_time'] ) )

    return fig


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
st.header('Markeplace - Visão Restaurantes')

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


# =====================
# filtro de clima 
# =====================

weather = st.sidebar.multiselect(
   "Qual a condição climática",
   options = ['conditions Cloudy', 'conditions Fog', 'conditions Sandstorms', 'conditions Stormy', 'conditions Sunny', 'conditions Windy'],
   default = ['conditions Cloudy', 'conditions Fog', 'conditions Sandstorms', 'conditions Stormy', 'conditions Sunny', 'conditions Windy'])

st.sidebar.markdown("""___""")
st.sidebar.markdown("### Powered by Arthur Sousa")

linhas_selecionadas = df1['Weatherconditions'].isin( weather )
df1 = df1.loc[linhas_selecionadas, :]


# =====================
# Layout Restaurantes
# =====================

tab1, tab2, tab3 = st.tabs( ['Visão Gerencial', '_', '_']) 

with tab1:
    with st.container():
        st.title('Overall Metrics')
        
        col1, col2, col3, col4, col5, col6 = st.columns( 6 )
        
        with col1:
            #Quantidade de entregadores únicos
            delivery_unique = len(df1.loc[:, 'Delivery_person_ID'].unique())
            col1.metric( "Entregadores únicos", delivery_unique) 
            
        with col2:
            # Distancia média 
            avg_distance = distance( df1 ) 
            col2.metric("Distancia média das entregas", avg_distance )
            
        with col3:
            # Tempo medio de entrega com festival
            df_aux = avg_std_time_delivery_festival( df1, 'Yes', 'avg_time')
            col3.metric("Avg Time C/Festival", df_aux ) 
        
        with col4:
            # Desvio padrao  de entrega com festival             
            df_aux = avg_std_time_delivery_festival( df1, 'Yes', 'std_time') 
            col4.metric("Std Time C/Festival", df_aux ) 
            
            
        with col5:
         # Tempo medio de entrega SEM festival 
            df_aux = avg_std_time_delivery_festival( df1, 'No', 'avg_time') 
            col5.metric("Avg Time S/Festival", df_aux )
            
        with col6: 
            # Desvio padrao  de entrega SEM festival 
            df_aux = avg_std_time_delivery_festival( df1, 'No', 'std_time' )            
            col6.metric("Std Time S/Festival", df_aux )
            
    
    with st.container():
        st.markdown( """---""" )
        col1, col2 = st.columns( 2 )
        
        with col1:
            # Media e desvio padras das entregas por cidade            
            fig = avg_std_time_by_city( df1 ) 
            st.plotly_chart( fig, use_container_width=True )
            
        with col2:
            
            df_aux = ( df1.loc[:, ['City', 'Time_taken(min)', 'Type_of_order']]
                          .groupby( ['City', 'Type_of_order'] )
                          .agg( {'Time_taken(min)': ['mean', 'std']} ) )

            df_aux.columns = ['avg_time', 'std_time']
            df_aux = df_aux.reset_index()

            st.dataframe( df_aux, use_container_width=True )
        
        
    with st.container():
        st.markdown( """---""" )
        st.title( "Distribuição do Tempo" )
        
        col1, col2 = st.columns( 2 )
        
        with col1:

            fig = avg_time_by_city( df1 ) 
            st.plotly_chart( fig, use_container_width=True )

            
        with col2:

            fig = avg_time_by_city_traffic( df1 ) 
            st.plotly_chart( fig, use_container_width=True )
    
    
    