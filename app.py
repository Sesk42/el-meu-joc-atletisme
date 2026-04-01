import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
import random
import time
import requests  # Necessari per enviar dades al formulari

# --- CONFIGURACIÓ ---
st.set_page_config(page_title="IAAF Database Pro", layout="wide")

# Connexió per LLEGIR (Aquesta no dona error)
conn = st.connection("gsheets", type=GSheetsConnection)

def carregar_atletes():
    try:
        # Aquí posa la URL de l'Excel que ha generat el teu FORMULARI (pestanya Respostes)
        df = conn.read(ttl=0)
        if df is None or df.empty:
            return pd.DataFrame(columns=['id', 'nom', 'pais', 'mitja', 'millor_marca', 'prova'])
        df['millor_marca'] = pd.to_numeric(df['millor_marca'], errors='coerce')
        return df
    except:
        return pd.DataFrame(columns=['id', 'nom', 'pais', 'mitja', 'millor_marca', 'prova'])

# --- FUNCIÓ MÀGICA PER GUARDAR SENSE TARGETA ---
def enviar_a_google_form(nom, pais, mitja, marca, prova):
    # La URL del teu formulari (versió "formResponse")
    url = "https://docs.google.com/forms/d/e/1FAIpQLSebKgp7PqO8nNPrR5yLzuzxdFS8ijlR127pGFpn_bpwaiNKIw/formResponse"
    
    # Aquests són els codis "entry" que he extret del teu formulari
    valors = {
        "entry.1030999587": nom,    # Camp 'nom'
        "entry.440237722": pais,    # Camp 'pais'
        "entry.1011387679": mitja,  # Camp 'mitja'
        "entry.550186989": marca,   # Camp 'millor_marca'
        "entry.2066863965": prova   # Camp 'prova'
    }
    
    try:
        requests.post(url, data=valors)
        return True
    except:
        return False

# --- DADES I MENÚ ---
PAISOS = {
    "Europa": ["Andorra", "Catalunya", "Espanya", "França", "Anglaterra", "Itàlia", "Alemanya"],
    "Amèrica": ["Estats Units", "Jamaica", "Brasil", "Canadà", "Mèxic"],
    "Àfrica": ["Kenya", "Etiòpia", "Marroc", "Nigèria", "Sud-àfrica"],
    "Asia": ["Japó", "Xina", "Corea del Sud", "Índia"],
    "Oceania": ["Austràlia", "Nova Zelanda"]
}

PROVES_LLISTAT = [
    "100 metres llisos", "200 metres llisos", "400 metres llisos", 
    "800 metres llisos", "1.500 metres llisos", "110 metres tanques", "400 metres tanques",
    "Salt de llargada", "Triple salt", "Salt d’alçada", "Salt amb perxa",
    "Llançament de pes", "Llançament de javelina", "Llançament de martell", "Llançament de disc"
]

menu = st.sidebar.radio("Menú", ["🏠 Inici", "📝 Inscripcions", "📋 Llista i PB", "🏆 COMPETICIÓ"])
df_actual = carregar_atletes()

if menu == "🏠 Inici":
    st.title("🏆 IAAF Database (Safe Mode)")
    st.write("Aquesta app guarda dades via Google Forms per evitar errors de permisos.")
    st.write(f"Atletes a l'Excel: **{len(df_actual)}**")

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
    
    if st.button("🚀 Guardar"):
        if nom:
            èxit = enviar_a_google_form(nom, pais_triat, nivell, "", prova_triada)
            if èxit:
                st.success(f"✅ {nom} enviat a l'Excel! Espera 2 segons...")
                time.sleep(2)
                st.rerun()
            else:
                st.error("Error en l'enviament.")

elif menu == "📋 Llista i PB":
    st.header("📋 Atletes Registrats")
    st.dataframe(df_actual)
    st.info("Nota: Per esborrar atletes, fes-ho directament des del teu Google Sheet.")

elif menu == "🏆 COMPETICIÓ":
    st.header("🏁 Simulació")
    prova_simu = st.selectbox("Tria la prova:", PROVES_LLISTAT)
    atletes_aptes = df_actual[df_actual['prova'] == prova_simu]
    
    if len(atletes_aptes) < 2:
        st.warning("Necessites 2 atletes d'aquesta prova.")
    else:
        triats = st.multiselect("Participants:", atletes_aptes['nom'].tolist())
        if st.button("🚀 INICIAR"):
            results = []
            for n in triats:
                atl = atletes_aptes[atletes_aptes['nom'] == n].iloc[0]
                marca = round(random.uniform(10, 15), 2) # Simulació simple
                results.append({"Atleta": n, "Marca": marca})
            st.table(pd.DataFrame(results).sort_values("Marca"))
