import streamlit as st
from streamlit_option_menu import option_menu
import pandas as pd
import datetime
import plotly.express as px
from pygwalker.api.streamlit import StreamlitRenderer
import statsmodels.api as sm

SzemelyData = pd.read_csv('https://raw.githubusercontent.com/aszilagyi1989/Shiny_CSV/refs/heads/main/OSAP1222_Szemely.csv', sep = ';')
SzemelyData['DATE'] = pd.to_datetime(SzemelyData['TEV'].astype(str) + '/' + SzemelyData['MHO'].astype(str) + '/01').dt.date
SzemelyData = SzemelyData.drop(columns = ['TEV', 'MHO'])

JarmuData = pd.read_csv('https://raw.githubusercontent.com/aszilagyi1989/Shiny_CSV/refs/heads/main/OSAP1222_Jarmu.csv', sep = ';')
JarmuData['DATE'] = pd.to_datetime(JarmuData['TEV'].astype(str) + '/' + JarmuData['MHO'].astype(str) + '/01').dt.date
JarmuData = JarmuData.drop(columns = ['TEV', 'MHO'])


# @st.cache_resource
def get_pyg_renderer() -> "StreamlitRenderer":
    return StreamlitRenderer(SzemelyData[(SzemelyData['MG05'] == Border) & (SzemelyData['MG02'].isin(Nationality)) & (SzemelyData['DATE'] >= start_date) & (SzemelyData['DATE'] <= end_date) & (SzemelyData['GADC041'] >= filter[0]) & (SzemelyData['GADC041'] <= filter[1])], spec = "./gw_config.json", spec_io_mode = "rw")

# @st.cache_resource
def get_pyg_renderer2() -> "StreamlitRenderer":
    return StreamlitRenderer(JarmuData[(JarmuData['MG05'] == Border2) & (JarmuData['MG64'].isin(Nationality2)) & (JarmuData['DATE'] >= start_date2) & (JarmuData['DATE'] <= end_date2)], spec = "./gw_config.json", spec_io_mode = "rw")


st.set_page_config(
  layout = 'wide',
  page_title = 'OSAP 1222 - Személy- és járműforgalmi jelentés',
  page_icon = 'https://map.ksh.hu/timea/images/shortcut.ico',
  menu_items = {'Get help': 'mailto:adam.szilagyi@ksh.hu',
                'Report a bug': 'mailto:adam.szilagyi@ksh.hu',
                'About': 'Ez a webalkalmazás az 1222-es OSAP számú adatgyűjtés adatait tartalmazza 2019-ig visszamenően azon határátkelőhelyekre, amelyek nincsenek benne a Schengeni övezetben 2025. január 01-e óta.'}
  )

selected = option_menu(None, ['Személy', 'Jármű'], menu_icon = 'cast', default_index = 0, orientation = 'horizontal')


# st.navigation([st.Page("Szemely.py", title = "Személyforgalom"),
#                st.Page("Jarmu.py", title = "Járműforgalom")
#                ])

# st.subheader('Személy- és járműforgalmi jelentés - OSAP 1222')
today = datetime.datetime.now()

#user_info = st.user
# st.write(f"User: {user_info}")

if selected == 'Személy': 

  with st.sidebar:
    
    DateRange = st.date_input(label = 'Időszak kiválasztása', value = (datetime.date(2019, 1, 1), datetime.date(today.year, today.month, 1)), min_value = datetime.date(2019, 1, 1), max_value = datetime.date(today.year, today.month, 1), format = 'YYYY.MM.DD')
    
    try:
      start_date = DateRange[0]
      end_date = DateRange[1]
      
      Border_All = SzemelyData[(SzemelyData['DATE'] >= start_date) & (SzemelyData['DATE'] <= end_date)]
      Border_All = Border_All['MG05'].unique()
      Border = st.selectbox('Határátkelőhely', Border_All)
    
    except:
      st.error('Kérlek, állíts be egy megfelelő időintervallumot!')
    
    filter_option = SzemelyData[(SzemelyData['MG05'] == Border) & (SzemelyData['DATE'] >= start_date) & (SzemelyData['DATE'] <= end_date)]
    filter = st.slider('Be- vagy kilépő személyek száma', filter_option['GADC041'].min(), filter_option['GADC041'].max(), (filter_option['GADC041'].min(), filter_option['GADC041'].max()))
    
    try:
    
      options = SzemelyData[(SzemelyData['MG05'] == Border) & (SzemelyData['DATE'] >= start_date) & (SzemelyData['DATE'] <= end_date)]
      Nationality_All = options['MG02'].unique().tolist()
      Nationality_All_filter = SzemelyData[(SzemelyData['MG05'] == Border) & (SzemelyData['DATE'] >= start_date) & (SzemelyData['DATE'] <= end_date) & (SzemelyData['GADC041'] >= filter[0]) & (SzemelyData['GADC041'] <= filter[1])]
      Nationality_All_filter = Nationality_All_filter['MG02'].unique().tolist()
      Nationality = st.multiselect('Állampolgárság', Nationality_All, Nationality_All_filter)
      
    except:
      st.error('Nem lehet állampolgárságot kiválasztani az oldalszárnyon megadott beállításokkal!')
    
    Diagram = st.selectbox('Diagramtípus', ['Vonal', 'Pont', 'Tableau', 'Dekompozíció'])
    
    if (Diagram == 'Dekompozíció'): 
      Direction = st.selectbox('Irány', ['Belépő', 'Kilépő'])
  
  # tab1, tab2 = st.tabs(['Személy', 'Jármű'])
  # with tab1:
    
  try:
      
    if (Diagram == 'Vonal'):
      fig = px.line(SzemelyData[(SzemelyData['DATE'] >= start_date) & (SzemelyData['DATE'] <= end_date) & (SzemelyData['MG05'] == Border) & (SzemelyData.MG02.isin(Nationality)) & (SzemelyData['GADC041'] >= filter[0]) & (SzemelyData['GADC041'] <= filter[1])], x = "DATE", y = "GADC041", color = "MG02", facet_row = "MG58", markers = True, 
                                  title = "Személyforgalom ki- és belépő személyek vonaldiagramja")
      st.plotly_chart(fig)
        
    elif (Diagram == 'Pont'):
      fig = px.scatter(SzemelyData[(SzemelyData['DATE'] >= start_date) & (SzemelyData['DATE'] <= end_date) & (SzemelyData['MG05'] == Border) & (SzemelyData.MG02.isin(Nationality)) & (SzemelyData['GADC041'] >= filter[0]) & (SzemelyData['GADC041'] <= filter[1])], x = "DATE", y = "GADC041", color = "MG02", facet_row = "MG58",
                                  title = "Személyforgalom ki- és belépő személyek pontdiagramja")
      st.plotly_chart(fig)
        
    elif (Diagram == 'Tableau'):
      renderer = get_pyg_renderer()
      renderer.explorer()
        
    elif (Diagram == 'Dekompozíció'):
      SzemelyData = SzemelyData[(SzemelyData['MG05'] == Border)]
      SzemelyData = SzemelyData[(SzemelyData.MG02.isin(Nationality))]
      SzemelyData = SzemelyData[(SzemelyData['DATE'] >= start_date) & (SzemelyData['DATE'] <= end_date) & (SzemelyData['GADC041'] >= filter[0]) & (SzemelyData['GADC041'] <= filter[1])]
      SzemelyData = SzemelyData.drop(columns = ['MG05', 'MG02'])
      SzemelyData = SzemelyData.groupby(['DATE', 'MG58']).agg({'GADC041': 'sum'}).reset_index()
      # print(SzemelyData.columns)
      
      tdi = pd.DatetimeIndex(SzemelyData['DATE']) # SzemelyData.DATE
      SzemelyData.set_index(tdi, inplace = True)
      SzemelyData.drop(columns = 'DATE', inplace = True)
      SzemelyData.index.name = 'datetimeindex'
      
      SzemelyData = SzemelyData.pivot(columns = 'MG58', values = 'GADC041') # index = 'DATE', 
  
      SzemelyData = SzemelyData.explode(['Belépő', 'Kilépő']) 
      SzemelyData.ffill(inplace = True) # fillna(method = 'ffill', 
      
      if (Direction == 'Belépő'): 
        res = sm.tsa.seasonal_decompose(SzemelyData['Belépő'], model = 'additive', period = 12) # multiplicative , 'Kilépő'
        resplot = res.plot()
        st.plotly_chart(resplot)
      elif (Direction == 'Kilépő'):
        res = sm.tsa.seasonal_decompose(SzemelyData['Kilépő'], model = 'additive', period = 12) # multiplicative , 'Kilépő'
        resplot = res.plot()
        st.plotly_chart(resplot)
        
  except:
    st.error('A diagram nem megjeleníthető az adott beállításokkal!')

elif selected == 'Jármű': 

  with st.sidebar:
    
    DateRange2 = st.date_input(label = 'Időszak kiválasztása', value = (datetime.date(2019, 1, 1), datetime.date(today.year, today.month, 1)), min_value = datetime.date(2019, 1, 1), max_value = datetime.date(today.year, today.month, 1), format = 'YYYY.MM.DD')
  
    try:
      start_date2 = DateRange2[0]
      end_date2 = DateRange2[1]
        
      Border_All2 = JarmuData[(JarmuData['DATE'] >= start_date2) & (JarmuData['DATE'] <= end_date2)]
      Border_All2 = Border_All2['MG05'].unique()
      Border2 = st.selectbox('Határátkelőhely', Border_All2)
    
    except:
      st.error('Kérlek, állíts be egy megfelelő időintervallumot!')
  
    try:
    
      options = JarmuData[(JarmuData['MG05'] == Border2) & (JarmuData['DATE'] >= start_date2) & (JarmuData['DATE'] <= end_date2)]
      Nationality_All2 = options['MG64'].unique().tolist()
      Nationality2 = st.multiselect('Honosság', Nationality_All2, Nationality_All2)
      
    except:
      st.error('Nem lehet honosságot kiválasztani az oldalszárnyon megadott beállításokkal!')
      
    Diagram2 = st.selectbox('Diagramtípus', ['Vonal', 'Pont', 'Tableau', 'Dekompozíció'])
    
    if (Diagram2 == 'Dekompozíció'): 
      Direction2 = st.selectbox('Irány', ['Belépő', 'Kilépő'])
  
  try:
      
    if (Diagram2 == 'Vonal'):
      fig = px.line(JarmuData[(JarmuData['DATE'] >= start_date2) & (JarmuData['DATE'] <= end_date2) & (JarmuData['MG05'] == Border2) & (JarmuData.MG64.isin(Nationality2))], x = 'DATE', y = 'GADF201', color = 'MG64', facet_row = 'MG58', facet_col = 'MG60', markers = True, 
                                  title = "Járműforgalom hazai és külföldi járművek eloszlása a határátkelés folyamán vonaldiagramja")
      st.plotly_chart(fig)
      
    elif (Diagram2 == 'Pont'):
      fig = px.scatter(JarmuData[(JarmuData['DATE'] >= start_date2) & (JarmuData['DATE'] <= end_date2) & (JarmuData['MG05'] == Border2) & (JarmuData.MG64.isin(Nationality2))], x = 'DATE', y = 'GADF201', color = 'MG64', facet_row = 'MG58', facet_col = 'MG60', 
                                  title = "Járműforgalom hazai és külföldi járművek eloszlása a határátkelés folyamán pontdiagramja")
      st.plotly_chart(fig)
      
    elif (Diagram2 == 'Tableau'):
      renderer = get_pyg_renderer2()
      renderer.explorer()
      
    elif (Diagram2 == 'Dekompozíció'):
      JarmuData = JarmuData[(JarmuData['MG05'] == Border2)]
      JarmuData = JarmuData[(JarmuData.MG64.isin(Nationality2))]
      JarmuData = JarmuData[(JarmuData['DATE'] >= start_date2) & (JarmuData['DATE'] <= end_date2)]
      JarmuData = JarmuData.drop(columns = ['MG05', 'MG64'])
      JarmuData = JarmuData.groupby(['DATE', 'MG58']).agg({'GADF201': 'sum'}).reset_index()
      # print(JarmuData.columns)
      
      tdi = pd.DatetimeIndex(JarmuData['DATE']) # SzemelyData.DATE
      JarmuData.set_index(tdi, inplace = True)
      JarmuData.drop(columns = 'DATE', inplace = True)
      JarmuData.index.name = 'datetimeindex'
      
      JarmuData = JarmuData.pivot(columns = 'MG58', values = 'GADF201') # index = 'DATE', 
  
      JarmuData = JarmuData.explode(['Belépő', 'Kilépő']) 
      JarmuData.ffill(inplace = True)
      
      if (Direction2 == 'Belépő'): 
        res = sm.tsa.seasonal_decompose(JarmuData['Belépő'], model = 'additive', period = 12) # multiplicative , 'Kilépő'
        resplot = res.plot()
        st.plotly_chart(resplot)
      elif (Direction2 == 'Kilépő'):
        res = sm.tsa.seasonal_decompose(JarmuData['Kilépő'], model = 'additive', period = 12) # multiplicative , 'Kilépő'
        resplot = res.plot()
        st.plotly_chart(resplot)
        
  except:
    st.error('A diagram nem megjeleníthető az adott beállításokkal!')
  # with tab2:
  #   ""
