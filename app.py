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

PROVES_LLISTAT = ["100 metres llisos", "200 metres llisos", "400 metres llisos", "800 metres llisos", "1.500 metres llisos", "110 metres tanques", "400 metres tanques", "Salt de llargada", "Triple salt", "Salt d’alçada", "Salt amb perxa", "Llançament de pes", "Llançament de javelina", "Llançament de martell", "Llançament de disc"]

# --- FUNCIÓ ENVIAMENT ---
def enviar_a_google_form(nom, pais, mitja, marca, prova):
    # URL de resposta del teu formulari
    url = "https://docs.google.com/forms/d/e/1FAIpQLSebKgp7PqO8nNPrR5yLzuzxdFS8ijlR127pGFpn_bpwaiNKIw/formResponse"
    
    # ARA SÍ: Els IDs Reals que has trobat
    payload = {
        "entry.1668159850": str(nom),     # Nom
        "entry.1670433567": str(pais),    # País
        "entry.1326600864": str(mitja),   # Nivell / Mitja
        "entry.1635147765": str(marca),   # Millor Marca
        "entry.445329310": str(prova)     # Prova
    }
    
    try:
        # Enviament tipus POST (estàndard de Google)
        response = requests.post(url, data=payload)
        
        # Si Google respon OK (200), l'atleta ja hauria de sortir a l'Excel
        return response.ok
    except Exception as e:
        st.error(f"Error de connexió: {e}")
        return False
# --- LÒGICA ---
menu = st.sidebar.radio("Menú", ["🏠 Inici", "📝 Inscripcions", "📋 Llista i PB", "🏆 COMPETICIÓ"])
df_actual = carregar_atletes()

if menu == "🏠 Inici":
    st.title("🏆 IAAF World Database & Records")
    st.write(f"Atletes registrats: **{len(df_actual)}**")

elif menu == "📝 Inscripcions":
    st.header("👤 Nova Inscripció")
    
    # FORA del form posem els selectbox perque s'actualitzin a l'instant
    nom_in = st.text_input("Nom de l'atleta:")
    c1, c2 = st.columns(2)
    with c1:
        cont = st.selectbox("Continent", sorted(PAISOS.keys()))
    with c2:
        # La clau 'key' és el que feia que funcionés abans!
        pais_triat = st.selectbox("País", sorted(PAISOS[cont]), key=f"p_{cont}")
    
    c3, c4 = st.columns(2)
    with c3:
        prova_triada = st.selectbox("Prova Especialitzada", PROVES_LLISTAT)
    with c4:
        nivell = st.slider("Nivell (0-100)", 10, 99, 80)
    
    # El botó sol, sense 'st.form' per evitar embolics de refresc
    if st.button("🚀 Guardar Atleta"):
        if nom_in.strip():
            if enviar_a_google_form(nom_in, pais_triat, nivell, "", prova_triada):
                st.success(f"✅ {nom_in} guardat correctament!")
                st.cache_data.clear()
                time.sleep(2)
                st.rerun()
            else:
                st.error("Error al guardar.")
        else:
            st.warning("Escriu un nom!")

elif menu == "📋 Llista i PB":
    st.header("📋 Rànquing Personal")
    st.dataframe(df_actual[['nom', 'pais', 'prova', 'mitja', 'millor_marca']], use_container_width=True)

elif menu == "🏆 COMPETICIÓ":
    st.header("🏁 Simulació de Proves")

    # 1. TAULA DE RESULTATS EDITABLE (Nivell 1 - Nivell 100)
    # Pots canviar aquests valors aquí mateix i el joc s'adaptarà
    config_proves = {
        "100 metres llisos": {"n1": 10.44, "n100": 9.58, "tipus": "temps"},
        "200 metres llisos": {"n1": 21.15, "n100": 19.19, "tipus": "temps"},
        "400 metres llisos": {"n1": 46.67, "n100": 43.03, "tipus": "temps"},
        "800 metres llisos": {"n1": 111.19, "n100": 100.91, "tipus": "temps"}, # Convertit a segons (1:51.19 -> 111.19)
        "1.500 metres llisos": {"n1": 222.36, "n100": 206.00, "tipus": "temps"}, # Convertit a segons (3:42.36 -> 222.36)
        "110 metres tanques": {"n1": 13.64, "n100": 12.80, "tipus": "temps"},
        "400 metres tanques": {"n1": 48.84, "n100": 45.94, "tipus": "temps"},
        "Salt de llargada": {"n1": 8.25, "n100": 8.95, "tipus": "metres"},
        "Triple salt": {"n1": 17.24, "n100": 18.29, "tipus": "metres"},
        "Salt d’alçada": {"n1": 2.28, "n100": 2.45, "tipus": "metres"},
        "Salt amb perxa": {"n1": 5.51, "n100": 6.24, "tipus": "metres"},
        "Llançament de pes": {"n1": 22.73, "n100": 23.56, "tipus": "metres"},
        "Llançament de disc": {"n1": 70.13, "n100": 74.08, "tipus": "metres"},
        "Llançament de martell": {"n1": 85.57, "n100": 86.74, "tipus": "metres"},
        "Llançament de javelina": {"n1": 89.34, "n100": 98.48, "tipus": "metres"}
    }

    prova_simu = st.selectbox("Tria la prova:", list(config_proves.keys()))
    atletes_aptes = df_actual[df_actual['prova'] == prova_simu]

    if len(atletes_aptes) < 2:
        st.warning(f"Necessites almenys 2 atletes de {prova_simu}.")
    else:
        triats = st.multiselect("Participants:", atletes_aptes['nom'].tolist())
        
        if st.button("🚀 INICIAR"):
            results = []
            conf = config_proves[prova_simu]
            
            for n in triats:
                atl = atletes_aptes[atletes_aptes['nom'] == n].iloc[0]
                nivell = float(atl['mitja'])
                
                # CÀLCUL BASE (Interpolació lineal entre 1 i 100)
                # Formula: y = y1 + (x - x1) * (y100 - y1) / (100 - 1)
                base = conf['n1'] + (nivell - 1) * (conf['n100'] - conf['n1']) / 99
                
                # APLICAR ALEATORIETAT
                if conf['tipus'] == "temps":
                    # Aleatorietat entre +4% (pitjor) i -1% (millor)
                    factor = 1 + random.uniform(-0.01, 0.04)
                else:
                    # Aleatorietat entre -4% (pitjor) i +1% (millor)
                    factor = 1 + random.uniform(-0.04, 0.01)
                
                marca_final = round(base * factor, 2)
                results.append({"Atleta": n, "País": atl['pais'], "Marca": marca_final})
            
            # Ordenar
            es_temps = conf['tipus'] == "temps"
            res_df = pd.DataFrame(results).sort_values("Marca", ascending=es_temps)
            
            # Format per a visualitzar temps llargs (opcional)
            st.table(res_df)
            st.balloons()
