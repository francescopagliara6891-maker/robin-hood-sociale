import streamlit as st
import pandas as pd
import plotly.express as px
import os

# --- 1. CONFIGURAZIONE ELITE ---
st.set_page_config(
    page_title="Robin Hood Sociale | Puglia",
    page_icon="🏹",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- COORDINATE STATICHE (Per la Mappa Strategica) ---
# Per evitare geocoding lento, mappiamo i comuni principali emersi dalla tua analisi
COORDINATE_COMUNI = {
    'LIZZANO': {'lat': 40.3906, 'lon': 17.4475},
    'GINOSA': {'lat': 40.5786, 'lon': 16.7561},
    'MARTINA FRANCA': {'lat': 40.7056, 'lon': 17.3364},
    'MANDURIA': {'lat': 40.4011, 'lon': 17.6339},
    'TARANTO': {'lat': 40.4644, 'lon': 17.2470},
    'SAN GIORGIO IONICO': {'lat': 40.4578, 'lon': 17.3789},
    'CASTELLANETA': {'lat': 40.6294, 'lon': 16.9381},
    'STATTE': {'lat': 40.5636, 'lon': 17.2047},
    'CAROSINO': {'lat': 40.4689, 'lon': 17.3986},
    'PULSANO': {'lat': 40.3833, 'lon': 17.3564},
    'MASSAFRA': {'lat': 40.5894, 'lon': 17.1128},
    'GROTTAGLIE': {'lat': 40.5333, 'lon': 17.4333},
    'LATERZA': {'lat': 40.6283, 'lon': 16.8000},
    'CRISPIANO': {'lat': 40.6053, 'lon': 17.2333},
    'PALAGIANO': {'lat': 40.5769, 'lon': 17.0475},
    'SAVA': {'lat': 40.4039, 'lon': 17.5583}
}

# --- 2. CARICAMENTO DATI ---
@st.cache_data
def load_data():
    # Percorso relativo per trovare il file nella cartella 'data'
    file_path = os.path.join('data', 'RobinHood_Elite_Data.xlsx')
    
    if not os.path.exists(file_path):
        st.error(f"❌ Errore: Non trovo il file '{file_path}'. Assicurati di aver eseguito lo script 'process_data.py'.")
        return None
    
    df = pd.read_excel(file_path)
    
    # Aggiungiamo Lat/Lon ai comuni per la mappa
    df['lat'] = df['Comune'].str.upper().map(lambda x: COORDINATE_COMUNI.get(x, {}).get('lat'))
    df['lon'] = df['Comune'].str.upper().map(lambda x: COORDINATE_COMUNI.get(x, {}).get('lon'))
    
    return df

df_full = load_data()

# --- 3. SIDEBAR E INFO ---
with st.sidebar:
    st.title("🏹 Robin Hood Sociale")
    st.markdown("""
    **Missione:**
    Trasformare i beni confiscati alle mafie in centri per l'inclusione sociale.
    
    **Algoritmo Elite:**
    Incrocia il *Bisogno* (mancanza di servizi) con la *Risorsa* (immobili vuoti).
    """)
    st.divider()
    st.info("💡 **Lo sapevi?** Lizzano ha un punteggio di opportunità critico.")

# --- 4. MAIN DASHBOARD ---
if df_full is not None:
    st.title("🗺️ Mappa delle Opportunità Sociali")
    st.markdown("Analisi strategica per la riqualificazione dei beni confiscati in provincia di Taranto.")
    
    # KPI GENERALI
    col1, col2, col3 = st.columns(3)
    tot_beni = len(df_full)
    top_comune = df_full.sort_values('ROBIN_HOOD_SCORE', ascending=False).iloc[0]['Comune']
    max_score = df_full['ROBIN_HOOD_SCORE'].max()
    
    col1.metric("🏠 Beni Confiscati Censiti", tot_beni)
    col2.metric("🏆 Comune Prioritario", top_comune)
    col3.metric("🔥 Opportunity Score Max", f"{max_score}")

    st.divider()

    # --- SEZIONE 1: LA MAPPA A BOLLE ---
    st.subheader("📍 Radar del Territorio")
    
    # Creiamo un dataset raggruppato per la mappa
    df_map = df_full.groupby('Comune').agg({
        'ROBIN_HOOD_SCORE': 'max',
        'NUM_SERVIZI': 'max',
        'Comune': 'count', # Conta beni
        'lat': 'max',
        'lon': 'max'
    }).rename(columns={'Comune': 'NUM_BENI'}).reset_index()
    
    # Filtriamo solo quelli con coordinate
    df_map = df_map.dropna(subset=['lat'])

    fig = px.scatter_mapbox(
        df_map,
        lat="lat",
        lon="lon",
        size="ROBIN_HOOD_SCORE", # La grandezza della bolla dipende dallo Score!
        color="ROBIN_HOOD_SCORE",
        hover_name="Comune",
        hover_data={"NUM_BENI": True, "NUM_SERVIZI": True, "lat": False, "lon": False},
        color_continuous_scale="RdYlGn_r", # Rosso = Alto Score (Urgente), Verde = Basso
        size_max=40,
        zoom=9,
        height=500
    )
    fig.update_layout(mapbox_style="open-street-map", margin={"r":0,"t":0,"l":0,"b":0})
    st.plotly_chart(fig, use_container_width=True)

    # --- SEZIONE 2: ANALISI TATTICA ---
    st.divider()
    st.subheader("🔎 Ispezione Tattica")
    
    lista_comuni = sorted(df_full['Comune'].unique())
    selected_city = st.selectbox("Seleziona un Comune per analizzare i beni:", lista_comuni, index=lista_comuni.index('Lizzano') if 'Lizzano' in lista_comuni else 0)
    
    # Filtriamo i dati
    dati_citta = df_full[df_full['Comune'] == selected_city]
    score_citta = dati_citta.iloc[0]['ROBIN_HOOD_SCORE']
    n_servizi = dati_citta.iloc[0]['NUM_SERVIZI']
    
    # Box Informativo
    c1, c2 = st.columns([1, 2])
    with c1:
        if score_citta > 100:
            st.error(f"### Score: {score_citta}\n🚨 **PRIORITÀ MASSIMA**")
        elif score_citta > 50:
            st.warning(f"### Score: {score_citta}\n⚠️ **ALTO POTENZIALE**")
        else:
            st.success(f"### Score: {score_citta}\n✅ **SITUAZIONE STABILE**")
        
        st.write(f"**Servizi Sociali Attivi:** {int(n_servizi)}")
        st.write(f"**Beni Confiscati Disponibili:** {len(dati_citta)}")

    with c2:
        st.info("👇 **Lista Immobili Disponibili:**")
        st.dataframe(
            dati_citta[['Indirizzo', 'Tipologia', 'Metri quadri/Consistenza', 'Categoria catastale']],
            hide_index=True,
            use_container_width=True
        )

    # --- SEZIONE 3: AZIONE (GENERATORE PEC) ---
    st.divider()
    st.subheader("✉️ Azione Civica: Genera Proposta")
    
    bene_scelto = st.selectbox("Per quale immobile vuoi proporre un progetto?", dati_citta['Indirizzo'].unique())
    progetto_tipo = st.selectbox("Cosa vorresti realizzarci?", ["Centro Diurno Disabili", "Dopo di Noi (Autonomia)", "Centro Antiviolenza", "Co-working Sociale"])
    
    if st.button("📝 Genera Bozza PEC"):
        bozza_pec = f"""
        OGGETTO: Proposta di riutilizzo sociale bene confiscato sito in {selected_city}, {bene_scelto}
        
        Spett.le Sindaco del Comune di {selected_city},
        
        Con la presente, in qualità di cittadino attivo,
        PREMESSO CHE
        dal monitoraggio civico "Robin Hood" risulta che nel Vostro comune vi è una carenza di servizi sociali ({int(n_servizi)} attivi) a fronte di una disponibilità di beni confiscati;
        
        SI PROPONE
        di valutare l'assegnazione dell'immobile sito in {bene_scelto} per la realizzazione di un "{progetto_tipo}".
        
        L'immobile risulta attualmente inutilizzato e potrebbe rispondere immediatamente ai bisogni della comunità.
        
        Cordiali Saluti,
        [Firma]
        """
        st.text_area("Copia e Incolla questa mail:", bozza_pec, height=300)
        st.success("Bozza generata! Copiala e inviala via PEC al Comune.")

else:
    st.stop()