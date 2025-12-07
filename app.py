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
primary_color = "#4361ee"    # Modern Mavi
accent_color = "#f72585"     # Pembe
bg_color = "#f0f4f8"         # Ferah Açık Gri/Mavi
text_dark = "#1e293b"        # Koyu Lacivert/Siyah

# --- CSS STİLLERİ ---
st.markdown(f"""
    <style>
    /* 1. GENEL AYARLAR */
    .stApp {{
        background-color: {bg_color};
        font-family: 'Segoe UI', Roboto, Helvetica, Arial, sans-serif;
    }}
    
    /* Mobil kenar boşlukları */
    .block-container {{
        padding-top: 1rem !important;
        padding-bottom: 2rem !important;
        max-width: 700px;
    }}

    h1, h2, h3 {{ color: {primary_color} !important; font-weight: 800; letter-spacing: -0.5px; }}
    p, span, div {{ color: {text_dark}; }}

    /* 2. ARKA PLAN ANİMASYONU */
    .psych-bg {{
        position: fixed; top: 0; left: 0; width: 100%; height: 100%;
        z-index: 0; overflow: hidden; pointer-events: none;
    }}
    @keyframes fall {{
        0% {{ transform: translateY(-10vh) rotate(0deg); }}
        100% {{ transform: translateY(120vh) rotate(360deg); }}
    }}

    /* 3. İSTATİSTİK KUTULARI (MOBİL DOSTU) */
    .stats-container {{
        display: flex; justify-content: space-between; gap: 8px; margin-bottom: 20px;
    }}
    .stat-mini-card {{
        background: white; flex: 1; padding: 10px 5px; border-radius: 12px;
        box-shadow: 0 4px 10px rgba(0,0,0,0.1); text-align: center;
        border-bottom: 4px solid {primary_color}; min-width: 0;
    }}
    .stat-icon {{ font-size: 1.2rem; display: block; margin-bottom: 2px; }}
    .stat-value {{ font-size: 1.1rem; font-weight: 800; color: {text_dark}; line-height: 1.2; }}
    .stat-label {{ font-size: 0.65rem; color: #666; font-weight: 700; text-transform: uppercase; }}

    /* 4. MODERN HERO BANNER */
    .modern-hero {{
        background: linear-gradient(120deg, #ffffff 0%, #f0f4ff 100%);
        border-radius: 20px; padding: 25px 15px;
        box-shadow: 0 8px 25px rgba(67, 97, 238, 0.15);
        border: 2px solid white;
        text-align: center; margin-bottom: 25px; position: relative; overflow: hidden;
    }}
    .modern-hero::after {{
        content: ""; position: absolute; top: 0; left: 0; width: 100%; height: 5px;
        background: linear-gradient(90deg, {primary_color}, {accent_color});
    }}
    .hero-title {{
        font-size: 1.8rem;
        background: linear-gradient(45deg, {primary_color}, {accent_color});
        -webkit-background-clip: text; -webkit-text-fill-color: transparent;
        font-weight: 900; margin-bottom: 5px;
    }}
    .hero-subtitle {{ font-size: 0.9rem; color: #64748b; font-weight: 600; }}

    /* 5. SORU KARTI TASARIMI */
    .quiz-card {{
        background-color: #ffffff;
        border: 1px solid #e2e8f0;
        border-radius: 20px;
        padding: 25px 20px;
        box-shadow: 0 10px 30px rgba(0,0,0,0.1);
        margin-bottom: 20px;
        position: relative;
        z-index: 2;
    }}
    
    .question-text {{
        font-size: 1.2rem;
        font-weight: 700;
        color: #0f172a;
        line-height: 1.5;
    }}
    
    /* 6. BUTONLAR */
    div.stButton > button[kind="primary"] {{
        background: linear-gradient(45deg, {primary_color}, {accent_color}) !important;
        color: white !important; border: none !important; border-radius: 12px !important;
        padding: 0.8rem 1rem !important; font-size: 1rem !important; width: 100%;
        box-shadow: 0 4px 12px rgba(67, 97, 238, 0.4) !important;
    }}
    
    div.stButton > button {{
        width: 100%;
        border-radius: 12px;
        background-color: #ffffff; 
        border: 2px solid #cbd5e1;
        color: #334155; 
        font-weight: 600;
        padding: 0.8rem 1rem;
    }}
    div.stButton > button:hover {{
        border-color: {primary_color};
        color: {primary_color};
        background-color: #eff6ff;
    }}

    /* ÖZEL: ÇIKIŞ BUTONU (KIRMIZI) */
    div[data-testid="column"]:nth-of-type(1) div.stButton > button {{
        background-color: #ef4444 !important;
        color: white !important;
        border: none !important;
        box-shadow: 0 4px 10px rgba(239, 68, 68, 0.4) !important;
        font-weight: bold !important;
    }}
    div[data-testid="column"]:nth-of-type(1) div.stButton > button:hover {{
        background-color: #dc2626 !important;
        transform: scale(1.05);
    }}

    /* Diğer */
    .greeting-pill {{
        background: white; display: inline-block; padding: 6px 20px; 
        border-radius: 20px; font-size: 0.9rem; color: #475569; font-weight: 700;
        box-shadow: 0 4px 10px rgba(0,0,0,0.05); margin-bottom: 15px;
    }}
    .feedback-box {{ padding: 15px; border-radius: 12px; margin-top: 15px; z-index:2; position:relative; background:white; }}
    .fb-correct {{ border-left: 5px solid #22c55e; color: #14532d; background-color: #f0fdf4; }}
    .fb-wrong {{ border-left: 5px solid #ef4444; color: #7f1d1d; background-color: #fef2f2; }}
    
    .info-pill {{
        background: white; 
        padding: 12px; 
        border-radius: 12px; 
        border-left: 5px solid {primary_color};
        margin-bottom: 20px; 
        color: #555; 
        font-size: 0.9rem; 
        text-align: center;
        box-shadow: 0 2px 8px rgba(0,0,0,0.05);
    }}

    #MainMenu {{visibility: hidden;}} footer {{visibility: hidden;}} header {{visibility: hidden;}}
    </style>
""", unsafe_allow_html=True)

# --- DİNAMİK ARKA PLAN ---
def create_dynamic_bg():
    icons = ["🧠", "🧩", "⚕️", "🧬", "💊", "🩺", "💡", "💭"]
    colors = ["#4361ee", "#f72585", "#7209b7", "#4cc9f0"]
    html_content = '<div class="psych-bg">'
    for _ in range(50):
        left = random.randint(1, 99)
        duration = random.uniform(5, 12)
        delay = random.uniform(0, 10)
        size = random.uniform(1.5, 3.5)
        opacity = random.uniform(0.3, 0.7)
        icon = random.choice(icons)
        color = random.choice(colors)
        style = f"position:absolute; left:{left}%; top:-10%; animation:fall {duration}s linear infinite; animation-delay:{delay}s; font-size:{size}rem; color:{color}; opacity:{opacity};"
        html_content += f'<div style="{style}">{icon}</div>'
    html_content += '</div>'
    st.markdown(html_content, unsafe_allow_html=True)

create_dynamic_bg()

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
if 'total_solved' not in st.session_state: st.session_state.total_solved = 0
if 'total_wrong' not in st.session_state: st.session_state.total_wrong = 0

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
    except:
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
            all_values = sheet.get_all_values()
            if len(all_values) > 0:
                headers = all_values[0]
                data = all_values[1:]
                df = pd.DataFrame(data, columns=headers)
                df.columns = df.columns.str.strip()
                df_cleaned = df[df['Kullanıcı'] != st.session_state.user_name]
            else:
                df_cleaned = pd.DataFrame(columns=['Kullanıcı', 'Skor', 'Tarih'])

            # DÜZELTME: UTC Saatini alıp 3 saat (TR Saati) ekliyoruz
            tarih = (pd.Timestamp.now('UTC') + pd.Timedelta(hours=3)).strftime('%Y-%m-%d %H:%M')
            
            new_row = pd.DataFrame([{
                'Kullanıcı': st.session_state.user_name,
                'Skor': st.session_state.score,
                'Tarih': tarih
            }])
            final_df = pd.concat([df_cleaned, new_row], ignore_index=True)
            sheet.clear()
            update_data = [final_df.columns.values.tolist()] + final_df.values.tolist()
            sheet.update(update_data)
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
    st.session_state.total_solved += 1
    
    if option == current_q['dogru_cevap']:
        st.session_state.score += 10
        st.session_state.is_correct = True
    else:
        st.session_state.is_correct = False
        st.session_state.total_wrong += 1

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
    if st.session_state.user_name == "Misafir":
        st.markdown(f"<div style='text-align:center; margin-bottom:30px;'><h1 style='font-size:3rem;'>👋</h1><h3>Psikiyatri Ligi</h3></div>", unsafe_allow_html=True)
        name = st.text_input("Yarışmak için adını gir:", placeholder="Adınız...")
        if name:
            st.session_state.user_name = name
            st.query_params["kullanici"] = name
            st.rerun()
    else:
        st.markdown(f"""
        <div style="text-align:center;">
            <span class="greeting-pill">👋 {st.session_state.user_name}</span>
        </div>
        """, unsafe_allow_html=True)

        st.markdown(f"""
        <div class="stats-container">
            <div class="stat-mini-card" style="border-bottom-color:#4cc9f0;">
                <span class="stat-icon">📝</span>
                <span class="stat-value">{st.session_state.total_solved}</span>
                <div class="stat-label">Soru</div>
            </div>
            <div class="stat-mini-card" style="border-bottom-color:#f72585;">
                <span class="stat-icon">🚨</span>
                <span class="stat-value">{st.session_state.total_wrong}</span>
                <div class="stat-label">Hata</div>
            </div>
            <div class="stat-mini-card" style="border-bottom-color:#2ecc71;">
                <span class="stat-icon">🟢</span>
                <span class="stat-value">Aktif</span>
                <div class="stat-label">Durum</div>
            </div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown(f"""
        <div class="modern-hero">
            <div style="font-size: 2.5rem; margin-bottom: 5px;">🏆</div>
            <div class="hero-title">Psikiyatri Ligi</div>
            <div class="hero-subtitle">Bilgini sına, zirveye çık!</div>
        </div>
    """, unsafe_allow_html=True)

    if st.button("🚀 Sınava Başla", type="primary", use_container_width=True):
        if st.session_state.user_name == "Misafir":
            st.warning("Lütfen isminizi girin.")
        else:
            start_quiz()
            
    st.write("") 
    
    if st.button("📊 Liderlik Tablosu", use_container_width=True):
        st.session_state.current_page = 'leaderboard'
        st.rerun()

def quiz_page():
    if not st.session_state.quiz_data:
        st.session_state.current_page = 'home'
        st.rerun()
    
    c1, c2 = st.columns([1.5, 3.5])
    with c1:
        if st.button("🛑 SINAVI BİTİR", help="Sınavı iptal et", use_container_width=True):
            quit_quiz()
    with c2: pass 
    
    total_q = len(st.session_state.quiz_data)
    idx = st.session_state.question_index
    q_data = st.session_state.quiz_data[idx]
    
    st.progress((idx + 1) / total_q)
    
    st.markdown(f"""
    <div class="quiz-card">
        <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:10px; font-size:0.8rem; color:#64748b;">
            <span>SORU {idx + 1} / {total_q}</span>
            <span style="color:{accent_color}; font-weight:bold;">💎 {st.session_state.score}</span>
        </div>
        <div class="question-text">{q_data["soru"]}</div>
    </div>
    """, unsafe_allow_html=True)
    
    if not st.session_state.answer_submitted:
        for i, opt in enumerate(q_data['secenekler']):
            st.write("") 
            if st.button(opt, key=f"q{idx}_o{i}", use_container_width=True):
                submit_answer(opt)
                st.rerun()
    else:
        if st.session_state.is_correct: 
            st.markdown(f'<div class="feedback-box fb-correct"><b>✅ Doğru Cevap!</b></div>', unsafe_allow_html=True)
        else:
            st.markdown(f'<div class="feedback-box fb-wrong"><b>❌ Yanlış!</b><br><small>Cevap: {q_data["dogru_cevap"]}</small></div>', unsafe_allow_html=True)
        
        if q_data.get('aciklama'):
            st.markdown(f'<div style="background:white; padding:15px; border-radius:10px; margin-top:10px; border:1px solid #e2e8f0; font-size:0.9rem;"><b>💡 Bilgi:</b><br>{q_data["aciklama"]}</div>', unsafe_allow_html=True)
            
        st.write("")
        btn_txt = "Sonraki Soru ➡️" if idx < total_q - 1 else "Bitir 🏁"
        if st.button(btn_txt, type="primary", use_container_width=True):
            next_question()

def result_page():
    if 'score_saved' not in st.session_state:
        status, msg = save_score_to_db()
        if status:
            st.toast("Skor kaydedildi!", icon="✅")
            st.session_state.score_saved = True
        else:
            st.error(f"Hata: {msg}")

    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown(f"""
        <div style="background:white; padding:30px 20px; border-radius:20px; text-align:center; box-shadow:0 10px 30px rgba(0,0,0,0.1);">
            <div style="font-size: 60px; margin-bottom:10px;">🎉</div>
            <h2 style="color: {primary_color}; margin:0;">Tebrikler!</h2>
            <p style="color: #64748b; font-size:0.9rem;">{st.session_state.user_name}</p>
            <div style="margin: 20px 0; padding: 15px; background:#f8f9fa; border-radius:15px;">
                <span style="font-size: 12px; text-transform:uppercase; color:#94a3b8; font-weight:bold;">Skor</span>
                <div style="font-size: 50px; font-weight:900; color:{accent_color}; line-height:1;">{st.session_state.score}</div>
            </div>
        </div>
    """, unsafe_allow_html=True)
    
    st.write("")
    c1, c2 = st.columns(2)
    with c1:
        if st.button("🏠 Menü", use_container_width=True):
            if 'score_saved' in st.session_state: del st.session_state.score_saved
            st.session_state.current_page = 'home'
            st.rerun()
    with c2:
        if st.button("🏆 Liste", type="primary", use_container_width=True):
            if 'score_saved' in st.session_state: del st.session_state.score_saved
            st.session_state.current_page = 'leaderboard'
            st.rerun()

def leaderboard_page():
    st.markdown(f"""
    <div style="text-align:center; margin-bottom:10px;">
        <h3 style="color:{primary_color};">🏆 Şampiyonlar</h3>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown(f"""
    <div class="info-pill">
        ℹ️ Sıralama, yarışmacıların <b>en son</b> aldıkları puana göre belirlenir.
    </div>
    """, unsafe_allow_html=True)
    
    with st.spinner('Yükleniyor...'):
        df = fetch_leaderboard()
    
    if not df.empty:
        try:
            skor_col = next((col for col in df.columns if 'skor' in col.lower()), None)
            if skor_col:
                df[skor_col] = pd.to_numeric(df[skor_col], errors='coerce').fillna(0)
                df = df.sort_values(by=[skor_col], ascending=False).reset_index(drop=True)
                df.index += 1
                st.markdown('<div style="background:white; padding:15px; border-radius:15px; box-shadow:0 5px 20px rgba(0,0,0,0.05);">', unsafe_allow_html=True)
                st.dataframe(df, use_container_width=True, column_config={"Skor": st.column_config.ProgressColumn("Skor", format="%d", min_value=0, max_value=100)})
                st.markdown('</div>', unsafe_allow_html=True)
            else:
                st.dataframe(df, use_container_width=True)
        except:
             st.dataframe(df, use_container_width=True)
    else:
        st.info("Veri yok.")
        
    st.write("")
    if st.button("⬅ Geri", use_container_width=True):
        st.session_state.current_page = 'home'
        st.rerun()

# --- YÖNLENDİRİCİ ---
if st.session_state.current_page == 'home': home_page()
elif st.session_state.current_page == 'quiz': quiz_page()
elif st.session_state.current_page == 'leaderboard': leaderboard_page()
elif st.session_state.current_page == 'result': result_page()
