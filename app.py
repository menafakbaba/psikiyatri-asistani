import streamlit as st
import utils
import time

# --- PAGE CONFIG ---
st.set_page_config(
    page_title="Psikiyatri Asistanı",
    page_icon="🧠",
    layout="centered",
    initial_sidebar_state="collapsed"
)

# --- LOAD CSS ---
def load_css():
    with open("assets/style.css", "r") as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

load_css()

# --- INITIALIZATION ---
if not utils.configure_genai():
    st.stop()

model_name = utils.get_model_name()
knowledge_base = utils.load_knowledge_base()

if not knowledge_base:
    st.error("⚠️ 'bilgi_bankasi.txt' dosyası bulunamadı veya boş. Lütfen veri dosyasını ekleyin.")
    st.stop()

# --- SESSION STATE ---
if "messages" not in st.session_state:
    st.session_state.messages = []
if "quiz_data" not in st.session_state:
    st.session_state.quiz_data = None
if "quiz_answered" not in st.session_state:
    st.session_state.quiz_answered = False

# --- UI COMPONENTS ---

def render_header():
    st.title("🧠 Dr. Gemini")
    st.markdown("<p style='text-align: center; color: #636e72;'>Psikiyatri Asistan Sınavı Hazırlık</p>", unsafe_allow_html=True)

def render_chat_tab():
    st.markdown("### 💬 Asistana Sor")
    st.markdown("Notlarınızdan aklınıza takılanları sorun.")

    # Display chat history
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    # Chat input
    if prompt := st.chat_input("Soru sor... (Örn: Şizofreni belirtileri nelerdir?)"):
        # Add user message
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

        # Generate response
        with st.chat_message("assistant"):
            with st.spinner("Düşünüyor..."):
                full_prompt = f"""
                Sen uzman bir Psikiyatri hocasısın. Aşağıdaki DERS NOTLARINI referans alarak,
                samimi, net ve eğitici bir dille cevap ver. Bilgi notlarda yoksa, genel tıbbi bilgine dayanarak cevapla ama bunu belirt.
                
                DERS NOTLARI:
                {knowledge_base}
                
                SORU:
                {prompt}
                """
                response = utils.get_gemini_response(full_prompt, model_name)
                
                if response:
                    st.markdown(response)
                    st.session_state.messages.append({"role": "assistant", "content": response})
                else:
                    st.error("Bir hata oluştu, lütfen tekrar deneyin.")

def render_quiz_tab():
    st.markdown("### 🎯 Soru Çöz")
    st.markdown("Bilgilerinizi test etmek için konu bazlı sorular çözün.")

    # Topic Input
    col1, col2 = st.columns([3, 1])
    with col1:
        topic = st.text_input("Konu", placeholder="Örn: Antipsikotikler, Bipolar...", label_visibility="collapsed")
    with col2:
        generate_btn = st.button("Soru Getir", use_container_width=True)

    if generate_btn and topic:
        with st.spinner("Soru hazırlanıyor..."):
            prompt = f"""
            Aşağıdaki DERS NOTLARINDAN yola çıkarak '{topic}' konusuyla ilgili
            ZORLUK DERECESİ YÜKSEK 1 adet çoktan seçmeli soru hazırla.
            
            Çıktıyı SADECE aşağıdaki JSON formatında ver (başka yazı yazma):
            {{
                "soru": "Soru metni buraya",
                "siklar": ["A) ...", "B) ...", "C) ...", "D) ...", "E) ..."],
                "dogru_cevap": "Doğru şıkkın tam metni (örn: A) ...)",
                "aciklama": "Neden doğru olduğuna dair kısa açıklama"
            }}
            
            DERS NOTLARI:
            {knowledge_base}
            """
            response = utils.get_gemini_response(prompt, model_name)
            if response:
                quiz_data = utils.parse_quiz_json(response)
                if quiz_data:
                    st.session_state.quiz_data = quiz_data
                    st.session_state.quiz_answered = False
                    st.rerun()
                else:
                    st.error("Soru formatı hatalı geldi, lütfen tekrar deneyin.")
            else:
                st.error("Soru oluşturulamadı.")

    # Display Quiz
    if st.session_state.quiz_data:
        data = st.session_state.quiz_data
        
        st.markdown(f"""
        <div class="css-1r6slb0">
            <h4 style="margin-bottom: 1rem;">{data['soru']}</h4>
        </div>
        """, unsafe_allow_html=True)

        # Options
        # We use a radio button but style it to look cleaner if possible, 
        # or just standard streamlit radio which is mobile friendly enough.
        choice = st.radio("Cevabınız:", data['siklar'], index=None, key="quiz_choice")

        if choice:
            check_btn = st.button("Kontrol Et", type="primary")
            if check_btn:
                st.session_state.quiz_answered = True

        # Feedback
        if st.session_state.quiz_answered:
            correct_answer = data['dogru_cevap']
            is_correct = (choice == correct_answer)
            
            if is_correct:
                st.success("🎉 Doğru Cevap!")
            else:
                st.error(f"Yanlış. Doğru cevap: {correct_answer}")
            
            st.info(f"💡 **Açıklama:** {data['aciklama']}")
            
            if st.button("Yeni Soru Çöz"):
                st.session_state.quiz_data = None
                st.session_state.quiz_answered = False
                st.rerun()

# --- MAIN LAYOUT ---
render_header()

tab1, tab2 = st.tabs(["Asistan", "Test"])

with tab1:
    render_chat_tab()

with tab2:
    render_quiz_tab()
