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

# --- CSS STİLLERİ (YENİ TASARIM) ---
st.markdown(f"""
    <style>
    /* 1. HAREKETLİ GRADIENT ARKA PLAN */
    .stApp {{
        background: linear-gradient(-45deg, #ee7752, #e73c7e, #23a6d5, #23d5ab);
        background-size: 400% 400%;
        animation: gradientBG 15s ease infinite;
        font-family: 'Poppins', 'Segoe UI', sans-serif;
    }}
    
    @keyframes gradientBG {{
        0% {{ background-position: 0% 50%; }}
        50% {{ background-position: 100% 50%; }}
        100% {{ background-position: 0% 50%; }}
    }}

    /* Mobil kenar boşlukları */
    .block-container {{
        padding-top: 2rem !important;
        padding-bottom: 3rem !important;
        max-width: 700px;
    }}

    /* 2. GENEL YAZI RENGİ (BEYAZ) */
    h1, h2, h3, h4, h5, h6, p, span, div, label {{
        color: #ffffff !important;
        text-shadow: 0 2px 4px rgba(0,0,0,0.2);
    }}

    /* 3. GLASSMORPHISM (CAM ETKİSİ) KUTULAR */
    .glass-card {{
        background: rgba(255, 255, 255, 0.1);
        backdrop-filter: blur(10px);
        -webkit-backdrop-filter: blur(10px);
        border-radius: 20px;
        border: 1px solid rgba(255, 255, 255, 0.2);
        box-shadow: 0 8px 32px 0 rgba(31, 38, 135, 0.37);
        padding: 25px;
        margin-bottom: 20px;
        text-align: center;
        transition: transform 0.3s ease;
    }}
    
    .glass-card:hover {{
        transform: translateY(-3px);
        border: 1px solid rgba(255, 255, 255, 0.4);
        background: rgba(255, 255, 255, 0.15);
    }}

    /* LİDERLİK TABLOSU İÇİN ÖZEL SATIR STİLİ */
    .leader-row {{
        display: flex; 
        align-items: center; 
        justify-content: space-between;
        padding: 15px 20px;
        margin-bottom: 12px;
        background: rgba(255, 255, 255, 0.1);
        border-radius: 15px;
        border: 1px solid rgba(255, 255, 255, 0.15);
        backdrop-filter: blur(5px);
    }}

    /* 4. İSTATİSTİK KUTULARI (Minimal) */
    .stats-container {{
        display: flex; justify-content: space-between; gap: 10px; margin-bottom: 20px;
    }}
    .stat-mini-card {{
        background: rgba(255, 255, 255, 0.15);
        backdrop-filter: blur(5px);
        flex: 1; padding: 15px 5px; border-radius: 15px;
        border: 1px solid rgba(255,255,255,0.2);
        text-align: center;
    }}
    .stat-value {{ font-size: 1.5rem; font-weight: 800; color: white; }}
    .stat-label {{ font-size: 0.75rem; color: rgba(255,255,255,0.8); font-weight: 600; text-transform: uppercase; letter-spacing: 1px; }}

    /* 5. BUTON TASARIMLARI */
    /* Normal Butonlar */
    div.stButton > button {{
        background: rgba(255, 255, 255, 0.1) !important;
        color: white !important;
        border: 1px solid rgba(255, 255, 255, 0.3) !important;
        border-radius: 15px !important;
        padding: 0.8rem 1rem !important;
        font-weight: 600 !important;
        transition: all 0.3s ease !important;
    }}
    div.stButton > button:hover {{
        background: rgba(255, 255, 255, 0.3) !important;
        border-color: white !important;
        transform: scale(1.02);
        box-shadow: 0 0 15px rgba(255,255,255,0.5);
    }}

    /* Primary (Özel) Butonlar - Daha parlak */
    div.stButton > button[kind="primary"] {{
        background: linear-gradient(90deg, #ff00cc, #333399) !important;
        border: none !important;
        box-shadow: 0 4px 15px rgba(0,0,0,0.3) !important;
    }}

    /* Çıkış Butonu (Kırmızımsı) */
    div[data-testid="column"]:nth-of-type(1) div.stButton > button {{
        background: rgba(239, 68, 68, 0.2) !important;
        border: 1px solid rgba(239, 68, 68, 0.5) !important;
    }}
    div[data-testid="column"]:nth-of-type(1) div.stButton > button:hover {{
        background: rgba(239, 68, 68, 0.5) !important;
    }}

    /* 6. INPUT ALANI (İsim Girişi) */
    div[data-testid="stTextInput"] input {{
        background-color: rgba(255, 255, 255, 0.1) !important;
        color: white !important;
        border-radius: 10px;
        border: 1px solid rgba(255, 255, 255, 0.3);
    }}
    div[data-testid="stTextInput"] label {{
        color: rgba(255,255,255,0.9) !important;
    }}

    /* 7. GERİ BİLDİRİM KUTULARI */
    .feedback-box {{ 
        padding: 20px; border-radius: 15px; margin-top: 15px; 
        backdrop-filter: blur(10px); color: white !important;
        text-shadow: none; border: 1px solid rgba(255,255,255,0.3);
    }}
    .fb-correct {{ background-color: rgba(34, 197, 94, 0.3); border-left: 5px solid #4ade80; }}
    .fb-wrong {{ background-color: rgba(239, 68, 68, 0.3); border-left: 5px solid #f87171; }}
    
    /* GİZLEME */
    #MainMenu {{visibility: hidden;}} footer {{visibility: hidden;}} header {{visibility: hidden;}}
    
    </style>
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
if 'total_solved' not in st.session_state: st.session_state.total_solved = 0
if 'total_wrong' not in st.session_state: st.session_state.total_wrong = 0
if 'active_mode' not in st.session_state: st.session_state.active_mode = None 
if 'seen_questions' not in st.session_state: st.session_state.seen_questions = []

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
            kayit_ismi = st.session_state.user_name
            if st.session_state.get("active_mode") == "notes":
                kayit_ismi = f"{st.session_state.user_name}, ders notları puanı"

            all_values = sheet.get_all_values()
            
            if len(all_values) > 0:
                headers = all_values[0]
                data = all_values[1:]
                df = pd.DataFrame(data, columns=headers)
                df.columns = df.columns.str.strip()
                df_cleaned = df[df['Kullanıcı'] != kayit_ismi]
            else:
                df_cleaned = pd.DataFrame(columns=['Kullanıcı', 'Skor', 'Tarih'])

            tarih = (pd.Timestamp.now('UTC') + pd.Timedelta(hours=3)).strftime('%Y-%m-%d %H:%M')
            
            new_row = pd.DataFrame([{
                'Kullanıcı': kayit_ismi,
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
def load_questions(json_filename):
    try:
        with open(json_filename, 'r', encoding='utf-8') as f:
            all_questions = json.load(f)
        
        available_questions = [
            q for q in all_questions 
            if q['soru'] not in st.session_state.seen_questions
        ]
        
        if len(available_questions) < 10:
            st.toast("Sorular bitti, havuz yenilendi! 🔄", icon="✨")
            st.session_state.seen_questions = []
            available_questions = all_questions
        
        question_count = min(10, len(available_questions))
        selected_questions = random.sample(available_questions, question_count)
        
        for q in selected_questions:
            st.session_state.seen_questions.append(q['soru'])
            
        st.session_state.quiz_data = selected_questions
        return True
    except Exception as e:
        st.error(f"Hata: {e}")
        return False

def start_quiz(mode_type, filename):
    if st.session_state.active_mode != mode_type:
        st.session_state.seen_questions = []
        st.session_state.active_mode = mode_type

    st.session_state.question_index = 0
    st.session_state.score = 0
    st.session_state.answer_submitted = False
    
    if st.session_state.user_name != "Misafir":
        st.query_params["kullanici"] = st.session_state.user_name
    
    if load_questions(filename):
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
    # Başlık Alanı
    st.markdown(f"""
        <div class="glass-card" style="padding: 40px 20px;">
            <div style="font-size: 3rem; margin-bottom: 10px; text-shadow: 0 0 20px rgba(255,255,255,0.5);">🧠</div>
            <div style="font-size: 2.2rem; font-weight: 900; margin-bottom: 5px;">Psikiyatri Ligi</div>
            <div style="font-size: 1rem; opacity: 0.9;">Bilginle Işılda ✨</div>
        </div>
    """, unsafe_allow_html=True)

    if st.session_state.user_name == "Misafir":
        name = st.text_input("Yarışmak için adını gir:", placeholder="İsminiz...")
        if name:
            st.session_state.user_name = name
            st.query_params["kullanici"] = name
            st.rerun()
    else:
        # BAŞARI ORANI HESAPLAMA
        if st.session_state.total_solved > 0:
            success_rate = int(((st.session_state.total_solved - st.session_state.total_wrong) / st.session_state.total_solved) * 100)
        else:
            success_rate = 0

        st.markdown(f"""<div style="text-align:center; margin-bottom:20px; font-weight:bold; font-size:1.2rem;">Hoşgeldin, {st.session_state.user_name} 👋</div>""", unsafe_allow_html=True)
        
        # İstatistikler
        st.markdown(f"""
        <div class="stats-container">
            <div class="stat-mini-card">
                <div class="stat-value">{st.session_state.total_solved}</div>
                <div class="stat-label">Soru</div>
            </div>
            <div class="stat-mini-card">
                <div class="stat-value">{st.session_state.total_wrong}</div>
                <div class="stat-label">Hata</div>
            </div>
            <div class="stat-mini-card">
                <div class="stat-value">%{success_rate}</div>
                <div class="stat-label">BAŞARI</div>
            </div>
        </div>
        """, unsafe_allow_html=True)

    # Butonlar
    col1, col2 = st.columns(2)
    with col1:
        if st.button("🚀 Genel Sınav", type="primary", use_container_width=True):
            if st.session_state.user_name == "Misafir":
                st.warning("Lütfen isminizi girin.")
            else:
                start_quiz("league", "sorular.json")
    
    with col2:
        if st.button("📚 Ders Notları", use_container_width=True):
            if st.session_state.user_name == "Misafir":
                st.warning("Lütfen isminizi girin.")
            else:
                start_quiz("notes", "ders_notlari.json")
    
    st.write("") 
    
    if st.button("🏆 Liderlik Tablosu", use_container_width=True):
        st.session_state.current_page = 'leaderboard'
        st.rerun()

def quiz_page():
    if not st.session_state.quiz_data:
        st.session_state.current_page = 'home'
        st.rerun()
    
    c1, c2 = st.columns([1.5, 3.5])
    with c1:
        if st.button("Kapat ✖", use_container_width=True):
            quit_quiz()
    with c2: 
        mode_label = "NOTLAR" if st.session_state.active_mode == "notes" else "GENEL"
        st.markdown(f"<div style='text-align:right; opacity:0.8; font-size:0.9rem; padding-top:10px;'>MOD: <b>{mode_label}</b></div>", unsafe_allow_html=True)
    
    total_q = len(st.session_state.quiz_data)
    idx = st.session_state.question_index
    q_data = st.session_state.quiz_data[idx]
    
    st.progress((idx + 1) / total_q)
    
    # Soru Kartı
    st.markdown(f"""
    <div class="glass-card" style="text-align:left;">
        <div style="display:flex; justify-content:space-between; margin-bottom:15px; opacity:0.8; font-size:0.85rem;">
            <span>SORU {idx + 1} / {total_q}</span>
            <span style="font-weight:bold;">💎 {st.session_state.score}</span>
        </div>
        <div style="font-size: 1.3rem; font-weight: 700; line-height: 1.5;">{q_data["soru"]}</div>
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
            st.markdown(f'<div class="feedback-box fb-correct"><b>✅ Mükemmel! Doğru Cevap.</b></div>', unsafe_allow_html=True)
        else:
            st.markdown(f'<div class="feedback-box fb-wrong"><b>❌ Yanlış Cevap</b><br><small>Doğrusu: {q_data["dogru_cevap"]}</small></div>', unsafe_allow_html=True)
        
        if q_data.get('aciklama'):
            st.markdown(f'<div style="background:rgba(255,255,255,0.1); padding:15px; border-radius:10px; margin-top:10px; border:1px solid rgba(255,255,255,0.2);"><b>💡 Açıklama:</b><br>{q_data["aciklama"]}</div>', unsafe_allow_html=True)
            
        st.write("")
        btn_txt = "Sonraki ➡️" if idx < total_q - 1 else "Sonuçları Gör 🏁"
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
        <div class="glass-card">
            <div style="font-size: 60px; margin-bottom:10px;">🎉</div>
            <h2 style="margin:0;">Tebrikler!</h2>
            <p style="opacity:0.8;">{st.session_state.user_name}</p>
            <div style="margin: 20px 0; padding: 20px; background:rgba(255,255,255,0.1); border-radius:15px; border:1px solid rgba(255,255,255,0.2);">
                <span style="font-size: 14px; text-transform:uppercase; opacity:0.7; font-weight:bold;">TOPLAM SKOR</span>
                <div style="font-size: 60px; font-weight:900; text-shadow:0 0 30px rgba(255,255,255,0.6);">{st.session_state.score}</div>
            </div>
        </div>
    """, unsafe_allow_html=True)
    
    st.write("")
    c1, c2 = st.columns(2)
    with c1:
        if st.button("🏠 Ana Menü", use_container_width=True):
            if 'score_saved' in st.session_state: del st.session_state.score_saved
            st.session_state.current_page = 'home'
            st.rerun()
    with c2:
        if st.button("🏆 Sıralama", type="primary", use_container_width=True):
            if 'score_saved' in st.session_state: del st.session_state.score_saved
            st.session_state.current_page = 'leaderboard'
            st.rerun()

def leaderboard_page():
    st.markdown(f"""
    <div style="text-align:center; margin-bottom:20px;">
        <h3>🏆 Şampiyonlar Ligi</h3>
    </div>
    """, unsafe_allow_html=True)
    
    with st.spinner('Yükleniyor...'):
        df = fetch_leaderboard()
    
    if not df.empty:
        try:
            skor_col = next((col for col in df.columns if 'skor' in col.lower()), None)
            if skor_col:
                # Skora göre sırala
                df[skor_col] = pd.to_numeric(df[skor_col], errors='coerce').fillna(0)
                df = df.sort_values(by=[skor_col], ascending=False).reset_index(drop=True)
                
                # Tablo yerine her kişi için bir KART oluştur
                for index, row in df.iterrows():
                    rank = index + 1
                    
                    # İkon Seçimi (İlk 3 için madalya)
                    if rank == 1:
                        rank_display = "🥇"
                        extra_style = "border: 2px solid #FFD700; background: rgba(255, 215, 0, 0.2);" # Altın
                    elif rank == 2:
                        rank_display = "🥈"
                        extra_style = "border: 2px solid #C0C0C0; background: rgba(192, 192, 192, 0.2);" # Gümüş
                    elif rank == 3:
                        rank_display = "🥉"
                        extra_style = "border: 2px solid #CD7F32; background: rgba(205, 127, 50, 0.2);" # Bronz
                    else:
                        rank_display = f"#{rank}"
                        extra_style = ""

                    st.markdown(f"""
                    <div class="leader-row" style="{extra_style}">
                        <div style="font-size:1.5rem; font-weight:900; width:50px; text-align:center;">{rank_display}</div>
                        <div style="flex:1; padding:0 15px; font-weight:600; font-size:1.1rem; text-align:left;">
                            {row['Kullanıcı']}
                        </div>
                        <div style="font-weight:800; font-size:1.2rem; background:rgba(255,255,255,0.2); padding:5px 15px; border-radius:10px;">
                            {int(row['Skor'])}
                        </div>
                    </div>
                    """, unsafe_allow_html=True)
            else:
                st.dataframe(df, use_container_width=True)
        except Exception as e:
             st.error(f"Hata oluştu: {e}")
             st.dataframe(df, use_container_width=True)
    else:
        st.info("Henüz veri yok.")
        
    st.write("")
    if st.button("⬅ Geri Dön", use_container_width=True):
        st.session_state.current_page = 'home'
        st.rerun()

# --- YÖNLENDİRİCİ ---
if st.session_state.current_page == 'home': home_page()
elif st.session_state.current_page == 'quiz': quiz_page()
elif st.session_state.current_page == 'leaderboard': leaderboard_page()
elif st.session_state.current_page == 'result': result_page()
