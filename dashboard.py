import streamlit as st
import pandas as pd
import plotly.express as px
import os

# --- 1. CONFIGURAZIONE & BRANDING ---
st.set_page_config(
    page_title="Robin Hood | Asset Reallocation",
    page_icon="🏹",
    layout="wide"
)

def add_branding():
    st.sidebar.image("https://img.icons8.com/color/96/engineering.png", width=50)
    st.sidebar.markdown("""
    <div style="text-align: left;">
        <h3 style="margin:0; padding:0;">ROBIN HOOD</h3>
        <p style="font-size: 12px; color: gray;">
            Social Asset Management<br>
            <b>Ing. Francesco</b>
        </p>
    </div>
    """, unsafe_allow_html=True)
    st.sidebar.markdown("---")

add_branding()

# --- 2. LOGICA "SMART ADVISOR" (Il Cervello Sociale) ---
def suggerisci_utilizzo(tipo, superficie):
    """
    Analizza il tipo di immobile e suggerisce lo scopo sociale ideale.
    """
    tipo = str(tipo).lower()
    try:
        mq = float(superficie)
    except:
        mq = 0

    suggerimenti = []
    
    # Logica Abitativa
    if 'abitazion' in tipo or 'appartamento' in tipo or 'villa' in tipo:
        if mq > 100:
            suggerimenti.append("🏠 **Dopo di Noi:** Co-housing per 4-5 persone con disabilità.")
            suggerimenti.append("👵 **Senior Housing:** Convivenza guidata per anziani soli.")
        else:
            suggerimenti.append("🆘 **Emergenza Abitativa:** Alloggio temporaneo per famiglie sfrattate.")
            suggerimenti.append("🛡️ **Rifugio:** Accoglienza donne vittime di violenza.")
            
    # Logica Terreni
    elif 'terren' in tipo or 'agricol' in tipo:
        suggerimenti.append("🚜 **Agricoltura Sociale:** Orti urbani e pet-therapy.")
        suggerimenti.append("🌳 **Parco Inclusivo:** Area verde senza barriere architettoniche.")
        
    # Logica Commerciale/Altro
    elif 'garage' in tipo or 'box' in tipo:
        suggerimenti.append("📦 **Magazzino Solidale:** Banco alimentare o deposito ausili.")
    elif 'negozi' in tipo or 'locale' in tipo:
        suggerimenti.append("🛠️ **Laboratorio Protetto:** Inserimento lavorativo ragazzi speciali.")
        suggerimenti.append("📚 **Centro Aggregativo:** Biblioteca sociale o sala studio.")
    
    if not suggerimenti:
        suggerimenti.append("🏳️ **Uso Polivalente:** Da valutare in base agli impianti.")
        
    return suggerimenti

# --- 3. CARICAMENTO DATI ---
# LINK DIRETTO REGIONE PUGLIA (Inserisci qui il tuo link se è cambiato, altrimenti lo pesca dalla cache)
URL_SERVIZI_SOCIALI = "https://dati.puglia.it/ckan/dataset/catalogo-disabili-e-anziani/resource/382c8bba-7faa-49c8-803f-678a6f74e75d/download/catalogo-disabili-e-anziani.csv"
FILE_BENI_CONFISCATI = "totale__immobili-destinato.csv"

# COORDINATE COMUNI (Mapping Strategico)
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
    'PALAGIANO': {'lat': 40.5769, 'lon': 17.0475},
    'LATERZA': {'lat': 40.6283, 'lon': 16.8000},
    'SAVA': {'lat': 40.4039, 'lon': 17.5583},
    'MOTTOLA': {'lat': 40.6333, 'lon': 17.0333},
    'CASTELLANETA': {'lat': 40.6305, 'lon': 16.9395}
}

@st.cache_data
def load_and_process():
    try:
        # 1. Carica
        df_sociali = pd.read_csv(URL_SERVIZI_SOCIALI, sep=None, engine='python', on_bad_lines='skip')
        df_beni = pd.read_csv(FILE_BENI_CONFISCATI, sep=None, engine='python', on_bad_lines='skip', encoding='utf-8')
        
        # 2. Pulisci
        df_beni['Provincia'] = df_beni['Provincia'].astype(str).str.upper().str.strip()
        df_taranto = df_beni[df_beni['Provincia'] == 'TARANTO'].copy()
        df_taranto['CITY_KEY'] = df_taranto['Comune'].astype(str).str.upper().str.strip()
        df_sociali['CITY_KEY'] = df_sociali['COMUNE'].astype(str).str.upper().str.strip()
        
        # 3. Incrocia
        risorse = df_taranto.groupby('CITY_KEY').size().reset_index(name='NUM_BENI')
        bisogni = df_sociali.groupby('CITY_KEY').size().reset_index(name='NUM_SERVIZI')
        df_merge = pd.merge(risorse, bisogni, on='CITY_KEY', how='outer').fillna(0)
        
        # 4. Calcola Score (Algoritmo Robin Hood)
        df_merge['SCORE'] = (df_merge['NUM_BENI'] * 10) / (df_merge['NUM_SERVIZI'] + 1)
        df_merge['SCORE'] = df_merge['SCORE'].round(1)
        
        # 5. Coordinate
        df_merge['lat'] = df_merge['CITY_KEY'].map(lambda x: COORDINATE_COMUNI.get(x, {}).get('lat'))
        df_merge['lon'] = df_merge['CITY_KEY'].map(lambda x: COORDINATE_COMUNI.get(x, {}).get('lon'))
        
        # 6. Dataset Dettaglio
        df_dettaglio = pd.merge(df_taranto, df_merge[['CITY_KEY', 'SCORE', 'NUM_SERVIZI']], on='CITY_KEY', how='left')
        
        return df_merge, df_dettaglio
    except Exception as e:
        st.error(f"Errore caricamento dati: {e}")
        return None, None

df_map, df_detail = load_and_process()

if df_map is None:
    st.stop()

# --- 4. INTERFACCIA MAIN ---
st.title("🏹 Robin Hood - Asset Reallocation System")
st.markdown("Piattaforma di Intelligence per la riqualificazione dei beni confiscati.")

# KPI
best_city = df_map.sort_values('SCORE', ascending=False).iloc[0]
c1, c2, c3 = st.columns(3)
c1.metric("Patrimonio Disponibile", f"{int(df_map['NUM_BENI'].sum())} Immobili")
c2.metric("Comune Target Prioritario", best_city['CITY_KEY'], delta="Max Opportunity")
c3.metric("Copertura Welfare", f"{int(df_map['NUM_SERVIZI'].sum())} Centri Attivi")

# --- GUIDA TATTICA (Richiesta Utente) ---
with st.expander("📖 MANUALE DI LETTURA DASHBOARD (Clicca qui)"):
    st.markdown("""
    **Come usare questo strumento:**
    
    1. **IL PUNTEGGIO (Score):** Più alto è il numero, più urgente è l'intervento. Indica comuni con **tanti beni confiscati ma pochi servizi**.
    2. **LA MAPPA:** Le bolle rosse indicano le aree di intervento prioritario. Selezionando un comune, la mappa si focalizza sul bersaglio.
    3. **SMART ADVISOR:** Nella sezione dettaglio, il sistema **legge** le caratteristiche dell'immobile e ti suggerisce se è adatto per *Anziani, Disabili o Giovani*.
    """)

st.divider()

# --- SEZIONE FILTRI E MAPPA INTERATTIVA ---
col_sinistra, col_destra = st.columns([1, 2])

with col_sinistra:
    st.subheader("📍 Selettore Tattico")
    comuni_list = sorted(df_detail['CITY_KEY'].unique())
    selected_city = st.selectbox("Seleziona Comune:", comuni_list, index=comuni_list.index('LIZZANO') if 'LIZZANO' in comuni_list else 0)
    
    # Estrazione Dati Città
    city_data = df_map[df_map['CITY_KEY'] == selected_city]
    assets_city = df_detail[df_detail['CITY_KEY'] == selected_city]
    
    st.info(f"**Analisi {selected_city}:**")
    st.write(f"- Beni Confiscati: **{len(assets_city)}**")
    st.write(f"- Servizi Sociali: **{int(city_data['NUM_SERVIZI'].values[0])}**")
    st.write(f"- Robin Hood Score: **{city_data['SCORE'].values[0]}**")

with col_destra:
    # MAPPA INTELLIGENTE (Mostra solo il target o tutto se nulla selezionato)
    st.subheader("🗺️ Radar Territoriale")
    
    # Selezioniamo solo il comune scelto per evidenziarlo
    map_target = df_map[df_map['CITY_KEY'] == selected_city].dropna(subset=['lat'])
    
    if not map_target.empty:
        fig = px.scatter_mapbox(
            map_target, lat="lat", lon="lon", size="SCORE", color="SCORE",
            hover_name="CITY_KEY",
            color_continuous_scale="Reds", size_max=40, zoom=12, height=400 # Zoom alto sul comune
        )
        fig.update_layout(mapbox_style="open-street-map", margin={"r":0,"t":0,"l":0,"b":0})
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.warning("Coordinate geografiche per questo comune non disponibili nel sistema statico.")

st.divider()

# --- SEZIONE DETTAGLIO & SMART ADVISOR ---
st.subheader(f"🏠 Dettaglio Immobili & Destinazione Sociale ({selected_city})")

# Selettore Immobile specifico
indirizzi = assets_city['Indirizzo'].unique()
scelta_immobile = st.selectbox("Seleziona Indirizzo Immobile:", indirizzi)

# Recupero dati immobile
row_immobile = assets_city[assets_city['Indirizzo'] == scelta_immobile].iloc[0]
tipo_imm = row_immobile.get('Tipologia', 'N/D')
cat_imm = row_immobile.get('Categoria catastale', 'N/D')
mq_imm = row_immobile.get('Metri quadri/Consistenza', 0)

# Card Dettaglio
cc1, cc2 = st.columns([1, 1])

with cc1:
    st.markdown("#### 📋 Scheda Tecnica")
    st.write(f"**Indirizzo:** {scelta_immobile}")
    st.write(f"**Tipologia:** {tipo_imm}")
    st.write(f"**Categoria Catastale:** {cat_imm}")
    st.write(f"**Consistenza:** {mq_imm} (mq/vani)")

with cc2:
    st.markdown("#### 💡 Smart Advisor (Suggerimenti)")
    # CHIAMATA ALLA FUNZIONE INTELLIGENTE
    consigli = suggerisci_utilizzo(tipo_imm, mq_imm)
    for consiglio in consigli:
        st.success(consiglio)

# --- GENERATORE PEC (Action) ---
st.divider()
st.subheader("✉️ Azione: Genera Istanza")

proposta_scelta = st.selectbox("Quale utilizzo vuoi proporre?", [c.split("**")[1].split(":")[0] for c in consigli] + ["Altro"])

if st.button("📝 Genera Bozza PEC"):
    bozza = f"""
    ALLA C.A. SINDACO DI {selected_city}
    
    OGGETTO: Proposta di utilizzo sociale bene confiscato sito in {scelta_immobile}.
    
    Il sottoscritto cittadino,
    VISTO il bene confiscato alla criminalità organizzata situato in {scelta_immobile} (Tipologia: {tipo_imm});
    CONSIDERATA la carenza di servizi rilevata nel territorio;
    
    PROPONE
    di destinare l'immobile alla realizzazione di un progetto di "{proposta_scelta}",
    per rispondere ai bisogni delle categorie fragili (Anziani/Disabili/Giovani).
    
    Si allega alla presente...
    
    Cordiali Saluti,
    Ing. Francesco
    """
    st.text_area("Copia il testo:", bozza, height=300)
