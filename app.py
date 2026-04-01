import streamlit as st
import pandas as pd
import random
import json
import os

# CONFIGURACIÓ DE L'APP
st.set_page_config(page_title="Simulador Atletisme", layout="wide")

# ARXIU DE DADES (Es guardarà al costat del codi)
DB_FILE = 'atletes.json'

def carregar_dades():
    if os.path.exists(DB_FILE):
        with open(DB_FILE, 'r') as f:
            return json.load(f)
    return {"atletes": []}

def guardar_dades(dades):
    with open(DB_FILE, 'w') as f:
        json.dump(dades, f, indent=4)

# Inicialitzar dades si no existeixen
if 'dades' not in st.session_state:
    st.session_state.dades = carregar_dades()

# DADES GEOGRÀFIQUES
PAISOS = {
    "Europa": ["Catalunya", "Espanya", "França", "Andorra", "Alemanya", "Itàlia", "Regne Unit"],
    "Amèrica": ["Estats Units", "Jamaica", "Brasil", "Canadà", "Mèxic"],
    "Àfrica": ["Kenya", "Etiòpia", "Marroc", "Nigèria", "Sud-àfrica"]
}

DISCIPLINES = ["100 metres", "200 metres", "Salt de llargada", "Llançament de Pes"]

# --- INTERFÍCIE ---
st.title("🏆 Simulador d'Atletisme")

menu = st.sidebar.radio("Menú", ["Inici", "Afegir Atletes", "La meva Llista"])

if menu == "Inici":
    st.write("Benvingut al teu centre de gestió d'atletisme.")
    st.info("Fes servir el menú de l'esquerra per començar a crear el teu club.")

elif menu == "Afegir Atletes":
    st.header("👤 Nou Atleta")
    with st.form("formulari"):
        nom = st.text_input("Nom de l'atleta:")
        col1, col2 = st.columns(2)
        with col1:
            continent = st.selectbox("Continent", list(PAISOS.keys()))
            pais = st.selectbox("País", PAISOS[continent])
        with col2:
            disciplina = st.selectbox("Disciplina principal", DISCIPLINES)
            mitja = st.slider("Nivell de l'atleta (Mitjana)", 1, 100, 50)
        
        if st.form_submit_button("Guardar al sistema"):
            nou_atleta = {
                "nom": nom, "pais": pais, "disciplina": disciplina, "mitja": mitja
            }
            st.session_state.dades["atletes"].append(nou_atleta)
            guardar_dades(st.session_state.dades)
            st.success(f"✅ {nom} s'ha afegit correctament!")

elif menu == "La meva Llista":
    st.header("📋 Atletes Registrats")
    if st.session_state.dades["atletes"]:
        df = pd.DataFrame(st.session_state.dades["atletes"])
        st.table(df)
    else:
        st.warning("Encara no has creat cap atleta.")
