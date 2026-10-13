import streamlit as st
from streamlit_option_menu import option_menu
from databricks import sql
import pandas as pd
import datetime
import plotly.express as px
import statsmodels.api as sm

@st.cache_resource
def get_databricks_connection():
  return sql.connect(
  server_hostname = st.secrets["DATABRICKS_SERVER_HOSTNAME"], 
  http_path = st.secrets["DATABRICKS_HTTP_PATH"], 
  access_token = st.secrets["DATABRICKS_TOKEN"]
  )
  
@st.cache_data
def load_databricks_SzemelyData():
  conn = get_databricks_connection()
  cursor = conn.cursor()
  cursor.execute("select * from GA.SZEMELY_FORGALOM")
  Szemely = cursor.fetchall_arrow().to_pandas()
  
  cursor.close()
  
  Szemely['DATE'] = pd.to_datetime(Szemely['TEV'].astype(str) + '/' + Szemely['MHO'].astype(str) + '/01').dt.date
  Szemely = Szemely.drop(columns = ['TEV', 'MHO'])
  
  return Szemely

@st.cache_data
def load_databricks_JarmuData():
  conn = get_databricks_connection()
  cursor = conn.cursor()
  cursor.execute("select * from GA.JARMU_FORGALOM")
  Jarmu = cursor.fetchall_arrow().to_pandas()
  
  cursor.close()
  conn.close()
  
  Jarmu['DATE'] = pd.to_datetime(Jarmu['TEV'].astype(str) + '/' + Jarmu['MHO'].astype(str) + '/01').dt.date
  Jarmu = Jarmu.drop(columns = ['TEV', 'MHO'])
  
  return Jarmu


SzemelyData = load_databricks_SzemelyData()
JarmuData = load_databricks_JarmuData()

st.set_page_config(
  layout = 'wide',
  page_title = 'OSAP 1222 - Személy- és járműforgalmi jelentés',
  page_icon = 'https://map.ksh.hu/timea/images/shortcut.ico',
  menu_items = {'Get help': 'mailto:sz.adam1989@gmail.com',
                'Report a bug': 'mailto:sz.adam1989i@gmail.com',
                'About': 'Ez a webalkalmazás az 1222-es OSAP számú adatgyűjtés adatait tartalmazza azon határátkelőhelyekre, amelyek nincsenek benne a Schengeni övezetben 2025. január 1-e óta.'}
  )

selected = option_menu(None, ['Személy', 'Jármű'], icons = ['person-circle', 'ev-front'], menu_icon = 'cast', default_index = 0, orientation = 'horizontal', 
  styles = {"container": {"padding": "0!important", "background-color": "#f0f2f6"},
        "icon": {"color": "#ff4b4b", "font-size": "25px"}, # Az ikonok színe (pl. pirosas)
        "nav-link": {
            "font-size": "18px", 
            "text-align": "center", 
            "margin": "5px", 
            "--hover-color": "#dee2e6"
        },
        "nav-link-selected": {
            "background-color": "#003366", # A kiválasztott gomb háttere (KSH sötétkék)
            "color": "white",              # A szöveg színe a kijelölt gombon
            "font-weight": "bold"
        },
      })

today = datetime.datetime.now()

if selected == 'Személy': 

  with st.sidebar:
    
    DateRange = st.date_input(label = 'Időszak kiválasztása', value = (datetime.date(2019, 1, 1), datetime.date(today.year, today.month, 1)), min_value = datetime.date(1998, 1, 1), max_value = datetime.date(today.year, today.month, 1), format = 'YYYY.MM.DD')
    
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
    
    Diagram = st.selectbox('Diagramtípus', ['Vonal', 'Pont', 'Dekompozíció']) 
    
    if (Diagram == 'Dekompozíció'): 
      Direction = st.selectbox('Irány', ['Belépő', 'Kilépő'])
    
  try:
      
    Szemely_Szurt = SzemelyData[(SzemelyData['DATE'] >= start_date) & (SzemelyData['DATE'] <= end_date) & (SzemelyData['MG05'] == Border) & (SzemelyData.MG02.isin(Nationality)) & (SzemelyData['GADC041'] >= filter[0]) & (SzemelyData['GADC041'] <= filter[1])]
    
    if (Diagram != 'Dekompozíció'):
      belepo_data = Szemely_Szurt[Szemely_Szurt['MG58'] == "Belépő"]
      kilepo_data = Szemely_Szurt[Szemely_Szurt['MG58'] == "Kilépő"]
      
      kpi1, kpi2, kpi3, kpi4, kpi5 = st.columns(5)
      with kpi1:
        st.metric("Összesített forgalom (fő)", f"{int(Szemely_Szurt['GADC041'].sum()):,}".replace(",", " "))
      with kpi2:
        max_belepo_row = belepo_data.loc[belepo_data['GADC041'].idxmax()] if not belepo_data.empty else None
        st.metric("Max Belépő forgalom", f"{int(max_belepo_row['GADC041']):,}".replace(",", " ") if max_belepo_row is not None else "0", help=f"Dátum: {max_belepo_row['DATE']}" if max_belepo_row is not None else "")
      
      with kpi3:
        max_kilepo_row = kilepo_data.loc[kilepo_data['GADC041'].idxmax()] if not kilepo_data.empty else None
        st.metric("Max Kilépő forgalom", f"{int(max_kilepo_row['GADC041']):,}".replace(",", " ") if max_kilepo_row is not None else "0", help=f"Dátum: {max_kilepo_row['DATE']}" if max_kilepo_row is not None else "")
      
      with kpi4:
        st.metric("Átlag Belépő (havi)", f"{int(belepo_data['GADC041'].mean()):,}".replace(",", " ") if not belepo_data.empty else "0")
      
      with kpi5:
        st.metric("Átlag Kilépő (havi)", f"{int(kilepo_data['GADC041'].mean()):,}".replace(",", " ") if not kilepo_data.empty else "0")
    
    if (Diagram == 'Vonal'):
      fig = px.line(Szemely_Szurt, x = "DATE", y = "GADC041", color = "MG02", facet_row = "MG58", markers = True, 
      title = "Személyforgalom ki- és belépő személyek vonaldiagramja")
      st.plotly_chart(fig)
        
    elif (Diagram == 'Pont'):
      plot_df = Szemely_Szurt.copy()
      # Python date-ből pandas datetime64-et csinálunk, amit a trendline már megért
      plot_df['DATE_PLOT'] = pd.to_datetime(plot_df['DATE'])
      fig = px.scatter(plot_df, x = "DATE_PLOT", y = "GADC041", color = "MG02", facet_row = "MG58", trendline = "ols", # trendline = "rolling", trendline_options = dict(window = 3), 
      title = "Személyforgalom ki- és belépő személyek pontdiagramja")
      fig.update_xaxes(title_text = "DATE") # Visszaírjuk a tengely feliratát szépre
      st.plotly_chart(fig)
        
    elif (Diagram == 'Dekompozíció'):
      Szemely = SzemelyData[(SzemelyData['MG05'] == Border)]
      Szemely = Szemely[(Szemely.MG02.isin(Nationality))]
      Szemely = Szemely[(Szemely['DATE'] >= start_date) & (Szemely['DATE'] <= end_date) & (Szemely['GADC041'] >= filter[0]) & (Szemely['GADC041'] <= filter[1])]
      Szemely = Szemely.drop(columns = ['MG05', 'MG02'])
      Szemely = Szemely.groupby(['DATE', 'MG58']).agg({'GADC041': 'sum'}).reset_index()
      
      tdi = pd.DatetimeIndex(Szemely['DATE'])
      Szemely.set_index(tdi, inplace = True)
      Szemely.drop(columns = 'DATE', inplace = True)
      Szemely.index.name = 'datetimeindex'
      
      Szemely = Szemely.pivot(columns = 'MG58', values = 'GADC041')
  
      Szemely = Szemely.explode(['Belépő', 'Kilépő']) 
      Szemely.ffill(inplace = True)
      Szemely.bfill(inplace = True)
      
      # Beállítjuk a havi frekvenciát ('MS' = Month Start), a hiányzó hónapokat pedig 0-val töltjük fel
      # Szemely = Szemely.asfreq('MS', fill_value = 0)
      
      # ELLENŐRZÉS
      if len(Szemely) < 24:
        st.warning(f"A kiválasztott határátkelőhöz csak {len(Szemely)} hónapnyi adat érhető el. A dekompozícióhoz legalább 24 hónap szükséges!")
      
      if (Direction == 'Belépő'): 
        res = sm.tsa.seasonal_decompose(Szemely['Belépő'], model = 'additive', period = 12) # multiplicative , 'Kilépő'
        fig = res.plot()
        st.plotly_chart(fig)
      elif (Direction == 'Kilépő'):
        res = sm.tsa.seasonal_decompose(Szemely['Kilépő'], model = 'additive', period = 12) # multiplicative , 'Kilépő'
        fig = res.plot()
        st.plotly_chart(fig)
        
    if (Diagram != 'Dekompozíció'):
      st.download_button(
        label = "📥 Szűrt adatok letöltése CSV formátumban",
        data = Szemely_Szurt.to_csv(index = False, sep = ';').encode('utf-8-sig'),
        file_name = f"OSAP1222_Szemely_szurt_{Border}_{datetime.date.today()}.csv",
        mime = "text/csv"
      )

  except Exception as e:
    st.error(f"A diagram nem megjeleníthető az adott beállításokkal! A hiba oka: {e}")

elif selected == 'Jármű': 

  with st.sidebar:
    
    DateRange2 = st.date_input(label = 'Időszak kiválasztása', value = (datetime.date(2019, 1, 1), datetime.date(today.year, today.month, 1)), min_value = datetime.date(2004, 1, 1), max_value = datetime.date(today.year, today.month, 1), format = 'YYYY.MM.DD')
  
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
      
    Diagram2 = st.selectbox('Diagramtípus', ['Vonal', 'Pont', 'Dekompozíció']) # 'Tableau',
    
    if (Diagram2 == 'Dekompozíció'): 
      Direction2 = st.selectbox('Irány', ['Belépő', 'Kilépő'])
  
  try:
    
    Jarmu_Szurt = JarmuData[(JarmuData['DATE'] >= start_date2) & (JarmuData['DATE'] <= end_date2) & (JarmuData['MG05'] == Border2) & (JarmuData.MG64.isin(Nationality2))]
    
    if (Diagram2 != 'Dekompozíció'):
      belepo_data = Jarmu_Szurt[Jarmu_Szurt['MG58'] == "Belépő"]
      kilepo_data = Jarmu_Szurt[Jarmu_Szurt['MG58'] == "Kilépő"]
      
      kpi1, kpi2, kpi3, kpi4, kpi5 = st.columns(5)
      with kpi1:
        st.metric("Összesített forgalom (fő)", f"{int(Jarmu_Szurt['GADF201'].sum()):,}".replace(",", " "))
      with kpi2:
        max_belepo_row = belepo_data.loc[belepo_data['GADF201'].idxmax()] if not belepo_data.empty else None
        st.metric("Max Belépő forgalom", f"{int(max_belepo_row['GADF201']):,}".replace(",", " ") if max_belepo_row is not None else "0", help=f"Dátum: {max_belepo_row['DATE']}" if max_belepo_row is not None else "")
      
      with kpi3:
        max_kilepo_row = kilepo_data.loc[kilepo_data['GADF201'].idxmax()] if not kilepo_data.empty else None
        st.metric("Max Kilépő forgalom", f"{int(max_kilepo_row['GADF201']):,}".replace(",", " ") if max_kilepo_row is not None else "0", help=f"Dátum: {max_kilepo_row['DATE']}" if max_kilepo_row is not None else "")
      
      with kpi4:
        st.metric("Átlag Belépő (havi)", f"{int(belepo_data['GADF201'].mean()):,}".replace(",", " ") if not belepo_data.empty else "0")
      
      with kpi5:
        st.metric("Átlag Kilépő (havi)", f"{int(kilepo_data['GADF201'].mean()):,}".replace(",", " ") if not kilepo_data.empty else "0")
    
    if (Diagram2 == 'Vonal'):
      fig = px.line(Jarmu_Szurt, x = 'DATE', y = 'GADF201', color = 'MG64', facet_row = 'MG58', facet_col = 'MG60', markers = True, 
      title = "Járműforgalom hazai és külföldi járművek eloszlása a határátkelés folyamán vonaldiagramja")
      st.plotly_chart(fig)
      
    elif (Diagram2 == 'Pont'):
      plot_df = Jarmu_Szurt.copy()
      # Python date-ből pandas datetime64-et csinálunk, amit a trendline már megért
      plot_df['DATE_PLOT'] = pd.to_datetime(plot_df['DATE'])
      fig = px.scatter(plot_df, x = 'DATE_PLOT', y = 'GADF201', color = 'MG64', facet_row = 'MG58', facet_col = 'MG60', trendline = "ols", # trendline = "rolling", trendline_options = dict(window = 3),
      title = "Járműforgalom hazai és külföldi járművek eloszlása a határátkelés folyamán pontdiagramja")
      fig.update_xaxes(title_text = "DATE") # Visszaírjuk a tengely feliratát szépre
      st.plotly_chart(fig)
      
    elif (Diagram2 == 'Dekompozíció'):
      Jarmu = JarmuData[(JarmuData['MG05'] == Border2)]
      Jarmu = Jarmu[(Jarmu.MG64.isin(Nationality2))]
      Jarmu = Jarmu[(Jarmu['DATE'] >= start_date2) & (Jarmu['DATE'] <= end_date2)]
      Jarmu = Jarmu.drop(columns = ['MG05', 'MG64'])
      Jarmu = Jarmu.groupby(['DATE', 'MG58']).agg({'GADF201': 'sum'}).reset_index()
      
      tdi = pd.DatetimeIndex(Jarmu['DATE']) # SzemelyData.DATE
      Jarmu.set_index(tdi, inplace = True)
      Jarmu.drop(columns = 'DATE', inplace = True)
      Jarmu.index.name = 'datetimeindex'
      
      Jarmu = Jarmu.pivot(columns = 'MG58', values = 'GADF201') # index = 'DATE', 
  
      Jarmu = Jarmu.explode(['Belépő', 'Kilépő']) 
      Jarmu.ffill(inplace = True)
      Jarmu.bfill(inplace = True)
      
      # Beállítjuk a havi frekvenciát ('MS' = Month Start), a hiányzó hónapokat pedig 0-val töltjük fel
      # Jarmu = Jarmu.asfreq('MS', fill_value = 0)
      
      # ELLENŐRZÉS
      if len(Jarmu) < 24:
        st.warning(f"A kiválasztott határátkelőhöz csak {len(Jarmu)} hónapnyi adat érhető el. A dekompozícióhoz legalább 24 hónap szükséges!")
      
      if (Direction2 == 'Belépő'): 
        res = sm.tsa.seasonal_decompose(Jarmu['Belépő'], model = 'additive', period = 12) # multiplicative , 'Kilépő'
        fig = res.plot()
        st.plotly_chart(fig)
      elif (Direction2 == 'Kilépő'):
        res = sm.tsa.seasonal_decompose(Jarmu['Kilépő'], model = 'additive', period = 12) # multiplicative , 'Kilépő'
        fig = res.plot()
        st.plotly_chart(fig)
    
    if (Diagram2 != 'Dekompozíció'):
      st.download_button(
        label = "📥 Szűrt adatok letöltése CSV formátumban",
        data = Jarmu_Szurt.to_csv(index = False, sep = ';').encode('utf-8-sig'),
        file_name = f"OSAP1222_Jarmu_szurt_{Border2}_{datetime.date.today()}.csv",
        mime = "text/csv"
      )
      
  except Exception as e:
    st.error(f"A diagram nem megjeleníthető az adott beállításokkal! A hiba oka: {e}")
