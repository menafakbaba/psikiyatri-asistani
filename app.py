import streamlit as st
import google.generativeai as genai
import os
import json

# --- SAYFA AYARLARI VE CSS ---
st.set_page_config(
    page_title="Psikiyatri Asistanı",
    page_icon="🧠",
    layout="centered",
    initial_sidebar_state="collapsed"
)

# --- ÖZEL CSS TASARIMI (MODERN UI/UX) ---
st.markdown("""
<style>
    /* Ana Arka Plan ve Yazı Tipi */
    .stApp {
        background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
        font-family: 'Helvetica Neue', sans-serif;
    }
    
    /* Başlık Stili */
    h1 {
        color: #2c3e50;
        font-weight: 700;
        text-align: center;
        padding-bottom: 20px;
    }
    
    /* Kart Tasarımı (Sorular ve Cevaplar İçin) */
    .css-1r6slb0, .stMarkdown {
        background-color: white;
        border-radius: 15px;
        padding: 20px;
        box-shadow: 0 4px 15px rgba(0,0,0,0.05);
        margin-bottom: 20px;
    }

    /* Buton Stili */
    .stButton > button {
        width: 100%;
        background-color: #111;
        color: white;
        border-radius: 12px;
        padding: 15px 20px;
        font-weight: 600;
        border: none;
        transition: all 0.3s ease;
    }
    .stButton > button:hover {
        background-color: #333;
        transform: translateY(-2px);
        box-shadow: 0 5px 15px rgba(0,0,0,0.2);
    }

    /* Text Area ve Input Stili */
    .stTextArea textarea, .stTextInput input {
        border-radius: 12px;
        border: 1px solid #e0e0e0;
        padding: 15px;
        background-color: #f8f9fa;
    }
    
    /* Sekme (Tab) Tasarımı */
    .stTabs [data-baseweb="tab-list"] {
        gap: 10px;
        background-color: transparent;
    }
    .stTabs [data-baseweb="tab"] {
        background-color: white;
        border-radius: 20px;
        padding: 10px 20px;
        box-shadow: 0 2px 5px rgba(0,0,0,0.05);
        border: none;
    }
    .stTabs [aria-selected="true"] {
        background-color: #6c5ce7 !important;
        color: white !important;
    }

    /* Başarı Mesajı */
    .stSuccess {
        background-color: #d4edda;
        color: #155724;
        border-radius: 10px;
    }
    
    /* Uyarı Mesajı */
    .stError {
        background-color: #f8d7da;
        color: #721c24;
        border-radius: 10px;
    }
</style>
""", unsafe_allow_html=True)

# --- API ANAHTARI KURULUMU ---
try:
    api_key = st.secrets["GEMINI_API_KEY"]
    genai.configure(api_key=api_key)
except Exception as e:
    st.error("⚠️ API Anahtarı hatası! Lütfen Streamlit Secrets ayarlarını kontrol et.")
    st.stop()

# --- SABİTLER ---
DOSYA_ADI = "bilgi_bankasi.txt"

# --- FONKSİYONLAR ---
@st.cache_resource
def get_working_model():
    try:
        # Öncelik sırası: En hızlı ve en yeni modeller
        preferred_models = [
            'models/gemini-1.5-flash',
            'models/gemini-1.5-pro',
            'models/gemini-1.0-pro',
            'models/gemini-pro'
        ]
        for m in genai.list_models():
            if 'generateContent' in m.supported_generation_methods:
                if m.name in preferred_models:
                    return m.name
        return 'models/gemini-pro' # Fallback
    except:
        return 'models/gemini-pro'

@st.cache_data(show_spinner=False)
def notlari_yukle():
    if not os.path.exists(DOSYA_ADI):
        return None
    try:
        with open(DOSYA_ADI, "r", encoding="utf-8") as f:
            return f.read()
    except:
        return None

def gemini_cevapla(soru, baglam, tur, model_ismi):
    model = genai.GenerativeModel(model_ismi)
    
    if tur == "soru":
        prompt = f"""
        Sen uzman bir Psikiyatri hocasısın. Aşağıdaki DERS NOTLARINI referans alarak,
        samimi, net ve eğitici bir dille cevap ver.
        
        DERS NOTLARI:
        {baglam}
        
        SORU:
        {soru}
        """
    else: # test modu - JSON formatında çıktı isteyelim ki güzel parse edelim
        prompt = f"""
        Aşağıdaki DERS NOTLARINDAN yola çıkarak '{soru}' konusuyla ilgili
        ZORLUK DERECESİ YÜKSEK 1 adet çoktan seçmeli soru hazırla.
        
        Çıktıyı SADECE aşağıdaki JSON formatında ver (başka yazı yazma):
        {{
            "soru": "Soru metni buraya",
            "siklar": ["A) Şık 1", "B) Şık 2", "C) Şık 3", "D) Şık 4", "E) Şık 5"],
            "dogru_cevap": "Doğru şıkkın tam metni (örn: A) Şık 1)",
            "aciklama": "Neden doğru olduğuna dair kısa açıklama"
        }}
        
        DERS NOTLARI:
        {baglam}
        """
    
    try:
        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        return "Hata"

# --- ARAYÜZ YAPISI ---

# Başlık Alanı
col1, col2, col3 = st.columns([1,2,1])
with col2:
    st.title("🧠 Dr. Gemini")
    st.markdown("<div style='text-align: center; color: gray; margin-top: -20px; margin-bottom: 20px;'>Psikiyatri Asistanı</div>", unsafe_allow_html=True)

# Model ve Veri Kontrolü
working_model = get_working_model()
notlar = notlari_yukle()

if not notlar:
    st.error("⚠️ Veri bankası bulunamadı.")
    st.stop()

# Sekmeler
tab_soru, tab_test = st.tabs(["💬 Asistana Sor", "🎯 Soru Çöz"])

# --- TAB 1: SORU SORMA ---
with tab_soru:
    st.markdown("### 💡 Aklına takılanı sor")
    soru_input = st.text_area("", placeholder="Örn: Antipsikotiklerde metabolik yan etkiler nelerdir?", height=100)
    
    if st.button("Yanıtla", key="btn_soru"):
        if soru_input:
            with st.spinner("Notlar taranıyor..."):
                cevap = gemini_cevapla(soru_input, notlar, "soru", working_model)
                st.markdown(f"""
                <div style="background-color: #fff; padding: 20px; border-radius: 15px; border-left: 5px solid #6c5ce7; box-shadow: 0 2px 10px rgba(0,0,0,0.05);">
                    {cevap}
                </div>
                """, unsafe_allow_html=True)
        else:
            st.toast("Lütfen bir soru yazın.")

# --- TAB 2: TEST ÇÖZME (MODERN UI) ---
with tab_test:
    st.markdown("### 🎯 Kendini Test Et")
    
    # Session state başlatma
    if 'quiz_data' not in st.session_state:
        st.session_state['quiz_data'] = None
    if 'quiz_answered' not in st.session_state:
        st.session_state['quiz_answered'] = False

    konu_input = st.text_input("", placeholder="Hangi konuda soru istersin? (Örn: Şizofreni)")
    
    if st.button("Soru Getir", key="btn_test"):
        if konu_input:
            with st.spinner("Soru hazırlanıyor..."):
                try:
                    json_str = gemini_cevapla(konu_input, notlar, "test", working_model)
                    # Temizlik (JSON dışı karakterleri temizle)
                    json_str = json_str.replace("```json", "").replace("```", "").strip()
                    st.session_state['quiz_data'] = json.loads(json_str)
                    st.session_state['quiz_answered'] = False
                    st.rerun()
                except:
                    st.error("Soru oluşturulurken bir hata oldu. Tekrar dene.")
        else:
            st.toast("Lütfen bir konu girin.")

    # Soru Gösterimi
    if st.session_state['quiz_data']:
        data = st.session_state['quiz_data']
        
        st.markdown(f"""
        <div style="background-color: white; padding: 20px; border-radius: 15px; margin-top: 20px; box-shadow: 0 4px 15px rgba(0,0,0,0.05);">
            <h3 style="color: #2d3436; font-size: 18px; margin-bottom: 15px;">{data['soru']}</h3>
        </div>
        """, unsafe_allow_html=True)

        # Şıklar (Radio button yerine özel butonlar gibi gösterelim)
        secim = st.radio("", data['siklar'], index=None, key="secilen_sik")
        
        if secim:
            if st.button("Cevabı Kontrol Et"):
                st.session_state['quiz_answered'] = True
                
        if st.session_state['quiz_answered']:
            dogru_mu = (secim == data['dogru_cevap'])
            
            if dogru_mu:
                st.success("🎉 Doğru Cevap!")
            else:
                st.error(f"Yanlış. Doğru cevap: {data['dogru_cevap']}")
            
            st.markdown(f"""
            <div style="background-color: #e1f5fe; padding: 15px; border-radius: 10px; margin-top: 10px; color: #0277bd;">
                <strong>💡 Açıklama:</strong> {data['aciklama']}
            </div>
            """, unsafe_allow_html=True)
            
            if st.button("Yeni Soru"):
                st.session_state['quiz_data'] = None
                st.session_state['quiz_answered'] = False
                st.rerun()
