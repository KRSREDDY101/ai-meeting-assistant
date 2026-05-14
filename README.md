# 🎙️ AI Meeting Assistant

AI pipeline that transcribes meetings, extracts summaries, action items 
and enables conversational Q&A over transcripts.

## Features
- Transcribe YouTube URLs or audio files using OpenAI Whisper
- Hindi/Hinglish support via Sarvam API
- Auto-generate meeting summaries, action items & key decisions
- Conversational Q&A over transcripts using RAG
- Export results as PDF or TXT

## Tech Stack
- Python
- OpenAI Whisper
- LangChain LCEL + Mistral AI
- HuggingFace sentence-transformers
- ChromaDB
- Streamlit
- yt-dlp

## Installation
pip install -r requirements.txt

## Usage
streamlit run app.py

## How It Works
1. Input a YouTube URL or upload an audio file
2. Whisper transcribes the audio locally
3. Mistral AI extracts summary, action items & decisions
4. Transcript is embedded into ChromaDB
5. Ask questions and get instant answers via semantic search
