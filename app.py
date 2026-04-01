import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
import random
import time
import requests

# --- CONFIGURACIÓ ---
st.set_page_config(page_title="IAAF Database Pro - Full World", layout="wide")

# Connexió per LLEGIR (Pestaña "Respostes" del teu Google Sheet)
conn = st.connection("gsheets", type=GSheetsConnection)

def carregar_atletes():
    try:
        df = conn.read(ttl=0)
        if df is None or df.empty:
            return pd.DataFrame(columns=['nom', 'pais', 'mitja', 'millor_marca', 'prova'])
        # Netegem noms de columnes per si Google Forms afegeix espais o la "Marca de temps"
        df.columns = [c.strip().lower() for c in df.columns]
        return df
    except:
        return pd.DataFrame(columns=['nom', 'pais', 'mitja', 'millor_marca', 'prova'])

# --- LLISTA COMPLETA DE PAÏSOS ---
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

# --- FUNCIÓ PER GUARDAR VIA GOOGLE FORM ---
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

# --- LÒGICA APP ---
menu = st.sidebar.radio("Menú", ["🏠 Inici", "📝 Inscripcions", "📋 Llista i PB", "🏆 COMPETICIÓ"])
df_actual = carregar_atletes()

if menu == "🏠 Inici":
    st.title("🏆 IAAF Database - Tots els Països")
    st.write(f"Atletes sincronitzats: **{len(df_actual)}**")

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
        prova_triada = st.selectbox("Prova", PROVES_LLISTAT)
    with c4:
        nivell = st.slider("Nivell", 10, 99, 80)
    
    if st.button("🚀 Guardar Atleta"):
        if nom.strip():
            èxit = enviar_a_google_form(nom, pais_triat, nivell, "", prova_triada)
            if èxit:
                st.success(f"✅ {nom} ({pais_triat}) enviat! Actualitzant...")
                time.sleep(2)
                st.rerun()
            else:
                st.error("Error en l'enviament.")

elif menu == "📋 Llista i PB":
    st.header("📋 Base de dades actual")
    if df_actual.empty:
        st.write("No hi ha dades.")
    else:
        st.dataframe(df_actual)

elif menu == "🏆 COMPETICIÓ":
    st.header("🏁 Simulació")
    # Aquí pots tornar a posar la lògica de simulació que tenies abans
    st.info("Tria la prova a la que vulguis competir.")
