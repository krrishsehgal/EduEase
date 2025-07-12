import os
import re
import json
import requests
import google.generativeai as genai
import streamlit as st
from faster_whisper import WhisperModel
from gtts import gTTS
import yt_dlp
from io import BytesIO

# --- Page Configuration ---
st.set_page_config(
    page_title="EduEase",
    page_icon="🧠",
    layout="wide"
)

# --- API Key Configuration ---
try:
    genai.configure(api_key=st.secrets["GOOGLE_API_KEY"])
except KeyError:
    st.error("Google AI API key not found. Please add it to your Streamlit secrets.", icon="🚨")
    st.stop()

# --- Helper Functions (Final, Stable Versions) ---

def parse_graphviz(notes_text: str) -> str:
    match = re.search(r"```dot\s*([\s\S]+?)\s*```", notes_text)
    if not match: return None
    content = match.group(1).strip()
    if not content.strip().startswith('digraph'): content = f'digraph G {{ {content} }}'
    styling = 'bgcolor="transparent"; node [style="filled", shape="box", fillcolor="#E8F0FE", fontcolor="black", color="#A0C4FF", penwidth=2, fontname="Helvetica"]; edge [color="#6c757d", fontname="Helvetica"];'
    return content.replace('{', f'{{ {styling}', 1)

def highlight_keywords(text: str) -> str:
    colors = ["#FFADAD", "#FFD6A5", "#FDFFB6", "#CAFFBF", "#9BF6FF", "#A0C4FF"]
    def color_replacer(match):
        keyword = match.group(1)
        color = colors[hash(keyword) % len(colors)]
        return f'<span style="background-color: {color}; color: black; padding: 2px 6px; border-radius: 5px; font-weight: 500;">{keyword}</span>'
    return re.sub(r"@@(.*?)@@", color_replacer, text)

def parse_quiz_from_json(notes_text: str) -> list:
    match = re.search(r"```json\s*([\s\S]+?)\s*```", notes_text)
    if not match: return []
    try: return json.loads(match.group(1))
    except json.JSONDecodeError: return []

def parse_mcq_options(question_text: str) -> list:
    return [opt.strip() for opt in re.findall(r'(\([a-zA-Z]\)\s*.*)', question_text)]

# --- Core AI and Processing Functions (Final, Stable Versions) ---

def video_to_audio(video_URL: str):
    try:
        FFMPEG_PATH = "C:/ffmpeg/bin"
        if os.path.exists("Target_audio.mp3"): os.remove("Target_audio.mp3")
        ydl_opts = {'format': 'bestaudio/best', 'outtmpl': 'Target_audio', 'postprocessors': [{'key': 'FFmpegExtractAudio', 'preferredcodec': 'mp3'}], 'ffmpeg_location': FFMPEG_PATH, 'noplaylist': True}
        with yt_dlp.YoutubeDL(ydl_opts) as ydl: ydl.extract_info(video_URL, download=True)
    except Exception as e: st.error(f"Error downloading video: {e}", icon="🚫"); st.stop()

def audio_to_text(audio_path: str) -> str:
    try:
        model = WhisperModel("base", device="cpu", compute_type="int8")
        segments, _ = model.transcribe(audio_path, beam_size=5)
        return "".join(segment.text for segment in segments)
    except Exception as e: st.error(f"Error during local transcription: {e}", icon="🎤"); st.stop()

def generate_notes(text: str) -> str:
    system_prompt = """You are an expert educator for students with learning disabilities. Your task is to transform a video transcript into clear, simple, and highly readable study notes.

The notes must ALWAYS include these sections, formatted in Markdown with `##` for headings:
1.  ## Title: A creative and relevant title.
2.  ## Detailed Summary: A detailed, easy-to-understand summary.
3.  ## Jargon Buster: Identify 2-3 complex terms. For each, provide a simple, one-sentence explanation.
4.  ## Key Concepts (for Flowchart): A list of key concepts for a Graphviz flowchart. Use a markdown code block labeled 'dot'.
5.  ## Key Takeaways: A bulleted list of important points. Wrap 3-5 important keywords in this section only in @@keyword@@ markers.
6.  ## Mnemonics: A clever memory aid for a key fact.
7.  ## Quiz Yourself!: A short quiz in JSON format.
"""
    model = genai.GenerativeModel('gemini-1.5-flash-latest')
    try:
        response = model.generate_content(system_prompt + "\n\nHere is the transcript:\n" + text)
        return response.text
    except Exception as e: st.error(f"Error generating notes with Google AI: {e}", icon="🤖"); st.stop()

# --- Main Streamlit App (Final, Architecturally Sound Version) ---
def app():
    # --- Sidebar ---
    with st.sidebar:
        st.image("assets/images/EduEase logo.png", use_container_width=True)
        st.header("Making Learning Accessible")
        st.markdown("Welcome to **EduEase**! Your personal AI learning assistant.")
        st.info("Created with ❤️ for a hackathon.", icon="🚀")

    # --- Main Page ---
    st.title("EduEase 🧠✨")
    st.write("Transform any educational YouTube video into simple, beautiful, and interactive study notes.")

    # --- Initialize Session State ---
    if "notes" not in st.session_state: st.session_state.notes = ""
    if "video_url" not in st.session_state: st.session_state.video_url = ""
    if "flashcards" not in st.session_state: st.session_state.flashcards = []
    if "current_card_index" not in st.session_state: st.session_state.current_card_index = 0
    if "summary_audio_data" not in st.session_state: st.session_state.summary_audio_data = None
    if "processing" not in st.session_state: st.session_state.processing = False

    video_URL = st.text_input("Paste the YouTube video URL here")

    # --- Generation Button Logic ---
    if st.button("✨ Generate My Notes ✨", use_container_width=True):
        if video_URL:
            st.session_state.video_url = video_URL
            st.session_state.notes = ""
            st.session_state.flashcards = []
            st.session_state.current_card_index = 0
            st.session_state.summary_audio_data = None
            st.session_state.processing = True
            # We call rerun here to immediately start showing the spinner
            st.rerun() 
        else:
            st.warning("Oops! You forgot to paste a YouTube URL.", icon="🤔")

    # --- Processing Logic (runs only when the processing flag is set) ---
    if st.session_state.processing:
        with st.spinner('Hang tight! Our AI is working its magic... 🧙‍♂️'):
            video_to_audio(st.session_state.video_url)
            transcript = audio_to_text("Target_audio.mp3")
            notes_text = generate_notes(transcript)
            
            st.session_state.notes = notes_text
            st.session_state.flashcards = parse_quiz_from_json(notes_text)
            os.remove("Target_audio.mp3")

            summary_match = re.search(r'##\s*(Detailed\s)?Summary\s*.*?\n(.*?)(?=##)', notes_text, re.DOTALL)
            if summary_match:
                summary_text = summary_match.group(2).strip()
                sound_file = BytesIO()
                tts = gTTS(text=summary_text, lang='en')
                tts.write_to_fp(sound_file)
                st.session_state.summary_audio_data = sound_file
            
            st.session_state.processing = False
            # Rerun one last time to clear the spinner and show the final results
            st.rerun()

    # --- Display Logic (runs only when NOT processing and notes exist) ---
    if not st.session_state.processing and st.session_state.notes:
        notes = st.session_state.notes
        
        st.success("Notes generated successfully!", icon="✅")
        st.markdown("---")
        
        st.subheader("1. Video & Audio Summary")
        st.video(st.session_state.video_url)
        if st.session_state.summary_audio_data:
            st.audio(st.session_state.summary_audio_data)

        st.subheader("2. Your Study Guide")
        
        sections = re.split(r'(?=##\s)', notes)
        for section in sections:
            if not section.strip() or "Quiz Yourself!" in section: continue
            
            if "Key Concepts (for Flowchart)" in section:
                graphviz_data = parse_graphviz(section)
                if graphviz_data:
                    st.markdown("## Key Concepts Flowchart")
                    st.graphviz_chart(graphviz_data)
            elif "Key Takeaways" in section:
                st.markdown(highlight_keywords(section), unsafe_allow_html=True)
            else:
                st.markdown(section)
        
        # --- FIXED: Handle both dict and list formats for flashcards ---
        flashcards_raw = st.session_state.get('flashcards', [])
        
        # Extract questions from the data structure
        if isinstance(flashcards_raw, dict) and 'questions' in flashcards_raw:
            flashcards = flashcards_raw['questions']
        elif isinstance(flashcards_raw, list):
            flashcards = flashcards_raw
        else:
            flashcards = []
        
        # Convert format if needed (the data structure has 'answers' and 'correct' instead of 'answer')
        processed_flashcards = []
        for card in flashcards:
            if 'answers' in card and 'correct' in card:
                # Convert to expected format
                processed_card = {
                    'question': card['question'],
                    'answer': card['answers'][card['correct']] if isinstance(card['answers'], list) else card['answers']
                }
                processed_flashcards.append(processed_card)
            else:
                # Already in expected format
                processed_flashcards.append(card)
        
        flashcards = processed_flashcards
        
        # Ensure flashcards is a list and has content
        if isinstance(flashcards, list) and len(flashcards) > 0:
            st.markdown("---")
            st.subheader("🧠 Test Your Knowledge")
            tab1, tab2 = st.tabs(["Interactive Quiz (MCQ)", "Study with Flashcards"])
            
            card_index = st.session_state.get('current_card_index', 0)
            
            # Self-healing logic: If index is out of bounds, reset it to 0.
            if card_index >= len(flashcards):
                st.session_state.current_card_index = 0
                card_index = 0
            
            # Additional safety check before accessing
            if card_index < len(flashcards):
                question_data = flashcards[card_index]
            else:
                st.error("Card index out of range")
                return

            with tab1:
                # MCQ Logic - Enhanced for the actual data structure
                st.markdown(f"**Question {card_index + 1} of {len(flashcards)}**")
                
                # Display the question
                st.markdown(question_data['question'])
                
                # For MCQ, we need to reconstruct the options from the original data
                original_card = flashcards_raw['questions'][card_index] if isinstance(flashcards_raw, dict) else flashcards_raw[card_index]
                
                if 'answers' in original_card and isinstance(original_card['answers'], list):
                    # Create MCQ options with (a), (b), (c), (d) format
                    options = []
                    for i, answer in enumerate(original_card['answers']):
                        letter = chr(ord('a') + i)
                        options.append(f"({letter}) {answer}")
                    
                    user_answer = st.radio("Choose your answer:", options, key=f"mcq_{card_index}", label_visibility="collapsed")
                    
                    if st.button("Check Answer", key=f"check_{card_index}"):
                        selected_index = options.index(user_answer)
                        if selected_index == original_card['correct']:
                            st.success("Correct! 🎉")
                        else:
                            correct_answer = original_card['answers'][original_card['correct']]
                            st.error(f"Not quite! The correct answer was: {correct_answer}")
                else:
                    # Fallback to simple question display
                    st.markdown("This question doesn't have multiple choice options.")
            
            with tab2:
                # Flashcard Logic
                st.markdown(f"**Flashcard {card_index + 1} of {len(flashcards)}**")
                st.markdown(question_data['question'])
                with st.expander("🤔 Reveal Answer"):
                    st.success(f"**Answer:** {question_data['answer']}")

            # Navigation Buttons
            col1, col2, _ = st.columns([1, 1, 4])
            if col1.button("⬅️ Previous", use_container_width=True, disabled=(card_index <= 0)):
                st.session_state.current_card_index -= 1
                st.rerun()
            if col2.button("Next ➡️", use_container_width=True, disabled=(card_index >= len(flashcards) - 1)):
                st.session_state.current_card_index += 1
                st.rerun()
        else:
            # Optional: Show a message when no quiz questions are available
            if st.session_state.notes:  # Only show if notes were generated
                st.info("No quiz questions were generated for this content. The AI might not have found suitable quiz material in the transcript.", icon="📝")

# --- Run the App ---
if __name__ == '__main__':
    app()
