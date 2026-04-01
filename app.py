import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
import random
import time
import requests

# --- CONFIGURACIÓ ---
st.set_page_config(page_title="IAAF World Database Pro", layout="wide")

# Connexió per LLEGIR
conn = st.connection("gsheets", type=GSheetsConnection)

def carregar_atletes():
    try:
        df_raw = conn.read(ttl=0)
        if df_raw is None or df_raw.empty:
            return pd.DataFrame(columns=['nom', 'pais', 'mitja', 'millor_marca', 'prova'])
        df_raw.columns = [str(c).strip().lower() for c in df_raw.columns]
        df = pd.DataFrame()
        for col in df_raw.columns:
            col_str = str(col)
            if "nom" in col_str: df['nom'] = df_raw[col]
            elif "pais" in col_str or "país" in col_str: df['pais'] = df_raw[col]
            elif "mitja" in col_str or "nivell" in col_str: df['mitja'] = df_raw[col]
            elif "prova" in col_str: df['prova'] = df_raw[col]
            elif "marca" in col_str and "temps" not in col_str: df['millor_marca'] = df_raw[col]
        for c in ['nom', 'pais', 'mitja', 'millor_marca', 'prova']:
            if c not in df.columns: df[c] = None
        df['mitja'] = pd.to_numeric(pd.Series(df['mitja']), errors='coerce').fillna(0)
        df['millor_marca'] = pd.to_numeric(pd.Series(df['millor_marca']), errors='coerce')
        df = df.dropna(subset=['nom'])
        return df[['nom', 'pais', 'mitja', 'millor_marca', 'prova']]
    except Exception as e:
        st.error(f"Error llegint l'Excel: {e}")
        return pd.DataFrame(columns=['nom', 'pais', 'mitja', 'millor_marca', 'prova'])

# --- DADES ---
PAISOS = {
    "Europa": ["Albània", "Alemanya", "Andorra", "Armènia", "Àustria", "Bèlgica", "Bielorússia", "Bòsnia i Hercegovina", "Bulgària", "Catalunya", "Xipre", "Croàcia", "Dinamarca", "Eslovàquia", "Eslovènia", "Espanya", "Estònia", "Finlàndia", "França", "Geòrgia", "Grècia", "Hongria", "Irlanda", "Islàndia", "Israel", "Itàlia", "Kosovo", "Letònia", "Liechtenstein", "Lituània", "Luxemburg", "Malta", "Moldàvia", "Mònaco", "Montenegro", "Noruega", "Pais Basc", "Països Baixos", "Polònia", "Portugal", "Inglaterra", "Escocia", "Gales", "Irlanda del Nord", "República Txeca", "Romania", "Rússia", "San Marino", "Sèrbia", "Suècia", "Suïssa", "Turquia", "Ucraïna"],
    "Àfrica": ["Algèria", "Angola", "Benín", "Botswana", "Burkina Faso", "Burundi", "Cabo Verde", "Camerun", "Comores", "Congo", "Costa d’Ivori", "Djibouti", "Egipte", "Eritrea", "Eswatini", "Etiòpia", "Gabon", "Gàmbia", "Ghana", "Guinea", "Guinea-Bissau", "Guinea Equatorial", "Kenya", "Lesotho", "Libèria", "Líbia", "Madagascar", "Malawi", "Mali", "Marroc", "Maurici", "Mauritània", "Moçambic", "Namíbia", "Níger", "Nigèria", "República Centreafricana", "República Democràtica del Congo", "Ruanda", "São Tomé i Príncipe", "Senegal", "Seychelles", "Sierra Leone", "Somàlia", "Sudan", "Sudan del Sud", "Tanzània", "Togo", "Tunísia", "Uganda", "Zàmbia", "Zimbabwe"],
    "Amèrica": ["Antigua i Barbuda", "Argentina", "Bahamas", "Barbados", "Belize", "Bolívia", "Brasil", "Canadà", "Xile", "Colòmbia", "Costa Rica", "Cuba", "Dominica", "República Dominicana", "Equador", "El Salvador", "Grenada", "Guatemala", "Guyana", "Haití", "Hondures", "Jamaica", "Mèxic", "Nicaragua", "Panamà", "Paraguai", "Perú", "Saint Kitts i Nevis", "Saint Lucia", "Saint Vincent i les Grenadines", "Surinam", "Trinitat i Tobago", "Estats Units", "Uruguai", "Veneçuela"],
    "Asia": ["Afganistan", "Aràbia Saudita", "Azerbaidjan", "Bahrain", "Bangladesh", "Bhutan", "Brunei", "Cambodja", "Xina", "Corea del Nord", "Corea del Sud", "Emirats Àrabs Units", "Filipines", "Índia", "Indonèsia", "Iran", "Iraq", "Japó", "Jordània", "Kazakhstan", "Kirguizistan", "Kuwait", "Laos", "Líban", "Malàisia", "Maldives", "Mongòlia", "Myanmar", "Nepal", "Oman", "Pakistan", "Qatar", "Singapur", "Sri Lanka", "Síria", "Tailàndia", "Taiwan", "Tajikistan", "Timor Oriental", "Turkmenistan", "Uzbekistan", "Vietnam", "Yemen"],
    "Oceania": ["Austràlia", "Fiji", "Illes Marshall", "Illes Salomó", "Kiribati", "Micronèsia", "Nauru", "Nova Zelanda", "Palau", "Papua Nova Guinea", "Samoa", "Tonga", "Tuvalu", "Vanuatu"]
}

PROVES_LLISTAT = ["100 metres llisos", "200 metres llisos", "400 metres llisos", "800 metres llisos", "1.500 metres llisos", "110 metres tanques", "400 metres tanques", "Salt de llargada", "Triple salt", "Salt d’alçada", "Salt amb perxa", "
