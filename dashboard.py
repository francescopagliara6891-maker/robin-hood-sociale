import streamlit as st
import pandas as pd
import plotly.express as px
import numpy as np

# --- CONFIGURAZIONE ELITE ---
st.set_page_config(page_title="Robin Hood Sociale | Puglia", page_icon="💎", layout="wide")

# --- LINK DATI (IL CUORE DELL'AUTOMAZIONE) ---
# 1. LINK DIRETTO REGIONE PUGLIA (Incolla qui quello copiato col tasto destro!)
URL_SERVIZI_SOCIALI = "https://dati.puglia.it/ckan/dataset/98118aea-0ec5-40b8-a2c9-944619b9383f/resource/382c8bba-7faa-49c8-803f-678a6f74e75d/download/catalogo-offerta-servizi-disabili-e-anziani.csv"

# 2. FILE LOCALE/GITHUB (Dati Mafia Blindati)
# Questo file deve essere nella repository GitHub insieme al codice
FILE_BENI_CONFISCATI = "totale__immobili-destinato.csv" 

# --- COORDINATE STRATEGICHE (TARANTO PROVINCE) ---
COORDINATE_COMUNI = {
    'LIZZANO': {'lat': 40.3906, 'lon': 17.4475},
    'GINOSA': {'lat': 40.5786, 'lon': 16.7561},
    'MARTINA FRANCA': {'lat': 40.7056, 'lon': 17.3364},
    'MANDURIA': {'lat': 40.4011, 'lon': 17.6339},
    'TARANTO': {'lat': 40.4644, 'lon': 17.2470},
    'SAN GIORGIO IONICO': {'lat': 40.4578, 'lon': 17.3789},
    'CASTELLANETA': {'lat': 40.6294, 'lon': 16.9381},
    'STATTE': {'lat': 40.5636, 'lon': 17.2047},
    'MASSAFRA': {'lat': 40.5894, 'lon': 17.1128},
    'GROTTAGLIE': {'lat': 40.5333, 'lon': 17.4333},
    # Aggiungi altri se necessario...
}

@st.cache_data(ttl=3600) # Aggiorna la cache ogni ora (Automazione!)
def load_and_process_data():
    try:
        # 1. Carica Servizi Sociali (LIVE dal Web)
        df_sociali = pd.read_csv(URL_SERVIZI_SOCIALI, sep=None, engine='python', on_bad_lines='skip')
        
        # 2. Carica Beni Confiscati (DAL FILE SICURO)
        df_beni = pd.read_csv(FILE_BENI_CONFISCATI, sep=None, engine='python', on_bad_lines='skip', encoding='utf-8')
        
        # --- ELABORAZIONE REAL-TIME (IL CERVELLONE) ---
        
        # Filtro Taranto e Standardizzazione
        df_beni['Provincia'] = df_beni['Provincia'].astype(str).str.upper().str.strip()
        df_taranto = df_beni[df_beni['Provincia'] == 'TARANTO'].copy()
        
        df_taranto['CITY_KEY'] = df_taranto['Comune'].astype(str).str.upper().str.strip()
        df_sociali['CITY_KEY'] = df_sociali['COMUNE'].astype(str).str.upper().str.strip()
        
        # Incrocio Dati
        risorse = df_taranto.groupby('CITY_KEY').size().reset_index(name='NUM_BENI')
        bisogni = df_sociali.groupby('CITY_KEY').size().reset_index(name='NUM_SERVIZI')
        
        df_merge = pd.merge(risorse, bisogni, on='CITY_KEY', how='outer').fillna(0)
        
        # Calcolo Score Robin Hood
        df_merge['SCORE'] = (df_merge['NUM_BENI'] * 10) / (df_merge['NUM_SERVIZI'] + 1)
        df_merge['SCORE'] = df_merge['SCORE'].round(1)
        
        # Aggiungo coordinate manuali per la mappa
        df_merge['lat'] = df_merge['CITY_KEY'].map(lambda x: COORDINATE_COMUNI.get(x, {}).get('lat'))
        df_merge['lon'] = df_merge['CITY_KEY'].map(lambda x: COORDINATE_COMUNI.get(x, {}).get('lon'))
        
        # Dataset dettagliato per le tabelle
        df_dettaglio = pd.merge(df_taranto, df_merge[['CITY_KEY', 'SCORE', 'NUM_SERVIZI']], on='CITY_KEY', how='left')
        
        return df_merge, df_dettaglio

    except Exception as e:
        st.error(f"⚠️ Errore critico nel caricamento dati: {e}")
        return None, None

# --- CARICAMENTO ---
df_map_data, df_detail_data = load_and_process_data()

# --- INTERFACCIA DASHBOARD ---
if df_detail_data is not None:
    with st.sidebar:
        st.title("💎 Robin Hood Sociale")
        st.info("Sistema automatizzato di monitoraggio beni confiscati e welfare.")
        st.markdown(f"**Stato Dati:**\n\n🟢 Welfare: ONLINE (Regione Puglia)\n🔒 Beni Confiscati: SECURE (ANBSC)")
        st.divider()
        st.write("Designed for Public Administration Excellence")

    st.title("🏛️ Cruscotto Strategico Provinciale")
    
    # KPI
    best_city = df_map_data.sort_values('SCORE', ascending=False).iloc[0]
    
    k1, k2, k3 = st.columns(3)
    k1.metric("Patrimonio Confiscato (Immobili)", int(df_map_data['NUM_BENI'].sum()))
    k2.metric("Comune con Maggiore Urgenza", best_city['CITY_KEY'], delta=f"Score: {best_city['SCORE']}")
    k3.metric("Servizi Sociali Monitorati", int(df_map_data['NUM_SERVIZI'].sum()))
    
    st.markdown("---")
    
    # MAPPA
    st.subheader("📍 Mappa delle Priorità d'Intervento")
    st.markdown("*Le bolle più grandi e rosse indicano dove c'è abbondanza di immobili ma carenza di servizi.*")
    
    map_clean = df_map_data.dropna(subset=['lat'])
    
    fig = px.scatter_mapbox(
        map_clean, lat="lat", lon="lon", size="SCORE", color="SCORE",
        hover_name="CITY_KEY",
        hover_data={"NUM_BENI": True, "NUM_SERVIZI": True, "lat": False, "lon": False},
        color_continuous_scale="RdYlGn_r", size_max=50, zoom=9, height=600
    )
    fig.update_layout(mapbox_style="open-street-map", margin={"r":0,"t":0,"l":0,"b":0})
    st.plotly_chart(fig, use_container_width=True)
    
    # DETTAGLIO COMUNE
    st.markdown("---")
    st.subheader("🔎 Analisi di Dettaglio & Generazione Atti")
    
    sel_comune = st.selectbox("Seleziona Amministrazione Comunale:", sorted(df_detail_data['CITY_KEY'].unique()))
    
    dati_comune = df_detail_data[df_detail_data['CITY_KEY'] == sel_comune]
    
    c1, c2 = st.columns([1, 1])
    
    with c1:
        st.dataframe(dati_comune[['Indirizzo', 'Tipologia', 'Categoria catastale']], use_container_width=True)
        
    with c2:
        st.info("🤖 **Assistente Amministrativo**")
        immobile = st.selectbox("Seleziona Immobile per Proposta:", dati_comune['Indirizzo'].unique())
        
        if st.button("Genera Bozza Istanza"):
            testo = f"""AL SIG. SINDACO DEL COMUNE DI {sel_comune}
            OGGETTO: Istanza di riutilizzo sociale bene confiscato - {immobile}
            
            Il sottoscritto cittadino, preso atto della disponibilità del bene in oggetto
            e rilevata la carenza di servizi nel monitoraggio regionale...
            CHIEDE
            l'assegnazione per finalità sociali ai sensi del Codice Antimafia.
            """
            st.text_area("Testo Proposta:", testo, height=200)

else:
    st.stop()