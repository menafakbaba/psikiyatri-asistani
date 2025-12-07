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

# --- RENK PALETİ ---
primary_color = "#3A0CA3"   # Ana Mor
secondary_color = "#F72585" # Pembe
bg_color = "#F8F9FA"        # Beyaz/Gri Zemin
text_color = "#212529"      # Siyah Yazı

# --- TEK PARÇA CSS VE ANİMASYON ---
st.markdown(f"""
    <style>
    /* 1. GENEL AYARLAR */
    .stApp {{
        background-color: {bg_color};
        font-family: 'Helvetica Neue', Helvetica, Arial, sans-serif;
    }}
    
    h1, h2, h3, h4 {{ color: {primary_color} !important; font-weight: 700; }}
    p, span, div {{ color: {text_color}; }}

    /* 2. ARKA PLAN ANİMASYONU (SABİT) */
    .psych-bg {{
        position: fixed;
        top: 0;
        left: 0;
        width: 100%;
        height: 100%;
        z-index: 0;
        overflow: hidden;
        pointer-events: none;
    }}
    
    .block-container {{
        position: relative;
        z-index: 1;
    }}

    .psych-icon {{
        position: absolute;
        top: -100px;
        opacity: 0.5;
        animation: fall linear infinite;
        font-weight: bold;
    }}

    @keyframes fall {{
        0% {{ transform: translateY(-10vh) rotate(0deg); }}
        100% {{ transform: translateY(120vh) rotate(360deg); }}
    }}
    
    /* 60 İKON POZİSYONLARI */
    .i1 {{ left: 2%; animation-duration: 12s; font-size: 3rem; color: #3A0CA3; }}
    .i2 {{ left: 5%; animation-duration: 15s; font-size: 2rem; color: #F72585; }}
    .i3 {{ left: 10%; animation-duration: 10s; font-size: 3.5rem; color: #4361ee; }}
    .i4 {{ left: 15%; animation-duration: 18s; font-size: 2.2rem; color: #06d6a0; }}
    .i5 {{ left: 20%; animation-duration: 14s; font-size: 3rem; color: #3A0CA3; }}
    .i6 {{ left: 25%; animation-duration: 11s; font-size: 2.8rem; color: #f9c74f; }}
    .i7 {{ left: 30%; animation-duration: 16s; font-size: 3rem; color: #F72585; }}
    .i8 {{ left: 35%; animation-duration: 13s; font-size: 2rem; color: #4361ee; }}
    .i9 {{ left: 40%; animation-duration: 19s; font-size: 3.2rem; color: #06d6a0; }}
    .i10 {{ left: 45%; animation-duration: 10s; font-size: 2.5rem; color: #3A0CA3; }}
    .i11 {{ left: 50%; animation-duration: 17s; font-size: 3rem; color: #F72585; }}
    .i12 {{ left: 55%; animation-duration: 12s; font-size: 2.2rem; color: #f9c74f; }}
    .i13 {{ left: 60%; animation-duration: 14s; font-size: 2.8rem; color: #4361ee; }}
    .i14 {{ left: 65%; animation-duration: 20s; font-size: 3.5rem; color: #3A0CA3; }}
    .i15 {{ left: 70%; animation-duration: 11s; font-size: 2rem; color: #F72585; }}
    .i16 {{ left: 75%; animation-duration: 15s; font-size: 3rem; color: #06d6a0; }}
    .i17 {{ left: 80%; animation-duration: 9s; font-size: 2.4rem; color: #4361ee; }}
    .i18 {{ left: 85%; animation-duration: 18s; font-size: 2.8rem; color: #3A0CA3; }}
    .i19 {{ left: 90%; animation-duration: 13s; font-size: 3.2rem; color: #F72585; }}
    .i20 {{ left: 95%; animation-duration: 16s; font-size: 2.5rem; color: #f9c74f; }}
    /* Ekstra İkonlar */
    .i21 {{ left: 3%; animation-duration: 22s; font-size: 2rem; color: #3A0CA3; animation-delay: 5s; }}
    .i22 {{ left: 12%; animation-duration: 13s; font-size: 3rem; color: #F72585; animation-delay: 2s; }}
    .i23 {{ left: 23%; animation-duration: 19s; font-size: 2.5rem; color: #4361ee; animation-delay: 7s; }}
    .i24 {{ left: 33%; animation-duration: 15s; font-size: 3.2rem; color: #06d6a0; animation-delay: 1s; }}
    .i25 {{ left: 43%; animation-duration: 11s; font-size: 2.8rem; color: #3A0CA3; animation-delay: 4s; }}
    .i26 {{ left: 53%; animation-duration: 18s; font-size: 3rem; color: #f9c74f; animation-delay: 6s; }}
    .i27 {{ left: 63%; animation-duration: 14s; font-size: 2.2rem; color: #F72585; animation-delay: 3s; }}
    .i28 {{ left: 73%; animation-duration: 21s; font-size: 3.5rem; color: #4361ee; animation-delay: 8s; }}
    .i29 {{ left: 83%; animation-duration: 10s; font-size: 2.5rem; color: #06d6a0; animation-delay: 2s; }}
    .i30 {{ left: 93%; animation-duration: 16s; font-size: 3rem; color: #3A0CA3; animation-delay: 5s; }}


    /* 3. BUTON DÜZELTMESİ (KESİN ÇÖZÜM) */
    /* Primary butonun (Sınava Başla) hem kendisini hem içindeki yazıyı zorla beyaz/mor yapıyoruz */
    div.stButton > button[kind="primary"] {{
        background-color: {primary_color} !important;
        color: white !important;
        border: none !important;
        box-shadow: 0 4px 6px rgba(0,0,0,0.2) !important;
    }}
    
    /* İçindeki yazı (p etiketi) gri olmasın diye */
    div.stButton > button[kind="primary"] p {{
        color: white !important;
    }}
    
    div.stButton > button[kind="primary"]:hover {{
        background-color: #4800b0 !important;
        color: white !important;
    }}
    
    /* Normal Butonlar (Liderlik Tablosu vb.) */
    div.stButton > button {{
        background-color: white;
        color: {text_color};
        border: 1px solid #e0e0e0;
        border-radius: 10px;
    }}

    /* 4. MERHABA BARI (ORTALANDI) */
    .greeting-card {{
        background-color: white;
        max-width: 500px;
        margin: 0 auto 10px auto;
        padding: 10px 20px;
        border-radius: 12px;
        box-shadow: 0 2px 10px rgba(0,0,0,0.05);
        border-left: 5px solid {secondary_color};
        
        /* İçerik Ortalama Kodları */
        display: flex;
        flex-direction: row;
        justify-content: center; /* Yatay Ortala */
        align-items: center;     /* Dikey Ortala */
        text-align: center;
    }}

    /* 5. KOMPAKT BANNER (ORTALANDI) */
    .compact-banner {{
        background: linear-gradient(135deg, {primary_color} 0%, #7209B7 100%);
        padding: 20px;
        border-radius: 20px;
        color: white !important;
        max-width: 500px;
        margin: 0 auto 30px auto;
        box-shadow: 0 10px 20px rgba(58, 12, 163, 0.2);
        
        /* İçerik Ortalama Kodları */
        display: flex;
        flex-direction: column;
        justify-content: center;
        align-items: center;
        text-align: center;
    }}
    .compact-banner h2 {{ color: white !important; margin: 5px 0; font-size: 1.8rem; }}
    .compact-banner p {{ color: rgba(255,255,255,0.9) !important; font-size: 0.9rem; margin: 0; }}

    /* 6. LİDERLİK TABLOSU */
    .leaderboard-container {{
        background-color: white;
        padding: 20px; border-radius: 15px;
        box-shadow: 0 4px 15px rgba(0,0,0,0.08);
        border: 1px solid #eee;
    }}

    #MainMenu {{visibility: hidden;}} footer {{visibility: hidden;}} header {{visibility: hidden;}}
    </style>

    <div class="psych-bg">
        <div class="psych-icon i1">🧠</div><div class="psych-icon i2">🧩</div><div class="psych-icon i3">⚕️</div>
        <div class="psych-icon i4">🧬</div><div class="psych-icon i5">💭</div><div class="psych-icon i6">🧠</div>
        <div class="psych-icon i7">🧩</div><div class="psych-icon i8">⚕️</div><div class="psych-icon i9">🧬</div>
        <div class="psych-icon i10">💭</div><div class="psych-icon i11">💊</div><div class="psych-icon i12">🩺</div>
        <div class="psych-icon i13">💡</div><div class="psych-icon i14">⚛️</div><div class="psych-icon i15">🧠</div>
        <div class="psych-icon i16">🧠</div><div class="psych-icon i17">🧩</div><div class="psych-icon i18">⚕️</div>
        <div class="psych-icon i19">🧬</div><div class="psych-icon i20">💭</div>
        <div class="psych-icon i21">🧠</div><div class="psych-icon i22">🧩</div><div class="psych-icon i23">⚕️</div>
        <div class="psych-icon i24">🧬</div><div class="psych-icon i25">💭</div><div class="psych-icon i26">🧠</div>
        <div class="psych-icon i27">🧩</div><div class="psych-icon i28">⚕️</div><div class="psych-icon i29">🧬</div>
        <div class="psych-icon i30">💭</div>
        <div class="psych-icon i1" style="animation-delay:5s; left:15%;">🧠</div>
        <div class="psych-icon i3" style="animation-delay:2s; left:35%;">⚕️</div>
        <div class="psych-icon i5" style="animation-delay:7s; left:55%;">💭</div>
        <div class="psych-icon i7" style="animation-delay:4s; left:75%;">🧩</div>
        <div class="psych-icon i9" style="animation-delay:1s; left:95%;">🧬</div>
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

# --- VERİTABANI BAĞLANTISI ---
def get_google_sheet():
    try:
        scope = ['https://spreadsheets.google.com/feeds', 'https://www.googleapis.com/auth/drive']
        creds_dict = dict(st.secrets["connections"]["gsheets"])
        creds = ServiceAccountCredentials.from_json_keyfile_dict(creds_dict, scope)
        client = gspread.authorize(creds)
        sheet_url = st.secrets["connections"]["gsheets"]["spreadsheet"]
        sheet = client.open_by_url(sheet_url).worksheet("Sayfa1") 
        return sheet
    except Exception:
        return None

def fetch_leaderboard():
    sheet = get_google_sheet()
    if sheet:
        try:
            all_values = sheet.get_all_values()
            if len(all_values) < 2: return pd.DataFrame(columns=['Kullanıcı', 'Skor', 'Tarih'])
            headers = all_values[0]
            data = all_values[1:]
            df = pd.DataFrame(data, columns=headers)
            df.columns = df.columns.str.strip()
            return df
        except:
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
        st.error("⚠️ sorular.json bulunamadı!")
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
    # GİRİŞ KONTROLÜ
    if st.session_state.user_name == "Misafir":
        st.markdown(f"<div style='text-align:center; margin-bottom:20px;'><h3>👋 Hoş Geldiniz</h3></div>", unsafe_allow_html=True)
        name = st.text_input("Yarışmak için adını gir:", placeholder="Adınız...")
        if name:
            st.session_state.user_name = name
            st.query_params["kullanici"] = name
            st.rerun()
    else:
        # MERHABA BARI (ORTALI)
        st.markdown(f"""
            <div class="greeting-card">
                <span style="font-size:1.5rem; margin-right:10px;">👋</span>
                <p style="margin:0; font-weight:600; color:#333;">Merhaba, {st.session_state.user_name}</p>
            </div>
        """, unsafe_allow_html=True)

    # BANNER (ORTALI)
    st.markdown(f"""
        <div class="compact-banner">
            <div style="font-size: 2.5rem; margin-bottom: 5px;">🏆</div>
            <h2>Psikiyatri Ligi</h2>
            <p>Bilgini test et, zirveye çık!</p>
        </div>
    """, unsafe_allow_html=True)

    c1, c2 = st.columns(2)
    with c1:
        # PRİMARY BUTON (ZORLA BEYAZ YAZI)
        if st.button("🚀 Sınava Başla", type="primary", use_container_width=True):
            if st.session_state.user_name == "Misafir":
                st.warning("Lütfen isminizi girin.")
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
    
    c_exit, c_score = st.columns([1, 4])
    with c_exit:
        if st.button("❌ Çıkış", help="Sınavı iptal et", use_container_width=True):
            quit_quiz()
    
    total_q = len(st.session_state.quiz_data)
    idx = st.session_state.question_index
    q_data = st.session_state.quiz_data[idx]
    
    st.progress((idx + 1) / total_q)
    
    st.markdown(f"""
    <div style="display:flex; justify-content:space-between; margin-bottom:10px; font-size:0.9rem; color:#555;">
        <span>Soru <b>{idx + 1}</b> / {total_q}</span>
        <span style="color:{primary_color}; font-weight:bold;">💎 Puan: {st.session_state.score}</span>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown(f"""
    <div style="background:white; padding:20px; border-radius:12px; border-left:5px solid {secondary_color}; box-shadow:0 2px 10px rgba(0,0,0,0.05); margin-bottom:20px; color:#333; font-weight:600; font-size:1.1rem;">
        {q_data["soru"]}
    </div>
    """, unsafe_allow_html=True)
    
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
            st.markdown(f"<div style='background:#ffebee; padding:10px; border-radius:8px; color:#c62828; margin-bottom:10px;'>Doğru Cevap: <b>{q_data['dogru_cevap']}</b></div>", unsafe_allow_html=True)
        
        with st.expander("ℹ️ Açıklama", expanded=True):
            st.info(q_data.get('aciklama', 'Açıklama yok.'))
            
        btn_txt = "Sonraki Soru ➡️" if idx < total_q - 1 else "Sınavı Bitir ve Kaydet 🏁"
        if st.button(btn_txt, type="primary", use_container_width=True):
            next_question()

def result_page():
    if 'score_saved' not in st.session_state:
        status, msg = save_score_to_db()
        if status:
            st.toast("Skor kaydedildi!", icon="✅")
            st.session_state.score_saved = True
        else:
            st.error(f"Kayıt Hatası: {msg}")

    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown(f"""
        <div style="background:white; padding:40px; border-radius:20px; text-align:center; box-shadow:0 10px 30px rgba(0,0,0,0.1);">
            <div style="font-size: 60px;">🎉</div>
            <h2 style="color: {primary_color}; margin:10px 0;">Sınav Tamamlandı!</h2>
            <p style="font-size: 18px; color: #555;">Tebrikler <b>{st.session_state.user_name}</b>,</p>
            <hr style="margin:20px 0; border:0; border-top:1px solid #eee;">
            <div style="font-size: 14px; color: #999; text-transform:uppercase; letter-spacing:1px;">Toplam Skor</div>
            <h1 style="color: {secondary_color}; font-size: 50px; margin: 0; font-weight:800;">
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
    st.markdown(f"""
    <div style="text-align:center; margin-bottom:20px;">
        <h2 style="color:{primary_color};">🏆 Liderlik Tablosu</h2>
        <p style="color:#666;">En yüksek puanı alan şampiyonlar</p>
    </div>
    """, unsafe_allow_html=True)
    
    with st.spinner('Veriler yükleniyor...'):
        df = fetch_leaderboard()
    
    st.markdown('<div class="leaderboard-container">', unsafe_allow_html=True)
    
    if not df.empty:
        try:
            skor_col = next((col for col in df.columns if 'skor' in col.lower()), None)
            if skor_col:
                df[skor_col] = pd.to_numeric(df[skor_col], errors='coerce').fillna(0)
                df = df.sort_values(by=[skor_col], ascending=False).reset_index(drop=True)
                df.index += 1
                
                st.dataframe(
                    df, 
                    use_container_width=True,
                    column_config={
                        "Skor": st.column_config.ProgressColumn("Skor", format="%d", min_value=0, max_value=100),
                    }
                )
            else:
                st.dataframe(df, use_container_width=True)
        except:
             st.dataframe(df, use_container_width=True)
    else:
        st.info("Henüz kayıtlı veri yok.")
        
    st.markdown('</div>', unsafe_allow_html=True)
    
    st.write("")
    if st.button("⬅ Ana Menü", use_container_width=True):
        st.session_state.current_page = 'home'
        st.rerun()

# --- YÖNLENDİRİCİ ---
if st.session_state.current_page == 'home': home_page()
elif st.session_state.current_page == 'quiz': quiz_page()
elif st.session_state.current_page == 'leaderboard': leaderboard_page()
elif st.session_state.current_page == 'result': result_page()
