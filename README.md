# 🎙️ MeetMind — AI Meeting Assistant

An end-to-end AI pipeline that transcribes meetings from YouTube URLs or audio files, generates structured summaries, extracts action items and key decisions, and lets you have a full conversation with your meeting transcript — all through a sleek Streamlit web interface.

---

## 🚀 Features

- **Transcription** — Transcribe YouTube URLs or local audio/video files using locally hosted OpenAI Whisper
- **Hindi/Hinglish Support** — Route multilingual content through Sarvam AI's speech-to-text-translate API
- **Meeting Summary** — Auto-generate concise bullet-point summaries using a Map-Reduce LangChain pipeline
- **Action Item Extraction** — Pull out tasks, owners, and deadlines from the transcript
- **Key Decisions** — Identify and list every decision made in the meeting
- **Open Questions** — Surface unresolved topics that need follow-up
- **RAG-powered Q&A** — Ask anything about the meeting; the system retrieves relevant context from ChromaDB and answers via Mistral AI
- **Export** — Download results as PDF or TXT in one click
- **Custom UI** — Dark-themed Streamlit interface with real-time progress tracking and tabbed results

---

## 🛠️ Tech Stack

| Layer | Technology |
|---|---|
| Speech-to-Text (English) | OpenAI Whisper (runs locally) |
| Speech-to-Text (Hindi/Hinglish) | Sarvam AI — `saaras:v2.5` |
| Audio Extraction | yt-dlp, pydub, FFmpeg |
| LLM | Mistral AI — `mistral-small-latest` |
| LLM Orchestration | LangChain LCEL (chains, prompts, parsers) |
| Embeddings | HuggingFace `all-MiniLM-L6-v2` |
| Vector Store | ChromaDB (local, persistent) |
| UI | Streamlit |
| PDF Export | ReportLab / fpdf2 |
| Environment | python-dotenv |

---

## 🏗️ Architecture & How It Works

```
Input (YouTube URL / Audio File)
        │
        ▼
┌─────────────────────┐
│   audio_processor   │  ← yt-dlp downloads audio, pydub converts & chunks into 10-min WAV files
└─────────────────────┘
        │
        ▼
┌─────────────────────┐
│     transcriber     │  ← Whisper (English) or Sarvam API (Hindi/Hinglish)
└─────────────────────┘     Sarvam chunks further split into 25s pieces (API limit)
        │
        ▼
┌──────────────────────────────────────────────┐
│              LangChain LCEL Chains            │
│                                              │
│  sammarize.py  → Map-Reduce summarization    │
│  extractor.py  → Action items, decisions,    │
│                  open questions              │
└──────────────────────────────────────────────┘
        │
        ▼
┌─────────────────────┐
│    vector_store     │  ← Transcript chunked (500 chars), embedded with HuggingFace,
└─────────────────────┘     stored in ChromaDB locally
        │
        ▼
┌─────────────────────┐
│     rag_engine      │  ← Retriever fetches top-4 relevant chunks → Mistral AI answers
└─────────────────────┘
        │
        ▼
┌─────────────────────┐
│       app.py        │  ← Streamlit UI — tabbed results, chat interface, export
└─────────────────────┘
```

### Step-by-step breakdown

**Step 1 — Audio Processing (`audio_processor.py`)**

- If given a YouTube URL, `yt-dlp` downloads the best audio stream and converts it to WAV via FFmpeg
- If given a local file, `pydub` converts it to mono 16kHz WAV (the format Whisper expects)
- The WAV file is then chunked into 10-minute pieces so large files can be processed without memory issues

**Step 2 — Transcription (`transcriber.py`)**

- For **English**: each chunk is sent to the locally loaded Whisper model (`small` by default, configurable via `.env`). No internet required.
- For **Hindi/Hinglish**: each chunk is further split into 25-second pieces (Sarvam's sync API limit) and sent to `https://api.sarvam.ai/speech-to-text-translate`, which transcribes AND translates to English in one call.
- All chunk transcripts are joined into one full transcript string.

**Step 3 — Summarization (`sammarize.py`)**

- Uses a **Map-Reduce** approach:
  - The transcript is split into 3000-character chunks with 200-character overlap using `RecursiveCharacterTextSplitter`
  - Each chunk is summarized independently via a Mistral AI chain (`map_chain`)
  - All partial summaries are combined and passed to a second chain that produces the final professional bullet-point summary
- A separate `generate_title()` chain generates a short meeting title (max 8 words) from the first 2000 characters of the transcript

**Step 4 — Extraction (`extractor.py`)**

- Three independent LangChain LCEL chains extract:
  - **Action items** — task, owner, deadline
  - **Key decisions** — what was decided
  - **Open questions** — unresolved topics needing follow-up
- All chains use `RunnablePassthrough` + `RunnableLambda` for clean LCEL composition with `StrOutputParser` for plain-text output

**Step 5 — Vector Store (`vector_store.py`)**

- The full transcript is split into 500-character chunks (50-char overlap)
- Each chunk becomes a `Document` object with metadata (`chunk_index`)
- HuggingFace `all-MiniLM-L6-v2` model generates dense embeddings locally (CPU)
- ChromaDB stores the vectors persistently in a local `vector_db/` folder under the collection name `meeting_transcript`

**Step 6 — RAG Q&A (`rag_engine.py`)**

- `build_rag_chain()` creates a full LCEL RAG pipeline:
  - A retriever fetches the top-4 most similar chunks from ChromaDB using cosine similarity
  - `format_docs()` joins them into a context string
  - A `ChatPromptTemplate` injects the context and the user's question
  - Mistral AI generates a grounded answer strictly based on the transcript context
- If the answer isn't in the transcript, the model is instructed to say so explicitly (no hallucination)

**Step 7 — Streamlit UI (`app.py`)**

- Custom dark-themed CSS with Syne, Inter, and JetBrains Mono fonts
- Sidebar handles input (URL / file upload) and language selection
- Real-time progress bar with status badges during pipeline execution
- Results shown in 5 tabs: Summary, Action Items, Key Decisions, Transcript, Chat
- Metrics row shows word count, action item count, decision count, question count
- Chat interface with persistent session history, user/bot bubbles, and clear button

---

## 📁 Project Structure

```
ai-meeting-assistant/
│
├── app.py                  # Streamlit UI — main entry point
├── main.py                 # CLI entry point (run without UI)
├── test.py                 # Quick test script for pipeline validation
├── requirements.txt        # All dependencies
├── .env                    # API keys (not committed)
├── .gitignore
│
├── core/
│   ├── transcriber.py      # Whisper + Sarvam transcription logic
│   ├── sammarize.py        # Map-reduce summarization + title generation
│   ├── extractor.py        # Action items, decisions, questions extraction
│   ├── rag_engine.py       # RAG chain builder and Q&A handler
│   └── vector_store.py     # ChromaDB vector store build/load/retrieve
│
└── utils/
    └── audio_processor.py  # YouTube download, WAV conversion, chunking
```

---

## ⚙️ Installation & Setup

### Prerequisites
- Python 3.10+
- [FFmpeg](https://ffmpeg.org/download.html) installed and added to PATH

### 1. Clone the repo
```bash
git clone https://github.com/KRSREDDY101/ai-meeting-assistant.git
cd ai-meeting-assistant
```

### 2. Create virtual environment
```bash
python -m venv .venv
.venv\Scripts\activate      # Windows
source .venv/bin/activate   # Mac/Linux
```

### 3. Install dependencies
```bash
pip install -r requirements.txt
```

### 4. Set up environment variables
Create a `.env` file in the root directory:
```
MISTRAL_API_KEY=your_mistral_api_key
SARVAM_API_KEY=your_sarvam_api_key       # Only needed for Hindi/Hinglish
WHISPER_MODEL=small                       # Options: tiny, base, small, medium, large
```

Get your free Mistral API key at [console.mistral.ai](https://console.mistral.ai)

### 5. Run the app
```bash
streamlit run app.py
```

Or use the CLI:
```bash
python main.py
```

---

## 🔑 Environment Variables

| Variable | Required | Description |
|---|---|---|
| `MISTRAL_API_KEY` | ✅ Yes | Mistral AI API key for LLM chains |
| `SARVAM_API_KEY` | Only for Hindi | Sarvam AI key for Hindi/Hinglish transcription |
| `WHISPER_MODEL` | No (default: small) | Whisper model size — larger = more accurate but slower |
| `SARVAM_STT_MODEL` | No (default: saaras:v2.5) | Sarvam model version |

---

## 💡 Design Decisions

**Why local Whisper instead of OpenAI's API?**
Privacy. Audio files are never sent to any external server for transcription. The Whisper model runs entirely on your machine.

**Why Mistral AI (free tier)?**
Accessible to everyone without a paid subscription. `mistral-small-latest` is fast and capable enough for structured extraction tasks.

**Why Map-Reduce for summarization?**
LLMs have context window limits. A 2-hour meeting transcript can exceed 50,000 tokens. Map-Reduce handles any length by summarizing chunks independently first, then combining.

**Why ChromaDB?**
Lightweight, runs locally with no server setup, and persists vectors to disk so the vector store survives between sessions.

**Why chunk audio into 10-minute pieces?**
Whisper loads the entire audio file into memory. Large files cause memory spikes. 10-minute chunks keep memory usage predictable and allow progress tracking per chunk.


---

## 📄 License

MIT
