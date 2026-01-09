import streamlit as st
import requests
import os

# 1. CONFIGURAÇÃO DA PÁGINA
st.set_page_config(page_title="Brawl Progress", page_icon="⭐", layout="centered")

# LINKS DE ASSETS
STARR_DROP = "https://cdn-assets-eu.frontify.com/s3/frontify-enterprise-files-eu/eyJwYXRoIjoic3VwZXJjZWxsXC9maWxlXC85NlZzVzI1bUpOOG1Sc2o5YUF4VC5wbmcifQ:supercell:K58Ema5gs3ZrzQmEGsNWX2oGs9RUZnuL-8EVVXb8jxE?width=200"

# 2. ESTILO CSS (O DESIGN DE OURO)
st.markdown(f"""
    <style>
    .stApp {{ background-color: #001a33; overflow-x: hidden; }}
    .bg-star {{ position: fixed; opacity: 0.1; z-index: 0; pointer-events: none; }}
    
    @keyframes stars-fall {{
        0% {{ top: -10%; opacity: 1; transform: rotate(0deg); }}
        100% {{ top: 110%; opacity: 0; transform: rotate(360deg); }}
    }}
    .brawl-star-rain {{
        position: fixed; top: -10%; font-size: 28px;
        animation: stars-fall 3s linear forwards; z-index: 9999; pointer-events: none;
    }}
    .main-container {{ text-align: center; position: relative; z-index: 1; padding-top: 30px; }}
    .brawl-title {{
        font-family: 'Arial Black', sans-serif; color: #FFCE00; font-size: 60px;
        text-transform: uppercase; line-height: 0.85; margin-top: 20px;
        text-shadow: 4px 4px 0 #000, 8px 8px 0 #000;
    }}
    .record-box {{
        background: rgba(255, 206, 0, 0.15); border: 3px solid #FFCE00;
        border-radius: 20px; padding: 20px; margin: 20px 0; text-align: center;
    }}
    .streamlit-expanderHeader {{
        background-color: rgba(255, 255, 255, 0.05) !important;
        border: 1px solid #FFCE00 !important; border-radius: 10px !important; color: #FFCE00 !important;
    }}
    </style>
    
    <img src="{STARR_DROP}" class="bg-star" style="width: 80px; top: 12%; left: 8%; transform: rotate(15deg);">
    <img src="{STARR_DROP}" class="bg-star" style="width: 110px; top: 65%; left: 82%; transform: rotate(-20deg);">
    <img src="{STARR_DROP}" class="bg-star" style="width: 70px; top: 25%; left: 88%; transform: rotate(35deg);">
    <img src="{STARR_DROP}" class="bg-star" style="width: 90px; top: 75%; left: 5%; transform: rotate(-10deg);">
    <img src="{STARR_DROP}" class="bg-star" style="width: 60px; top: 45%; left: 15%; transform: rotate(50deg);">
    """, unsafe_allow_html=True)

# 3. CABEÇALHO
st.markdown(f'<div class="main-container"><img src="{STARR_DROP}" width="180"><h1 class="brawl-title">BRAWL<br>PROGRESS</h1></div>', unsafe_allow_html=True)

# 4. ENTRADA
tag_input = st.text_input("DIGITE SUA TAG:", placeholder="Ex: 8G0CCCR").upper().strip()

if st.button("ANALISAR CONTA"):
    if tag_input:
        # Tenta pegar o Token do Streamlit Secrets OU usa o Token direto abaixo
        # Se for colar direto, substitua 'SEU_TOKEN_AQUI' pelo seu token da Supercell
        TOKEN_FINAL = st.secrets.get("BRAWL_TOKEN", "COLE_SEU_TOKEN_AQUI").strip()
        
        TAG_FINAL = tag_input.replace("#", "").replace(" ", "").strip().upper()
        headers = {"Authorization": f"Bearer {TOKEN_FINAL}", "Accept": "application/json"}
        
        # No Streamlit Cloud, tentamos direto a Oficial primeiro porque o IP é melhor
        url_oficial = f"https://api.brawlstars.com/v1/players/%23{TAG_FINAL}"
        url_proxy = f"https://bsproxy.vercel.app/api/v1/players/%23{TAG_FINAL}"

        try:
            with st.spinner('Conectando ao servidor da Supercell...'):
                res = requests.get(url_oficial, headers=headers, timeout=10)
                if res.status_code != 200:
                    res = requests.get(url_proxy, headers=headers, timeout=10)

            if res.status_code == 200:
                data = res.json()
                st.success(f"✅ CONECTADO! Jogador: {data.get('name')}")
                
                # FEATURE: ESTRELAS CAINDO
                st.markdown('<div class="brawl-star-rain" style="left:20%">⭐</div><div class="brawl-star-rain" style="left:50%">⭐</div><div class="brawl-star-rain" style="left:80%">⭐</div>', unsafe_allow_html=True)
                
                brawlers = data.get('brawlers', [])
                if brawlers:
                    # FEATURE: BRAWLER RECORDISTA
                    rec = max(brawlers, key=lambda x: x.get('highestTrophies', 0))
                    st.markdown(f"""
                        <div class="record-box">
                            <p style="color: #FFCE00; font-weight: bold; margin: 0;">BRAWLER QUE FOI MAIS LONGE</p>
                            <img src="https://cdn.brawlify.com/brawlers/borderless/{rec['id']}.png" width="120">
                            <h2 style="color: white; margin: 0;">{rec['name']}</h2>
                            <p style="color: #FFCE00; font-size: 18px; margin: 0;">Recorde Máximo: {rec.get('highestTrophies')} 🏆</p>
                        </div>
                    """, unsafe_allow_html=True)

                    # FEATURE: MÉTRICAS
                    c1, c2, c3 = st.columns(3)
                    c1.metric("🏆 Troféus", data.get('trophies'))
                    c2.metric("🎖️ Nível", data.get('expLevel'))
                    c3.metric("🥊 Brawlers", len(brawlers))
                    
                    st.write("---")
                    
                    # FEATURE: LISTA DE BRAWLERS
                    b_sorted = sorted(brawlers, key=lambda x: x['trophies'], reverse=True)
                    for b in b_sorted:
                        nome = f"⭐ {b['name']}" if b['trophies'] >= 1000 else b['name']
                        img_url = f"https://cdn.brawlify.com/brawlers/borderless/{b['id']}.png"
                        
                        with st.expander(f"{nome} - 🏆 {b['trophies']}"):
                            col_img, col_txt = st.columns([1, 3])
                            col_img.image(img_url, width=80)
                            col_txt.write(f"**Poder:** {b['power']} | **Recorde:** {b.get('highestTrophies')}")
                            col_txt.progress(min(b['power'] / 11, 1.0))
            else:
                st.error(f"Erro {res.status_code}: Não foi possível acessar os dados.")
                st.info("Crie uma Key com IP 0.0.0.0 no site Developer da Supercell.")
        except Exception as e:
            st.error(f"Erro de conexão: {e}")
    else:
        st.warning("Por favor, digite uma TAG.")
