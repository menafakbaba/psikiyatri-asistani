import os
import json
import google.generativeai as genai
import streamlit as st
from typing import Optional, Dict, Any

# --- CONFIGURATION ---
DATA_FILE = "bilgi_bankasi.txt"

def configure_genai():
    """Configures the Gemini API from Streamlit secrets."""
    try:
        api_key = st.secrets["GEMINI_API_KEY"]
        genai.configure(api_key=api_key)
        return True
    except Exception as e:
        st.error(f"⚠️ API Anahtarı hatası! Lütfen .streamlit/secrets.toml dosyasını kontrol edin. Hata: {e}")
        return False

@st.cache_resource
def get_model_name() -> str:
    """Selects the best available Gemini model."""
    preferred_models = [
        'models/gemini-1.5-flash',
        'models/gemini-1.5-pro',
        'models/gemini-1.0-pro',
        'models/gemini-pro'
    ]
    try:
        available_models = [m.name for m in genai.list_models() if 'generateContent' in m.supported_generation_methods]
        for model in preferred_models:
            if model in available_models:
                return model
        return 'models/gemini-pro' # Fallback
    except Exception:
        return 'models/gemini-pro'

@st.cache_data(show_spinner=False)
def load_knowledge_base() -> Optional[str]:
    """Loads the knowledge base text file."""
    if not os.path.exists(DATA_FILE):
        return None
    try:
        with open(DATA_FILE, "r", encoding="utf-8") as f:
            return f.read()
    except Exception as e:
        st.error(f"Dosya okuma hatası: {e}")
        return None

def get_gemini_response(prompt: str, model_name: str) -> Optional[str]:
    """Generates a response from Gemini."""
    try:
        model = genai.GenerativeModel(model_name)
        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        st.error(f"Gemini hatası: {e}")
        return None

def parse_quiz_json(json_str: str) -> Optional[Dict[str, Any]]:
    """Parses the JSON response from Gemini for the quiz."""
    try:
        # Clean up markdown code blocks if present
        cleaned_str = json_str.replace("```json", "").replace("```", "").strip()
        return json.loads(cleaned_str)
    except json.JSONDecodeError:
        return None
