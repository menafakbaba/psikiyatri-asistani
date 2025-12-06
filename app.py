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

# --- FONKSİYONLAR ---
@st.cache_data(show_spinner=False)
def notlari_yukle():
    """GitHub'daki metin dosyasını okur."""
    if not os.path.exists(DOSYA_ADI):
        return None
    try:
        with open(DOSYA_ADI, "r", encoding="utf-8") as f:
            return f.read()
    except Exception as e:
        return None

def gemini_cevapla(soru, baglam, tur):
    # Denenecek modeller listesi (En hızlıdan en güçlüye)
    model_listesi = [
        'gemini-1.5-flash',
        'gemini-1.5-pro',
        'gemini-1.0-pro',
        'gemini-pro'
    ]
    
    son_hata = ""

    # Prompt Hazırlığı
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

    # Modelleri sırayla dene
    for model_ismi in model_listesi:
        try:
            model = genai.GenerativeModel(model_ismi)
            response = model.generate_content(prompt)
            return response.text # Başarılı olursa cevabı döndür ve çık
        except Exception as e:
            son_hata = str(e)
            continue # Hata verirse bir sonraki modeli dene
            
    return f"⚠️ Üzgünüm, tüm modeller meşgul veya erişilemez durumda. Hata detayı: {son_hata}"

# --- ARAYÜZ ---
st.title("🧠 Psikiyatri Kıdem Sınavı Platformu")
st.caption("Sürüm: v2.0 (Auto-Model-Switch)")
st.markdown("---")

# Notları Yükleme Durumu
with st.spinner("Bilgi Bankası Yükleniyor..."):
    notlar = notlari_yukle()

if not notlar:
    st.error(f"⚠️ '{DOSYA_ADI}' dosyası bulunamadı! Lütfen GitHub'a bu isimle yüklediğinden emin ol.")
    st.stop()
else:
    st.success(f"✅ Bilgi Bankası Hazır! ({len(notlar)} karakter)")

# Sekmeler
tab1, tab2 = st.tabs(["💬 Soru & Cevap", "📝 Test Oluştur"])

with tab1:
    st.subheader("Hocaya Danış")
    soru = st.text_area("Aklına takılanı sor:", height=100, placeholder="Örn: Serotonin sendromu belirtileri nelerdir?")
    if st.button("Cevapla", type="primary"):
        if soru:
            with st.spinner("Dr. Gemini notları tarıyor..."):
                cevap = gemini_cevapla(soru, notlar, "soru")
                st.markdown(cevap)
        else:
            st.warning("Lütfen bir soru yazın.")

with tab2:
    st.subheader("Simülasyon Sınavı")
    konu = st.text_input("Hangi konuda test istiyorsun?", placeholder="Örn: Antipsikotikler, Kişilik Bozuklukları, Tüm Konular")
    if st.button("Testi Oluştur", type="primary"):
        if konu:
            with st.spinner("Sınav kağıdı hazırlanıyor..."):
                test = gemini_cevapla(konu, notlar, "test")
                st.markdown(test)
        else:
            st.warning("Lütfen bir konu başlığı girin.")
