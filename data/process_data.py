import pandas as pd
import numpy as np

print("⏳ Avvio Elaborazione Dati ELITE...")

# 1. CARICAMENTO DATI
# Carichiamo i Beni Confiscati (Il Dataset Gold)
try:
    df_beni = pd.read_csv('totale__immobili-destinato.csv', sep=None, engine='python', on_bad_lines='skip', encoding='utf-8')
    # Filtriamo solo TARANTO (Rimuoviamo spazi extra e standardizziamo)
    df_beni['Provincia'] = df_beni['Provincia'].astype(str).str.upper().str.strip()
    df_taranto = df_beni[df_beni['Provincia'] == 'TARANTO'].copy()
    print(f"✅ Beni Confiscati a Taranto trovati: {len(df_taranto)}")
except Exception as e:
    print(f"❌ Errore caricamento beni confiscati: {e}")
    exit()

# Carichiamo i Servizi Sociali
try:
    df_sociali = pd.read_csv('servizi_sociali.csv', sep=None, engine='python', on_bad_lines='skip')
    print(f"✅ Servizi Sociali Puglia caricati: {len(df_sociali)}")
except Exception as e:
    print(f"❌ Errore caricamento servizi sociali: {e}")
    exit()

# 2. STANDARDZZAZIONE COMUNI
# Creiamo una chiave comune 'CITY_KEY' per unire i dataset
df_taranto['CITY_KEY'] = df_taranto['Comune'].astype(str).str.upper().str.strip()
df_sociali['CITY_KEY'] = df_sociali['COMUNE'].astype(str).str.upper().str.strip()

# 3. CALCOLO STATISTICHE PER CITTÀ
# Contiamo quanti beni ci sono per ogni comune
risorse = df_taranto.groupby('CITY_KEY').size().reset_index(name='NUM_BENI')

# Contiamo quanti servizi sociali ci sono già
bisogni = df_sociali.groupby('CITY_KEY').size().reset_index(name='NUM_SERVIZI')

# 4. MERGE (INCROCIO DATI)
# Uniamo tutto in un unico dataframe di analisi
df_analysis = pd.merge(risorse, bisogni, on='CITY_KEY', how='left').fillna(0)

# 5. CALCOLO OPPORTUNITY SCORE (L'ALGORITMO ROBIN HOOD)
# Logica: Tanti Beni / (Servizi Esistenti + 1). Più è alto, più c'è potenziale sprecato.
df_analysis['ROBIN_HOOD_SCORE'] = (df_analysis['NUM_BENI'] * 10) / (df_analysis['NUM_SERVIZI'] + 1)
df_analysis['ROBIN_HOOD_SCORE'] = df_analysis['ROBIN_HOOD_SCORE'].round(1)

# Ordiniamo per priorità
df_analysis = df_analysis.sort_values('ROBIN_HOOD_SCORE', ascending=False)

# 6. CREAZIONE DATASET FINALE PER LA DASHBOARD
# Uniamo lo score ai dati grezzi dei beni per avere tutto in un file
df_final = pd.merge(df_taranto, df_analysis[['CITY_KEY', 'ROBIN_HOOD_SCORE', 'NUM_SERVIZI']], on='CITY_KEY', how='left')

# Salviamo solo colonne utili
cols_utili = [
    'Comune', 'Indirizzo', 'Tipologia', 'Categoria catastale', 'Metri quadri/Consistenza', 
    'Finalità', 'Destinatario', 'ROBIN_HOOD_SCORE', 'NUM_SERVIZI'
]
# Gestiamo il caso in cui alcune colonne abbiano nomi leggermente diversi nel CSV
cols_esistenti = [c for c in cols_utili if c in df_final.columns]
df_final = df_final[cols_esistenti]

file_output = 'RobinHood_Elite_Data.xlsx'
df_final.to_excel(file_output, index=False)

print(f"\n🏆 MISSIONE COMPIUTA!")
print(f"File generato: {file_output}")
print("Top 3 Comuni per Opportunità:")
print(df_analysis.head(3))