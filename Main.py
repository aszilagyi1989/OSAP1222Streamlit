import streamlit as st
import pandas as pd
import datetime
import plotly.express as px
from pygwalker.api.streamlit import StreamlitRenderer

SzemelyData = pd.read_csv('https://raw.githubusercontent.com/aszilagyi1989/Shiny_CSV/refs/heads/main/OSAP1222_Szemely.csv', sep = ';')
SzemelyData['DATE'] = pd.to_datetime(SzemelyData['TEV'].astype(str) + '/' + SzemelyData['MHO'].astype(str) + '/01').dt.date
SzemelyData = SzemelyData.drop(columns = ['TEV', 'MHO'])

# @st.cache_resource
def get_pyg_renderer() -> "StreamlitRenderer":
    return StreamlitRenderer(SzemelyData[(SzemelyData['MG05'] == Border) & (SzemelyData['MG02'].isin(Nationality)) & (SzemelyData['DATE'] >= start_date) & (SzemelyData['DATE'] <= end_date)], spec = "./gw_config.json", spec_io_mode = "rw")

st.set_page_config(
  layout = 'wide',
  page_title = 'OSAP 1222 - Személy- és járműforgalmi jelentés',
  page_icon = 'https://map.ksh.hu/timea/images/shortcut.ico')
  
st.subheader('Személy- és járműforgalmi jelentés - OSAP 1222')
today = datetime.datetime.now()

#user_info = st.user
# st.write(f"User: {user_info}")

with st.sidebar:
  
  DateRange = st.date_input(label = 'Időszak kiválasztása', value = (datetime.date(2019, 1, 1), datetime.date(2025, today.month - 1, 1)), min_value = datetime.date(2019, 1, 1), max_value = datetime.date(2025, today.month -1, 1), format = 'YYYY.MM.DD')
  
  try:
    start_date = DateRange[0]
    end_date = DateRange[1]
    
    Border_All = SzemelyData[(SzemelyData['DATE'] >= start_date) & (SzemelyData['DATE'] <= end_date)]
    Border_All = Border_All['MG05'].unique()
    Border = st.selectbox('Határátkelőhely', Border_All)
  
  except:
    st.error('Kérlek, állíts be egy megfelelő időintervallumot!')
  
  Diagram = st.selectbox('Diagramtípus', ['Vonal', 'Pont', 'Tableau'])

tab1, tab2 = st.tabs(['Személy', 'Jármű'])
with tab1:
  
  try:
  
    options = SzemelyData[(SzemelyData['MG05'] == Border) & (SzemelyData['DATE'] >= start_date) & (SzemelyData['DATE'] <= end_date)]
    Nationality_All = options['MG02'].unique().tolist()
    Nationality = st.multiselect('Állampolgárság', Nationality_All, Nationality_All)
    
  except:
    st.error('Nem lehet állampolgárságot kiválasztani az oldalszárnyon megadott beállításokkal!')
  
  try:
    
    if (Diagram == 'Vonal'):
      fig = px.line(SzemelyData[(SzemelyData['DATE'] >= start_date) & (SzemelyData['DATE'] <= end_date) & (SzemelyData['MG05'] == Border) & (SzemelyData.MG02.isin(Nationality))], x = "DATE", y = "GADC041", color = "MG02", facet_row = "MG58", markers = True, 
                                  title = "Személyforgalom ki- és belépő személyek vonaldiagramja")
      st.plotly_chart(fig)
    
    if (Diagram == 'Pont'):
      fig = px.scatter(SzemelyData[(SzemelyData['DATE'] >= start_date) & (SzemelyData['DATE'] <= end_date) & (SzemelyData['MG05'] == Border) & (SzemelyData.MG02.isin(Nationality))], x = "DATE", y = "GADC041", color = "MG02", facet_row = "MG58",
                                  title = "Személyforgalom ki- és belépő személyek pontdiagramja")
      st.plotly_chart(fig)
    
    if (Diagram == 'Tableau'):
      renderer = get_pyg_renderer()
      renderer.explorer()
      
  except:
    st.error('A diagram nem megjeleníthető az adott beállításokkal!')
  
with tab2:
  ""
