import streamlit as st

# Sayfa yapılandırması (Mevcut kodunuzda varsa burayı atlayın)
st.set_page_config(page_title="Psikiyatri Ligi", layout="centered")

# --- CSS VE ANİMASYON KODLARI ---
st.markdown("""
<style>
    /* 1. ARKA PLAN ANİMASYONU (Düşen Semboller) */
    .psych-bg {
        position: fixed;
        top: 0;
        left: 0;
        width: 100%;
        height: 100%;
        z-index: -1; /* En arkada durması için */
        overflow: hidden;
        pointer-events: none; /* Tıklamaları engellememesi için */
    }

    .psych-icon {
        position: absolute;
        top: -50px;
        color: #6a1b9a; /* Mor tonlarında */
        font-size: 2rem;
        opacity: 0.15; /* Göz yormaması için çok silik */
        animation: fall linear infinite;
    }

    /* Düşme Animasyonu */
    @keyframes fall {
        0% { transform: translateY(-10vh) rotate(0deg); }
        100% { transform: translateY(110vh) rotate(360deg); }
    }

    /* Sembollerin farklı hız ve konumlarda düşmesi için varyasyonlar */
    .icon-1 { left: 10%; animation-duration: 10s; animation-delay: 0s; font-size: 3rem; }
    .icon-2 { left: 25%; animation-duration: 15s; animation-delay: 2s; font-size: 2rem; }
    .icon-3 { left: 40%; animation-duration: 12s; animation-delay: 5s; font-size: 2.5rem; }
    .icon-4 { left: 60%; animation-duration: 18s; animation-delay: 1s; font-size: 3rem; }
    .icon-5 { left: 80%; animation-duration: 14s; animation-delay: 3s; font-size: 2rem; }
    .icon-6 { left: 90%; animation-duration: 20s; animation-delay: 7s; font-size: 2.5rem; }

    /* 2. BAŞLIK ALANI (SİLİK/ŞEFFAF MOR KUTU) */
    .transparent-banner {
        background: rgba(74, 20, 140, 0.75); /* Mor renk, %75 opaklık */
        border-radius: 20px;
        padding: 50px 20px;
        text-align: center;
        color: white;
        margin-bottom: 30px;
        box-shadow: 0 4px 30px rgba(0, 0, 0, 0.1);
        backdrop-filter: blur(5px); /* Buzlu cam efekti */
        border: 1px solid rgba(255, 255, 255, 0.2);
    }
    
    .transparent-banner h1 {
        color: white;
        font-family: 'Helvetica', sans-serif;
        margin-bottom: 10px;
    }
    
    .transparent-banner p {
        font-size: 1.2rem;
        opacity: 0.9;
    }
    
    /* İkon ve Başlık hizalaması */
    .title-icon {
        font-size: 3rem;
        margin-bottom: 10px;
        display: block;
    }

</style>

<div class="psych-bg">
    <div class="psych-icon icon-1">🧠</div> <div class="psych-icon icon-2">🧩</div> <div class="psych-icon icon-3">⚕️</div> <div class="psych-icon icon-4">🧬</div> <div class="psych-icon icon-5">🧠</div>
    <div class="psych-icon icon-6">💭</div> </div>
""", unsafe_allow_html=True)

# --- UYGULAMA İÇERİĞİ ---

st.write("👋 Merhaba, menaf")

# Eski st.info veya renkli kutu yerine bu HTML bloğunu kullanın:
st.markdown("""
<div class="transparent-banner">
    <span class="title-icon">🏆</span>
    <h1>Psikiyatri Ligi</h1>
    <p>Bilgini test et, ismini zirveye yazdır!</p>
</div>
""", unsafe_allow_html=True)

# Butonlarınız (Mevcut kodunuzdaki gibi kalabilir)
col1, col2 = st.columns(2)
with col1:
    st.button("🚀 Sınava Başla", use_container_width=True, type="primary")
with col2:
    st.button("📊 Liderlik Tablosu", use_container_width=True)
