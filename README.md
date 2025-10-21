# **EduEase 🧠✨**

An AI-powered learning assistant that transforms dense educational YouTube videos into simple, accessible, and interactive study materials.

EduEase is designed with a core mission: to make learning accessible for everyone, especially students with cognitive and attention-related disabilities like Dyslexia and ADHD. By leveraging a powerful suite of AI models, our app deconstructs long video lectures into notes that are easy to read, listen to, visualize, and test.

### **The Problem**

Traditional online learning, especially through video platforms like YouTube, presents significant barriers for students with learning disabilities. Long, unstructured content can be overwhelming, making it difficult to:

Maintain focus and attention.

Identify key concepts from conversational filler.

Recall information effectively.

Engage actively with the material instead of just passively watching.

### **Our Solution: EduEase 🚀**

EduEase tackles these challenges by providing a multimodal learning experience that caters to different learning styles and cognitive needs.

Simply paste a YouTube video URL, and EduEase generates a comprehensive and accessible study guide featuring:

🎧 Audio Notes: An audio version of the generated notes, perfect for auditory learners or for reinforcing concepts on the go.

📝 Simplified Text Notes: The core of the app, featuring:

Title & Summary: A quick overview and a simple, intuitive explanation.

Text-Based Flowchart: A clear, text-based diagram mapping out the core concepts.

Key Takeaways: A concise bulleted list of the most important information.

Mnemonics: Clever memory aids to help with retention of key facts.

🧠 Interactive Flashcards: An AI-generated quiz is turned into interactive flashcards, allowing students to actively test their knowledge and reinforce learning through recall.

### **Tech Stack & Architecture**

EduEase is built with a modern, hybrid AI architecture, combining the best of local and cloud-based models for performance, quality, and cost-effectiveness.

Frontend: Streamlit - For building a beautiful and interactive web interface with pure Python.

Video & Audio Processing:

yt-dlp - A robust library for reliably downloading video/audio from YouTube.

FFmpeg - The industry-standard tool for audio conversion.

### AI Models & APIs:

Speech-to-Text: Whisper (via faster-whisper) - Runs a state-of-the-art transcription model locally on the user's machine for speed and privacy.

Note & Quiz Generation: Google Gemini Pro API - Leverages Google's powerful, high-quality language model to generate structured, coherent, and helpful notes.

Image Generation: Stability AI API (Stable Diffusion) - Creates the visual summary image from a text prompt.

Text-to-Speech: gTTS - A simple library for converting the generated notes into audio.

### Future Roadmap

We believe EduEase is just the beginning. Future enhancements could include:

User Accounts & Progress Tracking: Allow users to save their notes and track their flashcard performance over time using a Spaced Repetition System (SRS).

Deeper Personalization: Allow users to select their specific learning disability to receive even more tailored note formats and visual aids.

Pull #1