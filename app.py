import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
import random
import time

# --- CONFIGURACIÓ ---
st.set_page_config(page_title="IAAF Database Pro", layout="wide")

conn = st.connection("gsheets", type=GSheetsConnection)

def carregar_atletes():
    df = conn.read(ttl=0)
    if df is None or df.empty:
        return pd.DataFrame(columns=['id', 'nom', 'pais', 'mitja', 'millor_marca', 'tipus_prova'])
    df['millor_marca'] = pd.to_numeric(df['millor_marca'], errors='coerce')
    return df

# --- PAÏSOS (La teva llista) ---
PAISOS = {
    "Europa": ["Albània", "Alemanya", "Andorra", "Armènia", "Àustria", "Bèlgica", "Bielorússia", "Bòsnia i Hercegovina", "Bulgària", "Catalunya", "Xipre", "Croàcia", "Dinamarca", "Eslovàquia", "Eslovènia", "Espanya", "Estònia", "Finlàndia", "França", "Geòrgia", "Grècia", "Hongria", "Irlanda", "Islàndia", "Israel", "Itàlia", "Kosovo", "Letònia", "Liechtenstein", "Lituània", "Luxemburg", "Malta", "Moldàvia", "Mònaco", "Montenegro", "Noruega", "Pais Basc", "Països Baixos", "Polònia", "Portugal", "Inglaterra", "Escocia", "Gales", "Irlanda del Nord", "República Txeca", "Romania", "Rússia", "San Marino", "Sèrbia", "Suècia", "Suïssa", "Turquia", "Ucraïna"],
    "Àfrica": ["Algèria", "Angola", "Benín", "Botswana", "Burkina Faso", "Burundi", "Cabo Verde", "Camerun", "Comores", "Congo", "Costa d’Ivori", "Djibouti", "Egipte", "Eritrea", "Eswatini", "Etiòpia", "Gabon", "Gàmbia", "Ghana", "Guinea", "Guinea-Bissau", "Guinea Equatorial", "Kenya", "Lesotho", "Libèria", "Líbia", "Madagascar", "Malawi", "Mali", "Marroc", "Maurici", "Mauritània", "Moçambic", "Namíbia", "Níger", "Nigèria", "República Centreafricana", "República Democràtica del Congo", "Ruanda", "São Tomé i Príncipe", "Senegal", "Seychelles", "Sierra Leone", "Somàlia", "Sudan", "Sudan del Sud", "Tanzània", "Togo", "Tunísia", "Uganda", "Zàmbia", "Zimbabwe"],
    "Amèrica": ["Antigua i Barbuda", "Argentina", "Bahamas", "Barbados", "Belize", "Bolívia", "Brasil", "Canadà", "Xile", "Colòmbia", "Costa Rica", "Cuba", "Dominica", "República Dominicana", "Equador", "El Salvador", "Grenada", "Guatemala", "Guyana", "Haití", "Hondures", "Jamaica", "Mèxic", "Nicaragua", "Panamà", "Paraguai", "Perú", "Saint Kitts i Nevis", "Saint Lucia", "Saint Vincent i les Grenadines", "Surinam", "Trinitat i Tobago", "Estats Units", "Uruguai", "Veneçuela"],
    "Asia": ["Afganistan", "Aràbia Saudita", "Azerbaidjan", "Bahrain", "Bangladesh", "Bhutan", "Brunei", "Cambodja", "Xina", "Corea del Nord", "Corea del Sud", "Emirats Àrabs Units", "Filipines", "Índia", "Indonèsia", "Iran", "Iraq", "Japó", "Jordània", "Kazakhstan", "Kirguizistan", "Kuwait", "Laos", "Líban", "Malàisia", "Maldives", "Mongòlia", "Myanmar", "Nepal", "Oman", "Pakistan", "Qatar", "Singapur", "Sri Lanka", "Síria", "Tailàndia", "Taiwan", "Tajikistan", "Timor Oriental", "Turkmenistan", "Uzbekistan", "Vietnam", "Yemen"],
    "Oceania": ["Austràlia", "Fiji", "Illes Marshall", "Illes Salomó", "Kiribati", "Micronèsia", "Nauru", "Nova Zelanda", "Palau", "Papua Nova Guinea", "Samoa", "Tonga", "Tuvalu", "Vanuatu"]
}

# --- MENÚ ---
menu = st.sidebar.radio("Menú", ["🏠 Inici", "📝 Inscripcions", "📋 Llista i PB", "🏆 COMPETICIÓ"])

df_actual = carregar_atletes()

if menu == "🏠 Inici":
    st.title("🏆 IAAF World Database & Records")
    st.write(f"Atletes sincronitzats: **{len(df_actual)}**")

elif menu == "📝 Inscripcions":
    st.header("👤 Nova Inscripció")
    
    # 1. Triem el nom
    nom = st.text_input("Nom de l'atleta:")
    
    # 2. Triem Continent i País (FORA del form perquè es refresquin al moment)
    c1, c2 = st.columns(2)
    with c1:
        cont = st.selectbox("Continent", sorted(PAISOS.keys()))
    with c2:
        # La clau dinàmica f"p_{cont}" obliga a Streamlit a refrescar la llista quan canvia el continent
        pais_triat = st.selectbox("País", sorted(PAISOS[cont]), key=f"p_{cont}")
    
    # 3. La resta de detalls
    col_t1, col_t2 = st.columns(2)
    with col_t1:
        tipus = st.selectbox("Tipus de Prova", ["Carrera (100m)", "Concurs (Salt/Llançament)"])
    with col_t2:
        nivell = st.slider("Nivell (Potencial)", 10, 99, 80)
    
    # 4. Botó de guardar
    if st.button("🚀 Guardar Atleta"):
        if nom.strip():
            nou_atleta = pd.DataFrame([{
                "id": str(time.time()), "nom": nom, "pais": pais_triat, 
                "mitja": nivell, "millor_marca": None, "tipus_prova": tipus
            }])
            df_actualitzat = pd.concat([df_actual, nou_atleta], ignore_index=True)
            conn.update(data=df_actualitzat)
            st.success(f"✅ {nom} ({pais_triat}) registrat correctament!")
            time.sleep(1)
            st.rerun()
        else:
            st.error("⚠️ Si us plau, introdueix un nom.")

elif menu == "📋 Llista i PB":
    st.header("📋 Rànquing Personal")
    if df_actual.empty:
        st.write("No hi ha atletes.")
    else:
        for i, row in df_actual.iterrows():
            c1, c2, c3, c4, c5 = st.columns([3, 2, 1, 2, 1])
            c1.write(f"**{row['nom']}**")
            c2.write(row['pais'])
            c3.write(f"⚡{row['mitja']}")
            
            pb = row['millor_marca']
            unitat = "s" if row['tipus_prova'] == "Carrera (100m)" else "m"
            display_pb = "Sense marca" if pd.isna(pb) else f"{pb}{unitat}"
            c4.write(f"⭐ PB: **{display_pb}**")
            
            if c5.button("Eliminar", key=f"del_{row['id']}"):
                df_nou = df_actual.drop(i)
                conn.update(data=df_nou)
                st.rerun()

elif menu == "🏆 COMPETICIÓ":
    st.header("🏁 Simulació")
    if len(df_actual) < 2:
        st.warning("Falten atletes.")
    else:
        triats = st.multiselect("Tria participants:", df_actual['nom'].tolist())
        if st.button("🚀 INICIAR"):
            if not triats:
                st.error("Tria algun atleta!")
            else:
                results = []
                updates = False
                for n in triats:
                    idx = df_actual[df_actual['nom'] == n].index[0]
                    atl = df_actual.iloc[idx]
                    
                    if atl['tipus_prova'] == "Carrera (100m)":
                        marca = round(13.5 - (int(atl['mitja'])/18) + random.uniform(-0.15, 0.15), 2)
                        es_millor = pd.isna(atl['millor_marca']) or marca < atl['millor_marca']
                    else: 
                        marca = round((int(atl['mitja'])/12) + random.uniform(-0.5, 0.5), 2)
                        es_millor = pd.isna(atl['millor_marca']) or marca > atl['millor_marca']
                    
                    msg = ""
                    if es_millor:
                        df_actual.at[idx, 'millor_marca'] = marca
                        updates = True
                        msg = "🔥 NOU PB!"
                    
                    results.append({"Atleta": n, "Tipus": atl['tipus_prova'], "Marca": marca, "Info": msg})
                
                if updates:
                    conn.update(data=df_actual)
                
                st.balloons()
                res_df = pd.DataFrame(results).sort_values("Marca", ascending=(True if "Carrera" in str(results[0]) else False))
                st.table(res_df)
                
