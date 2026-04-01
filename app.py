import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
import random
import time
import requests

# --- CONFIGURACIÓ ---
st.set_page_config(page_title="IAAF World Database Pro", layout="wide")

# Connexió per LLEGIR (Pestanya "Respostes" del teu Google Sheet)
conn = st.connection("gsheets", type=GSheetsConnection)

def carregar_atletes():
    try:
        # ttl=0 per forçar la lectura de dades noves
        df = conn.read(ttl=0)
        
        if df is None or df.empty:
            return pd.DataFrame(columns=['nom', 'pais', 'mitja', 'millor_marca', 'prova'])

        # 1. Netegem els noms de les columnes (treure espais i posar minúscules)
        df.columns = [c.strip().lower() for c in df.columns]

        # 2. Si Google Forms ha posat noms llargs com "nom de l'atleta", els simplifiquem
        # Busquem columnes que coninguin certes paraules clau
        mapeig = {}
        for col in df.columns:
            if "nom" in col: mapeig[col] = "nom"
            elif "pais" in col or "país" in col: mapeig[col] = "pais"
            elif "mitja" in col or "nivell" in col: mapeig[col] = "mitja"
            elif "marca" in col and "temps" not in col: mapeig[col] = "millor_marca"
            elif "prova" in col: mapeig[col] = "prova"
        
        df = df.rename(columns=mapeig)

        # 3. Ens assegurem que la columna 'millor_marca' sigui numèrica
        if 'millor_marca' in df.columns:
            df['millor_marca'] = pd.to_numeric(df['millor_marca'], errors='coerce')
        else:
            df['millor_marca'] = None

        # 4. Retornem només les columnes que ens interessen (ignorant la marca de temps)
        columnes_bones = [c for c in ['nom', 'pais', 'mitja', 'millor_marca', 'prova'] if c in df.columns]
        return df[columnes_bones]
        
    except Exception as e:
        st.error(f"Error llegint l'Excel: {e}")
        return pd.DataFrame(columns=['nom', 'pais', 'mitja', 'millor_marca', 'prova'])

# --- DADES COMPLETES ---
PAISOS = {
    "Europa": ["Albània", "Alemanya", "Andorra", "Armènia", "Àustria", "Bèlgica", "Bielorússia", "Bòsnia i Hercegovina", "Bulgària", "Catalunya", "Xipre", "Croàcia", "Dinamarca", "Eslovàquia", "Eslovènia", "Espanya", "Estònia", "Finlàndia", "França", "Geòrgia", "Grècia", "Hongria", "Irlanda", "Islàndia", "Israel", "Itàlia", "Kosovo", "Letònia", "Liechtenstein", "Lituània", "Luxemburg", "Malta", "Moldàvia", "Mònaco", "Montenegro", "Noruega", "Pais Basc", "Països Baixos", "Polònia", "Portugal", "Inglaterra", "Escocia", "Gales", "Irlanda del Nord", "República Txeca", "Romania", "Rússia", "San Marino", "Sèrbia", "Suècia", "Suïssa", "Turquia", "Ucraïna"],
    "Àfrica": ["Algèria", "Angola", "Benín", "Botswana", "Burkina Faso", "Burundi", "Cabo Verde", "Camerun", "Comores", "Congo", "Costa d’Ivori", "Djibouti", "Egipte", "Eritrea", "Eswatini", "Etiòpia", "Gabon", "Gàmbia", "Ghana", "Guinea", "Guinea-Bissau", "Guinea Equatorial", "Kenya", "Lesotho", "Libèria", "Líbia", "Madagascar", "Malawi", "Mali", "Marroc", "Maurici", "Mauritània", "Moçambic", "Namíbia", "Níger", "Nigèria", "República Centreafricana", "República Democràtica del Congo", "Ruanda", "São Tomé i Príncipe", "Senegal", "Seychelles", "Sierra Leone", "Somàlia", "Sudan", "Sudan del Sud", "Tanzània", "Togo", "Tunísia", "Uganda", "Zàmbia", "Zimbabwe"],
    "Amèrica": ["Antigua i Barbuda", "Argentina", "Bahamas", "Barbados", "Belize", "Bolívia", "Brasil", "Canadà", "Xile", "Colòmbia", "Costa Rica", "Cuba", "Dominica", "República Dominicana", "Equador", "El Salvador", "Grenada", "Guatemala", "Guyana", "Haití", "Hondures", "Jamaica", "Mèxic", "Nicaragua", "Panamà", "Paraguai", "Perú", "Saint Kitts i Nevis", "Saint Lucia", "Saint Vincent i les Grenadines", "Surinam", "Trinitat i Tobago", "Estats Units", "Uruguai", "Veneçuela"],
    "Asia": ["Afganistan", "Aràbia Saudita", "Azerbaidjan", "Bahrain", "Bangladesh", "Bhutan", "Brunei", "Cambodja", "Xina", "Corea del Nord", "Corea del Sud", "Emirats Àrabs Units", "Filipines", "Índia", "Indonèsia", "Iran", "Iraq", "Japó", "Jordània", "Kazakhstan", "Kirguizistan", "Kuwait", "Laos", "Líban", "Malàisia", "Maldives", "Mongòlia", "Myanmar", "Nepal", "Oman", "Pakistan", "Qatar", "Singapur", "Sri Lanka", "Síria", "Tailàndia", "Taiwan", "Tajikistan", "Timor Oriental", "Turkmenistan", "Uzbekistan", "Vietnam", "Yemen"],
    "Oceania": ["Austràlia", "Fiji", "Illes Marshall", "Illes Salomó", "Kiribati", "Micronèsia", "Nauru", "Nova Zelanda", "Palau", "Papua Nova Guinea", "Samoa", "Tonga", "Tuvalu", "Vanuatu"]
}

PROVES_LLISTAT = [
    "100 metres llisos", "200 metres llisos", "400 metres llisos", 
    "800 metres llisos", "1.500 metres llisos", "110 metres tanques", "400 metres tanques",
    "Salt de llargada", "Triple salt", "Salt d’alçada", "Salt amb perxa",
    "Llançament de pes", "Llançament de javelina", "Llançament de martell", "Llançament de disc"
]

# --- FUNCIÓ PER GUARDAR (SENSE TARGETA) ---
def enviar_a_google_form(nom, pais, mitja, marca, prova):
    url = "https://docs.google.com/forms/d/e/1FAIpQLSebKgp7PqO8nNPrR5yLzuzxdFS8ijlR127pGFpn_bpwaiNKIw/formResponse"
    valors = {
        "entry.1030999587": nom,
        "entry.440237722": pais,
        "entry.1011387679": mitja,
        "entry.550186989": marca,
        "entry.2066863965": prova
    }
    try:
        requests.post(url, data=valors)
        return True
    except:
        return False

# --- LÒGICA PRINCIPAL ---
menu = st.sidebar.radio("Menú", ["🏠 Inici", "📝 Inscripcions", "📋 Llista i PB", "🏆 COMPETICIÓ"])
df_actual = carregar_atletes()

if menu == "🏠 Inici":
    st.title("🏆 IAAF World Database & Records")
    st.write(f"Atletes registrats: **{len(df_actual)}**")

elif menu == "📝 Inscripcions":
    st.header("👤 Nova Inscripció")
    nom = st.text_input("Nom de l'atleta:")
    c1, c2 = st.columns(2)
    with c1:
        cont = st.selectbox("Continent", sorted(PAISOS.keys()))
    with c2:
        pais_triat = st.selectbox("País", sorted(PAISOS[cont]), key=f"p_{cont}")
    
    c3, c4 = st.columns(2)
    with c3:
        prova_triada = st.selectbox("Prova Especialitzada", PROVES_LLISTAT)
    with c4:
        nivell = st.slider("Nivell (0-100)", 10, 99, 80)
    
    if st.button("🚀 Guardar Atleta"):
        if nom.strip():
            èxit = enviar_a_google_form(nom, pais_triat, nivell, "", prova_triada)
            if èxit:
                st.success(f"✅ {nom} enviat! Espera que Google actualitzi l'Excel...")
                time.sleep(3) # Donem temps a Google
                st.rerun()
            else:
                st.error("Error de connexió.")

elif menu == "📋 Llista i PB":
    st.header("📋 Rànquing Personal")
    if df_actual.empty:
        st.info("No hi ha atletes. Si n'has guardat un ara mateix, refresca la pàgina en uns segons.")
    else:
        # Mostrem una taula neta
        st.dataframe(df_actual[['nom', 'pais', 'prova', 'mitja', 'millor_marca']])

elif menu == "🏆 COMPETICIÓ":
    st.header("🏁 Simulació de Proves")
    prova_simu = st.selectbox("Tria la prova:", PROVES_LLISTAT)
    
    # Filtrem
    atletes_aptes = df_actual[df_actual['prova'] == prova_simu]
    
    if len(atletes_aptes) < 2:
        st.warning(f"Necessites almenys 2 atletes de {prova_simu}.")
    else:
        triats = st.multiselect("Participants:", atletes_aptes['nom'].tolist())
        if st.button("🚀 INICIAR"):
            results = []
            es_cursa = any(x in prova_simu.lower() for x in ["metres", "tanques"])
            
            for n in triats:
                atl = atletes_aptes[atletes_aptes['nom'] == n].iloc[0]
                pot = int(atl['mitja'])
                
                # Fórmules de marques reals
                if prova_simu == "100 metres llisos": marca = round(13.0 - (pot/20) + random.uniform(-0.1, 0.1), 2)
                elif prova_simu == "200 metres llisos": marca = round(26.0 - (pot/10) + random.uniform(-0.2, 0.2), 2)
                elif prova_simu == "400 metres llisos": marca = round(60.0 - (pot/4) + random.uniform(-0.5, 0.5), 2)
                elif "Salt" in prova_simu: marca = round(2.0 + (pot/20) + random.uniform(-0.1, 0.1), 2)
                elif "Llançament" in prova_simu: marca = round(15.0 + (pot/1.2) + random.uniform(-1, 1), 2)
                else: marca = round(100 - pot + random.uniform(-5, 5), 2)
                
                results.append({"Atleta": n, "País": atl['pais'], "Marca": marca})
            
            st.balloons()
            res_df = pd.DataFrame(results).sort_values("Marca", ascending=es_cursa)
            st.table(res_df)
