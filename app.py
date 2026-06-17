from PyPDF2 import PdfReader
import re
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer 
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.lib.styles import ParagraphStyle
from io import BytesIO
import streamlit as st
import os
from dotenv import load_dotenv
from gemini_helper import get_ai_response
from learning_style import get_questions, calculate_learning_style
from quiz_tracker import (initialize_tracker, save_score, get_average_score,
                          get_weak_topics, get_strong_topics, get_best_topic,
                          get_worst_topic, get_all_scores)
import plotly.graph_objects as go

load_dotenv()
pdfmetrics.registerFont(
    TTFont(
        "HindiFont",
        "NotoSansDevanagari-VariableFont_wdth,wght.ttf"
    )
)
pdfmetrics.registerFont(
    TTFont(
        "NormalFont",
        "NotoSans-Regular.ttf"
    )
)

pdfmetrics.registerFont(
    TTFont(
        "BoldFont",
        "NotoSans-Bold.ttf"
    )
)

def extract_pdf_text(uploaded_file):
    text = ""

    try:
        pdf_reader = PdfReader(uploaded_file)

        for page in pdf_reader.pages:
            page_text = page.extract_text()

            if page_text:
                text += page_text + "\n"

        return text

    except Exception as e:
        return f"Error reading PDF: {str(e)}"

def create_pdf(content):
    buffer = BytesIO()

    doc = SimpleDocTemplate(buffer)

    styles = getSampleStyleSheet()
    styles.add(
    ParagraphStyle(
        name="HindiStyle",
        parent=styles["BodyText"],
        fontName="HindiFont",
        fontSize=14,
        leading=18,
    )
)
    styles.add(
    ParagraphStyle(
        name="NormalStyle",
        parent=styles["BodyText"],
        fontName="NormalFont",
        fontSize=12,
        leading=16,
    )
)
    styles.add(
    ParagraphStyle(
        name="BoldStyle",
        parent=styles["BodyText"],
        fontName="BoldFont",
        fontSize=18,
        leading=22,
        spaceBefore=10,
        spaceAfter=10,
    )
)
    story = []

    for line in content.split("\n"):

        line = line.strip()
        is_heading = bool(re.match(r"^\d+\.", line))

        if not line:
         story.append(Spacer(1, 8))
         continue

        # Convert markdown bold (**text**) to PDF bold
        line = re.sub(
            r"\*\*(.*?)\*\*",
            r"<b>\1</b>",
            line
        )

        if is_heading:
          story.append(
          Paragraph(line, styles["BoldStyle"])
    )
        else:
          story.append(
          Paragraph(line, styles["NormalStyle"])
    )
    doc.build(story)

    buffer.seek(0)

    return buffer
def get_achievements(tracker):

    achievements = []

    quizzes = tracker["total_attempted"]
    avg_score = get_average_score(tracker)

    if quizzes >= 1:
        achievements.append("🥉 Beginner Learner")

    if quizzes >= 5:
        achievements.append("🥈 Consistent Learner")

    if quizzes >= 10:
        achievements.append("🥇 Quiz Master")

    if avg_score >= 70:
        achievements.append("🎯 Smart Learner")

    if avg_score >= 85 and quizzes >= 10:
        achievements.append("👑 EduMind Champion")

    return achievements
def get_recommendations(tracker):

    recommendations = []

    weak_topics = get_weak_topics(tracker)
    strong_topics = get_strong_topics(tracker)

    if weak_topics:
        recommendations.append(
            f"📚 Revise: {', '.join(weak_topics[:3])}"
        )

    if strong_topics:
        recommendations.append(
            f"💪 Continue Advanced Learning in: {', '.join(strong_topics[:3])}"
        )

    if tracker["total_attempted"] < 5:
        recommendations.append(
            "🎯 Take more quizzes to improve learning insights."
        )

    avg_score = get_average_score(tracker)

    if avg_score < 60:
        recommendations.append(
            "⚡ Focus on revision before attempting harder topics."
        )

    elif avg_score >= 80:
        recommendations.append(
            "🚀 You're performing well. Try more advanced topics."
        )

    return recommendations
st.set_page_config(
    page_title="EduMind AI",
    page_icon="🧠",
    layout="wide",
    initial_sidebar_state="expanded"
)
if "theme" not in st.session_state:
    st.session_state.theme = "System"

theme = st.session_state.theme

if theme == "Dark":
    bg_color = "#0E1117"
    card_bg = "#1E293B"
    text_color = "#FFFFFF"
    secondary_text = "#CBD5E1"
    border_color = "#334155"

elif theme == "Light":
    bg_color = "#FFFFFF"
    card_bg = "#F8FAFC"
    text_color = "#1E293B"
    secondary_text = "#64748B"
    border_color = "#E2E8F0"

else:  # System
    bg_color = "#FFFFFF"
    card_bg = "#F8FAFC"
    text_color = "#1E293B"
    secondary_text = "#64748B"
    border_color = "#E2E8F0"

st.markdown(f"""
<style>

@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');

html, body, [class*="css"] {{
    font-family: 'Inter', sans-serif !important;
    color: {text_color};
}}

[data-testid="stAppViewContainer"] {{
    background-color: {bg_color};
    color: {text_color};
}}

[data-testid="stHeader"] {{
    background-color: {bg_color};
}}

section[data-testid="stSidebar"] {{
    background-color: {card_bg};
}}

section[data-testid="stSidebar"] label,
section[data-testid="stSidebar"] p,
section[data-testid="stSidebar"] h1,
section[data-testid="stSidebar"] h2,
section[data-testid="stSidebar"] h3,
section[data-testid="stSidebar"] h4,
section[data-testid="stSidebar"] h5,
section[data-testid="stSidebar"] h6,
section[data-testid="stSidebar"] span {{
    color: {text_color} !important;
}}
h1, h2, h3, h4, h5, h6 {{
    color: {text_color};
}}

p {{
    color: {text_color};
}}

label {{
    color: {text_color};
}}
.main .block-container {{
    padding-top: 0rem !important;
    padding-left: 1rem !important;
    padding-right: 1rem !important;
    max-width: 100% !important;
}}

.hero-container {{
    width:100%;
    max-width:100%;
    background: linear-gradient(135deg, #1E3A8A 0%, #3B82F6 50%, #06B6D4 100%);
    border-radius: 20px;
    padding: 3rem 2rem;
    text-align: center;
    margin-top: -100px !important;
    margin-bottom: 2rem;
    color: white !important;
}}

.hero-title {{
    font-size: 3.5rem;
    font-weight: 700;
    margin: 0;
    letter-spacing: -1px;
    color: white !important;
}}

.hero-subtitle {{
    font-size: 1.2rem;
    opacity: 0.9;
    margin-top: 0.5rem;
    font-weight: 300;
    color: white !important;
}}

.hero-badge {{
    display: inline-block;
    background: rgba(255,255,255,0.2);
    border: 1px solid rgba(255,255,255,0.3);
    border-radius: 50px;
    padding: 0.3rem 1rem;
    font-size: 0.85rem;
    margin-top: 1rem;
    color: white !important;
}}
.stats-bar {{
    background: {card_bg};
    border: 1px solid {border_color};
    border-radius: 12px;
    padding: 1.5rem;
    display: flex;
    justify-content: space-around;
    margin: 1.5rem 0;
}}

.stat-item {{
    text-align: center;
}}

.stat-number {{
    font-size: 2rem;
    font-weight: 700;
    color: {text_color};
}}

.stat-label {{
    font-size: 0.8rem;
    color: {secondary_text};
    font-weight: 500;
}}

.feature-card {{
    background: {card_bg};
    border: 1px solid {border_color};
    border-radius: 16px;
    padding: 1.5rem;
    text-align: center;
    box-shadow: 0 1px 3px rgba(0,0,0,0.05);
    margin-bottom: 1rem;

    height: 320px !important;
    width: 100% !important;

    display: flex;
    flex-direction: column;
    justify-content: center;
    align-items: center;
    box-sizing: border-box;
}}

.feature-icon {{
    font-size: 2.5rem;
    margin-bottom: 0.8rem;
}}

.feature-title {{
    font-size: 1rem;
    font-weight: 600;
    color: {text_color};
    margin-bottom: 0.5rem;
    min-height: 60px;
}}

.feature-desc {{
    font-size: 0.85rem;
    color: {secondary_text};
    line-height: 1.5;
    min-height: 90px;
}}

.lang-pill {{
    display: inline-block;
    background: linear-gradient(135deg, #1E3A8A, #3B82F6);
    color: white !important;
    border-radius: 50px;
    padding: 0.4rem 1.2rem;
    font-size: 0.9rem;
    font-weight: 500;
    margin: 0.3rem;
}}

.section-header {{
    font-size: 1.8rem;
    font-weight: 700;
    color: {text_color};
    margin-bottom: 1rem;
    padding-bottom: 0.5rem;
    border-bottom: 3px solid #3B82F6;
    display: inline-block;
}}

.page-title {{
    font-size: 2rem;
    font-weight: 700;
    color: {text_color};
    margin-bottom: 0.3rem;
}}

.page-subtitle {{
    font-size: 1rem;
    color: {secondary_text};
    margin-bottom: 1.5rem;
}}

.info-banner {{
    background: {card_bg};
    border: 1px solid {border_color};
    border-radius: 10px;
    padding: 0.8rem 1.2rem;
    font-size: 0.9rem;
    color: {text_color};
    margin-bottom: 1rem;
}}

.footer {{
    background: {card_bg};
    color: {secondary_text};
    text-align: center;
    padding: 1.5rem;
    border-radius: 12px;
    margin-top: 3rem;
    font-size: 0.85rem;
    border: 1px solid {border_color};
}}

hr {{
    border-color: {border_color};
}}
/* Selectbox */
.stSelectbox > div > div {{
    background-color: {card_bg} !important;
    color: {text_color} !important;
}}

/* Dropdown menu */
ul[role="listbox"] {{
    background-color: {card_bg} !important;
}}

ul[role="listbox"] li {{
    color: {text_color} !important;
    background-color: {card_bg} !important;
}}

ul[role="listbox"] li:hover {{
    background-color: #3B82F6 !important;
    color: white !important;
}}

/* Selected item */
div[data-baseweb="select"] {{
    color: {text_color} !important;
}}

div[role="listbox"] {{
    background-color: #243248 !important;
}}

div[role="option"] {{
    background-color: #243248 !important;
    color: white !important;
}}

div[role="option"]:hover {{
    background-color: #3B82F6 !important;
    color: white !important;
}}
/* Base
/* Language Selectbox */
.stSelectbox {{
    margin-top: 10px;
    margin-bottom: 15px;
}}
div[data-baseweb="select"] > div {{
    min-height: 50px !important;
    display: flex !important;
    align-items: center !important;
}}
.stSelectbox > div > div {{
    border-radius: 12px !important;
    border: 1px solid {border_color} !important;
    background-color: {card_bg} !important;
    min-height: 50px !important;
}}
/* ===== BUTTON FIX ===== */

.stButton > button {{
    background: linear-gradient(135deg, #2563EB, #3B82F6) !important;
    color: white !important;
    border: none !important;
    border-radius: 12px !important;
    font-weight: 600 !important;
    height: 3.2rem !important;
}}

.stButton > button p {{
    color: white !important;
}}

.stButton > button span {{
    color: white !important;
}}

.stButton > button:hover {{
    background: linear-gradient(135deg, #1D4ED8, #2563EB) !important;
    color: white !important;
}}

/* Form Buttons */
div[data-testid="stForm"] button {{
    color: white !important;
    font-weight: 600 !important;
}}

div[data-testid="stForm"] button span {{
    color: white !important;
}}
/* Force button text visibility */
.stButton button,
.stButton button p,
.stButton button span {{
    color: white !important;
    opacity: 1 !important;
}}

/* Form Submit Button Fix */
div[data-testid="stForm"] button {{
    background: linear-gradient(135deg, #2563EB, #3B82F6) !important;
    color: white !important;
    border-radius: 12px !important;
    font-weight: 600 !important;
}}

div[data-testid="stForm"] button * {{
    color: white !important;
    fill: white !important;
    opacity: 1 !important;
}}
/* Hover effect for form submit buttons */
div[data-testid="stForm"] button:hover {{
    background: linear-gradient(135deg, #1D4ED8, #2563EB) !important;
    color: white !important;
    transform: translateY(-1px);
    transition: all 0.2s ease;
}}
.flashcard {{
    background: {card_bg};
    border: 1px solid {border_color};
    border-radius: 16px;
    padding: 15px;
    margin-bottom: 15px;
}}
[data-testid="stChatMessage"] {{
    border-radius: 12px;
    padding: 12px;
}}
[data-testid="stChatMessage"] {{
    border-radius: 12px;
    padding: 12px;
}}
</style>
""", unsafe_allow_html=True)

# Initialize session state
if "learning_style" not in st.session_state:
    st.session_state.learning_style = None
if "quiz_tracker" not in st.session_state:
    st.session_state.quiz_tracker = initialize_tracker()
if "quiz_submitted" not in st.session_state:
    st.session_state.quiz_submitted = False
if "current_quiz" not in st.session_state:
    st.session_state.current_quiz = None
if "style_detected" not in st.session_state:
    st.session_state.style_detected = False
if "quiz_topic" not in st.session_state:
    st.session_state.quiz_topic = ""
if "parsed_questions" not in st.session_state:
    st.session_state.parsed_questions = []
if "selected_language" not in st.session_state:
    st.session_state.selected_language = "English"
if "theme" not in st.session_state:
    st.session_state.theme = "System"
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []
translations = {
    "English": {
        "workspace": "🚀 Workspace",
        "home": "🏠 Home",
        "learning": "🧬 Learning Style",
        "explainer": "📖 Topic Explainer",
        "summarizer": "📝 Summarizer",
        "pdf": "📄 PDF Learning",
        "tutor": "💬 AI Tutor",
        "quiz": "❓ Quiz",
        "flashcards": "🃏 Flashcards",
        "mindmap": "🗺️ Mind Map",
        "analytics": "📊 Analytics",
        "about": "ℹ️ About",
        "profile": "👤 Student Profile",
        "profile_msg": "👆 Take the Learning Style Quiz to personalize your experience!",
        "ls_title": "🧬 Learning Style Detection Quiz",
        "ls_subtitle": "Answer 10 quick questions to discover how your brain learns best!",
        "detect_btn": "🔍 Detect My Learning Style"
    },

    "Hindi": {
        "workspace": "🚀 कार्यक्षेत्र",
        "home": "🏠 होम",
        "learning": "🧬 सीखने की शैली",
        "explainer": "📖 विषय व्याख्या",
        "summarizer": "📝 सारांश",
        "pdf": "📄 पीडीएफ अध्ययन",
        "tutor": "💬 एआई शिक्षक",
        "quiz": "❓ प्रश्नोत्तरी",
        "flashcards": "🃏 फ्लैशकार्ड",
        "mindmap": "🗺️ माइंड मैप",
        "analytics": "📊 विश्लेषण",
        "about": "ℹ️ परिचय",
        "profile": "👤 छात्र प्रोफ़ाइल",
        "profile_msg": "👆 अपने अनुभव को व्यक्तिगत बनाने के लिए Learning Style Quiz दें!",
        "ls_title": "🧬 सीखने की शैली पहचान प्रश्नोत्तरी",
        "ls_subtitle": "यह जानने के लिए 10 प्रश्नों के उत्तर दें कि आपका मस्तिष्क सबसे अच्छा कैसे सीखता है!",
        "detect_btn": "🔍 मेरी सीखने की शैली पहचानें"
    },

    "French": {
        "workspace": "🚀 Espace de travail",
        "home": "🏠 Accueil",
        "learning": "🧬 Style d'apprentissage",
        "explainer": "📖 Explication",
        "summarizer": "📝 Résumé",
        "pdf": "📄 Apprentissage PDF",
        "tutor": "💬 Tuteur IA",
        "quiz": "❓ Quiz",
        "flashcards": "🃏 Cartes mémoire",
        "mindmap": "🗺️ Carte mentale",
        "analytics": "📊 Analyses",
        "about": "ℹ️ À propos",
        "profile": "👤 Profil étudiant",
        "profile_msg": "👆 Répondez au quiz de style d'apprentissage pour personnaliser votre expérience !",
        "ls_title": "🧬 Quiz de style d'apprentissage",
        "ls_subtitle": "Répondez à 10 questions pour découvrir comment votre cerveau apprend le mieux !",
        "detect_btn": "🔍 Détecter mon style d'apprentissage"
    },

    "German": {
        "workspace": "🚀 Arbeitsbereich",
        "home": "🏠 Startseite",
        "learning": "🧬 Lernstil",
        "explainer": "📖 Themen-Erklärung",
        "summarizer": "📝 Zusammenfassung",
        "pdf": "📄 PDF Lernen",
        "tutor": "💬 KI Tutor",
        "quiz": "❓ Quiz",
        "flashcards": "🃏 Lernkarten",
        "mindmap": "🗺️ Mindmap",
        "analytics": "📊 Analysen",
        "about": "ℹ️ Über",
        "profile": "👤 Studentenprofil",
        "profile_msg": "👆 Machen Sie das Lernstil-Quiz, um Ihre Erfahrung zu personalisieren!",
        "ls_title": "🧬 Lernstil-Erkennungsquiz",
        "ls_subtitle": "Beantworten Sie 10 Fragen, um herauszufinden, wie Ihr Gehirn am besten lernt!",
        "detect_btn": "🔍 Meinen Lernstil erkennen"
    }
}
# ── SIDEBAR ──
with st.sidebar:
    st.markdown("## ⚙️ Settings")
    theme = st.radio(
    "Theme",
    ["Light", "Dark", "System"],
    index=["Light", "Dark", "System"].index(st.session_state.theme),
    key="theme_select"
)
    if theme != st.session_state.theme:
     st.session_state.theme = theme
     st.rerun()

    st.markdown("## 🧠 EduMind AI")
    st.markdown("*Adaptive Learning Intelligence*")
    st.divider()

    language = st.selectbox(
        "🌐 Language",
        ["English", "Hindi", "French", "German"],
        index=["English", "Hindi", "French", "German"].index(
            st.session_state.selected_language),
        key="lang_select"
    )
    st.session_state.selected_language = language
    t = translations[language]

    st.divider()

    st.markdown("### 🚀 Workspace")

    page_options = {
        t["home"]: "home",
        t["learning"]: "learning",
        t["explainer"]: "explainer",
        t["summarizer"]: "summarizer",
        t["pdf"]: "pdf",
        t["tutor"]: "tutor",
        t["quiz"]: "quiz",
        t["flashcards"]: "flashcards",
        t["mindmap"]: "mindmap",
        t["analytics"]: "analytics",
        t["about"]: "about"
}

    selected_page = st.radio(
                "Navigation",
                list(page_options.keys()),
                label_visibility="collapsed"
            )

    page = page_options[selected_page]

    st.divider()

    st.markdown(f"### {t['profile']}")

    style = st.session_state.learning_style

    if style is None:
     st.info(t["profile_msg"])

    else:
        st.success(f"🧬 {style} Learner")
        st.caption(f"🌐 {language}")
        st.caption("✅ Personalized Learning Active")

    st.divider()
    st.markdown("""
    <div style='font-size:0.75rem; text-align:center; color: gray;'>
        🧠 Empowering Smarter Learning with AI<br>
        EduMind AI © 2026
    </div>
    """, unsafe_allow_html=True)
# ── HOME PAGE ──
if page == "home":
    st.markdown("""
    <style>
    .hero-container{
    margin-top:-20px !important;
}
</style>
""", unsafe_allow_html=True)
    st.markdown("""
    <div class="hero-container">
        <div class="hero-title">🧠 EduMind AI</div>
        <div class="hero-subtitle">AI-Powered Personalized Learning Platform</div>
        <div class="hero-badge">✨ Powered by LLaMA 3.3 • Adaptive Learning • Multilingual AI Education</div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("""
    <div class="stats-bar">
        <div class="stat-item">
            <div class="stat-number">9</div>
            <div class="stat-label">AI Tools</div>
        </div>
        <div class="stat-item">
            <div class="stat-number">4</div>
            <div class="stat-label">Languages</div>
        </div>
        <div class="stat-item">
            <div class="stat-number">3</div>
            <div class="stat-label">Difficulty Levels</div>
        </div>
        <div class="stat-item">
            <div class="stat-number">∞</div>
            <div class="stat-label">Topics</div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("---")
    st.markdown('<div class="section-header">✨ Features</div>', unsafe_allow_html=True)
    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown("<br>", unsafe_allow_html=True)
        
    col1, col2, col3 = st.columns(3)
    with col1:
        st.markdown("""<div class="feature-card">
            <div class="feature-icon">🧬</div>
            <div class="feature-title">Learning Style Detection</div>
            <div class="feature-desc">Detects if you are a Visual, Auditory or Read-Write learner and adapts content accordingly.</div>
        </div>""", unsafe_allow_html=True)
    with col2:
        st.markdown("""<div class="feature-card">
            <div class="feature-icon">📖</div>
            <div class="feature-title">Topic Explainer</div>
            <div class="feature-desc">Explains any topic adapted to your learning style in 4 languages with easy-to-understand examples.</div>
        </div>""", unsafe_allow_html=True)
    with col3:
        st.markdown("""<div class="feature-card">
            <div class="feature-icon">📝</div>
            <div class="feature-title">Note Summarizer</div>
            <div class="feature-desc">Paste messy notes and get clean structured summaries instantly for quick revision and learning.</div>
        </div>""", unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)
    col4, col5, col6 = st.columns(3)
    with col4:
        st.markdown("""<div class="feature-card">
            <div class="feature-icon">❓</div>
            <div class="feature-title">Quiz Generator</div>
            <div class="feature-desc">Generate interactive MCQ quizzes and track your performance with instant scoring and feedback.</div>
        </div>""", unsafe_allow_html=True)
    with col5:
        st.markdown("""<div class="feature-card">
            <div class="feature-icon">🃏</div>
            <div class="feature-title">Flashcard Generator</div>
            <div class="feature-desc">Create instant flashcards for quick and effective revision with downloadable study support.</div>
        </div>""", unsafe_allow_html=True)
    with col6:
        st.markdown("""<div class="feature-card">
            <div class="feature-icon">🗺️</div>
            <div class="feature-title">Mind Map Generator</div>
            <div class="feature-desc">Visualize any topic as a hierarchical concept mind map for better understanding and retention.</div>
        </div>""", unsafe_allow_html=True)
    st.markdown("<br>", unsafe_allow_html=True)

    col7, col8, col9 = st.columns(3)

    with col7:
        st.markdown("""<div class="feature-card">
            <div class="feature-icon">📄</div>
            <div class="feature-title">PDF Learning</div>
            <div class="feature-desc">Upload PDFs and instantly summarize, explain or generate quizzes from educational documents.</div>
        </div>""", unsafe_allow_html=True)

    with col8:
     st.markdown("""<div class="feature-card">
        <div class="feature-icon">💬</div>
        <div class="feature-title">AI Tutor</div>
        <div class="feature-desc">Ask questions naturally and learn interactively with your personal AI study assistant.</div>
    </div>""", unsafe_allow_html=True)

    with col9:
     st.markdown("""<div class="feature-card">
        <div class="feature-icon">📊</div>
        <div class="feature-title">Analytics Dashboard</div>
        <div class="feature-desc">Track quiz scores, learning progress and performance insights and study improvement trends.</div>
    </div>""", unsafe_allow_html=True)
    st.markdown("<br>", unsafe_allow_html=True)

    col_left, col10, col11, col_right = st.columns([0.5, 1, 1, 0.5])

    with col10:
     st.markdown("""<div class="feature-card">
        <div class="feature-icon">🏆</div>
        <div class="feature-title">Achievement System</div>
        <div class="feature-desc">Unlock badges, milestones and rewards as you progress through your learning journey.</div>
     </div>""", unsafe_allow_html=True)

    with col11:
     st.markdown("""<div class="feature-card">
        <div class="feature-icon">🎯</div>
        <div class="feature-title">Personalized Recommendations</div>
        <div class="feature-desc">Receive AI-powered study suggestions based on performance and learning patterns.</div>
    </div>""", unsafe_allow_html=True)
    st.markdown("---")
    st.markdown('<div class="section-header">🌐 Supported Languages</div>', unsafe_allow_html=True)
    st.markdown("""
    <br>
    <span class="lang-pill">🇬🇧 English</span>
    <span class="lang-pill">🇮🇳 Hindi</span>
    <span class="lang-pill">🇫🇷 French</span>
    <span class="lang-pill">🇩🇪 German</span>
    <br><br>
    """, unsafe_allow_html=True)

    st.markdown("---")
    st.info("👈 Start by taking the **🧬 Learning Style Quiz** from the sidebar!")
    tracker = st.session_state.quiz_tracker
    achievements = get_achievements(tracker)

    if achievements:

        st.markdown("### 🏆 Your Latest Achievement")

        st.success(achievements[-1])

# ── LEARNING STYLE QUIZ ──
elif page == "learning":
    st.markdown(f'<div class="page-title">{t["ls_title"]}</div>', unsafe_allow_html=True)
    st.markdown(f'<div class="page-subtitle">{t["ls_subtitle"]}</div>', unsafe_allow_html=True)
    st.markdown("---")

    questions = get_questions()

    with st.form("quiz_form"):
        answers = []
        for i, q in enumerate(questions):
            st.markdown(f"**{q['question']}**")
            options = [f"{k}) {v}" for k, v in q['options'].items()]
            answer = st.radio(
                f"Select answer for Q{i+1}",
                options,
                key=f"ls_q{i}",
                label_visibility="collapsed",
                index=None
            )
            answers.append(answer[0] if answer else None)
            st.markdown("")

        submitted = st.form_submit_button(t["detect_btn"],use_container_width=True)

    if submitted:
        if None in answers:
            st.warning("⚠️ Please answer all 10 questions before submitting!")
        else:
            result = calculate_learning_style(answers)

            style_map = {
                "V": "Visual",
                "A": "Auditory",
                "R": "Read-Write"
            }

            st.session_state.learning_style = style_map[result["style"]]
            st.session_state.style_detected = True

            # DEBUG
            st.write("Saved Style:", st.session_state.learning_style)
                        
            st.markdown("""
            <div id="result-section"></div>
            """, unsafe_allow_html=True)

            st.markdown("---")
            st.markdown("## 🎉 Your Learning Style Result!")
            st.components.v1.html("""
            <script>
            window.parent.document.getElementById('result-section')
            ?.scrollIntoView({behavior: 'smooth'});
            </script>
            """, height=0)
            details = result["details"]
            scores = result["scores"]

            if result["style"] == "V":
                st.success(f"## {details['name']}")
            elif result["style"] == "A":
                st.info(f"## {details['name']}")
            else:
                st.warning(f"## {details['name']}")

            st.markdown(f"**{details['description']}**")

            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("🎨 Visual", f"{scores['V']}/10")
            with col2:
                st.metric("🎧 Auditory", f"{scores['A']}/10")
            with col3:
                st.metric("📖 Read-Write", f"{scores['R']}/10")

            st.markdown("### 💡 Study Tips For You")
            for tip in details["tips"]:
                st.markdown(f"✅ {tip}")
            st.success("✅ Learning style saved!")

# ── TOPIC EXPLAINER ──
elif page == "explainer":
    st.markdown('<div class="page-title">📖 Topic Explainer</div>', unsafe_allow_html=True)
    st.markdown('<div class="page-subtitle">Enter any topic and get an AI explanation adapted to YOUR learning style!</div>', unsafe_allow_html=True)
    st.markdown("---")

    style_map = {"V": "🎨 Visual", "A": "🎧 Auditory", "R": "📖 Read-Write"}
    current_style = style_map.get(st.session_state.learning_style, "🎨 Visual")
    st.markdown(f'<div class="info-banner">🧬 Learning Style: <strong>{current_style}</strong> &nbsp;|&nbsp; 🌐 Language: <strong>{language}</strong></div>', unsafe_allow_html=True)

    topic = st.text_input("📚 Enter Topic", placeholder="e.g. Fourier Transform, Photosynthesis, Machine Learning...")
    difficulty = st.select_slider("📊 Difficulty Level", options=["School", "Undergrad", "Research"], value="Undergrad")

    if st.button("🚀 Explain This Topic", use_container_width=True):
        if topic:
            with st.spinner("🧠 Generating explanation..."):
                response = get_ai_response(topic=topic, feature="explainer",
                    learning_style=st.session_state.learning_style,
                    difficulty=difficulty, language=language)
            st.markdown("---")
            st.markdown("### 📖 Your Explanation")
            st.markdown(response)
            pdf_file = create_pdf(response)
            st.download_button("📥 Download Explanation", data=pdf_file,
                file_name=f"{topic}_explanation.pdf", mime="application/pdf", use_container_width=True)
        else:
            st.warning("⚠️ Please enter a topic first!")

# ── NOTE SUMMARIZER ──
elif page == "summarizer":
    st.markdown('<div class="page-title">📝 Note Summarizer</div>', unsafe_allow_html=True)
    st.markdown('<div class="page-subtitle">Paste your messy notes and get a clean structured summary!</div>', unsafe_allow_html=True)
    st.markdown("---")

    st.markdown(f'<div class="info-banner">🌐 Language: <strong>{language}</strong></div>', unsafe_allow_html=True)
    notes = st.text_area("📋 Paste Your Notes Here", placeholder="Paste your lecture notes here...", height=300)

    if st.button("✨ Summarize My Notes", use_container_width=True):
        if notes:
            with st.spinner("📝 Summarizing your notes..."):
                response = get_ai_response(topic=notes, feature="summarizer",
                    learning_style=st.session_state.learning_style, language=language)
            st.markdown("---")
            st.markdown("### 📋 Your Summary")
            st.markdown(response)
            pdf_file = create_pdf(response)
            st.download_button("📥 Download Summary", data=pdf_file,
                file_name="summary.pdf", mime="application/pdf", use_container_width=True)
        else:
            st.warning("⚠️ Please paste your notes first!")
# ── PDF LEARNING ──
elif page == "pdf":

    st.markdown(
        '<div class="page-title">📄 PDF Learning Assistant</div>',
        unsafe_allow_html=True
    )

    st.markdown(
        '<div class="page-subtitle">Upload a PDF and let AI help you learn smarter!</div>',
        unsafe_allow_html=True
    )

    st.markdown("---")

    uploaded_pdf = st.file_uploader(
        "📄 Upload PDF Notes",
        type=["pdf"]
    )

    action = st.selectbox(
        "Choose AI Action",
        [
            "Summarize",
            "Generate Quiz",
            "Generate Flashcards",
            "Generate Mind Map"
        ]
    )

    if uploaded_pdf:

        if st.button("🚀 Process PDF", use_container_width=True):

            pdf_text = extract_pdf_text(uploaded_pdf)

            if len(pdf_text.strip()) < 50:
                st.error("Could not extract enough text from PDF.")

            else:

                feature_map = {
                    "Summarize": "summarizer",
                    "Generate Quiz": "quiz",
                    "Generate Flashcards": "flashcard",
                    "Generate Mind Map": "mindmap"
                }

                feature = feature_map[action]

                with st.spinner("🧠 Processing PDF..."):

                    response = get_ai_response(
                        topic=pdf_text,
                        feature=feature,
                        learning_style=st.session_state.learning_style,
                        language=language
                    )

                st.markdown("---")
                st.markdown(f"### {action} Result")

                if feature == "mindmap":
                    st.code(response)
                else:
                    st.markdown(response)
                pdf_file = create_pdf(response)
                st.download_button(
                    "📥 Download Result",
                    data=pdf_file,
                    file_name=f"pdf_{feature}.pdf",
                    mime="application/pdf",
                    use_container_width=True
                )

    else:
        st.info("📄 Upload a PDF to begin.")
# ── AI TUTOR ──
elif page == "tutor":

    st.markdown(
        '<div class="page-title">💬 AI Tutor</div>',
        unsafe_allow_html=True
    )

    st.markdown(
        '<div class="page-subtitle">Ask anything and learn interactively!</div>',
        unsafe_allow_html=True
    )

    st.markdown("---")

    for msg in st.session_state.chat_history:
     with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

    # Clear chat button (outside loop)
    if st.session_state.chat_history:
     if st.button("🗑️ Clear Chat", key="clear_chat_btn"):
        st.session_state.chat_history = []
        st.rerun()

    prompt = st.chat_input("Ask EduMind AI...")

    if prompt:

        st.session_state.chat_history.append(
            {
                "role": "user",
                "content": prompt
            }
        )

        with st.chat_message("user"):
            st.markdown(prompt)

        with st.chat_message("assistant"):

            with st.spinner("🧠 Thinking..."):

                conversation = ""

                for msg in st.session_state.chat_history[-6:]:
                  conversation += f"{msg['role']}: {msg['content']}\n"

                conversation += f"user: {prompt}"

                response = get_ai_response(
                    topic=conversation,
                    feature="explainer",
                    learning_style=st.session_state.learning_style,
                    language=language
                )

                st.markdown(response)

        st.session_state.chat_history.append(
            {
                "role": "assistant",
                "content": response
            }
        )
# ── QUIZ GENERATOR ──
elif page == "quiz":
    st.markdown('<div class="page-title">❓ Quiz Generator</div>', unsafe_allow_html=True)
    st.markdown('<div class="page-subtitle">Generate interactive MCQ quizzes and test your knowledge!</div>', unsafe_allow_html=True)
    st.markdown("---")

    st.markdown(f'<div class="info-banner">🌐 Language: <strong>{language}</strong></div>', unsafe_allow_html=True)
    quiz_topic = st.text_input("📚 Enter Quiz Topic", placeholder="e.g. Newton's Laws, Python Programming...")

    if st.button("🎯 Generate Quiz", use_container_width=True):
        if quiz_topic:
            with st.spinner("❓ Generating your quiz..."):
                response = get_ai_response(topic=quiz_topic, feature="quiz",
                    learning_style=st.session_state.learning_style, language=language)

            questions = []
            current_q = {}
            for line in response.strip().split('\n'):
                line = line.strip()
                if not line:
                    continue
                if line.startswith('Q') and ':' in line and len(line.split(':')[0]) <= 3:
                    if current_q:
                        questions.append(current_q)
                    current_q = {'question': line.split(':', 1)[1].strip(),
                                 'options': [], 'answer': '', 'explanation': ''}
                elif line.startswith(('A)', 'B)', 'C)', 'D)')):
                    if current_q:
                        current_q['options'].append(line)
                elif line.startswith('ANSWER:'):
                    if current_q:
                        current_q['answer'] = line.replace('ANSWER:', '').strip()
                elif line.startswith('EXPLANATION:'):
                    if current_q:
                        current_q['explanation'] = line.replace('EXPLANATION:', '').strip()
            if current_q:
                questions.append(current_q)

            st.session_state.parsed_questions = questions
            st.session_state.quiz_topic = quiz_topic
            st.session_state.quiz_submitted = False
        else:
            st.warning("⚠️ Please enter a topic first!")

    if st.session_state.parsed_questions and not st.session_state.quiz_submitted:
        st.markdown("---")
        st.markdown("### 📝 Answer All Questions Below")
        user_answers = []
        for i, q in enumerate(st.session_state.parsed_questions):
            st.markdown(f"**Q{i+1}: {q['question']}**")
            if q['options']:
                selected = st.radio(f"Question {i+1}", q['options'],
                    key=f"quiz_q{i}", label_visibility="collapsed", index=None)
                user_answers.append({
                    'selected': selected[0] if selected else '',
                    'correct': q['answer'],
                    'explanation': q['explanation']
                })
            st.markdown("")

        st.markdown("---")
        if st.button("🎯 Submit Quiz", use_container_width=True):
            score = 0
            st.markdown("### 📊 Your Results")
            for i, ans in enumerate(user_answers):
                if ans['selected'] == ans['correct']:
                    score += 1
                    st.success(f"✅ Q{i+1}: Correct! {ans['explanation']}")
                else:
                    st.error(f"❌ Q{i+1}: Wrong! Correct: **{ans['correct']}**. {ans['explanation']}")

            percentage = (score / len(user_answers)) * 100
            st.markdown("---")
            if percentage >= 70:
                st.balloons()
                st.success(f"🎉 Excellent! You scored **{score}/{len(user_answers)} ({percentage:.0f}%)**")
            elif percentage >= 50:
                st.warning(f"📚 Good effort! **{score}/{len(user_answers)} ({percentage:.0f}%)**")
            else:
                st.error(f"💪 **{score}/{len(user_answers)} ({percentage:.0f}%)**. Revise this topic!")

            st.session_state.quiz_tracker = save_score(
                st.session_state.quiz_tracker, st.session_state.quiz_topic,
                score, len(user_answers))
            st.session_state.quiz_submitted = True

    if st.session_state.quiz_submitted:
        if st.button("🔄 Take Another Quiz", use_container_width=True):
            st.session_state.parsed_questions = []
            st.session_state.quiz_submitted = False
            st.rerun()

# ── FLASHCARD GENERATOR ──
elif page == "flashcards":
    st.markdown('<div class="page-title">🃏 Flashcard Generator</div>', unsafe_allow_html=True)
    st.markdown('<div class="page-subtitle">Generate instant flashcards for quick revision!</div>', unsafe_allow_html=True)
    st.markdown("---")

    st.markdown(f'<div class="info-banner">🌐 Language: <strong>{language}</strong></div>', unsafe_allow_html=True)
    flash_topic = st.text_input("📚 Enter Topic for Flashcards", placeholder="e.g. Data Structures, Indian History...")

    if st.button("🃏 Generate Flashcards", use_container_width=True):
        if flash_topic:
            with st.spinner("🃏 Creating your flashcards..."):
                response = get_ai_response(topic=flash_topic, feature="flashcard",
                    learning_style=st.session_state.learning_style, language=language)
                st.markdown("---")
                st.markdown("### 🃏 Interactive Flashcards")

                cards = []

                lines = response.split("\n")

                question = ""
                answer = ""

                for line in lines:

                    if line.startswith("Q:"):
                        question = line.replace("Q:", "").strip()

                    elif line.startswith("A:"):
                        answer = line.replace("A:", "").strip()

                        cards.append({
                            "question": question,
                            "answer": answer
                        })

                for i, card in enumerate(cards):

                    with st.expander(
                        f"🃏 Card {i+1}: {card['question']}",
                        expanded=False
                    ):
                        st.success(card["answer"])
            pdf_file = create_pdf(response)

            pdf_file = create_pdf(response)

            st.download_button(
                "📥 Download Flashcards PDF",
                data=pdf_file,
                file_name=f"{flash_topic}_flashcards.pdf",
                mime="application/pdf",
                use_container_width=True
            )
        else:
            st.warning("⚠️ Please enter a topic first!")

# ── MIND MAP ──
elif page == "mindmap":
    st.markdown('<div class="page-title">🗺️ Mind Map Generator</div>', unsafe_allow_html=True)
    st.markdown('<div class="page-subtitle">Visualize any topic as a structured concept mind map!</div>', unsafe_allow_html=True)
    st.markdown("---")

    st.markdown(f'<div class="info-banner">🌐 Language: <strong>{language}</strong></div>', unsafe_allow_html=True)
    map_topic = st.text_input("📚 Enter Topic", placeholder="e.g. Artificial Intelligence, Climate Change...")
    difficulty = st.select_slider("📊 Depth Level", options=["School", "Undergrad", "Research"], value="Undergrad")

    if st.button("🗺️ Generate Mind Map", use_container_width=True):
        if map_topic:
            with st.spinner("🗺️ Creating your mind map..."):
                response = get_ai_response(topic=map_topic, feature="mindmap",
                    learning_style=st.session_state.learning_style,
                    difficulty=difficulty, language=language)
            st.markdown("---")
            st.markdown("### 🗺️ Your Mind Map")
            st.code(response, language=None)
            pdf_file = create_pdf(response)
            st.download_button("📥 Download Mind Map", data=pdf_file,
                file_name=f"{map_topic}_mindmap.pdf", mime="application/pdf", use_container_width=True)
        else:
            st.warning("⚠️ Please enter a topic first!")

# ── ANALYTICS ──
elif page == "analytics":
    st.markdown('<div class="page-title">📊 Performance Analytics</div>', unsafe_allow_html=True)
    st.markdown('<div class="page-subtitle">Track your quiz performance and identify weak topics!</div>', unsafe_allow_html=True)
    st.markdown("---")

    tracker = st.session_state.quiz_tracker
    achievements = get_achievements(tracker)
    recommendations = get_recommendations(tracker)
    if tracker["total_attempted"] == 0:
        st.info("📊 No quiz data yet! Take some quizzes first.")
    else:
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("📝 Quizzes Taken", tracker["total_attempted"])
        with col2:
            st.metric("📊 Average Score", f"{get_average_score(tracker)}%")
        with col3:
            st.metric("💪 Best Topic", get_best_topic(tracker) or "N/A")
        with col4:
            st.metric("📚 Needs Work", get_worst_topic(tracker) or "N/A")

        st.markdown("---")
        topics, percentages, colors = get_all_scores(tracker)
        fig = go.Figure(data=[go.Bar(x=topics, y=percentages,
            marker_color=colors, text=[f"{p}%" for p in percentages], textposition="auto")])
        fig.update_layout(title="Quiz Performance by Topic",
            xaxis_title="Topics", yaxis_title="Score (%)",
            yaxis_range=[0, 100], plot_bgcolor="white", showlegend=False)
        fig.add_hline(y=70, line_dash="dash", line_color="green", annotation_text="Target: 70%")
        st.plotly_chart(fig, use_container_width=True)

        col1, col2 = st.columns(2)
        with col1:
            st.markdown("### 💪 Strong Topics")
            for t in get_strong_topics(tracker):
                st.success(f"✅ {t}")
        with col2:
            st.markdown("### 📚 Topics to Revise")
            for t in get_weak_topics(tracker):
                st.error(f"❌ {t}")
        st.markdown("---")
        st.markdown("## 🏆 Achievements")

        if achievements:

            cols = st.columns(len(achievements))

            for i, badge in enumerate(achievements):
                with cols[i]:
                    st.success(badge)

        else:
            st.info("Take your first quiz to unlock achievements!")
        st.markdown("---")
        st.markdown("## 🎯 Personalized Recommendations")

        if recommendations:

            for rec in recommendations:
                st.info(rec)

        else:
            st.info(
                "Complete more quizzes to receive personalized recommendations."
            )
            
# ── ABOUT ──
elif page == "about":
    st.markdown('<div class="page-title">ℹ️ About EduMind AI</div>', unsafe_allow_html=True)
    st.markdown("---")
    st.markdown("""
# 🧠 About EduMind AI

## 🌟 Meet EduMind AI

EduMind AI is an AI-powered Adaptive Learning Intelligence System designed to transform traditional learning into a personalized, intelligent and interactive educational experience.

The platform leverages Artificial Intelligence, Learning Analytics and Adaptive Learning methodologies to deliver customized educational content based on individual learning preferences.

EduMind AI helps students understand concepts faster, revise efficiently, assess their knowledge and track academic progress through an integrated AI learning ecosystem.

---

## 🔍 What Students Struggle With

Students often face challenges while studying due to:

- Lack of personalized learning support
- Difficulty understanding complex concepts
- Information overload from online resources
- Inefficient revision techniques
- Limited access to instant academic assistance

Most educational platforms follow a one-size-fits-all approach.

EduMind AI addresses these challenges through AI-driven personalized learning experiences.

---

## 🚀 How It Works ⭐

EduMind AI combines Generative AI and Adaptive Learning principles to:

- Personalize educational content
- Simplify difficult concepts
- Generate intelligent study materials
- Improve revision efficiency
- Track learning performance
- Provide personalized recommendations

---

## ⚡ Key Features

- 🧬 Learning Style Detection
- 📖 AI Topic Explainer
- 📝 Smart Note Summarizer
- 📄 PDF Learning Assistant
- 💬 AI Tutor
- ❓ Intelligent Quiz Generator
- 🃏 Flashcard Generator
- 🗺️ Mind Map Generator
- 📊 Learning Analytics Dashboard
- 🏆 Achievement System
- 🎯 Personalized Recommendations

---

## 🌍 Multilingual Learning Support

- 🇬🇧 English
- 🇮🇳 Hindi
- 🇫🇷 French
- 🇩🇪 German

---

## 📈 Future Scope

- Voice-Based AI Tutor
- AI Study Planner
- Mobile Application
- Gamified Learning Experience
- Performance Prediction Engine
- LMS Integration

""")
    
    col1, col2, col3 = st.columns(3)
    with col1:
     st.info("""
**Frontend**
• Streamlit

**Programming**
• Python
""")

    with col2:
     st.info("""
**AI Engine**
• Groq API
• LLaMA 3.3

**Learning Model**
• Adaptive Learning
""")

    with col3:
     st.info("""
**Visualization**
• Plotly

**Document Processing**
• PyPDF2 • ReportLab
""")
    st.markdown("---")

    st.markdown("""
    <div style='text-align:center; padding:25px;'>

    <h2>🧠 EduMind AI</h2>

    <p style='font-size:20px; font-weight:600;'>
    Empowering Smarter Learning Through Artificial Intelligence
    </p>

    <p style='color:gray;'>
    Personalized • Adaptive • Intelligent
    </p>

    </div>
    """, unsafe_allow_html=True)
    # Footer for all pages except AI Tutor
if page != "tutor":
    st.markdown("""
    <div class="footer">
        🤖 Empowering Smarter Learning with AI | EduMind AI © 2026
    </div>
    """, unsafe_allow_html=True)