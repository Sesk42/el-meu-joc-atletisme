import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
import random
import time

# --- CONFIGURACIÓ ---
st.set_page_config(page_title="IAAF Official Events Database", layout="wide")

conn = st.connection("gsheets", type=GSheetsConnection)

def carregar_atletes():
    df = conn.read(ttl=0)
    if df is None or df.empty:
        return pd.DataFrame(columns=['id', 'nom', 'pais', 'mitja', 'millor_marca', 'prova'])
    df['millor_marca'] = pd.to_numeric(df['millor_marca'], errors='coerce')
    return df

# --- PROVES OFICIALS ---
PROVES_LLISTAT = [
    "100 metres llisos", "200 metres llisos", "400 metres llisos", 
    "800 metres llisos", "1.500 metres llisos", "110 metres tanques", "400 metres tanques",
    "Salt de llargada", "Triple salt", "Salt d’alçada", "Salt amb perxa",
    "Llançament de pes", "Llançament de javelina", "Llançament de martell", "Llançament de disc"
]

# --- PAÏSOS (Llista completa) ---
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
    st.title("🏆 IAAF Official Events Manager")
    st.write(f"Atletes registrats a la base de dades: **{len(df_actual)}**")

elif menu == "📝 Inscripcions":
    st.header("👤 Registre d'Atleta per Prova")
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
        nivell = st.slider("Nivell de l'atleta (0-100)", 10, 99, 80)
    
    if st.button("🚀 Guardar Atleta"):
        if nom.strip():
            nou_atleta = pd.DataFrame([{
                "id": str(time.time()), "nom": nom, "pais": pais_triat, 
                "mitja": nivell, "millor_marca": None, "prova": prova_triada
            }])
            df_actualitzat = pd.concat([df_actual, nou_atleta], ignore_index=True)
            conn.update(data=df_actualitzat)
            st.success(f"✅ {nom} registrat en {prova_triada}!")
            time.sleep(1)
            st.rerun()
        else:
            st.error("Escriu un nom!")

elif menu == "📋 Llista i PB":
    st.header("📋 Rànquing d'Atletes i Marques Personals")
    if df_actual.empty:
        st.write("Encara no hi ha atletes.")
    else:
        for i, row in df_actual.iterrows():
            c1, c2, c3, c4, c5 = st.columns([2, 1, 2, 2, 1])
            c1.write(f"**{row['nom']}**")
            c2.write(row['pais'])
            c3.write(f"🏃 {row['prova']}")
            
            pb = row['millor_marca']
            es_cursa = any(x in row['prova'].lower() for x in ["metres", "tanques"])
            unitat = "s" if es_cursa else "m"
            display_pb = "---" if pd.isna(pb) else f"{pb}{unitat}"
            c4.write(f"⭐ PB: **{display_pb}**")
            
            if c5.button("🗑️", key=f"del_{row['id']}"):
                df_nou = df_actual.drop(i)
                conn.update(data=df_nou)
                st.rerun()

elif menu == "🏆 COMPETICIÓ":
    st.header("🏁 Simulació de Proves Oficials")
    prova_simu = st.selectbox("Tria la prova a disputar:", PROVES_LLISTAT)
    
    # Filtrem atletes que fan aquesta prova
    atletes_aptes = df_actual[df_actual['prova'] == prova_simu]
    
    if len(atletes_aptes) < 2:
        st.warning(f"Necessites almen_s 2 atletes registrats en la prova de '{prova_simu}' per competir.")
    else:
        triats = st.multiselect("Selecciona els participants:", atletes_aptes['nom'].tolist())
        
        if st.button("🚀 INICIAR PROVA"):
            if not triats:
                st.error("Selecciona participants!")
            else:
                results = []
                updates = False
                es_cursa = any(x in prova_simu.lower() for x in ["metres", "tanques"])
                
                for n in triats:
                    idx = df_actual[df_actual['nom'] == n].index[0]
                    atl = df_actual.iloc[idx]
                    pot = int(atl['mitja'])
                    
                    # --- LÒGICA DE MARQUES PER CADA PROVA ---
                    if prova_simu == "100 metres llisos": marca = round(13.0 - (pot/20) + random.uniform(-0.1, 0.1), 2)
                    elif prova_simu == "200 metres llisos": marca = round(26.0 - (pot/10) + random.uniform(-0.2, 0.2), 2)
                    elif prova_simu == "400 metres llisos": marca = round(60.0 - (pot/4) + random.uniform(-0.5, 0.5), 2)
                    elif prova_simu == "800 metres llisos": marca = round(140.0 - (pot/1.5) + random.uniform(-1, 1), 2)
                    elif prova_simu == "1.500 metres llisos": marca = round(280.0 - pot + random.uniform(-2, 2), 2)
                    elif prova_simu == "110 metres tanques": marca = round(17.0 - (pot/15) + random.uniform(-0.2, 0.2), 2)
                    elif prova_simu == "400 metres tanques": marca = round(65.0 - (pot/3.5) + random.uniform(-0.5, 0.5), 2)
                    elif prova_simu == "Salt de llargada": marca = round(4.0 + (pot/25) + random.uniform(-0.2, 0.2), 2)
                    elif prova_simu == "Triple salt": marca = round(10.0 + (pot/15) + random.uniform(-0.3, 0.3), 2)
                    elif prova_simu == "Salt d’alçada": marca = round(1.5 + (pot/100) + random.uniform(-0.05, 0.05), 2)
                    elif prova_simu == "Salt amb perxa": marca = round(3.0 + (pot/40) + random.uniform(-0.1, 0.1), 2)
                    elif "Llançament" in prova_simu: marca = round(10.0 + (pot/1.5) + random.uniform(-2, 2), 2)
                    else: marca = pot # fallback
                    
                    # Comprovar PB
                    if es_cursa:
                        es_millor = pd.isna(atl['millor_marca']) or marca < atl['millor_marca']
                    else:
                        es_millor = pd.isna(atl['millor_marca']) or marca > atl['millor_marca']
                    
                    msg = ""
                    if es_millor:
                        df_actual.at[idx, 'millor_marca'] = marca
                        updates = True
                        msg = "🔥 NOU PB!"
                    
                    results.append({"Atleta": n, "País": atl['pais'], "Marca": marca, "Info": msg})
                
                if updates:
                    conn.update(data=df_actual)
                
                st.balloons()
                # Ordenar: si és cursa (temps baix millor), si és salt/llançament (marca alta millor)
                res_df = pd.DataFrame(results).sort_values("Marca", ascending=es_cursa)
                st.table(res_df)
