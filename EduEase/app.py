import streamlit as st
from PIL import Image
import os
import re
import json
import requests
import google.generativeai as genai
from faster_whisper import WhisperModel
from gtts import gTTS
import yt_dlp
from io import BytesIO

# --- Page Configuration ---
st.set_page_config(page_title="EduEase", page_icon="🧠", layout="wide")

# --- CUSTOM CSS WITH NEW LOGO STYLING ---
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap');

    * {
        font-family: 'Inter', sans-serif;
    }

    /* --- Main App Styling --- */
    .stApp {
        background-color: #000000;
    }

    .main .block-container {
        padding: 1rem 1rem;
    }

    /* --- NEW LOGO STYLING --- */
    .logo-container {
        text-align: center;
        padding: 2rem 0;
    }

    .logo-title {
        font-size: 5rem; /* Larger font size for impact */
        font-weight: 800; /* Bolder font */
        background: -webkit-linear-gradient(45deg, #F08, #89f7fe);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 0.5rem;
    }

    .logo-underline {
        width: 150px;
        height: 4px;
        background: linear-gradient(90deg, #F08, #89f7fe);
        margin: 0 auto;
        border-radius: 2px;
        box-shadow: 0 0 12px 2px #F08, 0 0 12px 2px #89f7fe; /* Glow effect */
    }


    /* --- Text and Font Styling --- */
    .hero-title {
        font-size: 3.5rem;
        font-weight: 700;
        color: #FFFFFF;
        margin-bottom: 1rem;
    }

    .hero-subtitle {
        font-size: 1.3rem;
        color: #E0E0E0;
        font-weight: 400;
        margin-bottom: 2rem;
    }

    .section-header {
        font-size: 1.8rem;
        font-weight: 600;
        color: #FFFFFF;
        margin-bottom: 1.5rem;
        padding-bottom: 0.5rem;
        border-bottom: 3px solid #AEC6CF; /* Soft Pastel Blue */
    }

    /* --- Container Styling --- */
    .hero-section {
        text-align: center;
        padding: 3rem 2rem;
        background-color: #121212;
        border-radius: 20px;
        margin: 1rem auto 2rem auto; /* Adjusted margin */
        max-width: 800px;
        border: 1px solid #333333;
    }

    .input-container {
        background-color: #1E1E1E;
        border-radius: 15px;
        padding: 2rem;
        margin: 2rem auto;
        max-width: 600px;
        border: 1px solid #333333;
    }

    .content-section {
        background-color: #000000;
        padding: 2rem 0;
        margin: 2rem 0;
        border: none;
    }

    /* --- Interactive Element Styling --- */
    .badge {
        display: inline-flex;
        align-items: center;
        gap: 0.5rem;
        background: rgba(174, 198, 207, 0.2);
        color: #AEC6CF;
        padding: 0.5rem 1rem;
        border-radius: 25px;
        font-weight: 500;
        margin-bottom: 2rem;
        border: 1px solid #AEC6CF;
    }

    .stTextInput > div > div > input {
        background-color: #F0F0F0;
        border: 1px solid #BDBDBD;
        border-radius: 10px;
        color: #121212;
        padding: 1rem;
        font-size: 1rem;
    }

    .stTextInput > div > div > input::placeholder { color: #616161; }

    .stButton > button {
        background-color: #B9FBC0;
        color: #121212;
        border: none;
        padding: 1rem 2rem;
        border-radius: 12px;
        font-weight: 700;
        font-size: 1.1rem;
        width: 100%;
        transition: all 0.3s ease;
    }

    .stButton > button:hover { background-color: #98F9A9; }

    .stTabs [data-baseweb="tab-list"] { gap: 1rem; }
    .stTabs [data-baseweb="tab"] {
        background-color: #1E1E1E;
        border-radius: 10px;
        padding: 1rem;
        border: 1px solid #333333;
        color: #FFFFFF;
    }
    .stTabs [aria-selected="true"] {
        background-color: #AEC6CF;
        color: #121212;
    }

    /* --- Quiz Styling --- */
    .quiz-container {
        background-color: #1E1E1E;
        border-radius: 15px;
        padding: 2rem;
        margin: 1rem 0;
        border: 1px solid #333333;
    }
    .quiz-question {
        font-size: 1.2rem;
        font-weight: 600;
        color: #FFFFFF;
        margin-bottom: 1.5rem;
    }
    .quiz-option {
        background: #333333;
        border: 2px solid #555555;
        color: #FFFFFF;
        border-radius: 10px;
        padding: 1rem;
        margin: 0.5rem 0;
        transition: all 0.3s ease;
    }
    .quiz-option:hover { border-color: #AEC6CF; }
    .quiz-option.correct {
        background: #28a745;
        border-color: #28a745;
        color: #FFFFFF;
    }
    .quiz-option.incorrect {
        background: #dc3545;
        border-color: #dc3545;
        color: #FFFFFF;
    }

    /* --- Flashcard & Feature Styling --- */
    .flashcard {
        background-color: #1E1E1E;
        color: white;
        border-radius: 15px;
        padding: 2rem;
        margin: 1rem 0;
        border: 1px solid #333333;
    }
    .feature-grid {
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
        gap: 2rem; margin: 3rem 0;
    }
    .feature-card {
        background: #1E1E1E;
        border-radius: 15px;
        padding: 2rem;
        text-align: center;
        border: 1px solid #333333;
        transition: all 0.3s ease;
    }
    .feature-card:hover { transform: translateY(-5px); border-color: #AEC6CF; }
    .feature-icon { font-size: 3rem; margin-bottom: 1rem; display: block; color: white; }
    .feature-title { font-size: 1.5rem; font-weight: 600; margin-bottom: 1rem; color: white; }
    .feature-description { color: #E0E0E0; line-height: 1.6; }

    /* --- Visibility --- */
    #MainMenu, footer, header { visibility: hidden; }

</style>
""", unsafe_allow_html=True)

# --- API Key Configuration ---
try:
    genai.configure(api_key=st.secrets["GOOGLE_API_KEY"])
except KeyError:
    st.error("Google AI API key not found. Please add it to your Streamlit secrets.", icon="🚨")
    st.stop()

# --- Helper Functions (No changes here) ---
def parse_graphviz(notes_text: str) -> str:
    match = re.search(r"```dot\s*([\s\S]+?)\s*```", notes_text)
    if not match: return None
    content = match.group(1).strip()
    if not content.strip().startswith('digraph'): content = f'digraph G {{ {content} }}'
    styling = 'bgcolor="transparent"; node [style="filled", shape="box", fillcolor="#AEC6CF", fontcolor="#121212", color="#FFFFFF", penwidth=2, fontname="Inter"]; edge [color="#FFFFFF", fontname="Inter"];'
    return content.replace('{', f'{{ {styling}', 1)

def highlight_keywords(text: str) -> str:
    colors = ["#FFD6A5", "#FDFFB6", "#CAFFBF", "#9BF6FF", "#FFC0CB"]
    def color_replacer(match):
        keyword = match.group(1)
        color = colors[hash(keyword) % len(colors)]
        return f'<span style="background-color: {color}; color: #121212; padding: 2px 6px; border-radius: 5px; font-weight: 500;">{keyword}</span>'
    return re.sub(r"@@(.*?)@@", color_replacer, text)

def parse_quiz_from_json(notes_text: str, key: str) -> list:
    pattern = re.compile(f'##\\s*{key}[\\s\\S]*?```json\\s*([\\s\\S]+?)\\s*```', re.IGNORECASE)
    match = pattern.search(notes_text)
    if not match: return []
    try: return json.loads(match.group(1))
    except json.JSONDecodeError: return []


def video_to_audio(video_URL: str):
    try:
        if os.path.exists("Target_audio.mp3"):
            os.remove("Target_audio.mp3")

        # When deploying, ffmpeg is installed via packages.txt and is in the system's PATH.
        # Therefore, we do NOT need to specify the ffmpeg_location.
        ydl_opts = {
            'format': 'bestaudio/best',
            'outtmpl': 'Target_audio',
            'postprocessors': [{'key': 'FFmpegExtractAudio', 'preferredcodec': 'mp3'}],
            # 'ffmpeg_location': FFMPEG_PATH, <-- REMOVE THIS LINE
            'noplaylist': True
        }
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.extract_info(video_URL, download=True)
            
    except Exception as e:
        st.error(f"Error downloading video: {e}", icon="🚫")
        st.stop()

def audio_to_text(audio_path: str) -> str:
    try:
        model = WhisperModel("base", device="cpu", compute_type="int8")
        segments, _ = model.transcribe(audio_path, beam_size=5)
        return "".join(segment.text for segment in segments)
    except Exception as e: st.error(f"Error during local transcription: {e}", icon="🎤"); st.stop()

def find_correct_option(options, correct_answer):
    """
    Find the correct option from the list by matching against the correct_answer.
    Returns the index of the correct option, or None if not found.
    """
    if not options or not correct_answer:
        return None
    
    correct_answer_clean = correct_answer.strip().upper()
    
    # Method 1: Direct letter match (A, B, C, D)
    if len(correct_answer_clean) == 1 and correct_answer_clean.isalpha():
        target_letter = correct_answer_clean
        for i, option in enumerate(options):
            if option and len(option) > 0:
                match = re.match(r'^([A-Za-z])', option.strip())
                if match and match.group(1).upper() == target_letter:
                    return i
    
    # Method 2: Find by content similarity
    for i, option in enumerate(options):
        if option:
            option_clean = option.strip().upper()
            # Remove the letter prefix (A), B), etc.) from option
            option_content = re.sub(r'^[A-Za-z][\)\.\s]*', '', option_clean).strip()
            
            # Check if correct_answer matches the option content
            if (correct_answer_clean == option_content or 
                correct_answer_clean in option_content or
                option_content in correct_answer_clean):
                return i
    
    # Method 3: Fallback - find the longest matching substring
    best_match_index = None
    best_match_score = 0
    
    for i, option in enumerate(options):
        if option:
            option_content = re.sub(r'^[A-Za-z][\)\.\s]*', '', option.strip().upper())
            
            # Calculate similarity score
            common_words = set(correct_answer_clean.split()) & set(option_content.split())
            score = len(common_words)
            
            if score > best_match_score:
                best_match_score = score
                best_match_index = i
    
    return best_match_index if best_match_score > 0 else None

def generate_notes(text: str) -> str:
    system_prompt = """You are an expert educator for students with learning disabilities. Your task is to transform a video transcript into clear, simple, and engaging study notes. You MUST be creative and avoid repetitive phrasing.
The notes must ALWAYS include these sections, formatted in Markdown with `##` for headings:
1.  ## Title: A creative and relevant title.
2.  ## Detailed Summary: A detailed, easy-to-understand summary.
3.  ## Jargon Buster: Identify 2-3 complex terms. For each, provide a simple, one-sentence "in plain English" explanation.
4.  ## Key Concepts (for Flowchart): Identify the core concepts and their relationships. Format them for a Graphviz flowchart inside a 'dot' code block.
5.  ## Key Takeaways: A bulleted list of important points. Wrap 3-5 keywords in this section only in @@keyword@@ markers.
6.  ## Mnemonics: A unique and clever memory aid for a key fact.
7.  ## MCQ Quiz: Generate 3-5 varied multiple-choice questions (what, why, how). Format THIS SECTION ONLY as a valid JSON array. Each object must have "question", "options", "correct_answer", and "hint" keys.
8.  ## Flashcard Review: Generate 3-5 DIFFERENT open-ended questions for flashcard review (e.g., "Explain what X is."). Format THIS SECTION ONLY as a valid JSON array. Each object must have "question" and "answer" keys.
"""
    model = genai.GenerativeModel('gemini-1.5-flash-latest')
    try:
        response = model.generate_content(system_prompt + "\n\nHere is the transcript:\n" + text)
        return response.text
    except Exception as e:
        st.error(f"Error generating notes with Google AI: {e}", icon="🤖")
        return None

# --- Main Streamlit App ---
def app():
    # --- NEW LOGO IMPLEMENTATION ---
    st.markdown("""
    <div class="logo-container">
        <div class="logo-title">EduEase</div>
        <div class="logo-underline"></div>
    </div>
    """, unsafe_allow_html=True)

    # --- Hero Section (no change) ---
    st.markdown("""
    <div class="hero-section">
        <div class="badge">
            ⚡ Designed for cognitive accessibility
        </div>
        <h1 class="hero-title">Transform YouTube videos into<br>easy-to-understand notes</h1>
        <p class="hero-subtitle">EduEase helps people with ADHD and other cognitive differences learn better by converting video content into clear, structured notes.</p>
    </div>
    """, unsafe_allow_html=True)

    # --- Session State Initialization (no change) ---
    state_keys = {
        "notes": "", "video_url": "", "summary_audio_data": None,
        "mcq_questions": [], "flashcard_questions": [],
        "mcq_current_index": 0, "flashcard_current_index": 0,
        "mcq_answer_submitted": False, "mcq_user_answer": None,
        "processing": False
    }
    for key, default_value in state_keys.items():
        if key not in st.session_state:
            st.session_state[key] = default_value

    # --- Input Section (no change) ---
    st.markdown("""
    <div class="input-container">
        <div style="text-align: center; margin-bottom: 1rem;">
            <div style="font-size: 3rem; margin-bottom: 1rem;">📹</div>
            <h2 style="color: white; margin-bottom: 0.5rem;">Generate Your Notes</h2>
            <p style="color: #E0E0E0;">Paste any YouTube educational video link below and we'll create simplified, structured notes for you.</p>
        </div>
    """, unsafe_allow_html=True)

    video_URL = st.text_input("", placeholder="https://youtube.com/watch?v=...", key="video_input", label_visibility="collapsed")

    if st.button("📝 Generate Notes", use_container_width=True):
        if video_URL:
            if video_URL != st.session_state.video_url:
                for key, default_value in state_keys.items(): st.session_state[key] = default_value
                st.session_state.video_url = video_URL
            st.session_state.processing = True
            st.rerun()
        else:
            st.warning("Please enter a YouTube URL to get started.", icon="⚠️")

    st.markdown("</div>", unsafe_allow_html=True)

    # --- Features Section (no change) ---
    if not st.session_state.notes and not st.session_state.processing:
        st.markdown("""
        <div class="feature-grid">
            <div class="feature-card"><div class="feature-icon">🔮</div><h3 class="feature-title">Simplified Content</h3><p class="feature-description">Complex concepts broken down into easy-to-understand bullet points.</p></div>
            <div class="feature-card"><div class="feature-icon">📋</div><h3 class="feature-title">Structured Notes</h3><p class="feature-description">Organized information with clear headings and key takeaways.</p></div>
            <div class="feature-card"><div class="feature-icon">🎯</div><h3 class="feature-title">ADHD-Friendly</h3><p class="feature-description">Designed with cognitive accessibility and focus in mind.</p></div>
        </div>
        """, unsafe_allow_html=True)

    # --- Processing Logic (no change) ---
    if st.session_state.processing:
        st.markdown('<div class="content-section" style="text-align: center;">', unsafe_allow_html=True)
        with st.spinner('🧙‍♂️ Our AI is working its magic... This might take a moment.'):
            video_to_audio(st.session_state.video_url)
            transcript = audio_to_text("Target_audio.mp3")
            notes_text = generate_notes(transcript)
            if notes_text:
                st.session_state.notes = notes_text
                st.session_state.mcq_questions = parse_quiz_from_json(notes_text, key="MCQ Quiz")
                st.session_state.flashcard_questions = parse_quiz_from_json(notes_text, key="Flashcard Review")
                if os.path.exists("Target_audio.mp3"): os.remove("Target_audio.mp3")
                summary_match = re.search(r'##\s*(Detailed\s)?Summary\s*.*?\n(.*?)(?=##)', notes_text, re.DOTALL)
                if summary_match:
                    summary_text = summary_match.group(2).strip()
                    sound_file = BytesIO()
                    tts = gTTS(text=summary_text, lang='en')
                    tts.write_to_fp(sound_file)
                    st.session_state.summary_audio_data = sound_file
            else:
                st.error("Failed to generate notes. Please try again.", icon="🚨")
            st.session_state.processing = False
            st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)

    # --- Display Generated Content (no change) ---
    if not st.session_state.processing and st.session_state.notes:
        notes = st.session_state.notes
        st.markdown("""<div style="background: rgba(40, 167, 69, 0.2); border: 1px solid #28a745; border-radius: 10px; padding: 1rem; margin: 1rem 0; color: white; text-align: center;">✅ Notes generated successfully!</div>""", unsafe_allow_html=True)

        st.markdown('<div class="content-section">', unsafe_allow_html=True)
        st.markdown('<h2 class="section-header">📹 Video & Audio Summary</h2>', unsafe_allow_html=True)
        st.video(st.session_state.video_url)
        if st.session_state.summary_audio_data:
            st.markdown("<br>", unsafe_allow_html=True)
            st.markdown("**🎧 Listen to Summary**")
            st.audio(st.session_state.summary_audio_data)
        st.markdown('</div>', unsafe_allow_html=True)

        st.markdown('<div class="content-section">', unsafe_allow_html=True)
        st.markdown('<h2 class="section-header">📚 Your Study Guide</h2>', unsafe_allow_html=True)
        sections = re.split(r'(?=##\s)', notes)
        for section in sections:
            if any(keyword in section for keyword in ["MCQ Quiz", "Flashcard Review"]): continue
            if not section.strip(): continue
            if "Key Concepts (for Flowchart)" in section:
                graphviz_data = parse_graphviz(section)
                if graphviz_data: 
                    st.markdown("### 🔗 Key Concepts Flowchart", unsafe_allow_html=True)
                    st.graphviz_chart(graphviz_data)
            elif "Key Takeaways" in section: st.markdown(highlight_keywords(section), unsafe_allow_html=True)
            else: st.markdown(section, unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)

        mcq_questions = st.session_state.get('mcq_questions', [])
        flashcard_questions = st.session_state.get('flashcard_questions', [])
        
        if mcq_questions or flashcard_questions:
            st.markdown('<div class="content-section">', unsafe_allow_html=True)
            st.markdown('<h2 class="section-header">🧠 Test Your Knowledge</h2>', unsafe_allow_html=True)
            tabs_to_show = []
            if mcq_questions: tabs_to_show.append("🎯 Interactive Quiz")
            if flashcard_questions: tabs_to_show.append("📚 Flashcards")
            
            if tabs_to_show:
                tabs = st.tabs(tabs_to_show)
                # Replace the MCQ section in your code with this fixed version

                # Replace the MCQ section in your code with this fixed version

                if "🎯 Interactive Quiz" in tabs_to_show:
                    with tabs[tabs_to_show.index("🎯 Interactive Quiz")]:
                        st.markdown('<div class="quiz-container">', unsafe_allow_html=True)
                        mcq_index = st.session_state.mcq_current_index
                        
                        if mcq_index < len(mcq_questions):
                            question_data = mcq_questions[mcq_index]
                            st.markdown(f'<div style="font-size: 1rem; color: #AAAAAA; margin-bottom: 1rem;">Question {mcq_index + 1} of {len(mcq_questions)}</div>', unsafe_allow_html=True)
                            st.markdown(f'<div class="quiz-question">{question_data["question"]}</div>', unsafe_allow_html=True)
                            
                            options = question_data.get('options', [])
                            correct_answer = question_data.get('correct_answer', '').strip()
                            hint = question_data.get('hint', '')
                            
                            if not options:
                                st.error("No options found. Please regenerate.")
                                st.markdown('</div>', unsafe_allow_html=True)
                                return
                            
                            # Find the correct option index
                            correct_option_index = find_correct_option(options, correct_answer)
                            
                            if correct_option_index is None:
                                st.error(f"Could not determine correct answer. Raw correct_answer: '{correct_answer}'")
                                st.error("Available options:")
                                for i, opt in enumerate(options):
                                    st.write(f"{i}: {opt}")
                                st.markdown('</div>', unsafe_allow_html=True)
                                return
                            
                            if st.session_state.mcq_answer_submitted:
                                user_answer = st.session_state.get('mcq_user_answer', '')
                                
                                # Find user's selected option index
                                user_option_index = None
                                for i, option in enumerate(options):
                                    if option == user_answer:
                                        user_option_index = i
                                        break
                                
                                # Display options with correct styling
                                for i, option in enumerate(options):
                                    if i == correct_option_index:
                                        # This is the correct answer
                                        st.markdown(f'<div class="quiz-option correct">✅ {option}</div>', unsafe_allow_html=True)
                                    elif i == user_option_index and i != correct_option_index:
                                        # This is the user's incorrect choice
                                        st.markdown(f'<div class="quiz-option incorrect">❌ {option}</div>', unsafe_allow_html=True)
                                    else:
                                        # Regular option
                                        st.markdown(f'<div class="quiz-option">{option}</div>', unsafe_allow_html=True)
                                
                                # Show result
                                if user_option_index == correct_option_index:
                                    st.success("🎉 Correct! Well done!", icon="✅")
                                else:
                                    st.error(f"❌ Incorrect. The correct answer is: {options[correct_option_index]}", icon="🚫")
                                    if hint:
                                        st.info(f"💡 **Hint:** {hint}", icon="💡")
                                
                                # Navigation buttons
                                st.markdown("---")
                                col1, col2, col3 = st.columns([1, 1, 1])
                                
                                with col1:
                                    if mcq_index < len(mcq_questions) - 1:
                                        if st.button("Next ➡️", use_container_width=True, key=f"next_mcq_{mcq_index}"):
                                            st.session_state.mcq_current_index += 1
                                            st.session_state.mcq_answer_submitted = False
                                            st.session_state.mcq_user_answer = None
                                            st.rerun()
                                    else:
                                        st.button("✅ Quiz Complete!", use_container_width=True, disabled=True)
                                
                                with col2:
                                    if user_option_index != correct_option_index:
                                        if st.button("Try Again 🔄", use_container_width=True, key=f"retry_mcq_{mcq_index}"):
                                            st.session_state.mcq_answer_submitted = False
                                            st.session_state.mcq_user_answer = None
                                            st.rerun()
                                
                                with col3:
                                    if mcq_index > 0:
                                        if st.button("⬅️ Previous", use_container_width=True, key=f"prev_mcq_{mcq_index}"):
                                            st.session_state.mcq_current_index -= 1
                                            st.session_state.mcq_answer_submitted = False
                                            st.session_state.mcq_user_answer = None
                                            st.rerun()
                            
                            else:
                                # Show radio buttons for selection
                                user_choice = st.radio(
                                    "Select your answer:",
                                    options=options,
                                    index=None,
                                    key=f"mcq_radio_{mcq_index}",
                                    label_visibility="collapsed"
                                )
                                
                                if st.button("Submit Answer", use_container_width=True, key=f"submit_mcq_{mcq_index}"):
                                    if user_choice:
                                        st.session_state.mcq_user_answer = user_choice
                                        st.session_state.mcq_answer_submitted = True
                                        st.rerun()
                                    else:
                                        st.warning("Please select an answer.", icon="⚠️")
                        
                        else:
                            st.error("Question index out of range.")
                        
                        st.markdown('</div>', unsafe_allow_html=True)
                if "📚 Flashcards" in tabs_to_show:
                    with tabs[tabs_to_show.index("📚 Flashcards")]:
                        flashcard_index = st.session_state.flashcard_current_index; question_data = flashcard_questions[flashcard_index]
                        st.markdown(f'<div style="font-size: 1rem; color: #AAAAAA; margin-bottom: 1rem;">Flashcard {flashcard_index + 1} of {len(flashcard_questions)}</div>', unsafe_allow_html=True)
                        st.markdown(f'<div class="flashcard"><div style="font-size: 1.2rem; font-weight: 600;">{question_data["question"].replace(r"\\n", "<br>")}</div></div>', unsafe_allow_html=True)
                        with st.expander("🤔 Reveal Answer"): st.success(f"**Answer:** {question_data['answer']}")
                        st.write(""); col1, col2, _ = st.columns([1, 1, 4])
                        if col1.button("⬅️ Previous", use_container_width=True, disabled=(flashcard_index <= 0), key="prev_flash"): st.session_state.flashcard_current_index -= 1; st.rerun()
                        if col2.button("Next ➡️", use_container_width=True, disabled=(flashcard_index >= len(flashcard_questions) - 1), key="next_flash"): st.session_state.flashcard_current_index += 1; st.rerun()
            st.markdown('</div>', unsafe_allow_html=True)

# --- Run the App ---
if __name__ == '__main__':
    app()
