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
        # 1. Llegim les dades crues
        df_raw = conn.read(ttl=0)
        
        # Si no hi ha res, retornem estructura buida
        if df_raw is None or df_raw.empty:
            return pd.DataFrame(columns=['nom', 'pais', 'mitja', 'millor_marca', 'prova'])

        # 2. Netegem noms de columnes (treure espais i minúscules)
        df_raw.columns = [str(c).strip().lower() for c in df_raw.columns]

        # 3. Creem un nou DataFrame net per evitar l'error d'arguments de Pandas
        df = pd.DataFrame()

        # Busquem les columnes per paraula clau (més segur)
        for col in df_raw.columns:
            col_str = str(col)
            if "nom" in col_str: df['nom'] = df_raw[col]
            elif "pais" in col_str or "país" in col_str: df['pais'] = df_raw[col]
            elif "mitja" in col_str or "nivell" in col_str: df['mitja'] = df_raw[col]
            elif "prova" in col_str: df['prova'] = df_raw[col]
            elif "marca" in col_str and "temps" not in col_str: df['millor_marca'] = df_raw[col]

        # 4. Verifiquem que tinguem les 5 columnes, si no les creem buides
        for c in ['nom', 'pais', 'mitja', 'millor_marca', 'prova']:
            if c not in df.columns:
                df[c] = None

        # 5. EL TRUC PER EVITAR L'ERROR: Convertim a Sèrie explícitament
        # Això arregla l'error "arg must be a list, tuple..."
        df['mitja'] = pd.to_numeric(pd.Series(df['mitja']), errors='coerce').fillna(0)
        df['millor_marca'] = pd.to_numeric(pd.Series(df['millor_marca']), errors='coerce')

        # 6. Eliminem files on el nom estigui buit (neteja final)
        df = df.dropna(subset=['nom'])

        return df[['nom', 'pais', 'mitja', 'millor_marca', 'prova']]
        
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
    # La URL de resposta (formResponse)
    url = "https://docs.google.com/forms/d/e/1FAIpQLSebKgp7PqO8nNPrR5yLzuzxdFS8ijlR127pGFpn_bpwaiNKIw/formResponse"
    
    # Preparem les dades exactament com a l'enllaç que t'ha funcionat
    payload = {
        "entry.1030999587": str(nom),
        "entry.440237722": str(pais),
        "entry.1011387679": str(mitja),
        "entry.550186989": str(marca),
        "entry.2066863965": str(prova)
    }
    
    try:
        # Fem l'enviament real
        response = requests.post(url, data=payload)
        # Si Google respon 200, és que s'ha guardat
        return response.status_code == 200
    except Exception as e:
        st.error(f"Error de xarxa: {e}")
        return False

# --- LÒGICA PRINCIPAL ---
menu = st.sidebar.radio("Menú", ["🏠 Inici", "📝 Inscripcions", "📋 Llista i PB", "🏆 COMPETICIÓ"])

# Carreguem dades
df_actual = carregar_atletes()

if menu == "🏠 Inici":
    st.title("🏆 IAAF World Database & Records")
    st.write(f"Atletes registrats: **{len(df_actual)}**")
    st.info("Consell: Si acabes d'inscriure un atleta i no surt, espera 5 segons i canvia de pestanya al menú.")

elif menu == "📝 Inscripcions":
    st.header("👤 Nova Inscripció")
    with st.container():
        nom_in = st.text_input("Nom de l'atleta:")
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
            if nom_in.strip():
                amb_exit = enviar_a_google_form(nom_in, pais_triat, nivell, "", prova_triada)
                if amb_exit:
                    st.success(f"✅ {nom_in} s'ha registrat correctament!")
                    st.cache_data.clear() # Netegem cache per forçar lectura fresca
                    time.sleep(2)
                    st.rerun()
                else:
                    st.error("Error al connectar amb Google Forms.")
            else:
                st.warning("Escriu el nom de l'atleta!")

elif menu == "📋 Llista i PB":
    st.header("📋 Rànquing Personal")
    if df_actual.empty:
        st.info("La base de dades està buida.")
    else:
        # Mostrem una taula neta (traiem columnes internes si n'hi hagués)
        st.dataframe(df_actual[['nom', 'pais', 'prova', 'mitja', 'millor_marca']], use_container_width=True)

elif menu == "🏆 COMPETICIÓ":
    st.header("🏁 Simulació de Proves")
    prova_simu = st.selectbox("Tria la prova a competir:", PROVES_LLISTAT)
    
    # Filtrem atletes que fan aquesta prova
    atletes_aptes = df_actual[df_actual['prova'] == prova_simu]
    
    if len(atletes_aptes) < 2:
        st.warning(f"Es necessiten almenys 2 atletes especialitzats en {prova_simu} per competir.")
    else:
        triats = st.multiselect("Selecciona els participants:", atletes_aptes['nom'].tolist())
        
        if st.button("🚀 INICIAR CURSA / SALT"):
            if len(triats) < 2:
                st.error("Tria almenys 2 participants!")
            else:
                results = []
                es_cursa = any(x in prova_simu.lower() for x in ["metres", "tanques"])
                
                barra = st.progress(0)
                for i, n in enumerate(triats):
                    time.sleep(0.3) # Efecte d'espera
                    barra.progress((i + 1) / len(triats))
                    
                    atl = atletes_aptes[atletes_aptes['nom'] == n].iloc[0]
                    pot = int(atl['mitja'])
                    
                    # Fórmules segons prova
                    if "100 metres" in prova_simu: marca = round(13.0 - (pot/20) + random.uniform(-0.15, 0.15), 2)
                    elif "200 metres" in prova_simu: marca = round(26.0 - (pot/10) + random.uniform(-0.25, 0.25), 2)
                    elif "Salt de llargada" in prova_simu: marca = round(3.0 + (pot/20) + random.uniform(-0.2, 0.2), 2)
                    elif "Llançament" in prova_simu: marca = round(15.0 + (pot/1.2) + random.uniform(-1, 1), 2)
                    else: marca = round(100 - pot + random.uniform(-5, 5), 2)
                    
                    results.append({"Posició": 0, "Atleta": n, "País": atl['pais'], "Marca": marca})
                
                st.balloons()
                res_df = pd.DataFrame(results).sort_values("Marca", ascending=es_cursa)
                
                # Afegir medalles
                res_df['Posició'] = range(1, len(res_df) + 1)
                st.subheader(f"🏆 Resultats de {prova_simu}")
                st.table(res_df)
