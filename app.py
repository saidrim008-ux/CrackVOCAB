import streamlit as st
import pandas as pd
import random, json, base64
from datetime import date, timedelta
from pathlib import Path
import streamlit as st
import pandas as pd
import random, json
from datetime import date, timedelta
from pathlib import Path
st.markdown(
    f"""
    <style>
      /* Sidebar color */
      [data-testid="stSidebar"] {{
          background-color: {RUST} !important;
      }}

      /* Default text */
      html, body, .stApp {{
        color: #111 !important;
      }}

      /* Inputs (search, dropdown, date) */
      input, textarea, select, div[data-baseweb="select"], .stDateInput input {{
        background-color: #fff !important;
        color: #111 !important;
        border: 1px solid #ccc !important;
        border-radius: 10px !important;
      }}

      /* Buttons */
      div.stButton > button, .stButton button {{
        background: {SKY_BLUE} !important;
        color: #fff !important;
        border: none !important;
        border-radius: 12px !important;
        padding: 10px 16px !important;
        font-weight: 600 !important;
      }}
      div.stButton > button:hover, .stButton button:hover {{
        background: {SKY_BLUE_HOVER} !important;
      }}

      /* Checkbox / Mark as Learned */
      div.stCheckbox > label span, .stCheckbox input {{
        background: #fff !important;
        color: #111 !important;
        border: 2px solid {SKY_BLUE} !important;
        border-radius: 6px !important;
      }}
    </style>
    """,
    unsafe_allow_html=True
)

# ----------------- COLORS -----------------
RUST = "#d99072"        # lighter sidebar
BEIGE = "#e3b896"       # background for Home + Words
SKY_BLUE = "#38bdf8"    # main button color (sky blue)
SKY_BLUE_HOVER = "#0ea5e9"  # darker hover
# ------------------------------------------

# ---------- Global CSS ----------
st.set_page_config(page_title="crackVOCAB", page_icon="📘", layout="wide")

st.markdown(
    f"""
    <style>
    /* ... (all that CSS code I gave you) ... */
    </style>
    """,
    unsafe_allow_html=True
)

# ---------- Sidebar color ----------
def set_sidebar_color(color: str):
    st.markdown(
        f"""
        <style>
        [data-testid="stSidebar"] {{
            background-color: {color} !important;
        }}
        </style>
        """,
        unsafe_allow_html=True,
    )

set_sidebar_color(RUST)

# ---------- Page background helper ----------
def set_page_bg_color(color: str):
    st.markdown(
        f"""
        <style>
        .stApp {{
            background-color: {color} !important;
        }}
        </style>
        """,
        unsafe_allow_html=True
    )

# ---------- Example: set Home + Words to same beige ----------
current_page = st.session_state.get("page", "Home")  # depends how you route pages
if current_page in ["Home", "Words"]:
    set_page_bg_color(BEIGE)

# ===================== App setup =====================
st.set_page_config(page_title="crackVOCAB", page_icon="📘", layout="wide")

# ===================== Theme Colors (from your inspo) =====================
RUST = "#8a3f21"       # left image (sidebar color)
BEIGE = "#e3b896"      # right image (home page)
BLUE = "#2563eb"       # buttons
BLUE_HOVER = "#1e4fbf"

# ===================== Tiny CSS (shared) =====================
st.markdown(
    f"""
    <style>
      /* Do NOT set global background here. Each page sets its own. */
      .stApp {{ color: #111 !important; }}

      /* Headings + text */
      html, body, [class*="st-"], .stMarkdown, .stMarkdown p, .stMarkdown span {{
        color: #111 !important;
      }}
      h1, h2, h3, .stMarkdown h1, .stMarkdown h2 {{
        font-family: ui-sans-serif, system-ui, -apple-system, "Segoe UI", Roboto, "Helvetica Neue", Arial;
        color: #111 !important;
      }}

      /* Inputs: white box, dark text */
      .stTextInput > div > div input {{
        background: #fff !important;
        color: #111 !important;
        border: 1px solid #d1d5db !important;
        border-radius: 12px !important;
      }}

      /* Default buttons (Show Definition, Previous, Next) */
      div.stButton > button {{
        background: {BLUE};
        color: #fff !important;
        border: 0;
        padding: 10px 16px;
        border-radius: 12px;
        font-weight: 600;
      }}
      div.stButton > button:hover {{ background: {BLUE_HOVER}; }}

      /* Card look */
      .card {{
        background: #ffffffcc;
        border: 1px solid rgba(0,0,0,0.06);
        box-shadow: 0 8px 20px rgba(0,0,0,0.06);
        border-radius: 16px;
        padding: 1.1rem 1.2rem;
      }}

      /* Streak bar */
      .streak-wrap {{
        background: #e5edff;
        border-radius: 999px;
        height: 10px;
        width: 100%;
        overflow: hidden;
      }}
      .streak-fill {{
        background: {BLUE};
        height: 100%;
        transition: width 300ms ease;
      }}
      .muted {{ color: #5b6b7a !important; }}

      /* Special: Mark as Learned (same blue, pill) */
      .learn-btn button {{
        background: {BLUE} !important;
        color: #fff !important;
        border-radius: 22px !important;
        padding: 10px 18px !important;
      }}
      .learn-btn button:hover {{ background: {BLUE_HOVER} !important; }}

      /* Special: Home button (green) */
      .home-btn button {{
        background: #22c55e !important;
        color: #fff !important;
        border-radius: 10px !important;
        padding: 10px 16px !important;
        font-weight: 700 !important;
      }}
      .home-btn button:hover {{ background: #16a34a !important; }}
    </style>
    """,
    unsafe_allow_html=True
)

# ===================== Background helpers =====================
def set_sidebar_color(hex_color: str):
    st.markdown(
        f"""
        <style>
          section[data-testid="stSidebar"] {{
            background: {hex_color};
            color: #fff !important;
            border-right: 1px solid rgba(0,0,0,0.08);
          }}
          section[data-testid="stSidebar"] * {{ color: #fff !important; }}
        </style>
        """,
        unsafe_allow_html=True
    )

def set_page_bg_color(hex_color: str):
    st.markdown(
        f"""
        <style>
          .stApp {{ background: {hex_color}; }}
        </style>
        """,
        unsafe_allow_html=True
    )

def set_page_bg_image_local(image_file: str):
    # image_file should be 'bg_welcome.jpg' (or .png) in repo root
    with open(image_file, "rb") as f:
        encoded = base64.b64encode(f.read()).decode()
    st.markdown(
        f"""
        <style>
          .stApp {{
            background-image: url("data:image/jpg;base64,{encoded}");
            background-size: cover;
            background-attachment: fixed;
            background-position: center;
          }}
        </style>
        """,
        unsafe_allow_html=True
    )

# ===================== Config & data =====================
LEARNED_LIMIT = 10                 # recent pool for Quiz
PROGRESS_FILE = Path("progress.json")
STREAK_WINDOW = 30                 # visual window for streak bar

data = (
    pd.read_csv("words.csv")
      .dropna()
      .drop_duplicates(subset=["word"])
      .reset_index(drop=True)
)
TOTAL_WORDS = len(data)

# ===================== Persistence =====================
def load_progress():
    if PROGRESS_FILE.exists():
        try:
            return json.loads(PROGRESS_FILE.read_text(encoding="utf-8"))
        except Exception:
            pass
    return {"dates": [], "mastered_idxs": [], "name": None, "first_seen": None}

def save_progress(p):
    PROGRESS_FILE.write_text(json.dumps(p, ensure_ascii=False, indent=2), encoding="utf-8")

progress = load_progress()

def mark_active_today():
    today = str(date.today())
    if today not in progress["dates"]:
        progress["dates"].append(today)
        save_progress(progress)

def add_mastered(idx: int):
    if idx not in progress["mastered_idxs"]:
        progress["mastered_idxs"].append(idx)
        save_progress(progress)

# ===================== Streak helpers =====================
def consecutive_streak(dates_list):
    s = set(dates_list)
    streak, d = 0, date.today()
    while str(d) in s:
        streak += 1
        d -= timedelta(days=1)
    return streak

def streak_bar_html(streak: int, window: int = STREAK_WINDOW):
    pct = min(streak, window) / max(1, window) * 100
    return f"""
      <div class="streak-wrap"><div class="streak-fill" style="width:{pct:.2f}%"></div></div>
      <div style="display:flex;justify-content:space-between;align-items:center;margin-top:6px;">
        <div style="font-weight:700;">🔥 {streak}-day streak</div>
        <div class="muted">view last {window} days</div>
      </div>
    """

# ===================== Session =====================
if "mode" not in st.session_state:
    st.session_state.mode = "Welcome"   # first screen
if "index" not in st.session_state:
    st.session_state.index = 0
if "learned_recent" not in st.session_state:
    st.session_state.learned_recent = []
if "quiz" not in st.session_state:
    st.session_state.quiz = {"q": None, "score": 0, "num": 0}

# ===================== Sidebar (hidden on Welcome) =====================
def render_sidebar():
    st.session_state.mode = st.sidebar.radio(
        "Go to", ["Home", "Words", "Quiz"],
        index=["Home","Words","Quiz"].index(st.session_state.mode) if st.session_state.mode in ["Home","Words","Quiz"] else 0
    )

    if st.session_state.mode != "Home":
        st.sidebar.markdown("### 📚 Word list")
        st.sidebar.write(f"Total words: **{TOTAL_WORDS}**")
        q = st.sidebar.text_input("Search")
        labels = [f"{w} ({p})" for w, p in zip(data["word"], data["part_of_speech"])]
        if q:
            filtered = [(i, lbl) for i, lbl in enumerate(labels) if q.lower() in lbl.lower()]
        else:
            filtered = list(enumerate(labels))
        if filtered:
            idx_opts = [i for i, _ in filtered]
            lbl_opts = [lbl for _, lbl in filtered]
            sel = st.sidebar.selectbox("Select a word", lbl_opts, index=0, key="sel_word")
            st.session_state.index = idx_opts[lbl_opts.index(sel)]
        else:
            st.sidebar.info("No words match your search.")

    with st.sidebar:
        st.markdown("---")
        streak = consecutive_streak(progress["dates"])
        st.subheader("🔥 Streak")
        st.markdown(streak_bar_html(streak), unsafe_allow_html=True)

        mastered_count = len(progress["mastered_idxs"])
        st.subheader("📈 Progress")
        st.write(f"Words mastered: **{mastered_count} / {TOTAL_WORDS}**")
        st.progress((mastered_count / TOTAL_WORDS) if TOTAL_WORDS else 0.0)

        st.write(f"Quiz pool (recent): **{len(st.session_state.learned_recent)} / {LEARNED_LIMIT}**")
        st.markdown('<div class="home-btn">', unsafe_allow_html=True)
        if st.button("🏠 Home", key="home_sidebar"):
            st.session_state.mode = "Home"; st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)

# ===================== Pages =====================

# ---- Welcome (nickname) ----
if st.session_state.mode == "Welcome":
    set_sidebar_color(RUST)                 # rust sidebar on first screen too
    set_page_bg_image_local("bg_welcome.jpg")  # <-- your image (rename file accordingly)

    st.markdown("<div class='card'>", unsafe_allow_html=True)
    st.title("Let’s master vocabulary together 💪")
    st.write("Enter your **name or nickname** to personalize your experience.")

    default_name = progress.get("name") or ""
    nickname = st.text_input("Enter your name or nickname", value=default_name, placeholder="e.g., Youssef / Laila / Ayman")

    if progress.get("name"):
        st.caption(f"Saved name: **{progress['name']}**")

    if st.button("Go →"):
        clean = nickname.strip()
        if clean:
            progress["name"] = clean
            if not progress.get("first_seen"):
                progress["first_seen"] = str(date.today())
            save_progress(progress)
            st.session_state.mode = "Home"
            st.rerun()
        else:
            st.warning("Please enter your name or nickname to continue.")
    st.markdown("</div>", unsafe_allow_html=True)

# ---- Home (intro) ----
elif st.session_state.mode == "Home":
    set_sidebar_color(RUST)
    set_page_bg_color(BEIGE)               # beige background

    render_sidebar()

    user = progress.get("name") or "there"
    st.markdown("<div class='card'>", unsafe_allow_html=True)
    st.header(f"Hi there, **{user}** — welcome to crackVOCAB 👋")
    st.write(
        """
**crackVOCAB** helps you master **advanced English vocabulary** with bilingual
(English–French–Arabic) explanations — built for focus and flow.

**How it works**
1) Open **Words** (left sidebar), pick any word (use search or scroll).
2) Click **Show Definition**, then **Mark as Learned** when you’re ready.
3) Your **streak** (🔥 smooth line) and **lifetime progress** update automatically.
4) Use **Quiz** to practice only your **recently learned** words (last 10 by default).
        """
    )
    st.button("Start learning →", on_click=lambda: st.session_state.update({"mode": "Words"}))
    st.markdown("</div>", unsafe_allow_html=True)

# ---- Words (Learn) ----
elif st.session_state.mode == "Words":
    set_page_bg_color(BEIGE)   # <<< this sets beige background
    set_sidebar_color(RUST)
    # gentle default gradient for content area
    st.markdown(
        """
        <style>.stApp{background: linear-gradient(180deg, #f6fbff 0%, #eef3ff 100%);}</style>
        """, unsafe_allow_html=True
    )

    render_sidebar()

    row = data.iloc[st.session_state.index]
    st.header("Words")
    st.subheader(f"{row['word']} ({row['part_of_speech']})")

    if st.button("Show Definition"):
        st.markdown("<div class='card'>", unsafe_allow_html=True)
        st.write(f"**Definition:** {row['definition']}")
        st.write(f"**French:** {row['french']}")
        st.write(f"**Arabic:** {row['arabic']}")
        st.write(f"**Example:** {row['example']}")
        st.markdown("</div>", unsafe_allow_html=True)

    c1, c2, c3 = st.columns(3)
    if c1.button("⬅️ Previous"):
        st.session_state.index = (st.session_state.index - 1) % TOTAL_WORDS
        st.rerun()

    st.markdown('<div class="learn-btn">', unsafe_allow_html=True)
    if c2.button("Mark as Learned ✅", key="learn_btn", help="Adds to streak, mastered list, and quiz pool"):
        mark_active_today()
        if st.session_state.index not in st.session_state.learned_recent:
            st.session_state.learned_recent.insert(0, st.session_state.index)
            st.session_state.learned_recent = st.session_state.learned_recent[:LEARNED_LIMIT]
        add_mastered(st.session_state.index)
        st.toast("Added to learned + streak updated")
        st.rerun()
    st.markdown('</div>', unsafe_allow_html=True)

    if c3.button("Next ➡️"):
        st.session_state.index = (st.session_state.index + 1) % TOTAL_WORDS
        st.rerun()

# ---- Quiz ----
else:
    set_sidebar_color(RUST)
    st.markdown(
        """
        <style>.stApp{background: linear-gradient(180deg, #f6fbff 0%, #eef3ff 100%);}</style>
        """, unsafe_allow_html=True
    )

    render_sidebar()

    pool = st.session_state.learned_recent
    st.header("Quiz")
    if not pool:
        st.info("Your recent learned pool is empty. Go to **Words** and mark some items ✅.")
    else:
        if st.session_state.quiz["q"] is None:
            i = random.choice(pool)
            row = data.iloc[i]
            others = [j for j in pool if j != i]
            pick = random.sample(others, k=min(3, len(others))) if others else []
            choices = [row["word"]] + [data.iloc[j]["word"] for j in pick]
            random.shuffle(choices)
            st.session_state.quiz["q"] = {
                "prompt": f'Which word matches this definition?\n\n**{row["definition"]}**',
                "choices": choices,
                "correct": choices.index(row["word"]),
                "row": row,
            }

        q = st.session_state.quiz["q"]
        st.subheader(f"From your last {len(pool)} learned words • Q{st.session_state.quiz['num']+1}")
        st.markdown(q["prompt"])
        choice = st.radio("Choose one:", q["choices"], index=None, key=f"q{st.session_state.quiz['num']}")

        c1, c2 = st.columns(2)
        if c1.button("Check"):
            if choice is None:
                st.warning("Pick an answer first 🙂")
            else:
                if q["choices"].index(choice) == q["correct"]:
                    st.success("✅ Correct!")
                    st.session_state.quiz["score"] += 1
                else:
                    st.error(f"❌ Correct answer: **{q['choices'][q['correct']]}**")
                with st.expander("Explanation"):
                    r = q["row"]
                    st.write(f"**Definition:** {r['definition']}")
                    st.write(f"**French:** {r['french']}")
                    st.write(f"**Arabic:** {r['arabic']}")
                    st.write(f"**Example:** {r['example']}")
                mark_active_today()

        if c2.button("Next Question ➡️"):
            st.session_state.quiz["num"] += 1
            st.session_state.quiz["q"] = None
            st.rerun()

        st.info(f"Score: **{st.session_state.quiz['score']}** / {st.session_state.quiz['num']}")
