import streamlit as st
import pandas as pd
import json
import random
import time
import gspread
from oauth2client.service_account import ServiceAccountCredentials

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

# --- CSS VE ANİMASYON (40 İKONLU VERSİYON) ---
st.markdown(f"""
    <style>
    .stApp {{ background-color: {bg_color}; }}
    
    /* Arka plan konteyneri */
    .psych-bg {{
        position: fixed; top: 0; left: 0; width: 100%; height: 100%;
        z-index: 0; overflow: hidden; pointer-events: none;
    }}

    /* Ana İkon Stili (ÇOK NET - Opaklık %95) */
    .psych-icon {{
        position: absolute; top: -100px;
        opacity: 0.95; /* Neredeyse tam net, çok belirgin */
        animation: fall linear infinite;
        font-weight: bold;
    }}

    @keyframes fall {{
        0% {{ transform: translateY(-10vh) rotate(0deg); }}
        100% {{ transform: translateY(120vh) rotate(360deg); }}
    }}

    /* --- 40 ADET İKON VARYASYONU (Konum, Hız, Renk) --- */
    
    /* GRUP 1 (1-10) */
    .i1 {{ left: 2%;  animation-duration: 12s; font-size: 3rem; color: #3A0CA3; }} 
    .i2 {{ left: 8%;  animation-duration: 15s; animation-delay: 2s; font-size: 2.5rem; color: #F72585; }} 
    .i3 {{ left: 15%; animation-duration: 10s; animation-delay: 4s; font-size: 3rem; color: #4361ee; }} 
    .i4 {{ left: 22%; animation-duration: 18s; font-size: 2.2rem; color: #06d6a0; }} 
    .i5 {{ left: 29%; animation-duration: 14s; animation-delay: 1s; font-size: 3.5rem; color: #4cc9f0; }} 
    .i6 {{ left: 36%; animation-duration: 11s; animation-delay: 3s; font-size: 2.8rem; color: #f9c74f; }} 
    .i7 {{ left: 42%; animation-duration: 16s; animation-delay: 0.5s; font-size: 3rem; color: #7209B7; }}
    .i8 {{ left: 48%; animation-duration: 13s; animation-delay: 5s; font-size: 2rem; color: #F72585; }}
    .i9 {{ left: 55%; animation-duration: 19s; animation-delay: 2s; font-size: 3.2rem; color: #4361ee; }}
    .i10 {{ left: 62%; animation-duration: 10s; animation-delay: 1.5s; font-size: 2.5rem; color: #06d6a0; }}

    /* GRUP 2 (11-20) */
    .i11 {{ left: 68%; animation-duration: 17s; animation-delay: 6s; font-size: 3rem; color: #4cc9f0; }}
    .i12 {{ left: 75%; animation-duration: 12s; animation-delay: 3.5s; font-size: 2.2rem; color: #f9c74f; }}
    .i13 {{ left: 82%; animation-duration: 14s; animation-delay: 7s; font-size: 2.8rem; color: #3A0CA3; }}
    .i14 {{ left: 88%; animation-duration: 20s; animation-delay: 0s; font-size: 3.5rem; color: #F72585; }}
    .i15 {{ left: 95%; animation-duration: 11s; animation-delay: 4.5s; font-size: 2rem; color: #4361ee; }}
    .i16 {{ left: 5%;  animation-duration: 15s; animation-delay: 2.5s; font-size: 3rem; color: #06d6a0; }}
    .i17 {{ left: 12%; animation-duration: 9s;  animation-delay: 1s; font-size: 2.4rem; color: #4cc9f0; }}
    .i18 {{ left: 33%; animation-duration: 18s; animation-delay: 5.5s; font-size: 2.8rem; color: #3A0CA3; }}
    .i19 {{ left: 60%; animation-duration: 13s; animation-delay: 8s; font-size: 3.2rem; color: #F72585; }}
    .i20 {{ left: 80%; animation-duration: 16s; animation-delay: 3s; font-size: 2.5rem; color: #4361ee; }}

    /* GRUP 3 (21-30) - Yeni Eklenenler */
    .i21 {{ left: 1%;  animation-duration: 22s; animation-delay: 1s; font-size: 2rem; color: #F72585; }}
    .i22 {{ left: 10%; animation-duration: 13s; animation-delay: 5s; font-size: 2.8rem; color: #4361ee; }}
    .i23 {{ left: 18%; animation-duration: 19s; animation-delay: 2s; font-size: 3.5rem; color: #3A0CA3; }}
    .i24 {{ left: 25%; animation-duration: 14s; animation-delay: 9s; font-size: 2.2rem; color: #06d6a0; }}
    .i25 {{ left: 32%; animation-duration: 11s; animation-delay: 0s; font-size: 3rem; color: #f9c74f; }}
    .i26 {{ left: 45%; animation-duration: 17s; animation-delay: 4s; font-size: 2.5rem; color: #7209B7; }}
    .i27 {{ left: 52%; animation-duration: 12s; animation-delay: 7s; font-size: 3.2rem; color: #4cc9f0; }}
    .i28 {{ left: 65%; animation-duration: 21s; animation-delay: 3s; font-size: 2.1rem; color: #F72585; }}
    .i29 {{ left: 72%; animation-duration: 15s; animation-delay: 6s; font-size: 2.9rem; color: #3A0CA3; }}
    .i30 {{ left: 90%; animation-duration: 10s; animation-delay: 1s; font-size: 3.5rem; color: #06d6a0; }}

    /* GRUP 4 (31-40) - Yeni Eklenenler */
    .i31 {{ left: 4%;  animation-duration: 16s; animation-delay: 8s; font-size: 2.5rem; color: #4361ee; }}
    .i32 {{ left: 14%; animation-duration: 24s; animation-delay: 2s; font-size: 3rem; color: #f9c74f; }}
    .i33 {{ left: 28%; animation-duration: 13s; animation-delay: 5s; font-size: 2.2rem; color: #F72585; }}
    .i34 {{ left: 39%; animation-duration: 18s; animation-delay: 1s; font-size: 3.1rem; color: #3A0CA3; }}
    .i35 {{ left: 58%; animation-duration: 11s; animation-delay: 9s; font-size: 2.6rem; color: #4cc9f0; }}
    .i36 {{ left: 70%; animation-duration: 20s; animation-delay: 4s; font-size: 3.3rem; color: #7209B7; }}
    .i37 {{ left: 78%; animation-duration: 14s; animation-delay: 0s; font-size: 2rem; color: #06d6a0; }}
    .i38 {{ left: 86%; animation-duration: 17s; animation-delay: 6s; font-size: 2.8rem; color: #F72585; }}
    .i39 {{ left: 94%; animation-duration: 12s; animation-delay: 3s; font-size: 3.4rem; color: #4361ee; }}
    .i40 {{ left: 50%; animation-duration: 23s; animation-delay: 5s; font-size: 2.4rem; color: #f9c74f; }}
    
    
    /* --- DİĞER --- */
    .block-container {{ z-index: 1; position: relative; }}
    
    .glass-banner {{
        background: linear-gradient(135deg, rgba(58, 12, 163, 0.9), rgba(114, 9, 183, 0.9));
        backdrop-filter: blur(12px); padding: 15px 20px; border-radius: 25px;
        color: white; text-align: center; margin: 0 auto 30px auto; max-width: 80%;
        border: 1px solid rgba(255, 255, 255, 0.4); box-shadow: 0 10px 30px rgba(58, 12, 163, 0.4);
    }}
    .glass-banner h2 {{ color: white !important; margin: 0; font-size: 1.8rem; font-weight: 700; text-shadow: 0 2px 5px rgba(0,0,0,0.3); }}
    .glass-banner p {{ font-size: 1rem; opacity: 1; margin-top: 5px; margin-bottom: 0; text-shadow: 0 1px 3px rgba(0,0,0,0.3); }}
    .banner-icon {{ font-size: 2rem; margin-bottom: 5px; display: block; }}
    
    h1, h2, h3, h4 {{ color: {primary_color} !important; }}
    
    .question-card {{
        background-color: white; padding: 20px; border-radius: 15px;
        border-left: 5px solid {secondary_color}; box-shadow: 0 4px 10px rgba(0,0,0,0.1);
        margin-bottom: 20px; font-size: 18px; font-weight: 600; color: #333;
    }}
    
    div.stButton > button {{
        width: 100%; border-radius: 12px; border: 1px solid #ddd;
        background-color: white; color: #333; font-weight: 600; padding: 0.5rem 1rem;
    }}
    div.stButton > button:hover {{
        background-color: #F3E5F5; border-color: {primary_color}; color: {primary_color};
    }}
    div.stButton > button[kind="primary"] {{ background-color: {primary_color}; color: white; border: none; }}
    div.stButton > button[kind="primary"]:hover {{ background-color: #4800b0; color: white; }}
    
    .result-box {{
        background-color: white; padding: 30px; border-radius: 20px;
        text-align: center; box-shadow: 0 4px 15px rgba(0,0,0,0.15);
    }}
    
    #MainMenu {{visibility: hidden;}} footer {{visibility: hidden;}} header {{visibility: hidden;}}
    </style>

    <div class="psych-bg">
        <div class="psych-icon i1">🧠</div><div class="psych-icon i2">🧩</div><div class="psych-icon i3">⚕️</div><div class="psych-icon i4">🧬</div><div class="psych-icon i5">💭</div>
        <div class="psych-icon i6">🧠</div><div class="psych-icon i7">🧩</div><div class="psych-icon i8">⚕️</div><div class="psych-icon i9">🧬</div><div class="psych-icon i10">💭</div>
        <div class="psych-icon i11">🧠</div><div class="psych-icon i12">🧩</div><div class="psych-icon i13">⚕️</div><div class="psych-icon i14">🧬</div><div class="psych-icon i15">💭</div>
        <div class="psych-icon i16">🧠</div><div class="psych-icon i17">🧩</div><div class="psych-icon i18">⚕️</div><div class="psych-icon i19">🧬</div><div class="psych-icon i20">💭</div>
        <div class="psych-icon i21">💊</div><div class="psych-icon i22">🩺</div><div class="psych-icon i23">🧠</div><div class="psych-icon i24">🧩</div><div class="psych-icon i25">💡</div>
        <div class="psych-icon i26">🧬</div><div class="psych-icon i27">⚕️</div><div class="psych-icon i28">💭</div><div class="psych-icon i29">🧠</div><div class="psych-icon i30">🧩</div>
        <div class="psych-icon i31">🩺</div><div class="psych-icon i32">💊</div><div class="psych-icon i33">💡</div><div class="psych-icon i34">⚕️</div><div class="psych-icon i35">🧬</div>
        <div class="psych-icon i36">🧠</div><div class="psych-icon i37">💭</div><div class="psych-icon i38">🧩</div><div class="psych-icon i39">🧬</div><div class="psych-icon i40">⚕️</div>
    </div>
""", unsafe_allow_html=True)

# --- STATE YÖNETİMİ ---
query_params = st.query_params
url_user = query_params.get("kullanici", None)

if 'user_name' not in st.session_state: st.session_state.user_name = url_user if url_user else "Misafir"
if 'current_page' not in st.session_state: st.session_state.current_page = 'home'
if 'question_index' not in st.session_state: st.session_state.question_index = 0
if 'score' not in st.session_state: st.session_state.score = 0
if 'quiz_data' not in st.session_state: st.session_state.quiz_data = []
if 'answer_submitted' not in st.session_state: st.session_state.answer_submitted = False
if 'is_correct' not in st.session_state: st.session_state.is_correct = False

# --- YENİ VERİTABANI BAĞLANTISI (GSPREAD) ---

def get_google_sheet():
    try:
        scope = ['https://spreadsheets.google.com/feeds', 'https://www.googleapis.com/auth/drive']
        creds_dict = dict(st.secrets["connections"]["gsheets"])
        creds = ServiceAccountCredentials.from_json_keyfile_dict(creds_dict, scope)
        client = gspread.authorize(creds)
        sheet_url = st.secrets["connections"]["gsheets"]["spreadsheet"]
        # Eğer sekme isminiz farklıysa burayı düzeltmeyi unutmayın
        sheet = client.open_by_url(sheet_url).worksheet("Sayfa1") 
        return sheet
    except Exception as e:
        st.error(f"Veritabanı bağlantı hatası: {e}")
        return None

def fetch_leaderboard():
    sheet = get_google_sheet()
    if sheet:
        try:
            data = sheet.get_all_records()
            return pd.DataFrame(data)
        except Exception as e:
            return pd.DataFrame(columns=['Kullanıcı', 'Skor', 'Tarih'])
    return pd.DataFrame(columns=['Kullanıcı', 'Skor', 'Tarih'])

def save_score_to_db():
    sheet = get_google_sheet()
    if sheet:
        try:
            tarih = pd.to_datetime('today').strftime('%Y-%m-%d %H:%M')
            sheet.append_row([st.session_state.user_name, st.session_state.score, tarih])
            return True, "Başarılı"
        except Exception as e:
            return False, str(e)
    return False, "Bağlantı yok"

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

def quit_quiz():
    st.session_state.current_page = 'home'
    st.session_state.score = 0
    st.session_state.question_index = 0
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

    st.markdown(f"""
        <div class="glass-banner">
            <span class="banner-icon">🏆</span>
            <h2>Psikiyatri Ligi</h2>
            <p>Bilgini test et, zirveye çık!</p>
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
    
    c_exit, c_score = st.columns([1, 3])
    with c_exit:
        if st.button("❌ Çıkış", help="Sınavı iptal et (Puan kaydedilmez)", use_container_width=True):
            quit_quiz()
            
    total_q = len(st.session_state.quiz_data)
    idx = st.session_state.question_index
    q_data = st.session_state.quiz_data[idx]
    
    st.progress((idx + 1) / total_q)
    st.markdown(f"""
    <div style="display:flex; justify-content:space-between; margin-bottom:10px; font-size:0.9rem; color:#666;">
        <span>Soru <b>{idx + 1}</b> / {total_q}</span>
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
        if st.session_state.is_correct: st.success("✅ Doğru Cevap!")
        else:
            st.error("❌ Yanlış Cevap!")
            st.write(f"Doğru Cevap: **{q_data['dogru_cevap']}**")
        with st.expander("ℹ️ Açıklama", expanded=True):
            st.info(q_data.get('aciklama', 'Açıklama yok.'))
        btn_txt = "Sonraki Soru ➡️" if idx < total_q - 1 else "Sınavı Bitir ve Kaydet 🏁"
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
            st.warning("Google Sheet bağlantısını kontrol et.")

    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown(f"""
        <div class="result-box">
            <div style="font-size: 60px;">🎉</div>
            <h2 style="color: {primary_color};">Sınav Tamamlandı!</h2>
            <p style="font-size: 18px;">Tebrikler <b>{st.session_state.user_name}</b>,</p>
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
    with st.spinner('Veriler çekiliyor...'):
        df = fetch_leaderboard()
    
    if not df.empty and 'Skor' in df.columns:
        try:
            df['Skor'] = pd.to_numeric(df['Skor'], errors='coerce').fillna(0)
            df = df.sort_values(by=['Skor', 'Tarih'], ascending=[False, False]).reset_index(drop=True)
            df.index += 1
            st.dataframe(df, use_container_width=True)
        except Exception as e:
             st.error(f"Tablo format hatası: {e}")
             st.dataframe(df)
    else:
        st.info("Henüz veri yok veya bağlantı kurulamadı.")
    
    if st.button("⬅ Ana Menü", use_container_width=True):
        st.session_state.current_page = 'home'
        st.rerun()

if st.session_state.current_page == 'home': home_page()
elif st.session_state.current_page == 'quiz': quiz_page()
elif st.session_state.current_page == 'leaderboard': leaderboard_page()
elif st.session_state.current_page == 'result': result_page()
