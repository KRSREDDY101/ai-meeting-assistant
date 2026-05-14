import streamlit as st
import os
import tempfile
from dotenv import load_dotenv

load_dotenv()

# ── Page config ────────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="MeetMind – AI Meeting Assistant",
    page_icon="🎙️",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── Custom CSS ─────────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Syne:wght@400;600;700;800&family=JetBrains+Mono:wght@400;500&family=Inter:wght@300;400;500&display=swap');

/* ── Root variables ── */
:root {
    --bg:        #0d0f14;
    --surface:   #13161e;
    --border:    #1f2433;
    --accent:    #00e5a0;
    --accent2:   #5b6af5;
    --warn:      #f5a623;
    --danger:    #f55b5b;
    --text:      #e8eaf0;
    --muted:     #6b7280;
    --radius:    12px;
}

/* ── Global reset ── */
html, body, [class*="css"] {
    font-family: 'Inter', sans-serif;
    background-color: var(--bg) !important;
    color: var(--text) !important;
}

/* ── Hide Streamlit chrome ── */
#MainMenu, footer, header { visibility: hidden; }
.block-container { padding: 2rem 2.5rem 4rem !important; max-width: 1200px; }

/* ── Sidebar ── */
section[data-testid="stSidebar"] {
    background: var(--surface) !important;
    border-right: 1px solid var(--border) !important;
}
section[data-testid="stSidebar"] .block-container { padding: 1.5rem 1.2rem !important; }

/* ── Header brand ── */
.brand {
    font-family: 'Syne', sans-serif;
    font-size: 2.6rem;
    font-weight: 800;
    letter-spacing: -1px;
    line-height: 1;
    background: linear-gradient(135deg, var(--accent) 0%, var(--accent2) 100%);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
}
.brand-sub {
    font-size: 0.8rem;
    color: var(--muted);
    letter-spacing: 3px;
    text-transform: uppercase;
    font-family: 'JetBrains Mono', monospace;
    margin-top: 2px;
}

/* ── Section labels ── */
.section-label {
    font-family: 'JetBrains Mono', monospace;
    font-size: 0.68rem;
    letter-spacing: 3px;
    text-transform: uppercase;
    color: var(--accent);
    margin-bottom: 10px;
    display: flex;
    align-items: center;
    gap: 8px;
}
.section-label::after {
    content: '';
    flex: 1;
    height: 1px;
    background: var(--border);
}

/* ── Cards ── */
.card {
    background: var(--surface);
    border: 1px solid var(--border);
    border-radius: var(--radius);
    padding: 1.4rem 1.6rem;
    margin-bottom: 1rem;
    transition: border-color 0.2s;
}
.card:hover { border-color: #2a3050; }

.card-accent { border-left: 3px solid var(--accent); }
.card-blue   { border-left: 3px solid var(--accent2); }
.card-warn   { border-left: 3px solid var(--warn); }
.card-danger { border-left: 3px solid var(--danger); }

/* ── Transcript box ── */
.transcript-box {
    background: #0a0c10;
    border: 1px solid var(--border);
    border-radius: var(--radius);
    padding: 1.2rem 1.4rem;
    font-family: 'JetBrains Mono', monospace;
    font-size: 0.82rem;
    line-height: 1.8;
    color: #9da8c0;
    max-height: 280px;
    overflow-y: auto;
    white-space: pre-wrap;
}
.transcript-box::-webkit-scrollbar { width: 4px; }
.transcript-box::-webkit-scrollbar-thumb { background: var(--border); border-radius: 4px; }

/* ── Bullet items ── */
.bullet-item {
    display: flex;
    gap: 10px;
    align-items: flex-start;
    padding: 8px 0;
    border-bottom: 1px solid var(--border);
    font-size: 0.9rem;
    line-height: 1.5;
}
.bullet-item:last-child { border-bottom: none; }
.bullet-dot {
    width: 6px;
    height: 6px;
    border-radius: 50%;
    margin-top: 7px;
    flex-shrink: 0;
}

/* ── Chat ── */
.chat-wrap {
    display: flex;
    flex-direction: column;
    gap: 12px;
    max-height: 420px;
    overflow-y: auto;
    padding-right: 6px;
    margin-bottom: 1rem;
}
.chat-wrap::-webkit-scrollbar { width: 4px; }
.chat-wrap::-webkit-scrollbar-thumb { background: var(--border); border-radius: 4px; }

.chat-bubble {
    padding: 10px 14px;
    border-radius: 10px;
    font-size: 0.88rem;
    line-height: 1.6;
    max-width: 85%;
}
.user-bubble {
    background: #1a2040;
    border: 1px solid var(--accent2);
    margin-left: auto;
    text-align: right;
}
.bot-bubble {
    background: #0f1a14;
    border: 1px solid var(--accent);
    margin-right: auto;
}
.bubble-label {
    font-family: 'JetBrains Mono', monospace;
    font-size: 0.65rem;
    letter-spacing: 2px;
    text-transform: uppercase;
    margin-bottom: 4px;
    opacity: 0.5;
}

/* ── Status badge ── */
.status-badge {
    display: inline-flex;
    align-items: center;
    gap: 6px;
    background: #0f1a14;
    border: 1px solid var(--accent);
    border-radius: 20px;
    padding: 4px 12px;
    font-size: 0.75rem;
    font-family: 'JetBrains Mono', monospace;
    color: var(--accent);
}
.status-dot {
    width: 6px; height: 6px;
    background: var(--accent);
    border-radius: 50%;
    animation: pulse 1.5s infinite;
}
@keyframes pulse {
    0%, 100% { opacity: 1; }
    50%       { opacity: 0.3; }
}

/* ── Streamlit widget overrides ── */
.stTextInput > div > div > input,
.stSelectbox > div > div,
.stTextArea > div > div > textarea {
    background: var(--surface) !important;
    border: 1px solid var(--border) !important;
    border-radius: 8px !important;
    color: var(--text) !important;
    font-family: 'Inter', sans-serif !important;
}
.stTextInput > div > div > input:focus,
.stTextArea > div > div > textarea:focus {
    border-color: var(--accent) !important;
    box-shadow: 0 0 0 2px rgba(0,229,160,0.15) !important;
}

.stButton > button {
    background: linear-gradient(135deg, var(--accent), #00b87a) !important;
    color: #0d0f14 !important;
    font-family: 'Syne', sans-serif !important;
    font-weight: 700 !important;
    font-size: 0.9rem !important;
    border: none !important;
    border-radius: 8px !important;
    padding: 0.55rem 1.6rem !important;
    transition: opacity 0.2s, transform 0.1s !important;
}
.stButton > button:hover {
    opacity: 0.88 !important;
    transform: translateY(-1px) !important;
}
.stButton > button:active { transform: translateY(0) !important; }

/* Secondary button */
.sec-btn > button {
    background: var(--surface) !important;
    color: var(--text) !important;
    border: 1px solid var(--border) !important;
}
.sec-btn > button:hover { border-color: var(--accent2) !important; }

/* ── Tab overrides ── */
.stTabs [data-baseweb="tab-list"] {
    background: var(--surface);
    border-radius: 10px;
    border: 1px solid var(--border);
    padding: 4px;
    gap: 2px;
}
.stTabs [data-baseweb="tab"] {
    background: transparent !important;
    color: var(--muted) !important;
    font-family: 'Syne', sans-serif !important;
    font-weight: 600 !important;
    border-radius: 7px !important;
    padding: 6px 18px !important;
}
.stTabs [aria-selected="true"] {
    background: var(--bg) !important;
    color: var(--text) !important;
}

/* ── File uploader ── */
[data-testid="stFileUploader"] {
    background: var(--surface) !important;
    border: 1px dashed var(--border) !important;
    border-radius: var(--radius) !important;
}

/* ── Divider ── */
hr { border-color: var(--border) !important; margin: 1.5rem 0 !important; }

/* ── Metric cards ── */
.metric-row { display: flex; gap: 12px; margin-bottom: 1.2rem; }
.metric-card {
    flex: 1;
    background: var(--surface);
    border: 1px solid var(--border);
    border-radius: var(--radius);
    padding: 1rem 1.2rem;
    text-align: center;
}
.metric-val {
    font-family: 'Syne', sans-serif;
    font-size: 2rem;
    font-weight: 800;
    color: var(--accent);
}
.metric-lbl {
    font-size: 0.72rem;
    color: var(--muted);
    text-transform: uppercase;
    letter-spacing: 1.5px;
    font-family: 'JetBrains Mono', monospace;
}
</style>
""", unsafe_allow_html=True)


# ── Session state init ──────────────────────────────────────────────────────────
for key in ["result", "chat_history", "processing", "pipeline_done"]:
    if key not in st.session_state:
        st.session_state[key] = None if key in ["result"] else ([] if key == "chat_history" else False)


# ── Sidebar ─────────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown('<div class="brand">MeetMind</div>', unsafe_allow_html=True)
    st.markdown('<div class="brand-sub">AI Meeting Assistant</div>', unsafe_allow_html=True)
    st.markdown("<br>", unsafe_allow_html=True)

    st.markdown('<div class="section-label">Input Source</div>', unsafe_allow_html=True)

    input_mode = st.radio(
        "Source type",
        ["YouTube URL", "Upload File"],
        label_visibility="collapsed"
    )

    source_value = None

    if input_mode == "YouTube URL":
        yt_url = st.text_input(
            "YouTube URL",
            placeholder="https://youtube.com/watch?v=...",
            label_visibility="collapsed"
        )
        source_value = yt_url.strip() if yt_url else None
    else:
        uploaded = st.file_uploader(
            "Upload audio/video",
            type=["mp3", "mp4", "wav", "m4a", "webm"],
            label_visibility="collapsed"
        )
        if uploaded:
            tmp = tempfile.NamedTemporaryFile(delete=False, suffix=os.path.splitext(uploaded.name)[1])
            tmp.write(uploaded.read())
            tmp.flush()
            source_value = tmp.name

    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown('<div class="section-label">Language</div>', unsafe_allow_html=True)

    language = st.selectbox(
        "Language",
        ["english", "hinglish"],
        label_visibility="collapsed"
    )

    st.markdown("<br>", unsafe_allow_html=True)

    run_btn = st.button("⚡ Run Pipeline", use_container_width=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # Export section — only shown after pipeline runs
    if st.session_state.pipeline_done and st.session_state.result:
        st.markdown('<div class="section-label">Export</div>', unsafe_allow_html=True)
        result = st.session_state.result

        # TXT export
        txt_content = f"""MEETMIND — MEETING REPORT
{'='*60}

TITLE: {result['title']}

SUMMARY:
{result['summary']}

ACTION ITEMS:
{result['action_items']}

KEY DECISIONS:
{result['key_decisions']}

OPEN QUESTIONS:
{result['open_questions']}

FULL TRANSCRIPT:
{result['transcript']}
"""
        st.download_button(
            "📄 Export TXT",
            data=txt_content,
            file_name="meeting_report.txt",
            mime="text/plain",
            use_container_width=True
        )

        # PDF export
        try:
            from fpdf import FPDF

            def build_pdf(r):
                pdf = FPDF()
                pdf.add_page()
                pdf.set_font("Helvetica", "B", 20)
                pdf.set_text_color(0, 229, 160)
                pdf.cell(0, 12, "MeetMind — Meeting Report", ln=True)
                pdf.set_text_color(200, 200, 200)
                pdf.set_font("Helvetica", "B", 14)
                pdf.cell(0, 10, r["title"], ln=True)
                pdf.ln(4)

                for section, content in [
                    ("Summary", r["summary"]),
                    ("Action Items", r["action_items"]),
                    ("Key Decisions", r["key_decisions"]),
                    ("Open Questions", r["open_questions"]),
                    ("Full Transcript", r["transcript"]),
                ]:
                    pdf.set_font("Helvetica", "B", 11)
                    pdf.set_text_color(0, 200, 140)
                    pdf.cell(0, 8, section, ln=True)
                    pdf.set_font("Helvetica", "", 9)
                    pdf.set_text_color(180, 180, 180)
                    pdf.multi_cell(0, 5, str(content))
                    pdf.ln(4)

                return pdf.output(dest="S").encode("latin-1")

            pdf_bytes = build_pdf(result)
            st.download_button(
                "📑 Export PDF",
                data=pdf_bytes,
                file_name="meeting_report.pdf",
                mime="application/pdf",
                use_container_width=True
            )
        except Exception:
            st.caption("Install fpdf2 for PDF export")

    st.markdown("<br><br>", unsafe_allow_html=True)
    st.markdown(
        '<div style="font-size:0.7rem;color:#3a4060;font-family:JetBrains Mono,monospace;text-align:center">powered by Whisper · Mistral · LangChain</div>',
        unsafe_allow_html=True
    )


# ── Main area ───────────────────────────────────────────────────────────────────

# Header
col_h1, col_h2 = st.columns([3, 1])
with col_h1:
    st.markdown('<div class="brand" style="font-size:2rem">AI Meeting Assistant</div>', unsafe_allow_html=True)
    st.markdown(
        '<div style="color:#6b7280;font-size:0.88rem;margin-top:4px">Transcribe · Summarise · Extract · Chat with your meetings</div>',
        unsafe_allow_html=True
    )
with col_h2:
    if st.session_state.pipeline_done:
        st.markdown(
            '<div style="text-align:right;padding-top:8px"><span class="status-badge"><span class="status-dot"></span>Analysis Ready</span></div>',
            unsafe_allow_html=True
        )

st.markdown("<hr>", unsafe_allow_html=True)


# ── Pipeline execution ──────────────────────────────────────────────────────────
if run_btn:
    if not source_value:
        st.error("⚠️  Please provide a YouTube URL or upload a file first.")
    else:
        with st.spinner(""):
            progress_bar = st.progress(0)
            status_text  = st.empty()

            try:
                from utils.audio_processor import process_input
                from core.transcriber import transcribe_all
                from core.sammarize import summarize, generate_title
                from core.extractor import extract_action_items, extract_key_decisions, extract_questions
                from core.rag_engine import build_rag_chain

                status_text.markdown(
                    '<div class="status-badge"><span class="status-dot"></span>Processing audio...</div>',
                    unsafe_allow_html=True
                )
                chunks = process_input(source_value)
                progress_bar.progress(20)

                status_text.markdown(
                    '<div class="status-badge"><span class="status-dot"></span>Transcribing with Whisper...</div>',
                    unsafe_allow_html=True
                )
                transcript = transcribe_all(chunks, language)
                progress_bar.progress(45)

                status_text.markdown(
                    '<div class="status-badge"><span class="status-dot"></span>Generating summary...</div>',
                    unsafe_allow_html=True
                )
                title   = generate_title(transcript)
                summary = summarize(transcript)
                progress_bar.progress(65)

                status_text.markdown(
                    '<div class="status-badge"><span class="status-dot"></span>Extracting insights...</div>',
                    unsafe_allow_html=True
                )
                action_items = extract_action_items(transcript)
                decisions    = extract_key_decisions(transcript)
                questions    = extract_questions(transcript)
                progress_bar.progress(82)

                status_text.markdown(
                    '<div class="status-badge"><span class="status-dot"></span>Building RAG index...</div>',
                    unsafe_allow_html=True
                )
                rag_chain = build_rag_chain(transcript)
                progress_bar.progress(100)
                status_text.empty()
                progress_bar.empty()

                st.session_state.result = {
                    "title":        title,
                    "transcript":   transcript,
                    "summary":      summary,
                    "action_items": action_items,
                    "key_decisions": decisions,
                    "open_questions": questions,
                    "rag_chain":    rag_chain,
                }
                st.session_state.pipeline_done = True
                st.session_state.chat_history  = []
                st.rerun()

            except Exception as e:
                progress_bar.empty()
                status_text.empty()
                st.error(f"Pipeline error: {e}")


# ── Results display ─────────────────────────────────────────────────────────────
if st.session_state.pipeline_done and st.session_state.result:
    result = st.session_state.result

    # Metrics row
    word_count   = len(result["transcript"].split())
    action_count = len([l for l in str(result["action_items"]).split("\n") if l.strip()])
    dec_count    = len([l for l in str(result["key_decisions"]).split("\n") if l.strip()])
    q_count      = len([l for l in str(result["open_questions"]).split("\n") if l.strip()])

    st.markdown(f"""
    <div class="metric-row">
        <div class="metric-card">
            <div class="metric-val">{word_count:,}</div>
            <div class="metric-lbl">Words Transcribed</div>
        </div>
        <div class="metric-card">
            <div class="metric-val">{action_count}</div>
            <div class="metric-lbl">Action Items</div>
        </div>
        <div class="metric-card">
            <div class="metric-val">{dec_count}</div>
            <div class="metric-lbl">Key Decisions</div>
        </div>
        <div class="metric-card">
            <div class="metric-val">{q_count}</div>
            <div class="metric-lbl">Open Questions</div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # Meeting title
    st.markdown(f"""
    <div class="card card-accent">
        <div style="font-family:'JetBrains Mono',monospace;font-size:0.65rem;color:#00e5a0;letter-spacing:2px;text-transform:uppercase;margin-bottom:6px">Meeting Title</div>
        <div style="font-family:'Syne',sans-serif;font-size:1.3rem;font-weight:700">{result['title']}</div>
    </div>
    """, unsafe_allow_html=True)

    # Tabs
    tab1, tab2, tab3, tab4, tab5 = st.tabs(["📋 Summary", "✅ Actions", "🔑 Decisions", "📄 Transcript", "💬 Chat"])

    # ── Tab 1: Summary ──
    with tab1:
        st.markdown('<div class="section-label">Meeting Summary</div>', unsafe_allow_html=True)
        st.markdown(f'<div class="card">{result["summary"]}</div>', unsafe_allow_html=True)

        st.markdown('<div class="section-label">Open Questions</div>', unsafe_allow_html=True)
        lines = [l.strip() for l in str(result["open_questions"]).split("\n") if l.strip()]
        items_html = "".join([
            f'<div class="bullet-item"><span class="bullet-dot" style="background:#f5a623"></span><span>{l}</span></div>'
            for l in lines
        ])
        st.markdown(f'<div class="card card-warn">{items_html}</div>', unsafe_allow_html=True)

    # ── Tab 2: Action Items ──
    with tab2:
        st.markdown('<div class="section-label">Action Items</div>', unsafe_allow_html=True)
        lines = [l.strip() for l in str(result["action_items"]).split("\n") if l.strip()]
        items_html = "".join([
            f'<div class="bullet-item"><span class="bullet-dot" style="background:#00e5a0"></span><span>{l}</span></div>'
            for l in lines
        ])
        st.markdown(f'<div class="card card-accent">{items_html}</div>', unsafe_allow_html=True)

    # ── Tab 3: Key Decisions ──
    with tab3:
        st.markdown('<div class="section-label">Key Decisions</div>', unsafe_allow_html=True)
        lines = [l.strip() for l in str(result["key_decisions"]).split("\n") if l.strip()]
        items_html = "".join([
            f'<div class="bullet-item"><span class="bullet-dot" style="background:#5b6af5"></span><span>{l}</span></div>'
            for l in lines
        ])
        st.markdown(f'<div class="card card-blue">{items_html}</div>', unsafe_allow_html=True)

    # ── Tab 4: Transcript ──
    with tab4:
        st.markdown('<div class="section-label">Full Transcript</div>', unsafe_allow_html=True)
        st.markdown(
            f'<div class="transcript-box">{result["transcript"]}</div>',
            unsafe_allow_html=True
        )

    # ── Tab 5: Chat ──
    with tab5:
        st.markdown('<div class="section-label">Chat with your Meeting</div>', unsafe_allow_html=True)

        # Chat history
        if st.session_state.chat_history:
            bubbles = ""
            for msg in st.session_state.chat_history:
                if msg["role"] == "user":
                    bubbles += f'''
                    <div class="chat-bubble user-bubble">
                        <div class="bubble-label">You</div>
                        {msg["content"]}
                    </div>'''
                else:
                    bubbles += f'''
                    <div class="chat-bubble bot-bubble">
                        <div class="bubble-label">MeetMind</div>
                        {msg["content"]}
                    </div>'''
            st.markdown(f'<div class="chat-wrap">{bubbles}</div>', unsafe_allow_html=True)
        else:
            st.markdown(
                '<div style="color:#3a4060;font-size:0.85rem;padding:1rem 0;font-family:JetBrains Mono,monospace">Ask anything about your meeting — action owners, decisions, topics discussed...</div>',
                unsafe_allow_html=True
            )

        # Input row
        c1, c2 = st.columns([5, 1])
        with c1:
            question = st.text_input(
                "Ask a question",
                placeholder="Who is responsible for the design review?",
                key="chat_input",
                label_visibility="collapsed"
            )
        with c2:
            ask_btn = st.button("Ask →", use_container_width=True)

        if ask_btn and question.strip():
            try:
                from core.rag_engine import ask_question
                answer = ask_question(result["rag_chain"], question.strip())
                st.session_state.chat_history.append({"role": "user",      "content": question.strip()})
                st.session_state.chat_history.append({"role": "assistant", "content": answer})
                st.rerun()
            except Exception as e:
                st.error(f"RAG error: {e}")

        # Clear chat
        if st.session_state.chat_history:
            if st.button("🗑 Clear chat", key="clear_chat"):
                st.session_state.chat_history = []
                st.rerun()


# ── Empty state ─────────────────────────────────────────────────────────────────
else:
    st.markdown("""
    <div style="text-align:center;padding:5rem 2rem">
        <div style="font-size:4rem;margin-bottom:1rem">🎙️</div>
        <div style="font-family:'Syne',sans-serif;font-size:1.6rem;font-weight:700;margin-bottom:0.5rem">Ready to analyse your meeting</div>
        <div style="color:#6b7280;font-size:0.9rem;max-width:420px;margin:0 auto;line-height:1.7">
            Paste a YouTube URL or upload an audio/video file in the sidebar,
            choose the language, and hit <strong style="color:#00e5a0">Run Pipeline</strong>.
        </div>
        <div style="margin-top:3rem;display:flex;justify-content:center;gap:2rem;flex-wrap:wrap">
            <div style="text-align:center">
                <div style="font-size:1.8rem">🔊</div>
                <div style="font-size:0.75rem;color:#6b7280;margin-top:6px;font-family:JetBrains Mono,monospace">LOCAL WHISPER</div>
            </div>
            <div style="text-align:center">
                <div style="font-size:1.8rem">🤖</div>
                <div style="font-size:0.75rem;color:#6b7280;margin-top:6px;font-family:JetBrains Mono,monospace">MISTRAL AI</div>
            </div>
            <div style="text-align:center">
                <div style="font-size:1.8rem">🔍</div>
                <div style="font-size:0.75rem;color:#6b7280;margin-top:6px;font-family:JetBrains Mono,monospace">RAG PIPELINE</div>
            </div>
            <div style="text-align:center">
                <div style="font-size:1.8rem">📤</div>
                <div style="font-size:0.75rem;color:#6b7280;margin-top:6px;font-family:JetBrains Mono,monospace">PDF / TXT EXPORT</div>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)