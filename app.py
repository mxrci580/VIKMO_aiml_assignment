import html
import time
import streamlit as st
from assistant.agent import process_query
from assistant.tools import check_stock, create_order, find_parts_by_vehicle  # noqa: F401

# ── Page config ───────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="VIKMO Dealer Assistant",
    page_icon="🔩",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# ── Global CSS ────────────────────────────────────────────────────────────────
st.markdown("""
<style>
[data-testid="stAppViewContainer"] { background: #F8F9FA; }
[data-testid="stHeader"] { display: none; }
[data-testid="stSidebar"] { background: #fff; border-right: 1px solid #E5E7EB; }

.main-shell {
    display: flex; flex-direction: column;
    height: 100vh; max-width: 860px;
    margin: 0 auto; padding: 0 1rem;
}

/* ── Top bar ── */
.topbar {
    display: flex; align-items: center; gap: 12px;
    padding: 18px 0 14px; border-bottom: 1px solid #E5E7EB;
}
.topbar-icon {
    width: 36px; height: 36px; background: #1A1A2E;
    border-radius: 8px; display: flex;
    align-items: center; justify-content: center; font-size: 17px;
}
.topbar-title { font-size: 15px; font-weight: 600; color: #111827; letter-spacing: -0.2px; }
.topbar-sub   { font-size: 12px; color: #6B7280; margin-top: 1px; }
.status-dot   { width: 7px; height: 7px; background: #10B981; border-radius: 50%; margin-left: auto; }

/* ── Message bubbles ── */
.msg-row { display: flex; gap: 10px; margin-bottom: 20px; align-items: flex-start; }
.msg-row.user { flex-direction: row-reverse; }

.avatar {
    width: 30px; height: 30px; border-radius: 50%;
    display: flex; align-items: center; justify-content: center;
    font-size: 12px; font-weight: 600; flex-shrink: 0;
}
.avatar.bot  { background: #1A1A2E; color: #fff; }
.avatar.user { background: #E5E7EB; color: #374151; }

.bubble {
    max-width: 72%; padding: 11px 15px;
    border-radius: 14px; font-size: 14px;
    line-height: 1.6; color: #111827;
}
.bubble.bot  { background: #fff; border: 1px solid #E5E7EB; border-top-left-radius: 4px; }
.bubble.user { background: #1A1A2E; color: #F9FAFB; border-top-right-radius: 4px; }

/* ── Tool pill ── */
.tool-pill {
    display: inline-flex; align-items: center; gap: 6px;
    background: #F3F4F6; border: 1px solid #E5E7EB;
    border-radius: 20px; padding: 4px 10px;
    font-size: 12px; color: #6B7280; margin: 4px 0 6px;
}
.tool-pill .tool-name   { font-weight: 600; color: #374151; }
.tool-pill .tool-status { width: 6px; height: 6px; border-radius: 50%; background: #10B981; display: inline-block; }

/* ── Source cards ── */
.source-row  { display: flex; gap: 8px; flex-wrap: wrap; margin-top: 10px; }
.source-card { background: #F9FAFB; border: 1px solid #E5E7EB; border-radius: 8px; padding: 7px 11px; font-size: 12px; color: #374151; }
.source-card .src-label { color: #9CA3AF; font-size: 11px; }

/* ── Input row ── */
.input-wrap { padding: 12px 0 20px; border-top: 1px solid #E5E7EB; }

/* Streamlit input overrides */
[data-testid="stTextInput"] input {
    border-radius: 10px !important;
    border: 1px solid #D1D5DB !important;
    padding: 12px 16px !important;
    font-size: 14px !important;
    background: #fff !important;
    box-shadow: none !important;
    color: #111827 !important;
    -webkit-text-fill-color: #111827 !important;
    opacity: 1 !important;
}
[data-testid="stTextInput"] input:focus {
    border-color: #1A1A2E !important;
    box-shadow: 0 0 0 2px rgba(26,26,46,0.08) !important;
}
[data-testid="stTextInput"] input::placeholder {
    color: #9CA3AF !important;
    -webkit-text-fill-color: #9CA3AF !important;
    opacity: 1 !important;
}

/* Send button */
[data-testid="stButton"] > button {
    background: #1A1A2E !important; color: #fff !important;
    border-radius: 10px !important; border: none !important;
    padding: 10px 22px !important; font-size: 13px !important;
    font-weight: 500 !important; height: 46px !important; margin-top: 0 !important;
}
[data-testid="stButton"] > button:hover { background: #2D2D4E !important; }

/* ── Empty state ── */
.empty-state  { text-align: center; padding: 60px 20px; }
.empty-title  { font-size: 20px; font-weight: 600; color: #111827; margin-bottom: 8px; }
.empty-sub    { font-size: 14px; color: #6B7280; }

/* ── Sidebar ── */
.sidebar-section {
    font-size: 11px; font-weight: 600; color: #9CA3AF;
    text-transform: uppercase; letter-spacing: 0.6px; margin: 18px 0 8px;
}
.history-item {
    padding: 8px 10px; border-radius: 7px; font-size: 13px; color: #374151;
    cursor: pointer; margin-bottom: 2px; border: 1px solid transparent;
    white-space: nowrap; overflow: hidden; text-overflow: ellipsis;
}
.history-item:hover { background: #F3F4F6; border-color: #E5E7EB; }
</style>
""", unsafe_allow_html=True)


# ── Session state ─────────────────────────────────────────────────────────────
if "messages" not in st.session_state:
    st.session_state.messages = []
if "input_key" not in st.session_state:
    st.session_state.input_key = 0
if "pending_query" not in st.session_state:
    st.session_state.pending_query = None


# ── Sidebar ───────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("### 🔩 VIKMO")
    st.markdown("---")

    if st.button("＋  New conversation", use_container_width=True):
        st.session_state.messages = []
        st.session_state.pending_query = None
        st.rerun()

    if st.session_state.messages:
        st.markdown('<div class="sidebar-section">This session</div>', unsafe_allow_html=True)
        user_msgs = [m["content"] for m in st.session_state.messages if m["role"] == "user"]
        for msg in user_msgs[-6:]:
            preview = f"{msg[:48]}…" if len(msg) > 48 else msg
            st.markdown(f'<div class="history-item">💬 {html.escape(preview)}</div>', unsafe_allow_html=True)

    st.markdown("---")
    st.markdown('<div class="sidebar-section">Quick references</div>', unsafe_allow_html=True)
    st.markdown("**Common part categories**")
    for cat in ["Brakes", "Engine", "Filters", "Suspension", "Electrical", "Exhaust"]:
        st.caption(f"• {cat}")


# ── Top bar ───────────────────────────────────────────────────────────────────
st.markdown("""
<div class="topbar">
  <div class="topbar-icon">🔩</div>
  <div>
    <div class="topbar-title">VIKMO Dealer Assistant</div>
    <div class="topbar-sub">RAG · Gemini Function Calling · Forecasting</div>
  </div>
  <div class="status-dot" title="Online"></div>
</div>
""", unsafe_allow_html=True)


# ── Render a single message ───────────────────────────────────────────────────
def render_message(msg):
    role       = msg["role"]
    content    = msg.get("content", "")
    tool_calls = msg.get("tool_calls", [])
    sources    = msg.get("sources", [])

    if role == "user":
        safe = html.escape(content)
        st.markdown(f"""
        <div class="msg-row user">
          <div class="avatar user">You</div>
          <div class="bubble user">{safe}</div>
        </div>""", unsafe_allow_html=True)
        return

    # ── assistant bubble ──
    tools_html = ""
    for tc in tool_calls:
        icon = {"check_stock": "🔍", "find_parts_by_vehicle": "🚗", "create_order": "📦"}.get(tc.get("name", ""), "⚙️")
        name = html.escape(tc.get("name", "tool"))
        tools_html += f"""
        <div class="tool-pill">
          <span class="tool-status"></span>
          {icon} <span class="tool-name">{name}</span>
          <span style="color:#D1D5DB">·</span>
          <span>completed</span>
        </div>"""

    sources_html = ""
    if sources:
        cards = "".join(
            f'<div class="source-card">'
            f'<div class="src-label">{html.escape(str(s.get("label","")))} </div>'
            f'{html.escape(str(s.get("value","")))}</div>'
            for s in sources
        )
        sources_html = f'<div class="source-row">{cards}</div>'

    # Escape content but restore newlines as <br>
    content_html = html.escape(content).replace("\n", "<br>")

    st.markdown(f"""
    <div class="msg-row">
      <div class="avatar bot">V</div>
      <div class="bubble bot">
        {tools_html}
        {content_html}
        {sources_html}
      </div>
    </div>""", unsafe_allow_html=True)


# ── Chat history ──────────────────────────────────────────────────────────────
if not st.session_state.messages:
    st.markdown("""
    <div class="empty-state">
      <div class="empty-title">How can I help you today?</div>
      <div class="empty-sub">Ask about parts, check stock levels, or place an order.</div>
    </div>""", unsafe_allow_html=True)

    chips = [
        "Do you have brake pads for Bajaj Pulsar 150?",
        "Check stock for BRK-1002",
        "Find parts for Bajaj Pulsar 150",
        "Place an order for 10 units of BRK-1002 for ABC Motors",
    ]
    cols = st.columns(len(chips))
    for i, chip in enumerate(chips):
        with cols[i]:
            if st.button(chip, key=f"chip_{i}"):
                st.session_state.pending_query = chip
                st.rerun()
else:
    for msg in st.session_state.messages:
        render_message(msg)


# ── Process pending query ─────────────────────────────────────────────────────
if st.session_state.pending_query:
    query = st.session_state.pending_query
    st.session_state.pending_query = None

    st.session_state.messages.append({"role": "user", "content": query})
    render_message({"role": "user", "content": query})

    with st.spinner("Thinking…"):
        result = process_query(query)

    # Support both:
    #   process_query() returning a plain string, OR
    #   a dict with keys: response, tool_calls, sources
    if isinstance(result, str):
        bot_msg = {"role": "assistant", "content": result, "tool_calls": [], "sources": []}
    else:
        bot_msg = {
            "role": "assistant",
            "content": result.get("response", ""),
            "tool_calls": result.get("tool_calls", []),
            "sources": result.get("sources", []),
        }

    st.session_state.messages.append(bot_msg)
    render_message(bot_msg)


# ── Input bar ─────────────────────────────────────────────────────────────────
st.markdown('<div class="input-wrap">', unsafe_allow_html=True)
col_input, col_btn = st.columns([5, 1])

with col_input:
    user_input = st.text_input(
        label="",
        placeholder="Ask about a part, vehicle, or order…",
        key=f"chat_input_{st.session_state.input_key}",
        label_visibility="collapsed",
    )

with col_btn:
    send_clicked = st.button("Send →", key="send_btn")

st.markdown("</div>", unsafe_allow_html=True)

if (send_clicked or user_input) and user_input.strip():
    st.session_state.pending_query = user_input.strip()
    st.session_state.input_key += 1
    st.rerun()