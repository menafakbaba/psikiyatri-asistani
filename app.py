import streamlit as st
import google.generativeai as genai
from PyPDF2 import PdfReader

# Sayfa Ayarları
st.set_page_config(
    page_title="Psikiyatri Asistanlık Sınav Botu",
    page_icon="🧠",
    layout="wide"
)

# --- 1. API ANAHTARI KURULUMU ---
# Streamlit'in "Secrets" özelliğini kullanacağız, böylece anahtarın kod içinde görünmeyecek.
try:
    api_key = st.secrets["GEMINI_API_KEY"]
    genai.configure(api_key=api_key)
except Exception as e:
    st.error("⚠️ API Anahtarı bulunamadı! Lütfen Streamlit ayarlarından 'GEMINI_API_KEY' ekleyin.")
    st.stop()

# --- 2. FONKSİYONLAR ---
@st.cache_data # Bu dekoratör, PDF bir kez okunduğunda tekrar tekrar okumasın diye önbellekler.
def get_pdf_text(pdf_docs):
    text = ""
    for pdf in pdf_docs:
        pdf_reader = PdfReader(pdf)
        for page in pdf_reader.pages:
            text += page.extract_text()
    return text

def get_gemini_response(input_text, pdf_text, prompt_type):
    # Model Seçimi (Hız ve maliyet için Flash ideal)
    model = genai.GenerativeModel('gemini-1.5-flash')
    
    if prompt_type == "Soru Sor":
        base_prompt = f"""
        Sen uzman bir Psikiyatri hocasısın. Aşağıdaki notları referans alarak kullanıcının sorusunu cevapla.
        Cevabın net, akademik ve notlara dayalı olsun.
        
        NOTLAR:
        {pdf_text}
        
        KULLANICI SORUSU:
        {input_text}
        """
    elif prompt_type == "Test Hazırla":
        base_prompt = f"""
        Sen bir sınav hazırlama uzmanısın. Aşağıdaki notlardan yola çıkarak, kullanıcının istediği konuda
        ZORLU, ÇELDİRİCİLİ ve TUS/Kıdem sınavı formatında 5 adet çoktan seçmeli soru hazırla.
        Her sorunun altına doğru cevabı ve nedenini açıkla.
        
        NOTLAR:
        {pdf_text}
        
        İSTENEN KONU/DETAY:
        {input_text}
        """
    
    response = model.generate_content(base_prompt)
    return response.text

# --- 3. ARAYÜZ (UI) TASARIMI ---
st.title("🧠 Psikiyatri Kıdem Sınavı Hazırlık Platformu")
st.markdown("---")

# Yan Menü (Sidebar)
with st.sidebar:
    st.header("📂 Doküman Yükleme")
    st.info("Not: Arkadaşlarınla çalışmak için PDF'leri bir kere yüklemen yeterli.")
    pdf_docs = st.file_uploader("Ders Notları & Çıkmış Sorular (PDF)", accept_multiple_files=True)
    
    if st.button("Notları İşle ve Yükle"):
        with st.spinner("PDF'ler analiz ediliyor..."):
            if pdf_docs:
                raw_text = get_pdf_text(pdf_docs)
                st.session_state['pdf_text'] = raw_text # Metni oturuma kaydet
                st.success(f"✅ Başarılı! Toplam {len(raw_text)} karakter işlendi.")
            else:
                st.warning("Lütfen önce PDF dosyası seçin.")

    st.markdown("---")
    st.write("🔧 **Mod**: Dr. Gemini Asistan")

# Ana Ekran
if 'pdf_text' not in st.session_state:
    st.info("👈 Lütfen önce sol menüden ders notlarını (PDF) yükle ve 'İşle' butonuna bas.")
else:
    # Sekmeler
    tab1, tab2 = st.tabs(["💬 Soru & Cevap", "📝 Test Oluştur"])
    
    with tab1:
        st.subheader("Notlara Danış")
        user_question = st.text_area("Aklına takılan bir konu veya terim sor:", height=100, placeholder="Örn: Deliryum tremens tedavisinde en kritik adım nedir?")
        if st.button("Cevapla"):
            if user_question:
                with st.spinner("Dr. Gemini düşünüyor..."):
                    answer = get_gemini_response(user_question, st.session_state['pdf_text'], "Soru Sor")
                    st.markdown(answer)
            else:
                st.warning("Lütfen bir soru yazın.")

    with tab2:
        st.subheader("Simülasyon Sınavı")
        topic = st.text_input("Hangi konuda test istiyorsun?", placeholder="Örn: Antipsikotikler, Kişilik Bozuklukları, Tüm Konular")
        if st.button("Testi Oluştur"):
            if topic:
                with st.spinner("Sorular hazırlanıyor..."):
                    quiz = get_gemini_response(topic, st.session_state['pdf_text'], "Test Hazırla")
                    st.markdown(quiz)
            else:
                st.warning("Lütfen bir konu başlığı girin.")
