import streamlit as st
import google.generativeai as genai
import os

# --- SAYFA AYARLARI ---
st.set_page_config(
    page_title="Psikiyatri Asistanlık Sınav Botu",
    page_icon="🧠",
    layout="wide"
)

# --- API ANAHTARI KURULUMU ---
try:
    api_key = st.secrets["GEMINI_API_KEY"]
    genai.configure(api_key=api_key)
except Exception as e:
    st.error("⚠️ API Anahtarı hatası! Lütfen Streamlit Secrets ayarlarını kontrol et.")
    st.stop()

# --- SABİTLER ---
DOSYA_ADI = "bilgi_bankasi.txt"

# --- AKILLI MODEL SEÇİCİ (TEŞHİS MODU) ---
@st.cache_resource
def get_working_model():
    """API anahtarının erişebildiği modelleri bulur ve en iyisini seçer."""
    try:
        available_models = []
        for m in genai.list_models():
            if 'generateContent' in m.supported_generation_methods:
                available_models.append(m.name)
        
        # Tercih sıramız (En iyiden en eskiye)
        preferred_order = [
            'models/gemini-1.5-flash',
            'models/gemini-1.5-pro',
            'models/gemini-1.0-pro',
            'models/gemini-pro'
        ]
        
        # Listemizde olan ve erişebildiğimiz ilk modeli seç
        for model_name in preferred_order:
            if model_name in available_models:
                return model_name
        
        # Hiçbiri yoksa listeden ilk bulduğunu al
        if available_models:
            return available_models[0]
            
        return None
    except Exception as e:
        return None

# --- FONKSİYONLAR ---
@st.cache_data(show_spinner=False)
def notlari_yukle():
    if not os.path.exists(DOSYA_ADI):
        return None
    try:
        with open(DOSYA_ADI, "r", encoding="utf-8") as f:
            return f.read()
    except Exception as e:
        return None

def gemini_cevapla(soru, baglam, tur, model_ismi):
    model = genai.GenerativeModel(model_ismi)
    
    if tur == "soru":
        prompt = f"""
        Sen uzman bir Psikiyatri hocasısın. Aşağıdaki DERS NOTLARINI tek gerçek kaynağın olarak kullan.
        Kullanıcının sorusunu sadece bu notlara dayanarak, akademik, net ve açıklayıcı cevapla.
        
        DERS NOTLARI:
        {baglam}
        
        SORU:
        {soru}
        """
    else: # test
        prompt = f"""
        Sen TUS ve Asistanlık sınavı hazırlayan uzman bir hocasın.
        Aşağıdaki DERS NOTLARINDAN yola çıkarak, '{soru}' konusuyla ilgili
        5 adet ÇOKTAN SEÇMELİ (A,B,C,D,E şıklı), ZORLU ve ÇELDİRİCİLİ soru hazırla.
        
        Format şöyle olsun:
        **Soru X:** ...
        A) ...
        B) ...
        
        **Doğru Cevap:** ...
        **Açıklama:** ... (Neden doğru olduğunu notlara atıf yaparak kısaca açıkla)
        
        DERS NOTLARI:
        {baglam}
        """
    
    response = model.generate_content(prompt)
    return response.text

# --- ARAYÜZ ---
st.title("🧠 Psikiyatri Kıdem Sınavı Platformu")

# Modeli Belirle
working_model = get_working_model()

if not working_model:
    st.error("⚠️ HATA: API anahtarınız hiçbir modele erişemiyor. Lütfen Google AI Studio'dan yeni bir anahtar alıp deneyin.")
    st.stop()
else:
    st.caption(f"✅ Aktif Model: {working_model}")

st.markdown("---")

# Notları Yükleme Durumu
with st.spinner("Bilgi Bankası Yükleniyor..."):
    notlar = notlari_yukle()

if not notlar:
    st.error(f"⚠️ '{DOSYA_ADI}' dosyası bulunamadı! GitHub'a yüklediğinden emin ol.")
    st.stop()
else:
    st.success(f"📚 Bilgi Bankası Hazır! ({len(notlar)} karakter)")

# Sekmeler
tab1, tab2 = st.tabs(["💬 Soru & Cevap", "📝 Test Oluştur"])

with tab1:
    st.subheader("Hocaya Danış")
    soru = st.text_area("Aklına takılanı sor:", height=100, placeholder="Örn: Serotonin sendromu belirtileri nelerdir?")
    if st.button("Cevapla", type="primary"):
        if soru:
            with st.spinner("Dr. Gemini notları tarıyor..."):
                try:
                    cevap = gemini_cevapla(soru, notlar, "soru", working_model)
                    st.markdown(cevap)
                except Exception as e:
                    st.error(f"Bir hata oluştu: {e}")
        else:
            st.warning("Lütfen bir soru yazın.")

with tab2:
    st.subheader("Simülasyon Sınavı")
    konu = st.text_input("Hangi konuda test istiyorsun?", placeholder="Örn: Antipsikotikler, Kişilik Bozuklukları, Tüm Konular")
    if st.button("Testi Oluştur", type="primary"):
        if konu:
            with st.spinner("Sınav kağıdı hazırlanıyor..."):
                try:
                    test = gemini_cevapla(konu, notlar, "test", working_model)
                    st.markdown(test)
                except Exception as e:
                    st.error(f"Bir hata oluştu: {e}")
        else:
            st.warning("Lütfen bir konu başlığı girin.")
