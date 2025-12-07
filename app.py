import streamlit as st
import pandas as pd
import json
import random
import time
from streamlit_gsheets import GSheetsConnection

# --- SAYFA VE STİL AYARLARI ---
st.set_page_config(
    page_title="Psikiyatri Quiz Ligi",
    page_icon="🧠",
    layout="centered",
    initial_sidebar_state="collapsed"
)

# Renk Paleti
primary_color = "#3A0CA3"
secondary_color = "#F72585"
bg_color = "#F8F9FA"

# --- GÜÇLENDİRİLMİŞ CSS VE ANİMASYON ---
st.markdown(f"""
    <style>
    /* Arka planı zorla uygula */
    .stApp {{
        background-color: {bg_color};
    }}
    
    /* --- 1. ARKA PLAN ANİMASYONU (DÜŞEN SEMBOLLER) --- */
    .psych-bg {{
        position: fixed;
        top: 0;
        left: 0;
        width: 100%;
        height: 100%;
        z-index: 0; /* İçeriğin arkasında, arka planın önünde */
        overflow: hidden;
        pointer-events: none; /* Tıklamayı engellemez */
    }}

    .psych-icon {{
        position: absolute;
        top: -50px;
        color: {primary_color};
        font-size: 2rem;
        opacity: 0.08; /* Çok silik, göz yormaz */
        animation: fall linear infinite;
    }}

    @keyframes fall {{
        0% {{ transform: translateY(-10vh) rotate(0deg); }}
        100% {{ transform: translateY(110vh) rotate(360deg); }}
    }}

    /* Sembollerin rastgele düşüş varyasyonları */
    .i1 {{ left: 10%; animation-duration: 12s; animation-delay: 0s; font-size: 3rem; }}
    .i2 {{ left: 25%; animation-duration: 15s; animation-delay: 2s; font-size: 2rem; }}
    .i3 {{ left: 45%; animation-duration: 10s; animation-delay: 5s; font-size: 2.5rem; }}
    .i4 {{ left: 70%; animation-duration: 18s; animation-delay: 1s; font-size: 3rem; }}
    .i5 {{ left: 85%; animation-duration: 14s; animation-delay: 3s; font-size: 2rem; }}
    
    /* İçeriği öne çıkarmak için z-index ayarı */
    .block-container {{
        z-index: 1;
        position: relative;
    }}
    
    /* --- 2. GLASSMORPHISM BANNER (SİLİK BAŞLIK) --- */
    .glass-banner {{
        background: rgba(58, 12, 163, 0.75); /* Mor renk ama %75 opak */
        backdrop-filter: blur(8px); /* Arkadaki nesneleri flulaştırır */
        -webkit-backdrop-filter: blur(8px);
        padding: 30px 20px;
        border-radius: 20px;
        color: white;
        text-align: center;
        margin-bottom: 30px;
        border: 1px solid rgba(255, 255, 255, 0.2);
        box-shadow: 0 8px 32px 0 rgba(31, 38, 135, 0.2);
    }}
    
    .glass-banner h2 {{
        color: white !important;
        margin: 0;
        font-size: 2.5rem;
        text-shadow: 0 2px 4px rgba(0,0,0,0.2);
    }}
    
    .glass-banner p {{
        font-size: 1.1rem;
        opacity: 0.9;
        margin-top: 10px;
    }}

    /* --- DİĞER STİLLER --- */
    
    h1, h2, h3, h4 {{ color: {primary_color} !important; }}
    
    /* Soru Kartı */
    .question-card {{
        background-color: white;
        padding: 20px;
        border-radius: 15px;
        border-left: 5px solid {secondary_color};
        box-shadow: 0 2px 5px rgba(0,0,0,0.05);
        margin-bottom: 20px;
        font-size: 18px;
        font-weight: 600;
        color: #333;
    }}
    
    /* Butonlar */
    div.stButton > button {{
        width: 100%;
        border-radius: 10px;
        border: 1px solid #ddd;
        background-color: white;
        color: #333;
        font-weight: 500;
        transition: all 0.3s;
    }}
    div.stButton > button:hover {{
        background-color: #F3E5F5;
        border-color: {primary_color};
        color: {primary_color};
    }}
    
    /* Primary Butonlar */
    div.stButton > button[kind="primary"] {{
        background-color: {primary_color};
        color: white;
        border: none;
    }}
    div.stButton > button[kind="primary"]:hover {{
        background-color: #4800b0;
        color: white;
    }}

    /* Sonuç Kartı */
    .result-box {{
        background-color: white;
        padding: 30px;
        border-radius: 20px;
        text-align: center;
        box-shadow: 0 4px 15px rgba(0,0,0,0.1);
    }}
    
    #MainMenu {{visibility: hidden;}}
    footer {{visibility: hidden;}}
    header {{visibility: hidden;}}
    </style>

    <div class="psych-bg">
        <div class="psych-icon i1">🧠</div> <div class="psych-icon i2">🧩</div> <div class="psych-icon i3">⚕️</div> <div class="psych-icon i4">🧬</div> <div class="psych-icon i5">💭</div> </div>
""", unsafe_allow_html=True)

# --- STATE YÖNETİMİ ---
query_params = st.query_params
url_user = query_params.get("kullanici", None)

if 'user_name' not in st.session_state:
    st.session_state.user_name = url_user if url_user else "Misafir"

if 'current_page' not in st.session_state:
    st.session_state.current_page = 'home'
if 'question_index' not in st.session_state:
    st.session_state.question_index = 0
if 'score' not in st.session_state:
    st.session_state.score = 0
if 'quiz_data' not in st.session_state:
    st.session_state.quiz_data = []
if 'answer_submitted' not in st.session_state:
    st.session_state.answer_submitted = False
if 'is_correct' not in st.session_state:
    st.session_state.is_correct = False

# --- VERİTABANI FONKSİYONLARI ---

def get_connection():
    return st.connection("gsheets", type=GSheetsConnection)

def fetch_leaderboard():
    try:
        conn = get_connection()
        df = conn.read(worksheet="Sayfa1", ttl=0)
        df.columns = df.columns.str.strip()
        return df
    except Exception as e:
        print(f"Veri çekme hatası: {e}")
        return pd.DataFrame(columns=['Kullanıcı', 'Skor', 'Tarih'])

def save_score_to_db():
    try:
        conn = get_connection()
        existing_data = conn.read(worksheet="Sayfa1", ttl=0)
        
        new_entry = pd.DataFrame([{
            'Kullanıcı': st.session_state.user_name,
            'Skor': st.session_state.score,
            'Tarih': pd.to_datetime('today').strftime('%Y-%m-%d %H:%M')
        }])
        
        updated_data = pd.concat([existing_data, new_entry], ignore_index=True)
        conn.update(worksheet="Sayfa1", data=updated_data)
        return True, "Başarılı"
    except Exception as e:
        return False, str(e)

# --- QUIZ FONKSİYONLARI ---

def load_questions():
    try:
        with open('sorular.json', 'r', encoding='utf-8') as f:
            all_questions = json.load(f)
        question_count = min(10, len(all_questions))
        st.session_state.quiz_data = random.sample(all_questions, question_count)
        return True
    except:
        st.error("⚠️ sorular.json bulunamadı.")
        return False

def start_quiz():
    st.session_state.question_index = 0
    st.session_state.score = 0
    st.session_state.answer_submitted = False
    
    if st.session_state.user_name != "Misafir":
        st.query_params["kullanici"] = st.session_state.user_name
        
    if load_questions():
        st.session_state.current_page = 'quiz'
        st.rerun()

def submit_answer(option):
    current_q = st.session_state.quiz_data[st.session_state.question_index]
    st.session_state.answer_submitted = True
    if option == current_q['dogru_cevap']:
        st.session_state.score += 10
        st.session_state.is_correct = True
    else:
        st.session_state.is_correct = False

def next_question():
    st.session_state.answer_submitted = False
    if st.session_state.question_index < len(st.session_state.quiz_data) - 1:
        st.session_state.question_index += 1
        st.rerun()
    else:
        st.session_state.current_page = 'result'
        st.rerun()

# --- SAYFALAR ---

def home_page():
    st.write(f"👋 **Merhaba, {st.session_state.user_name}**")
    
    if st.session_state.user_name == "Misafir":
        name = st.text_input("Yarışmak için adını gir:", placeholder="Adınız...")
        if name:
            st.session_state.user_name = name
            st.query_params["kullanici"] = name
            st.rerun()

    # YENİ GLASS BANNER YAPISI
    st.markdown(f"""
        <div class="glass-banner">
            <div style="font-size: 3rem; margin-bottom: 10px;">🏆</div>
            <h2>Psikiyatri Ligi</h2>
            <p>Bilgini test et, ismini zirveye yazdır!</p>
        </div>
    """, unsafe_allow_html=True)

    c1, c2 = st.columns(2)
    with c1:
        if st.button("🚀 Sınava Başla", type="primary", use_container_width=True):
            if st.session_state.user_name == "Misafir":
                st.warning("Lütfen önce isminizi girin.")
            else:
                start_quiz()
    with c2:
        if st.button("📊 Liderlik Tablosu", use_container_width=True):
            st.session_state.current_page = 'leaderboard'
            st.rerun()

def quiz_page():
    if not st.session_state.quiz_data:
        st.session_state.current_page = 'home'
        st.rerun()
        
    total_q = len(st.session_state.quiz_data)
    idx = st.session_state.question_index
    q_data = st.session_state.quiz_data[idx]
    
    st.progress((idx + 1) / total_q)
    
    st.markdown(f"""
    <div style="display:flex; justify-content:space-between; margin-bottom:10px;">
        <span>Soru {idx + 1} / {total_q}</span>
        <span style="color:{primary_color}; font-weight:bold;">💎 Puan: {st.session_state.score}</span>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown(f'<div class="question-card">{q_data["soru"]}</div>', unsafe_allow_html=True)
    
    if not st.session_state.answer_submitted:
        for i, opt in enumerate(q_data['secenekler']):
            if st.button(opt, key=f"q{idx}_o{i}", use_container_width=True):
                submit_answer(opt)
                st.rerun()
    else:
        if st.session_state.is_correct:
            st.success("✅ Doğru Cevap!")
        else:
            st.error("❌ Yanlış Cevap!")
            st.write(f"Doğru Cevap: **{q_data['dogru_cevap']}**")
        
        with st.expander("ℹ️ Açıklama", expanded=True):
            st.info(q_data.get('aciklama', 'Açıklama yok.'))
            
        btn_txt = "Sonraki Soru ➡️" if idx < total_q - 1 else "Sınavı Bitir 🏁"
        if st.button(btn_txt, type="primary", use_container_width=True):
            next_question()

def result_page():
    if 'score_saved' not in st.session_state:
        status, msg = save_score_to_db()
        if status:
            st.toast("Skor başarıyla kaydedildi!", icon="✅")
            st.session_state.score_saved = True
        else:
            st.error(f"Skor kaydedilemedi! Hata: {msg}")
            st.warning("Lütfen Google Sheet 'client_email' adresine Editör yetkisi verdiğinizden emin olun.")

    st.markdown("<br>", unsafe_allow_html=True)
    total_q = len(st.session_state.quiz_data)
    
    st.markdown(f"""
        <div class="result-box">
            <div style="font-size: 60px;">🎉</div>
            <h2 style="color: {primary_color};">Sınav Bitti!</h2>
            <p style="font-size: 18px;">Sayın <b>{st.session_state.user_name}</b>,</p>
            <hr>
            <div style="font-size: 16px; color: #555;">Toplam Skorun</div>
            <h1 style="color: {secondary_color}; font-size: 50px; margin: 0;">
                {st.session_state.score}
            </h1>
        </div>
    """, unsafe_allow_html=True)
    
    st.write("")
    c1, c2 = st.columns(2)
    with c1:
        if st.button("🏠 Ana Sayfa", use_container_width=True):
            if 'score_saved' in st.session_state: del st.session_state.score_saved
            st.session_state.current_page = 'home'
            st.rerun()
    with c2:
        if st.button("🏆 Liderlik Tablosu", type="primary", use_container_width=True):
            if 'score_saved' in st.session_state: del st.session_state.score_saved
            st.session_state.current_page = 'leaderboard'
            st.rerun()

def leaderboard_page():
    st.markdown(f"<h3 style='text-align:center; color:{primary_color}'>🏆 Canlı Liderlik Tablosu</h3>", unsafe_allow_html=True)
    
    with st.spinner('Veriler Google Sheets\'ten çekiliyor...'):
        df = fetch_leaderboard()
    
    if not df.empty and 'Skor' in df.columns:
        try:
            df['Skor'] = pd.to_numeric(df['Skor'], errors='coerce').fillna(0)
            df = df.sort_values(by=['Skor', 'Tarih'], ascending=[False, False]).reset_index(drop=True)
            df.index += 1
            
            st.dataframe(
                df, 
                use_container_width=True,
                column_config={
                    "Skor": st.column_config.ProgressColumn("Skor", format="%d", min_value=0, max_value=100),
                    "Tarih": st.column_config.TextColumn("Tarih"),
                    "Kullanıcı": st.column_config.TextColumn("Yarışmacı")
                }
            )
        except Exception as e:
             st.error(f"Tablo format hatası: {e}")
             st.dataframe(df)
    else:
        st.info("Henüz kimse yarışmadı veya veritabanı bağlantısı kurulamadı.")
        st.write("Google Sheets ayarlarını ve sütun isimlerinin (Kullanıcı, Skor, Tarih) doğru olduğundan emin olun.")

    if st.button("⬅ Ana Menü", use_container_width=True):
        st.session_state.current_page = 'home'
        st.rerun()

# --- YÖNLENDİRİCİ ---
if st.session_state.current_page == 'home': home_page()
elif st.session_state.current_page == 'quiz': quiz_page()
elif st.session_state.current_page == 'leaderboard': leaderboard_page()
elif st.session_state.current_page == 'result': result_page()
