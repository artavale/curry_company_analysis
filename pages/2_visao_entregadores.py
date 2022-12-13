# Libraries

import folium
import pandas as pd

import streamlit as st
import plotly.express as px
import plotly.graph_objects as go

from PIL import Image
from haversine import haversine
from streamlit_folium import folium_static

st.set_page_config( page_title='Visão Entregadores', page_icon="🚗", layout='wide')

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


def top_deliveries( df1, top_asc ): 
    df2 = ( df1.loc[:, ['Delivery_person_ID', 'City','Time_taken(min)']]
                .groupby( ['City','Delivery_person_ID'] )
                .mean()
                .sort_values(['City', 'Time_taken(min)'], ascending=top_asc)
                .reset_index() )

    df_aux1 = df2.loc[df2['City'] == 'Metropolitian', :].head(10)
    df_aux2 = df2.loc[df2['City'] == 'Urban', :].head(10)
    df_aux3 = df2.loc[df2['City'] == 'Semi-Urban', :].head(10)

    df3 = pd.concat( [ df_aux1, df_aux2, df_aux3 ]).reset_index(drop=True)
                
    return df3 
            


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
st.header('Markeplace - Visão Entregadores')

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



# ==================================
# ===    Layout no Streamlit   =====
# ==================================

tab1, tab2, tab3 = st.tabs( ['Visão Gerencial', '_', '_']) 

with tab1:
    with st.container():
        st.title('Overall Mertrics')
        
        col1, col2, col3, col4 = st.columns( 4, gap='large')
        with col1: 
            # A maior idade dos entregadores
            #st.subheader( "Maior Idade")
            maior_idade = df1.loc[: , 'Delivery_person_Age'].max()
            col1.metric("Maior Idade", maior_idade ) 

            
        with col2:
            # A menor idade dos entregadores
            #st.subheader( "Menor Idade")
            menor_idade = df1.loc[: , 'Delivery_person_Age'].min()
            col2.metric("Menor Idade", menor_idade ) 
            
        with col3:
            # A melhor coondição dos veículos
            #st.subheader("Melhor condição de veículo")
            melhor_condicao = df1.loc[:, 'Vehicle_condition'].max()
            col3.metric( "Melhor Condição Veicular", melhor_condicao ) 
                    
            
        with col4:
            # A pior coondição dos veículos
            #st.subheader("Pior condição de veículo")
            pior_condicao =  df1.loc[:, 'Vehicle_condition'].min()
            col4.metric("Pior condição de veículo", pior_condicao )
    
    with st.container():
        st.markdown( """___""" )
        st.title('Avaliações')
        
        col1, col2 = st.columns( 2 )
        
        with col1: 
            st.markdown('##### Avaliação média por entregador')
            df_avg_ratings = ( df1.loc[:, ['Delivery_person_Ratings','Delivery_person_ID']]
                                     .groupby( 'Delivery_person_ID' )
                                     .mean()
                                     .reset_index() )
            st.dataframe (df_avg_ratings)
            
        
        with col2:
            # Avaliação nedia por transito
            st.markdown('##### Avaliação média por trânsito')
            df_avg_std_ratings = ( df1.loc[:, ['Delivery_person_Ratings', 'Road_traffic_density']]
                                  .groupby( 'Road_traffic_density' )
                                  .agg(['mean', 'std'])
                                  .reset_index() ) 
            df_avg_std_ratings.columns = ['Road_traffic_density','delivery_mean', 'delivery_std']
            st.dataframe( df_avg_std_ratings )
            
            # Avaliação nedia por clima
            st.markdown('##### Avaliação por clima')
            df_avg_std_ratings_weather = ( df1.loc[:, ['Delivery_person_Ratings', 'Weatherconditions']]
                                          .groupby( 'Weatherconditions' )
                                          .agg(['mean', 'std'])
                                          .reset_index())
            df_avg_std_ratings_weather.columns = ['Weatherconditions','delivery_mean', 'delivery_std']
            st.dataframe( df_avg_std_ratings_weather )
            
            
    
    with st.container():
        st.markdown( """___""")
        st.title('Velocidade de Entrega')
        
        col1, col2 = st.columns( 2 )
        
        with col1:
            st.markdown('##### Top Entregadores mais rápidos')
            df3 = top_deliveries( df1, top_asc=True ) 
            st.dataframe( df3 )
                        
        
        with col2:
            st.markdown('##### Top Entregadores mais lentos')
            df3 = top_deliveries( df1, top_asc=False ) 
            st.dataframe( df3 )
        
        
