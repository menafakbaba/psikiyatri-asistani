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

# --- RENK PALETİ (DARK MODE) ---
# Arka plan için koyu mor, vurgular için neon renkler
dark_bg = "#1a0b2e"  # Çok koyu mor (Arka plan)
card_bg = "#2d1b4e"  # Kartlar için biraz daha açık mor
text_color = "#ffffff" # Beyaz yazılar
primary_accent = "#7209B7" # Butonlar ve vurgular
secondary_accent = "#F72585" # İkinci vurgu (Pembe)

# --- CSS VE ANİMASYON ---
st.markdown(f"""
    <style>
    /* 1. GENEL SAYFA YAPISI */
    .stApp {{
        background-color: {dark_bg};
    }}
    
    /* Yazı renklerini beyaza çekiyoruz (Dark mode uyumu) */
    h1, h2, h3, h4, h5, h6, p, span, div {{
        color: {text_color} !important;
        font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
    }}

    /* 2. ARKA PLAN ANİMASYONU (EN ARKADA KALACAK) */
    .psych-bg {{
        position: fixed;
        top: 0;
        left: 0;
        width: 100%;
        height: 100%;
        z-index: -1; /* EKSİ BİR: Bu sayede yazıların hep arkasında kalır */
        overflow: hidden;
        pointer-events: none;
    }}

    /* İkon Stili (Neon Efektli) */
    .psych-icon {{
        position: absolute;
        top: -100px;
        opacity: 0.3; /* Karanlık modda çok parlamaması için ayarlandı */
        animation: fall linear infinite;
        font-weight: bold;
        text-shadow: 0 0 10px rgba(255, 255, 255, 0.3); /* Hafif neon parlaması */
    }}

    @keyframes fall {{
        0% {{ transform: translateY(-10vh) rotate(0deg); }}
        100% {{ transform: translateY(120vh) rotate(360deg); }}
    }}

    /* 40 İKONLU ANİMASYON GRUPLARI */
    /* Grup 1 */
    .i1 {{ left: 2%;  animation-duration: 12s; font-size: 3rem; color: #7209B7; }} 
    .i2 {{ left: 8%;  animation-duration: 15s; animation-delay: 2s; font-size: 2.5rem; color: #F72585; }} 
    .i3 {{ left: 15%; animation-duration: 10s; animation-delay: 4s; font-size: 3rem; color: #4361ee; }} 
    .i4 {{ left: 22%; animation-duration: 18s; font-size: 2.2rem; color: #4cc9f0; }} 
    .i5 {{ left: 29%; animation-duration: 14s; animation-delay: 1s; font-size: 3.5rem; color: #F72585; }} 
    /* Grup 2 */
    .i6 {{ left: 36%; animation-duration: 11s; animation-delay: 3s; font-size: 2.8rem; color: #f9c74f; }} 
    .i7 {{ left: 42%; animation-duration: 16s; animation-delay: 0.5s; font-size: 3rem; color: #7209B7; }}
    .i8 {{ left: 48%; animation-duration: 13s; animation-delay: 5s; font-size: 2rem; color: #4361ee; }}
    .i9 {{ left: 55%; animation-duration: 19s; animation-delay: 2s; font-size: 3.2rem; color: #4cc9f0; }}
    .i10 {{ left: 62%; animation-duration: 10s; animation-delay: 1.5s; font-size: 2.5rem; color: #F72585; }}
    /* Grup 3 (Ekstra) */
    .i11 {{ left: 70%; animation-duration: 14s; font-size: 3rem; color: #7209B7; }}
    .i12 {{ left: 78%; animation-duration: 12s; animation-delay: 2s; font-size: 2.5rem; color: #4361ee; }}
    .i13 {{ left: 85%; animation-duration: 16s; font-size: 3.2rem; color: #f9c74f; }}
    .i14 {{ left: 92%; animation-duration: 9s; animation-delay: 4s; font-size: 2.8rem; color: #F72585; }}
    .i15 {{ left: 5%; animation-duration: 20s; animation-delay: 5s; font-size: 2.2rem; color: #4cc9f0; }}
    
    /* 3. KART VE BANNER TASARIMLARI */
    
    /* Ana Banner (Koyu Glassmorphism) */
    .glass-banner {{
        background: rgba(114, 9, 183, 0.25); /* Şeffaf mor */
        backdrop-filter: blur(12px);
        -webkit-backdrop-filter: blur(12px);
        padding: 20px;
        border-radius: 20px;
        text-align: center;
        border: 1px solid rgba(255, 255, 255, 0.1);
        box-shadow: 0 0 20px rgba(114, 9, 183, 0.3);
        margin-bottom: 30px;
    }}
    .glass-banner h2 {{ font-weight: 800; letter-spacing: 1px; margin-bottom: 5px; }}
    
    /* Soru Kartı (Okunabilirlik için koyu arka plan + açık yazı) */
    .question-card {{
        background-color: {card_bg};
        padding: 25px;
        border-radius: 15px;
        border-left: 6px solid {secondary_accent};
        box-shadow: 0 4px 15px rgba(0,0,0,0.3);
        margin-bottom: 20px;
        font-size: 1.1rem;
        line-height: 1.6;
    }}
    
    /* Buton Özelleştirmeleri */
    div.stButton > button {{
        background-color: transparent;
        color: white;
        border: 1px solid rgba(255,255,255,0.3);
        border-radius: 10px;
        transition: all 0.3s ease;
    }}
    div.stButton > button:hover {{
        background-color: {primary_accent};
        border-color: {primary_accent};
        transform: scale(1.02);
        box-shadow: 0 0 15px rgba(114, 9, 183, 0.5);
    }}
    
    /* Primary Buton (Sınava Başla vb.) */
    div.stButton > button[kind="primary"] {{
        background: linear-gradient(90deg, {primary_accent}, {secondary_accent});
        border: none;
        font-weight: bold;
    }}
    div.stButton > button[kind="primary"]:hover {{
        opacity: 0.9;
    }}
    
    /* Sonuç Kutusu */
    .result-box {{
        background-color: {card_bg};
        padding: 30px;
        border-radius: 20px;
        text-align: center;
        border: 1px solid rgba(255,255,255,0.1);
        box-shadow: 0 0 30px rgba(247, 37, 133, 0.2);
    }}

    /* Streamlit varsayılanlarını gizle */
    #MainMenu {{visibility: hidden;}} footer {{visibility: hidden;}} header {{visibility: hidden;}}
    </style>

    <div class="psych-bg">
        <div class="psych-icon i1">🧠</div><div class="psych-icon i2">🧩</div><div class="psych-icon i3">⚕️</div>
        <div class="psych-icon i4">🧬</div><div class="psych-icon i5">💭</div><div class="psych-icon i6">🧠</div>
        <div class="psych-icon i7">🧩</div><div class="psych-icon i8">⚕️</div><div class="psych-icon i9">🧬</div>
        <div class="psych-icon i10">💭</div><div class="psych-icon i11">💊</div><div class="psych-icon i12">🩺</div>
        <div class="psych-icon i13">💡</div><div class="psych-icon i14">⚛️</div><div class="psych-icon i15">🧠</div>
        <div class="psych-icon i1" style="animation-delay: 5s; left: 30%;">🧠</div>
        <div class="psych-icon i3" style="animation-delay: 7s; left: 60%;">⚕️</div>
        <div class="psych-icon i5" style="animation-delay: 3s; left: 90%;">💭</div>
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

# --- GÜÇLENDİRİLMİŞ VERİTABANI BAĞLANTISI ---

def get_google_sheet():
    try:
        scope = ['https://spreadsheets.google.com/feeds', 'https://www.googleapis.com/auth/drive']
        creds_dict = dict(st.secrets["connections"]["gsheets"])
        creds = ServiceAccountCredentials.from_json_keyfile_dict(creds_dict, scope)
        client = gspread.authorize(creds)
        sheet_url = st.secrets["connections"]["gsheets"]["spreadsheet"]
        # "Sayfa1" veya "Liderlik Tablosu" - Kendi sekme adınızı buraya yazın
        sheet = client.open_by_url(sheet_url).worksheet("Sayfa1") 
        return sheet
    except Exception as e:
        st.error(f"Bağlantı Hatası: {e}")
        return None

def fetch_leaderboard():
    """Hatasız veri çekme fonksiyonu"""
    sheet = get_google_sheet()
    if sheet:
        try:
            # Tüm verileri ham olarak al (Daha güvenli)
            all_values = sheet.get_all_values()
            
            if len(all_values) < 2: # Sadece başlık varsa veya boşsa
                return pd.DataFrame(columns=['Kullanıcı', 'Skor', 'Tarih'])
            
            headers = all_values[0]
            data = all_values[1:]
            
            df = pd.DataFrame(data, columns=headers)
            # Başlıklardaki olası boşlukları temizle
            df.columns = df.columns.str.strip()
            return df
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

# --- QUIZ MANTIĞI ---

def load_questions():
    try:
        with open('sorular.json', 'r', encoding='utf-8') as f:
            all_questions = json.load(f)
        question_count = min(10, len(all_questions))
        st.session_state.quiz_data = random.sample(all_questions, question_count)
        return True
    except:
        st.error("⚠️ sorular.json dosyası bulunamadı! Lütfen GitHub'a yükleyin.")
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

# --- SAYFA TASARIMLARI ---

def home_page():
    st.markdown(f"<h3 style='text-align:center;'>👋 Merhaba, <span style='color:{secondary_accent}'>{st.session_state.user_name}</span></h3>", unsafe_allow_html=True)
    
    if st.session_state.user_name == "Misafir":
        name = st.text_input("Yarışmak için adını gir:", placeholder="Adınız...")
        if name:
            st.session_state.user_name = name
            st.query_params["kullanici"] = name
            st.rerun()

    st.markdown(f"""
        <div class="glass-banner">
            <div style="font-size: 3rem; margin-bottom: 10px;">🏆</div>
            <h2>Psikiyatri Ligi</h2>
            <p style="color: #ddd;">Bilgini test et, ismini zirveye yazdır!</p>
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
    
    # Çıkış Butonu
    c_exit, c_score = st.columns([1, 4])
    with c_exit:
        if st.button("❌ Çıkış", help="Sınavı iptal et", use_container_width=True):
            quit_quiz()
    
    total_q = len(st.session_state.quiz_data)
    idx = st.session_state.question_index
    q_data = st.session_state.quiz_data[idx]
    
    # Progress Bar Rengini Değiştirmek Zor Olduğu İçin Standart Kalır
    st.progress((idx + 1) / total_q)
    
    st.markdown(f"""
    <div style="display:flex; justify-content:space-between; margin-bottom:10px; font-size:0.9rem; color:#bbb;">
        <span>Soru <b>{idx + 1}</b> / {total_q}</span>
        <span style="color:{secondary_accent}; font-weight:bold;">💎 Puan: {st.session_state.score}</span>
    </div>
    """, unsafe_allow_html=True)
    
    # Koyu Temalı Soru Kartı
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
            st.markdown(f"<div style='color:{text_color}; background-color:{card_bg}; padding:10px; border-radius:10px;'>Doğru Cevap: <b>{q_data['dogru_cevap']}</b></div>", unsafe_allow_html=True)
        
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
            st.error(f"Kayıt Hatası: {msg}")

    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown(f"""
        <div class="result-box">
            <div style="font-size: 60px;">🎉</div>
            <h2 style="color: {secondary_accent};">Sınav Tamamlandı!</h2>
            <p style="font-size: 18px; color: #ddd;">Tebrikler <b>{st.session_state.user_name}</b>,</p>
            <hr style="border-color: rgba(255,255,255,0.1);">
            <div style="font-size: 16px; color: #aaa;">Toplam Skorun</div>
            <h1 style="color: {secondary_accent}; font-size: 50px; margin: 0;">
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
    st.markdown(f"<h3 style='text-align:center; color:{primary_accent}'>🏆 Canlı Liderlik Tablosu</h3>", unsafe_allow_html=True)
    
    with st.spinner('Veriler çekiliyor...'):
        df = fetch_leaderboard()
    
    if not df.empty:
        try:
            # Skor sütununu bul (Büyük/küçük harf duyarsız)
            skor_col = next((col for col in df.columns if 'skor' in col.lower()), None)
            
            if skor_col:
                df[skor_col] = pd.to_numeric(df[skor_col], errors='coerce').fillna(0)
                df = df.sort_values(by=[skor_col], ascending=False).reset_index(drop=True)
                df.index += 1
                st.dataframe(df, use_container_width=True)
            else:
                st.dataframe(df)
        except Exception as e:
             st.dataframe(df)
    else:
        st.info("Henüz veri yok.")
    
    if st.button("⬅ Ana Menü", use_container_width=True):
        st.session_state.current_page = 'home'
        st.rerun()

# --- YÖNLENDİRİCİ ---
if st.session_state.current_page == 'home': home_page()
elif st.session_state.current_page == 'quiz': quiz_page()
elif st.session_state.current_page == 'leaderboard': leaderboard_page()
elif st.session_state.current_page == 'result': result_page()
