import streamlit as st
import pandas as pd
import random
import time

# --- CONFIGURACIÓ DE PÀGINA ---
st.set_page_config(page_title="Simulador Mundial d'Atletisme", layout="wide")

# Inicialitzar la llista d'atletes a la memòria de la sessió
if 'atletes' not in st.session_state:
    st.session_state.atletes = []

# --- BASE DE DADES DE PAÏSOS (AMB ELS TEUS CANVIS) ---
PAISOS = {
    "Europa": [
        "Catalunya", "Andorra", "Espanya", "França", "Alemanya", "Itàlia", 
        "Anglaterra", "Escòcia", "Gal·les", "Irlanda del Nord", 
        "Irlanda", "Portugal", "Bèlgica", "Països Baixos", "Suïssa", 
        "Àustria", "Grècia", "Noruega", "Suècia", "Finlàndia", "Dinamarca", 
        "Polònia", "República Txeca", "Hongria", "Ucraïna", "Croàcia"
    ],
    "Amèrica": [
        "Estats Units", "Jamaica", "Canadà", "Mèxic", "Brasil", "Argentina", 
        "Colòmbia", "Xile", "Cuba", "Bahames", "Trinitat i Tobago", "Veneçuela", 
        "Equador", "Perú", "Uruguai", "República Dominicana"
    ],
    "Àfrica": [
        "Kenya", "Etiòpia", "Marroc", "Sud-àfrica", "Nigèria", "Algèria", 
        "Egipte", "Botswana", "Uganda", "Costa d'Ivori", "Senegal", "Eritrea"
    ],
    "Àsia": [
        "Japó", "Xina", "Corea del Sud", "Índia", "Qatar", "Bahrain", 
        "Kazakhstan", "Tailàndia", "Vietnam", "Indonèsia"
    ],
    "Oceania": [
        "Austràlia", "Nova Zelanda", "Fiji", "Samoa", "Papua Nova Guinea"
    ]
}

# --- ESTILS I MENÚ ---
st.sidebar.title("🏃 Control de Pista")
menu = st.sidebar.radio("Seccions:", ["🏠 Inici", "📝 Inscriure Atletes", "📋 Llista d'Atletes", "🏆 COMPETICIÓ"])

# --- 1. PANTALLA D'INICI ---
if menu == "🏠 Inici":
    st.title("🏆 Simulador de Competicions d'Atletisme")
    st.markdown("""
    Benvingut al teu sistema de gestió esportiva. Des d'aquí podràs:
    * **Crear** el teu propi planter d'atletes internacionals.
    * **Gestionar** les baixes i les inscripcions.
    * **Simular** curses basades en el nivell de cada corredor.
    """)
    st.info("💡 Consell: Ves a 'Inscriure Atletes' per començar a omplir la graella.")

# --- 2. PANTALLA D'INSCRIPCIÓ ---
elif menu == "📝 Inscriure Atletes":
    st.header("👤 Formulari d'Inscripció")
    
    with st.form("nou_atleta", clear_on_submit=True):
        nom = st.text_input("Nom complet de l'atleta:")
        
        col1, col2 = st.columns(2)
        with col1:
            continent = st.selectbox("Continent", list(PAISOS.keys()))
        with col2:
            # Això fa que la llista de països canviï segons el continent triat
            pais = st.selectbox("País", PAISOS[continent])
            
        mitja = st.slider("Potencial / Nivell (0-100)", 10, 99, 75)
        
        botó_guardar = st.form_submit_button("Confirmar Inscripció")
        
        if botó_guardar:
            if nom.strip() != "":
                # Afegim un ID únic amb time.time() per poder esborrar sense errors
                nou_atl = {"id": time.time(), "nom": nom, "pais": pais, "mitja": mitja}
                st.session_state.atletes.append(nou_atl)
                st.success(f"✅ {nom} s'ha afegit a la delegació de {pais}!")
            else:
                st.warning("⚠️ Per favor, posa un nom vàlid.")

# --- 3. PANTALLA DE LLISTA I ESBORRAT ---
elif menu == "📋 Llista d'Atletes":
    st.header("📋 Atletes Federats")
    
    if not st.session_state.atletes:
        st.info("Encara no hi ha cap atleta inscrit.")
    else:
        # Botó per netejar-ho tot de cop
        if st.button("🗑️ ESBORRAR TOTA LA LLISTA"):
            st.session_state.atletes = []
            st.rerun()
            
        st.write("---")
        
        # Mostrar cada atleta amb el seu botó d'eliminar
        for index, atleta in enumerate(st.session_state.atletes):
            c1, c2, c3, c4 = st.columns([3, 2, 1, 1])
            c1.write(f"**{atleta['nom']}**")
            c2.write(f"🌍 {atleta['pais']}")
            c3.write(f"⚡ {atleta['mitja']}")
            
            # El "key" ha de ser únic per a cada botó
            if c4.button("Eliminar", key=f"btn_{atleta['id']}"):
                st.session_state.atletes.pop(index)
                st.rerun()

# --- 4. PANTALLA DE COMPETICIÓ ---
elif menu == "🏆 COMPETICIÓ":
    st.header("🏁 Graella de Sortida")
    
    if len(st.session_state.atletes) < 2:
        st.error("Es necessiten almenys 2 atletes per iniciar una competició.")
    else:
        noms_disponibles = [a['nom'] for a in st.session_state.atletes]
        triats = st.multiselect("Selecciona els participants:", noms_disponibles)
        
        if st.button("🚀 DISPARAR SORTIDA"):
            if len(triats) < 2:
                st.warning("Selecciona almenys dos corredors per a la cursa.")
            else:
                st.write("🏃 *Corrent...*")
                progress_bar = st.progress(0)
                for i in range(100):
                    time.sleep(0.01)
                    progress_bar.progress(i + 1)
                
                # Càlcul de resultats
                resultats = []
                for n in triats:
                    # Trobar l'objecte de l'atleta triat
                    atl_info = next(item for item in st.session_state.atletes if item["nom"] == n)
                    # Lògica: a més mitja, menys temps (més ràpid), amb un toc de sort aleatòria
                    base_temps = 14.0 
                    factor_velocitat = atl_info['mitja'] / 15
                    sort = random.uniform(-0.3, 0.3)
                    temps_final = round(base_temps - factor_velocitat + sort, 2)
                    
                    resultats.append({"Posició": 0, "Atleta": n, "País": atl_info['pais'], "Temps": temps_final})
                
                # Ordenar i posar posició
                df_final = pd.DataFrame(resultats).sort_values(by="Temps")
                df_final["Posició"] = range(1, len(df_final) + 1)
                
                st.balloons()
                st.subheader("📊 Podi i Resultats")
                st.table(df_final.set_index("Posició"))
