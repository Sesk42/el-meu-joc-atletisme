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

# --- FUNCIÓ ENVIAMENT CORREGIDA ---
def enviar_a_google_form(nom, pais, mitja, marca, prova):
    url = "https://docs.google.com/forms/d/e/1FAIpQLSebKgp7PqO8nNPrR5yLzuzxdFS8ijlR127pGFpn_bpwaiNKIw/formResponse"
    
    # Payload exacte (els números que t'han funcionat al navegador)
    payload = {
        "entry.1030999587": str(nom),
        "entry.440237722": str(pais),
        "entry.1011387679": str(mitja),
        "entry.550186989": str(marca),
        "entry.2066863965": str(prova)
    }
    
    # Afegim headers per "enganyar" Google i que sembli un navegador
    headers = {
        "Content-Type": "application/x-www-form-urlencoded"
    }
    
    try:
        response = requests.post(url, data=payload, headers=headers)
        return response.status_code == 200
    except:
        return False

# --- LÒGICA ---
menu = st.sidebar.radio("Menú", ["🏠 Inici", "📝 Inscripcions", "📋 Llista i PB", "🏆 COMPETICIÓ"])
df_actual = carregar_atletes()

if menu == "🏠 Inici":
    st.title("🏆 IAAF World Database & Records")
    st.write(f"Atletes registrats: **{len(df_actual)}**")

elif menu == "📝 Inscripcions":
    st.header("👤 Nova Inscripció")
    with st.container():
        # Fem servir un formulari de Streamlit per agrupar
        with st.form("meu_formulari"):
            nom_in = st.text_input("Nom de l'atleta:")
            c1, c2 = st.columns(2)
            with c1:
                cont = st.selectbox("Continent", sorted(PAISOS.keys()))
            with c2:
                pais_triat = st.selectbox("País", sorted(PAISOS[cont]))
            
            c3, c4 = st.columns(2)
            with c3:
                prova_triada = st.selectbox("Prova Especialitzada", PROVES_LLISTAT)
            with c4:
                nivell = st.slider("Nivell (0-100)", 10, 99, 80)
            
            submès = st.form_submit_button("🚀 Guardar Atleta")
            
            if submès:
                if nom_in.strip():
                    if enviar_a_google_form(nom_in, pais_triat, nivell, "", prova_triada):
                        st.success(f"✅ {nom_in} guardat!")
                        st.cache_data.clear()
                        time.sleep(1)
                        st.rerun()
                    else:
                        st.error("Error d'enviament. Revisa la configuració del Form.")
                else:
                    st.warning("Escriu un nom!")

elif menu == "📋 Llista i PB":
    st.header("📋 Rànquing Personal")
    st.dataframe(df_actual[['nom', 'pais', 'prova', 'mitja', 'millor_marca']], use_container_width=True)

elif menu == "🏆 COMPETICIÓ":
    st.header("🏁 Simulació de Proves")
    prova_simu = st.selectbox("Tria la prova:", PROVES_LLISTAT)
    atletes_aptes = df_actual[df_actual['prova'] == prova_simu]
    
    if len(atletes_aptes) < 2:
        st.warning(f"Falten atletes per a {prova_simu}.")
    else:
        triats = st.multiselect("Participants:", atletes_aptes['nom'].tolist())
        if st.button("🚀 INICIAR"):
            if len(triats) >= 2:
                results = []
                es_cursa = any(x in prova_simu.lower() for x in ["metres", "tanques"])
                for n in triats:
                    atl = atletes_aptes[atletes_aptes['nom'] == n].iloc[0]
                    pot = int(atl['mitja'])
                    if "100 metres" in prova_simu: marca = round(13.0 - (pot/20) + random.uniform(-0.1, 0.1), 2)
                    elif "200 metres" in prova_simu: marca = round(26.0 - (pot/10) + random.uniform(-0.2, 0.2), 2)
                    else: marca = round(100 - pot + random.uniform(-5, 5), 2)
                    results.append({"Atleta": n, "País": atl['pais'], "Marca": marca})
                
                res_df = pd.DataFrame(results).sort_values("Marca", ascending=es_cursa)
                st.table(res_df)
