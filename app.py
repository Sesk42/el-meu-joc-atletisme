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

def calcular_marca(nivell, conf):
    """Calcula una marca individual amb aleatorietat."""
    base = conf['n1'] + (nivell - 1) * (conf['n100'] - conf['n1']) / 99
    if conf['tipus'] == "temps":
        factor = 1 + random.uniform(-0.01, 0.04)
        return round(base * factor, 2)
    else:
        # 10% de probabilitat de nul
        if random.random() < 0.10:
            return None # Nul
        factor = 1 + random.uniform(-0.04, 0.01)
        return round(base * factor, 2)

def millor_intent(intents, tipus):
    """Retorna la millor marca d'una llista (ignorant None/Nuls)."""
    valids = [i for i in intents if i is not None]
    if not valids: return None
    return min(valids) if tipus == "temps" else max(valids)
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

# --- FUNCIÓ ENVIAMENT ---
def enviar_a_google_form(nom, pais, mitja, marca, prova):
    # URL de resposta del teu formulari
    url = "https://docs.google.com/forms/d/e/1FAIpQLSebKgp7PqO8nNPrR5yLzuzxdFS8ijlR127pGFpn_bpwaiNKIw/formResponse"
    
    # ARA SÍ: Els IDs Reals que has trobat
    payload = {
        "entry.1668159850": str(nom),     # Nom
        "entry.1670433567": str(pais),    # País
        "entry.1326600864": str(mitja),   # Nivell / Mitja
        "entry.1635147765": str(marca),   # Millor Marca
        "entry.445329310": str(prova)     # Prova
    }
    
    try:
        # Enviament tipus POST (estàndard de Google)
        response = requests.post(url, data=payload)
        
        # Si Google respon OK (200), l'atleta ja hauria de sortir a l'Excel
        return response.ok
    except Exception as e:
        st.error(f"Error de connexió: {e}")
        return False
# --- LÒGICA ---
menu = st.sidebar.radio("Menú", ["🏠 Inici", "📝 Inscripcions", "📋 Llista i PB", "🏆 COMPETICIÓ"])
df_actual = carregar_atletes()

if menu == "🏠 Inici":
    st.title("🏆 IAAF World Database & Records")
    st.write(f"Atletes registrats: **{len(df_actual)}**")

elif menu == "📝 Inscripcions":
    st.header("👤 Nova Inscripció")
    
    # FORA del form posem els selectbox perque s'actualitzin a l'instant
    nom_in = st.text_input("Nom de l'atleta:")
    c1, c2 = st.columns(2)
    with c1:
        cont = st.selectbox("Continent", sorted(PAISOS.keys()))
    with c2:
        # La clau 'key' és el que feia que funcionés abans!
        pais_triat = st.selectbox("País", sorted(PAISOS[cont]), key=f"p_{cont}")
    
    c3, c4 = st.columns(2)
    with c3:
        prova_triada = st.selectbox("Prova Especialitzada", PROVES_LLISTAT)
    with c4:
        nivell = st.slider("Nivell (0-100)", 10, 99, 80)
    
    # El botó sol, sense 'st.form' per evitar embolics de refresc
    if st.button("🚀 Guardar Atleta"):
        if nom_in.strip():
            if enviar_a_google_form(nom_in, pais_triat, nivell, "", prova_triada):
                st.success(f"✅ {nom_in} guardat correctament!")
                st.cache_data.clear()
                time.sleep(2)
                st.rerun()
            else:
                st.error("Error al guardar.")
        else:
            st.warning("Escriu un nom!")

elif menu == "📋 Llista i PB":
    st.header("📋 Rànquing Personal")
    st.dataframe(df_actual[['nom', 'pais', 'prova', 'mitja', 'millor_marca']], use_container_width=True)

elif menu == "🏆 COMPETICIÓ":
    st.header("🏁 Sistema de Competició Oficial")

    # Mantenim config_proves igual que abans...
    config_proves = {
        "100 metres llisos": {"n1": 10.44, "n100": 9.58, "tipus": "temps", "fase": "curses"},
        "200 metres llisos": {"n1": 21.15, "n100": 19.19, "tipus": "temps", "fase": "curses"},
        "400 metres llisos": {"n1": 46.67, "n100": 43.03, "tipus": "temps", "fase": "curses"},
        "800 metres llisos": {"n1": 111.19, "n100": 100.91, "tipus": "temps", "fase": "curses"},
        "1.500 metres llisos": {"n1": 222.36, "n100": 206.00, "tipus": "temps", "fase": "curses"},
        "110 metres tanques": {"n1": 13.64, "n100": 12.80, "tipus": "temps", "fase": "curses"},
        "400 metres tanques": {"n1": 48.84, "n100": 45.94, "tipus": "temps", "fase": "curses"},
        "Salt de llargada": {"n1": 8.25, "n100": 8.95, "tipus": "metres", "fase": "concurs"},
        "Triple salt": {"n1": 17.24, "n100": 18.29, "tipus": "metres", "fase": "concurs"},
        "Salt d’alçada": {"n1": 2.28, "n100": 2.45, "tipus": "metres", "fase": "concurs"},
        "Salt amb perxa": {"n1": 5.51, "n100": 6.24, "tipus": "metres", "fase": "concurs"},
        "Llançament de pes": {"n1": 22.73, "n100": 23.56, "tipus": "metres", "fase": "concurs"},
        "Llançament de disc": {"n1": 70.13, "n100": 74.08, "tipus": "metres", "fase": "concurs"},
        "Llançament de martell": {"n1": 85.57, "n100": 86.74, "tipus": "metres", "fase": "concurs"},
        "Llançament de javelina": {"n1": 89.34, "n100": 98.48, "tipus": "metres", "fase": "concurs"}
    }

    prova_simu = st.selectbox("Tria la prova:", list(config_proves.keys()))
    conf = config_proves[prova_simu]
    atletes_aptes = df_actual[df_actual['prova'] == prova_simu]

    # Requisits mínims
    num_necessari = 48 if conf['fase'] == "curses" else 48
    if len(atletes_aptes) < num_necessari:
        st.warning(f"Falten atletes per completar els quadres de competició (Teniu {len(atletes_aptes)}/{num_necessari}).")
    else:
        if st.button(f"🚀 INICIAR {prova_simu.upper()}"):
            participats = atletes_aptes.sample(48).to_dict('records') # Seleccionem 48 a l'atzar
            
            # --- LÒGICA PER A CURSES ---
            if conf['fase'] == "curses":
                # ELIMINATÒRIES (6 grups de 8)
                grups = [participats[i:i+8] for i in range(0, 48, 8)]
                st.subheader("🏁 ELIMINATÒRIES (6 sèries)")
                
                classificats_semi = []
                tercers = []
                
                for idx, grup in enumerate(grups):
                    results = []
                    for atl in grup:
                        m = calcular_marca(float(atl['mitja']), conf)
                        results.append({"nom": atl['nom'], "pais": atl['pais'], "mitja": atl['mitja'], "marca": m})
                    
                    df_res = pd.DataFrame(results).sort_values("marca")
                    st.write(f"**Sèrie {idx+1}**")
                    st.table(df_res)
                    
                    # 1er i 2on passen directe
                    classificats_semi.extend(df_res.iloc[0:2].to_dict('records'))
                    # El 3er va a la "repesca"
                    tercers.append(df_res.iloc[2].to_dict('records'))
                
                # Millors 4 tercers (amb sorteig en cas d'empat)
                df_tercers = pd.DataFrame(tercers).sort_values("marca")
                # Si hi ha empat en la posició 4, barregem els que tenen el mateix temps
                millors_4_tercers = df_tercers.sample(frac=1).sort_values("marca").head(4) 
                classificats_semi.extend(millors_4_tercers.to_dict('records'))
                
                st.success(f"Classificats per a Semifinals: {len(classificats_semi)} atletes.")

                # SEMIFINALS (2 grups de 8)
                st.subheader("🏃 SEMIFINALS (2 sèries)")
                grups_semi = [classificats_semi[i:i+8] for i in range(0, 16, 8)]
                classificats_final = []
                
                for idx, grup in enumerate(grups_semi):
                    results = []
                    for atl in grup:
                        m = calcular_marca(float(atl['mitja']), conf)
                        results.append({"nom": atl['nom'], "pais": atl['pais'], "mitja": atl['mitja'], "marca": m})
                    df_res = pd.DataFrame(results).sort_values("marca")
                    st.write(f"**Semifinal {idx+1}**")
                    st.table(df_res)
                    classificats_final.extend(df_res.iloc[0:4].to_dict('records'))
                
                # FINAL
                st.subheader("🥇 FINAL")
                final_res = []
                for atl in classificats_final:
                    m = calcular_marca(float(atl['mitja']), conf)
                    final_res.append({"Atleta": atl['nom'], "País": atl['pais'], "Marca": m})
                    # Guardar a l'Excel la marca final
                    enviar_a_google_form(atl['nom'], atl['pais'], atl['mitja'], m, prova_simu)
                
                df_final = pd.DataFrame(final_res).sort_values("Marca")
                st.table(df_final)
                st.balloons()

            # --- LÒGICA PER A CONCURSOS (Salts/Llançaments) ---
            else:
                st.subheader("📐 ELIMINATÒRIES DE CONCURS (2 grups de 24)")
                grups_concurs = [participats[i:i+24] for i in range(0, 48, 24)]
                classificats_final = []
                
                for idx, grup in enumerate(grups_concurs):
                    results = []
                    for atl in grup:
                        # 3 intents en eliminatòria
                        intents = [calcular_marca(float(atl['mitja']), conf) for _ in range(3)]
                        # Desempat per segon millor intent, tercer, etc. (ordenant la llista d'intents)
                        intents_ordenats = sorted([i if i is not None else -1 for i in intents], reverse=True)
                        m_max = intents_ordenats[0]
                        results.append({
                            "nom": atl['nom'], "pais": atl['pais'], "mitja": atl['mitja'],
                            "marca": m_max if m_max != -1 else "Nul",
                            "intents": intents_ordenats
                        })
                    
                    # Ordenació complexa: Marca principal, després 2on millor, després 3er
                    df_res = pd.DataFrame(results)
                    df_res[['m1', 'm2', 'm3']] = pd.DataFrame(df_res['intents'].tolist(), index=df_res.index)
                    df_res = df_res.sort_values(['m1', 'm2', 'm3'], ascending=False)
                    
                    st.write(f"**Grup {idx+1}** (Top 8 passen)")
                    st.table(df_res[['nom', 'pais', 'marca']].head(12)) # Mostrem 12 per veure el tall
                    classificats_final.extend(df_res.iloc[0:8].to_dict('records'))
                
                # FINAL DE CONCURS (16 atletes)
                st.subheader("🥇 FINAL DE CONCURS")
                final_res = []
                for atl in classificats_final:
                    # En la final solen fer 6 intents, però seguim la teva regla de nuls
                    intents = [calcular_marca(float(atl['mitja']), conf) for _ in range(3)]
                    intents_ordenats = sorted([i if i is not None else -1 for i in intents], reverse=True)
                    m_max = intents_ordenats[0]
                    marca_final = m_max if m_max != -1 else 0
                    
                    final_res.append({"Atleta": atl['nom'], "País": atl['pais'], "Marca": marca_final})
                    enviar_a_google_form(atl['nom'], atl['pais'], atl['mitja'], marca_final, prova_simu)
                
                df_final = pd.DataFrame(final_res).sort_values("Marca", ascending=False)
                st.table(df_final)
                st.balloons()

        st.cache_data.clear()
