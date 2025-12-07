import streamlit as st
import pandas as pd
import json
import random
import time

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
correct_color = "#2E7D32" # Yeşil
wrong_color = "#C62828"   # Kırmızı
bg_color = "#F8F9FA"

# Özel CSS (Daha sade ve kararlı)
st.markdown(f"""
    <style>
    /* Genel Arka Plan */
    .stApp {{
        background-color: {bg_color};
    }}
    
    /* Banner */
    .banner {{
        background: linear-gradient(135deg, {primary_color} 0%, #7209B7 100%);
        padding: 20px;
        border-radius: 15px;
        color: white;
        text-align: center;
        margin-bottom: 20px;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
    }}
    
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
    
    /* Butonlar için genel stil düzeltmesi */
    .stButton button {{
        width: 100%;
        border-radius: 10px;
        height: auto;
        padding: 10px;
        font-weight: 500;
        transition: all 0.3s;
    }}
    
    /* Sonuç Kartı */
    .result-box {{
        background-color: white;
        padding: 30px;
        border-radius: 20px;
        text-align: center;
        box-shadow: 0 4px 15px rgba(0,0,0,0.1);
    }}
    
    /* Gizleme */
    #MainMenu {{visibility: hidden;}}
    footer {{visibility: hidden;}}
    header {{visibility: hidden;}}
    </style>
""", unsafe_allow_html=True)

# --- STATE YÖNETİMİ ---
# Değişkenleri başlat
if 'current_page' not in st.session_state:
    st.session_state.current_page = 'home'
if 'question_index' not in st.session_state:
    st.session_state.question_index = 0
if 'score' not in st.session_state:
    st.session_state.score = 0
if 'user_name' not in st.session_state:
    st.session_state.user_name = "Misafir"
if 'quiz_data' not in st.session_state:
    st.session_state.quiz_data = []
if 'leaderboard' not in st.session_state:
    st.session_state.leaderboard = pd.DataFrame([
        {'Kullanıcı': 'Dr. Freud', 'Skor': 9, 'Tarih': '2025-10-25'},
        {'Kullanıcı': 'Jung', 'Skor': 8, 'Tarih': '2025-10-26'}
    ])

# --- YENİ EKLENEN STATE: ANLIK GERİ BİLDİRİM İÇİN ---
if 'answer_submitted' not in st.session_state:
    st.session_state.answer_submitted = False
if 'selected_option' not in st.session_state:
    st.session_state.selected_option = None
if 'is_correct' not in st.session_state:
    st.session_state.is_correct = False

# --- FONKSİYONLAR ---

def load_data():
    """sorular.json dosyasını yükler."""
    try:
        with open('sorular.json', 'r', encoding='utf-8') as f:
            all_questions = json.load(f)
        
        # Her seferinde rastgele 10 soru seç
        question_count = min(10, len(all_questions))
        st.session_state.quiz_data = random.sample(all_questions, question_count)
        return True
    except FileNotFoundError:
        st.error("⚠️ 'sorular.json' dosyası bulunamadı! Dosyanın app.py ile aynı klasörde olduğundan emin olun.")
        return False
    except json.JSONDecodeError:
        st.error("⚠️ JSON dosya formatı hatalı. Süslü parantezleri kontrol edin.")
        return False

def save_score():
    new_entry = pd.DataFrame([{
        'Kullanıcı': st.session_state.user_name,
        'Skor': st.session_state.score,
        'Tarih': pd.to_datetime('today').strftime('%Y-%m-%d')
    }])
    st.session_state.leaderboard = pd.concat([st.session_state.leaderboard, new_entry], ignore_index=True)

def start_quiz():
    """Quizi başlatır ve değişkenleri sıfırlar."""
    st.session_state.question_index = 0
    st.session_state.score = 0
    st.session_state.answer_submitted = False
    if load_data():
        st.session_state.current_page = 'quiz'
        st.rerun()

def submit_answer(option):
    """Cevabı işaretler ama hemen diğer soruya geçmez (Geri bildirim için)."""
    current_q = st.session_state.quiz_data[st.session_state.question_index]
    correct_option = current_q['dogru_cevap']
    
    st.session_state.selected_option = option
    st.session_state.answer_submitted = True
    
    if option == correct_option:
        st.session_state.score += 1
        st.session_state.is_correct = True
    else:
        st.session_state.is_correct = False
    # Rerun yapmıyoruz, akış aşağıda devam edecek

def next_question():
    """Sonraki soruya geçer."""
    st.session_state.answer_submitted = False
    st.session_state.selected_option = None
    
    if st.session_state.question_index < len(st.session_state.quiz_data) - 1:
        st.session_state.question_index += 1
        st.rerun()
    else:
        save_score()
        st.session_state.current_page = 'result'
        st.rerun()

# --- SAYFALAR ---

# 1. ANA SAYFA
def home_page():
    st.write(f"👋 **Merhaba, {st.session_state.user_name}**")
    
    if st.session_state.user_name == "Misafir":
        name = st.text_input("Yarışmak için adını gir:", placeholder="Adınız...")
        if name:
            st.session_state.user_name = name
            st.rerun()

    st.markdown(f"""
        <div class="banner">
            <h2>🏆 Psikiyatri Ligi</h2>
            <p>Bilgini test et, anında geri bildirim al!</p>
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

# 2. QUIZ SAYFASI (YENİLENDİ)
def quiz_page():
    # Veri kontrolü
    if not st.session_state.quiz_data:
        st.warning("Veri yüklenemedi. Ana sayfaya dönülüyor.")
        time.sleep(1)
        st.session_state.current_page = 'home'
        st.rerun()

    # Üst Bilgi
    total_q = len(st.session_state.quiz_data)
    current_idx = st.session_state.question_index
    progress = (current_idx + 1) / total_q
    
    c1, c2 = st.columns([1, 4])
    with c1:
        if st.button("🏠", help="Ana Menü"):
            st.session_state.current_page = 'home'
            st.rerun()
    with c2:
        st.progress(progress)
        st.caption(f"Soru {current_idx + 1} / {total_q} | Puan: {st.session_state.score}")

    # Soru Verisi
    q_data = st.session_state.quiz_data[current_idx]

    # Soru Kutusu
    st.markdown(f"""
        <div class="question-card">
            {q_data['soru']}
        </div>
    """, unsafe_allow_html=True)

    # --- DURUM 1: HENÜZ CEVAP VERİLMEDİ ---
    if not st.session_state.answer_submitted:
        # Seçenekleri Göster
        for idx, option in enumerate(q_data['secenekler']):
            # Her butona benzersiz key veriyoruz
            btn_key = f"q{current_idx}_opt{idx}"
            if st.button(option, key=btn_key, use_container_width=True):
                submit_answer(option)
                st.rerun() # Cevap verildi, sayfayı yenile ve Durum 2'ye geç

    # --- DURUM 2: CEVAP VERİLDİ (GERİ BİLDİRİM EKRANI) ---
    else:
        # Sonucu Göster
        if st.session_state.is_correct:
            st.success("✅ **DOĞRU!**")
        else:
            st.error(f"❌ **YANLIŞ!**")
            st.write(f"👉 **Doğru Cevap:** {q_data['dogru_cevap']}")
        
        # Açıklama Kutusu
        with st.expander("ℹ️ Açıklamayı Göster", expanded=True):
            st.info(q_data.get('aciklama', 'Açıklama mevcut değil.'))

        # Sonraki Soru Butonu
        btn_label = "Sonraki Soru ➡️" if current_idx < total_q - 1 else "Sonuçları Gör 🏁"
        if st.button(btn_label, type="primary", use_container_width=True):
            next_question()

# 3. SONUÇ SAYFASI
def result_page():
    st.markdown("<br>", unsafe_allow_html=True)
    total_q = len(st.session_state.quiz_data)
    score = st.session_state.score
    
    st.markdown(f"""
        <div class="result-box">
            <div style="font-size: 60px;">🎉</div>
            <h2 style="color: {primary_color};">Sınav Bitti!</h2>
            <p style="font-size: 18px;">Sayın <b>{st.session_state.user_name}</b>,</p>
            <hr>
            <div style="font-size: 16px; color: #555;">Toplam Skorun</div>
            <h1 style="color: {secondary_color}; font-size: 50px; margin: 0;">
                {score} / {total_q}
            </h1>
        </div>
    """, unsafe_allow_html=True)
    
    st.write("")
    c1, c2 = st.columns(2)
    with c1:
        if st.button("🏠 Ana Sayfa", use_container_width=True):
            st.session_state.current_page = 'home'
            st.rerun()
    with c2:
        if st.button("🏆 Liderlik Tablosu", type="primary", use_container_width=True):
            st.session_state.current_page = 'leaderboard'
            st.rerun()

# 4. LİDERLİK TABLOSU
def leaderboard_page():
    st.markdown(f"<h3 style='text-align:center; color:{primary_color};'>🏆 Liderlik Tablosu</h3>", unsafe_allow_html=True)
    
    df = st.session_state.leaderboard.sort_values(by=['Skor', 'Tarih'], ascending=[False, True]).reset_index(drop=True)
    df.index += 1
    
    st.dataframe(
        df,
        use_container_width=True,
        column_config={
            "Skor": st.column_config.ProgressColumn(
                "Skor", format="%d", min_value=0, max_value=10
            )
        }
    )
    
    if st.button("⬅ Geri Dön", use_container_width=True):
        st.session_state.current_page = 'home'
        st.rerun()

# --- YÖNLENDİRİCİ ---
if st.session_state.current_page == 'home':
    home_page()
elif st.session_state.current_page == 'quiz':
    quiz_page()
elif st.session_state.current_page == 'result':
    result_page()
elif st.session_state.current_page == 'leaderboard':
    leaderboard_page()
