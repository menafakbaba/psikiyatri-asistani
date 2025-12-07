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

# --- RENK PALETİ (SİYAH/BEYAZ UYUMU) ---
primary_color = "#3A0CA3"   # Ana Mor
secondary_color = "#F72585" # Pembe Vurgu
bg_color = "#F8F9FA"        # Beyaz/Gri Arka Plan
text_color = "#212529"      # Net Siyah Yazı

# --- CSS VE ANİMASYON ---
st.markdown(f"""
    <style>
    /* 1. GENEL AYARLAR */
    .stApp {{
        background-color: {bg_color};
        color: {text_color};
        font-family: 'Helvetica Neue', Helvetica, Arial, sans-serif;
    }}
    
    h1, h2, h3, h4 {{ color: {primary_color} !important; font-weight: 700; }}
    p {{ color: #495057; }} /* Koyu gri paragraflar */

    /* 2. ARKA PLAN ANİMASYONU (60 İKON, %50 OPAK) */
    .psych-bg {{
        position: fixed; top: 0; left: 0; width: 100%; height: 100%;
        z-index: -1; overflow: hidden; pointer-events: none;
    }}

    .psych-icon {{
        position: absolute; top: -100px;
        opacity: 0.5; /* İstenilen %50 Opaklık */
        animation: fall linear infinite;
        font-weight: bold;
    }}

    @keyframes fall {{
        0% {{ transform: translateY(-10vh) rotate(0deg); }}
        100% {{ transform: translateY(120vh) rotate(360deg); }}
    }}

    /* Dinamik CSS Sınıfları (Aşağıda HTML ile oluşturulacak) */
    
    /* 3. MERHABA BARI (%10 Kalınlık, Tam Genişlik) */
    .greeting-card {{
        background-color: white;
        max-width: 500px; /* Banner ile aynı genişlik */
        margin: 0 auto 10px auto; /* Banner'a yakın */
        padding: 10px 20px;
        border-radius: 12px;
        box-shadow: 0 2px 10px rgba(0,0,0,0.05);
        display: flex;
        align-items: center;
        border-left: 5px solid {secondary_color};
    }}
    .greeting-text {{
        font-size: 1.1rem;
        font-weight: 600;
        color: {text_color};
        margin: 0;
    }}

    /* 4. ANA BANNER (%50 KÜÇÜLTÜLMÜŞ) */
    .compact-banner {{
        background: linear-gradient(135deg, {primary_color} 0%, #7209B7 100%);
        padding: 20px; /* Dolgu azaltıldı */
        border-radius: 20px;
        color: white !important;
        text-align: center;
        max-width: 500px; /* Genişlik sınırlandı */
        margin: 0 auto 30px auto;
        box-shadow: 0 10px 20px rgba(58, 12, 163, 0.2);
    }}
    .compact-banner h2 {{
        color: white !important;
        margin: 0;
        font-size: 1.8rem; /* Font küçüldü */
    }}
    .compact-banner p {{
        color: rgba(255,255,255,0.9);
        font-size: 0.9rem;
        margin-top: 5px;
    }}

    /* 5. LİDERLİK TABLOSU GÜZELLEŞTİRME */
    .leaderboard-container {{
        background-color: white;
        padding: 20px;
        border-radius: 15px;
        box-shadow: 0 4px 15px rgba(0,0,0,0.08);
        border: 1px solid #eee;
    }}
    
    /* Butonlar */
    div.stButton > button {{
        border-radius: 10px; border: 1px solid #e0e0e0;
        background-color: white; color: {text_color}; font-weight: 600;
        transition: all 0.2s;
    }}
    div.stButton > button:hover {{
        border-color: {primary_color}; color: {primary_color}; background-color: #f8f0fc;
    }}
    div.stButton > button[kind="primary"] {{
        background-color: {primary_color}; color: white; border: none;
    }}
    div.stButton > button[kind="primary"]:hover {{
        background-color: #4800b0;
    }}

    /* Elementleri gizle */
    #MainMenu {{visibility: hidden;}} footer {{visibility: hidden;}} header {{visibility: hidden;}}
    </style>
""", unsafe_allow_html=True)

# --- 60 TANE ANİMASYON İKONU OLUŞTURUCU ---
# Tek tek yazmak yerine Python ile HTML üretiyoruz (Kod kirliliğini önler)
icons = ["🧠", "🧩", "⚕️", "🧬", "💭", "💊", "🩺", "💡"]
colors = ["#3A0CA3", "#F72585", "#4361ee", "#06d6a0", "#f9c74f"]
animation_html = '<div class="psych-bg">'
for i in range(1, 61):
    left = random.randint(1, 98)
    dur = random.randint(10, 25)
    delay = random.randint(0, 10)
    size = random.uniform(1.5, 3.5)
    icon = random.choice(icons)
    color = random.choice(colors)
    
    style = f"left:{left}%; animation-duration:{dur}s; animation-delay:{delay}s; font-size:{size}rem; color:{color};"
    animation_html += f'<div class="psych-icon" style="{style}">{icon}</div>'
animation_html += '</div>'
st.markdown(animation_html, unsafe_allow_html=True)


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
    except Exception as e:
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
    # GİRİŞ KONTROLÜ (GİZLİ)
    if st.session_state.user_name == "Misafir":
        st.markdown(f"<div style='text-align:center; margin-bottom:20px;'><h3>👋 Hoş Geldiniz</h3></div>", unsafe_allow_html=True)
        name = st.text_input("Yarışmak için adını gir:", placeholder="Adınız...")
        if name:
            st.session_state.user_name = name
            st.query_params["kullanici"] = name
            st.rerun()
    else:
        # 1. YENİ MERHABA BARI (İnce, Banner Genişliğinde)
        st.markdown(f"""
            <div class="greeting-card">
                <span style="font-size:1.5rem; margin-right:10px;">👋</span>
                <p class="greeting-text">Merhaba, {st.session_state.user_name}</p>
            </div>
        """, unsafe_allow_html=True)

    # 2. KOMPAKT BANNER (%50 Küçültüldü)
    st.markdown(f"""
        <div class="compact-banner">
            <div style="font-size: 2.5rem; margin-bottom: 5px;">🏆</div>
            <h2>Psikiyatri Ligi</h2>
            <p>Bilgini test et, zirveye çık!</p>
        </div>
    """, unsafe_allow_html=True)

    c1, c2 = st.columns(2)
    with c1:
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
    
    # Soru Kartı (Daha şık)
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
    # ŞIK BAŞLIK
    st.markdown(f"""
    <div style="text-align:center; margin-bottom:20px;">
        <h2 style="color:{primary_color};">🏆 Liderlik Tablosu</h2>
        <p style="color:#666;">En yüksek puanı alan şampiyonlar</p>
    </div>
    """, unsafe_allow_html=True)
    
    with st.spinner('Veriler yükleniyor...'):
        df = fetch_leaderboard()
    
    # ŞIK TABLO GÖRÜNÜMÜ
    st.markdown('<div class="leaderboard-container">', unsafe_allow_html=True)
    
    if not df.empty:
        try:
            skor_col = next((col for col in df.columns if 'skor' in col.lower()), None)
            if skor_col:
                df[skor_col] = pd.to_numeric(df[skor_col], errors='coerce').fillna(0)
                df = df.sort_values(by=[skor_col], ascending=False).reset_index(drop=True)
                df.index += 1
                
                # Tabloyu göster
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
        
    st.markdown('</div>', unsafe_allow_html=True) # Container bitiş
    
    st.write("")
    if st.button("⬅ Ana Menü", use_container_width=True):
        st.session_state.current_page = 'home'
        st.rerun()

# --- YÖNLENDİRİCİ ---
if st.session_state.current_page == 'home': home_page()
elif st.session_state.current_page == 'quiz': quiz_page()
elif st.session_state.current_page == 'leaderboard': leaderboard_page()
elif st.session_state.current_page == 'result': result_page()
