{\rtf1\ansi\ansicpg1252\cocoartf2867
\cocoatextscaling0\cocoaplatform0{\fonttbl\f0\fswiss\fcharset0 Helvetica;}
{\colortbl;\red255\green255\blue255;}
{\*\expandedcolortbl;;}
\paperw11900\paperh16840\margl1440\margr1440\vieww25060\viewh12400\viewkind0
\pard\tx720\tx1440\tx2160\tx2880\tx3600\tx4320\tx5040\tx5760\tx6480\tx7200\tx7920\tx8640\pardirnatural\partightenfactor0

\f0\fs24 \cf0 import streamlit as st\
import google.generativeai as genai\
from PyPDF2 import PdfReader\
\
# Sayfa Ayarlar\uc0\u305 \
st.set_page_config(\
    page_title="Psikiyatri Asistanl\uc0\u305 k S\u305 nav Botu",\
    page_icon="\uc0\u55358 \u56800 ",\
    layout="wide"\
)\
\
# --- 1. API ANAHTARI KURULUMU ---\
# Streamlit'in "Secrets" \'f6zelli\uc0\u287 ini kullanaca\u287 \u305 z, b\'f6ylece anahtar\u305 n kod i\'e7inde g\'f6r\'fcnmeyecek.\
try:\
    api_key = st.secrets["GEMINI_API_KEY"]\
    genai.configure(api_key=api_key)\
except Exception as e:\
    st.error("\uc0\u9888 \u65039  API Anahtar\u305  bulunamad\u305 ! L\'fctfen Streamlit ayarlar\u305 ndan 'GEMINI_API_KEY' ekleyin.")\
    st.stop()\
\
# --- 2. FONKS\uc0\u304 YONLAR ---\
@st.cache_data # Bu dekorat\'f6r, PDF bir kez okundu\uc0\u287 unda tekrar tekrar okumas\u305 n diye \'f6nbellekler.\
def get_pdf_text(pdf_docs):\
    text = ""\
    for pdf in pdf_docs:\
        pdf_reader = PdfReader(pdf)\
        for page in pdf_reader.pages:\
            text += page.extract_text()\
    return text\
\
def get_gemini_response(input_text, pdf_text, prompt_type):\
    # Model Se\'e7imi (H\uc0\u305 z ve maliyet i\'e7in Flash ideal)\
    model = genai.GenerativeModel('gemini-1.5-flash')\
    \
    if prompt_type == "Soru Sor":\
        base_prompt = f"""\
        Sen uzman bir Psikiyatri hocas\uc0\u305 s\u305 n. A\u351 a\u287 \u305 daki notlar\u305  referans alarak kullan\u305 c\u305 n\u305 n sorusunu cevapla.\
        Cevab\uc0\u305 n net, akademik ve notlara dayal\u305  olsun.\
        \
        NOTLAR:\
        \{pdf_text\}\
        \
        KULLANICI SORUSU:\
        \{input_text\}\
        """\
    elif prompt_type == "Test Haz\uc0\u305 rla":\
        base_prompt = f"""\
        Sen bir s\uc0\u305 nav haz\u305 rlama uzman\u305 s\u305 n. A\u351 a\u287 \u305 daki notlardan yola \'e7\u305 karak, kullan\u305 c\u305 n\u305 n istedi\u287 i konuda\
        ZORLU, \'c7ELD\uc0\u304 R\u304 C\u304 L\u304  ve TUS/K\u305 dem s\u305 nav\u305  format\u305 nda 5 adet \'e7oktan se\'e7meli soru haz\u305 rla.\
        Her sorunun alt\uc0\u305 na do\u287 ru cevab\u305  ve nedenini a\'e7\u305 kla.\
        \
        NOTLAR:\
        \{pdf_text\}\
        \
        \uc0\u304 STENEN KONU/DETAY:\
        \{input_text\}\
        """\
    \
    response = model.generate_content(base_prompt)\
    return response.text\
\
# --- 3. ARAY\'dcZ (UI) TASARIMI ---\
st.title("\uc0\u55358 \u56800  Psikiyatri K\u305 dem S\u305 nav\u305  Haz\u305 rl\u305 k Platformu")\
st.markdown("---")\
\
# Yan Men\'fc (Sidebar)\
with st.sidebar:\
    st.header("\uc0\u55357 \u56514  Dok\'fcman Y\'fckleme")\
    st.info("Not: Arkada\uc0\u351 lar\u305 nla \'e7al\u305 \u351 mak i\'e7in PDF'leri bir kere y\'fcklemen yeterli.")\
    pdf_docs = st.file_uploader("Ders Notlar\uc0\u305  & \'c7\u305 km\u305 \u351  Sorular (PDF)", accept_multiple_files=True)\
    \
    if st.button("Notlar\uc0\u305  \u304 \u351 le ve Y\'fckle"):\
        with st.spinner("PDF'ler analiz ediliyor..."):\
            if pdf_docs:\
                raw_text = get_pdf_text(pdf_docs)\
                st.session_state['pdf_text'] = raw_text # Metni oturuma kaydet\
                st.success(f"\uc0\u9989  Ba\u351 ar\u305 l\u305 ! Toplam \{len(raw_text)\} karakter i\u351 lendi.")\
            else:\
                st.warning("L\'fctfen \'f6nce PDF dosyas\uc0\u305  se\'e7in.")\
\
    st.markdown("---")\
    st.write("\uc0\u55357 \u56615  **Mod**: Dr. Gemini Asistan")\
\
# Ana Ekran\
if 'pdf_text' not in st.session_state:\
    st.info("\uc0\u55357 \u56392  L\'fctfen \'f6nce sol men\'fcden ders notlar\u305 n\u305  (PDF) y\'fckle ve '\u304 \u351 le' butonuna bas.")\
else:\
    # Sekmeler\
    tab1, tab2 = st.tabs(["\uc0\u55357 \u56492  Soru & Cevap", "\u55357 \u56541  Test Olu\u351 tur"])\
    \
    with tab1:\
        st.subheader("Notlara Dan\uc0\u305 \u351 ")\
        user_question = st.text_area("Akl\uc0\u305 na tak\u305 lan bir konu veya terim sor:", height=100, placeholder="\'d6rn: Deliryum tremens tedavisinde en kritik ad\u305 m nedir?")\
        if st.button("Cevapla"):\
            if user_question:\
                with st.spinner("Dr. Gemini d\'fc\uc0\u351 \'fcn\'fcyor..."):\
                    answer = get_gemini_response(user_question, st.session_state['pdf_text'], "Soru Sor")\
                    st.markdown(answer)\
            else:\
                st.warning("L\'fctfen bir soru yaz\uc0\u305 n.")\
\
    with tab2:\
        st.subheader("Sim\'fclasyon S\uc0\u305 nav\u305 ")\
        topic = st.text_input("Hangi konuda test istiyorsun?", placeholder="\'d6rn: Antipsikotikler, Ki\uc0\u351 ilik Bozukluklar\u305 , T\'fcm Konular")\
        if st.button("Testi Olu\uc0\u351 tur"):\
            if topic:\
                with st.spinner("Sorular haz\uc0\u305 rlan\u305 yor..."):\
                    quiz = get_gemini_response(topic, st.session_state['pdf_text'], "Test Haz\uc0\u305 rla")\
                    st.markdown(quiz)\
            else:\
                st.warning("L\'fctfen bir konu ba\uc0\u351 l\u305 \u287 \u305  girin.")}