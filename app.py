import streamlit as st
import pandas as pd
import random
import time

# --- CONFIGURACIÓ DE PÀGINA ---
st.set_page_config(page_title="Simulador Mundial d'Atletisme", layout="wide")

# Inicialitzar la llista d'atletes si no existeix
if 'atletes' not in st.session_state:
    st.session_state.atletes = []

# --- BASE DE DADES DE PAÏSOS (LA TEVA LLISTA EXACTA) ---
PAISOS = {
    "Europa": [
        "Albània", "Alemanya", "Andorra", "Armènia", "Àustria", "Bèlgica", "Bielorússia", 
        "Bòsnia i Hercegovina", "Bulgària", "Catalunya", "Xipre", "Croàcia", "Dinamarca", 
        "Eslovàquia", "Eslovènia", "Espanya", "Estònia", "Finlàndia", "França", "Geòrgia", 
        "Grècia", "Hongria", "Irlanda", "Islàndia", "Israel", "Itàlia", "Kosovo", "Letònia", 
        "Liechtenstein", "Lituània", "Luxemburg", "Malta", "Moldàvia", "Mònaco", "Montenegro", 
        "Noruega", "Pais Basc", "Països Baixos", "Polònia", "Portugal", "Inglaterra", 
        "Escocia", "Gales", "Irlanda del Nord", "República Txeca", "Romania", "Rússia", 
        "San Marino", "Sèrbia", "Suècia", "Suïssa", "Turquia", "Ucraïna"
    ],
    "Àfrica": [
        "Algèria", "Angola", "Benín", "Botswana", "Burkina Faso", "Burundi", "Cabo Verde", 
        "Camerun", "Comores", "Congo", "Costa d’Ivori", "Djibouti", "Egipte", "Eritrea", 
        "Eswatini", "Etiòpia", "Gabon", "Gàmbia", "Ghana", "Guinea", "Guinea-Bissau", 
        "Guinea Equatorial", "Kenya", "Lesotho", "Libèria", "Líbia", "Madagascar", 
        "Malawi", "Mali", "Marroc", "Maurici", "Mauritània", "Moçambic", "Namíbia", 
        "Níger", "Nigèria", "República Centreafricana", "República Democràtica del Congo", 
        "Ruanda", "São Tomé i Príncipe", "Senegal", "Seychelles", "Sierra Leone", 
        "Somàlia", "Sudan", "Sudan del Sud", "Tanzània", "Togo", "Tunísia", "Uganda", 
        "Zàmbia", "Zimbabwe"
    ],
    "Amèrica": [
        "Antigua i Barbuda", "Argentina", "Bahamas", "Barbados", "Belize", "Bolívia", 
        "Brasil", "Canadà", "Xile", "Colòmbia", "Costa Rica", "Cuba", "Dominica", 
        "República Dominicana", "Equador", "El Salvador", "Grenada", "Guatemala", 
        "Guyana", "Haití", "Hondures", "Jamaica", "Mèxic", "Nicaragua", "Panamà", 
        "Paraguai", "Perú", "Saint Kitts i Nevis", "Saint Lucia", "Saint Vincent i les Grenadines", 
        "Surinam", "Trinitat i Tobago", "Estats Units", "Uruguai", "Veneçuela"
    ],
    "Asia": [
        "Afganistan", "Aràbia Saudita", "Azerbaidjan", "Bahrain", "Bangladesh", "Bhutan", 
        "Brunei", "Cambodja", "Xina", "Corea del Nord", "Corea del Sud", "Emirats Àrabs Units", 
        "Filipines", "Índia", "Indonèsia", "Iran", "Iraq", "Japó", "Jordània", "Kazakhstan", 
        "Kirguizistan", "Kuwait", "Laos", "Líban", "Malàisia", "Maldives", "Mongòlia", 
        "Myanmar", "Nepal", "Oman", "Pakistan", "Qatar", "Singapur", "Sri Lanka", "Síria", 
        "Tailàndia", "Taiwan", "Tajikistan", "Timor Oriental", "Turkmenistan", "Uzbekistan", 
        "Vietnam", "Yemen"
    ],
    "Oceania": [
        "Austràlia", "Fiji", "Illes Marshall", "Illes Salomó", "Kiribati", "Micronèsia", 
        "Nauru", "Nova Zelanda", "Palau", "Papua Nova Guinea", "Samoa", "Tonga", "Tuvalu", "Vanuatu"
    ]
}

# --- MENÚ LATERAL ---
st.sidebar.title("🏃 IAAF Manager")
menu = st.sidebar.radio("Menú:", ["🏠 Inici", "📝 Inscripcions", "📋 Llista d'Atletes", "🏆 COMPETICIÓ"])

# --- PANTALLES ---
if menu == "🏠 Inici":
    st.title("🏆 Simulador d'Atletisme")
    st.write("Gestiona els teus atletes i simula curses amb la teva pròpia base de dades.")
    st.info("Utilitza el menú de l'esquerra per començar.")

elif menu == "📝 Inscripcions":
    st.header("👤 Nova Inscripció")
    with st.form("form_atl", clear_on_submit=True):
        nom = st.text_input("Nom de l'atleta:")
        c1, c2 = st.columns(2)
        with c1:
            cont = st.selectbox("Continent", sorted(list(PAISOS.keys())))
        with c2:
            pais_triat = st.selectbox("País", sorted(PAISOS[cont]))
        
        nivell = st.slider("Nivell (0-100)", 10, 99, 80)
        
        if st.form_submit_button("Guardar Atleta"):
            if nom.strip():
                st.session_state.atletes.append({
                    "id": time.time(), "nom": nom, "pais": pais_triat, "mitja": nivell
                })
                st.success(f"✅ {nom} ({pais_triat}) inscrit!")
            else:
                st.error("Posa un nom vàlid.")

elif menu == "📋 Llista d'Atletes":
    st.header("📋 Atletes Registrats")
    if not st.session_state.atletes:
        st.write("No hi ha atletes.")
    else:
        if st.button("🗑️ BUIDAR TOTA LA LLISTA"):
            st.session_state.atletes = []
            st.rerun()
        
        st.write("---")
        for i, atl in enumerate(st.session_state.atletes):
            col1, col2, col3, col4 = st.columns([3, 2, 1, 1])
            col1.write(f"**{atl['nom']}**")
            col2.write(f"📍 {atl['pais']}")
            col3.write(f"⚡ {atl['mitja']}")
            if col4.button("Eliminar", key=f"del_{atl['id']}"):
                st.session_state.atletes.pop(i)
                st.rerun()

elif menu == "🏆 COMPETICIÓ":
    st.header("🏁 Simulació de Carrera")
    if len(st.session_state.atletes) < 2:
        st.warning("Necessites almenys 2 atletes per fer una cursa.")
    else:
        triats = st.multiselect("Tria els participants:", [a['nom'] for a in st.session_state.atletes])
        
        if st.button("🚀 INICIAR CURSA"):
            if len(triats) >= 2:
                results = []
                for n in triats:
                    atl = next(x for x in st.session_state.atletes if x['nom'] == n)
                    marca = round(13.0 - (atl['mitja']/20) + random.uniform(-0.15, 0.15), 2)
                    results.append({"Atleta": n, "País": atl['pais'], "Marca": marca})
                
                df = pd.DataFrame(results).sort_values("Marca")
                df.insert(0, "Pos", range(1, len(df) + 1))
                st.balloons()
                st.table(df.set_index("Pos"))
            else:
                st.error("Tria almenys 2 corredors.")
