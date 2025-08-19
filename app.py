# app.py — crackVOCAB (welcome → sidebar layout, beach theme)

import streamlit as st
import pandas as pd
import random, json
from datetime import date, timedelta
from pathlib import Path
# ---------------------------
# Load progress or create new
# ---------------------------
import os, json
from datetime import date

PROGRESS_FILE = "progress.json"

def load_progress():
    if os.path.exists(PROGRESS_FILE):
        with open(PROGRESS_FILE, "r") as f:
            try:
                return json.load(f)
            except:
                return {}
    return {}

def save_progress(progress):
    with open(PROGRESS_FILE, "w") as f:
        json.dump(progress, f)

# Always start with something valid
progress = load_progress()
if not isinstance(progress, dict):
    progress = {}

progress.setdefault("name", "")
progress.setdefault("learned", [])
progress.setdefault("recent_pool", [])
progress.setdefault("streak_days", 0)
# ---------------------------
# Welcome Screen (if no name)
# ---------------------------
if not progress.get("name"):
    st.markdown(
        """
        <div style="background-color:#F5F5DC; padding:40px; border-radius:10px;">
            <h1 style="color:#111; text-align:center;">Let’s master our vocabulary together 💪</h1>
            <p style="text-align:center;">Enter your <b>name</b> or <b>nickname</b> to personalize your experience.</p>
        </div>
        """,
        unsafe_allow_html=True
    )

    name = st.text_input("Enter your name or nickname", "")
    if st.button("Go →"):
        clean = (name or "").strip()
        if clean:
            progress["name"] = clean
            save_progress(progress)
            st.rerun()  # reload with name set

    st.stop()  # stop here → don’t show the rest

# Ensure progress dictionary
progress = progress if isinstance(progress, dict) else {}
progress.setdefault("name", "")
progress.setdefault("learned", [])
progress.setdefault("recent_pool", [])
progress.setdefault("streak_days", 0)

# --------------------------
# FORCE WELCOME SCREEN FIRST
# --------------------------
if not progress.get("name"):  
    st.markdown("<h1 style='color:#111;'>Let’s master our vocabulary together 💪</h1>", unsafe_allow_html=True)
    name = st.text_input("Enter your name or nickname", "")
    if st.button("Go →"):
        clean = (name or "").strip()
        if clean:
            progress["name"] = clean
            try:
                save_progress(progress)
            except Exception:
                pass
            st.rerun()  # refresh → now will go to Home
    st.stop()  # ⛔ stop here, don’t show sidebar or other pages

# =========================
# THEME & PAGE CONFIG
# =========================
BEIGE_BG   = "#F3E6D8"   # app background
SIDEBAR_BG = "#D9C3A8"   # soft brown/beige for sidebar
SKY        = "#38bdf8"   # sky-blue buttons
SKY_HOVER  = "#0ea5e9"   # button hover
TEXT       = "#111111"

st.set_page_config(page_title="crackVOCAB", page_icon="📘", layout="wide")

# Global CSS: all pages beige, sidebar soft brown, buttons sky-blue, text black
st.markdown(
    f"""
    <style>
      /* App background + text */
      .stApp, html, body {{
        background: {BEIGE_BG} !important;
        color: {TEXT} !important;
      }}

      /* Sidebar */
      section[data-testid="stSidebar"] {{
        background: {SIDEBAR_BG} !important;
        color: {TEXT} !important;
        border-right: 1px solid rgba(0,0,0,0.08);
      }}
      section[data-testid="stSidebar"] * {{ color: {TEXT} !important; }}

      /* Inputs (search/select/text) */
      input, textarea, select, div[data-baseweb="select"], .stTextInput input {{
        background: #fff !important;
        color: {TEXT} !important;
        border: 1px solid #cfcfcf !important;
        border-radius: 10px !important;
      }}

      /* Buttons (Go, Start learning, Show Definition, Previous, Next, Mark as Learned, Reset, Home/Learn/Quiz) */
      .stButton button {{
        background: {SKY} !important;
        color: #fff !important;
        border: none !important;
        border-radius: 12px !important;
        padding: 10px 16px !important;
        font-weight: 700 !important;
      }}
      .stButton button:hover {{ background: {SKY_HOVER} !important; }}

      /* Card look */
      .card {{
        background: rgba(255,255,255,0.9);
        border: 1px solid rgba(0,0,0,0.08);
        border-radius: 14px;
        padding: 14px 16px;
        box-shadow: 0 8px 20px rgba(0,0,0,0.05);
      }}

      /* Streak bar */
      .streak-rail {{
        width: 100%; height: 8px; background: rgba(0,0,0,0.15);
        border-radius: 999px; overflow: hidden;
      }}
      .streak-fill {{ height: 100%; background: {SKY}; transition: width .3s ease; }}
      .muted {{ color: rgba(0,0,0,0.65) !important; font-size: 0.9rem; }}
    </style>
    """,
    unsafe_allow_html=True
)

# =========================
# DATA / STORAGE
# =========================
DATA_FILE = Path("words.csv")
PROGRESS_FILE = Path("progress.json")

@st.cache_data
def load_words():
    if not DATA_FILE.exists():
        st.error("words.csv not found at repo root.")
        st.stop()
    df = pd.read_csv(DATA_FILE).dropna(subset=["word"]).drop_duplicates(subset=["word"]).reset_index(drop=True)
    cols = ["word","part_of_speech","definition","french","arabic","example"]
    for c in cols:
        if c not in df.columns:
            df[c] = ""
    return df[cols]

def load_progress():
    if PROGRESS_FILE.exists():
        try:
            return json.loads(PROGRESS_FILE.read_text(encoding="utf-8"))
        except Exception:
            pass
    return {}

def save_progress(p):
    PROGRESS_FILE.write_text(json.dumps(p, ensure_ascii=False, indent=2), encoding="utf-8")

data = load_words()
TOTAL_WORDS = len(data)

# normalize progress keys (safe for old files)
progress = load_progress()
defaults = {
    "name": "",
    "learned": [],
    "recent_pool": [],
    "opened_dates": [],   # for streak
    "streak_days": 0
}
for k, v in defaults.items():
    if k not in progress: progress[k] = v
save_progress(progress)

# =========================
# SESSION STATE
# =========================
ss = st.session_state
ss.setdefault("mode", "Welcome" if not progress.get("name") else "Home")  # force Welcome until name saved
ss.setdefault("index", 0)
ss.setdefault("show_def", False)
ss.setdefault("quiz_q", None)
ss.setdefault("quiz_choices", [])
ss.setdefault("quiz_score", 0)
ss.setdefault("quiz_total", 0)

# =========================
# STREAK (count daily opens)
# =========================
today = date.today()
if str(today) not in progress["opened_dates"]:
    yest = today - timedelta(days=1)
    if str(yest) in progress["opened_dates"]:
        progress["streak_days"] = int(progress.get("streak_days", 0)) + 1
    else:
        progress["streak_days"] = 1
    progress["opened_dates"].append(str(today))
    save_progress(progress)

# =========================
# SIDEBAR (always visible on main app screens)
# =========================
with st.sidebar:
    st.markdown("### Navigate")
    nav1, nav2, nav3 = st.columns(3)
    if nav1.button("Home"):
        ss.mode = "Home"; ss.show_def = False
    if nav2.button("Learn"):
        ss.mode = "Learn"; ss.show_def = False
    if nav3.button("Quiz"):
        ss.mode = "Quiz"; ss.quiz_q = None; ss.quiz_choices = []

    st.markdown("---")
    st.markdown("### 📚 Word list")
    st.caption(f"Total words: **{TOTAL_WORDS}**")
    search = st.text_input("Search words")
    if search:
        matches = data[data["word"].str.contains(search, case=False, na=False)]
    else:
        matches = data
    # current selection
    current_word = data.iloc[ss.index]["word"]
    drop = st.selectbox("Select a word", matches["word"].tolist() if not matches.empty else data["word"].tolist())
    if drop != current_word:
        try:
            ss.index = int(data.index[data["word"] == drop][0])
            ss.show_def = False
        except Exception:
            pass

    st.markdown("---")
    st.markdown("### 🔥 Streak")
    days = max(1, min(progress.get("streak_days", 0), 30))
    pct = int(days/30 * 100)
    st.markdown(f"""
      <div class="streak-rail"><div class="streak-fill" style="width:{pct}%"></div></div>
      <div class="muted" style="margin-top:6px;">{progress.get('streak_days',0)} day streak</div>
    """, unsafe_allow_html=True)

    st.markdown("### ☑️ Progress")
    st.caption(f"Words mastered: **{len(progress.get('learned', []))} / {TOTAL_WORDS}**")

# =========================
# PAGES
# =========================

# --- WELCOME (first screen) ---
if ss.mode == "Welcome":
    st.title("Let’s master vocabulary together 💪")
    st.write("Enter your **name or nickname** to personalize your experience.")
    name = st.text_input("Enter your name or nickname", value=progress.get("name",""))
    if st.button("Go →"):
        clean = (name or "").strip()
        if clean:
            progress["name"] = clean
            save_progress(progress)
            ss.mode = "Home"
            st.rerun()
        else:
            st.warning("Please enter a name or nickname to continue.")

# --- HOME ---
elif ss.mode == "Home":
    nm = progress.get("name","").strip() or "friend"
    st.title(f"Hi {nm}, welcome to **crackVOCAB** 📘")
    st.markdown(
        """
        **crackVOCAB** helps you master **advanced English vocabulary** with bilingual
        (English–French–Arabic) explanations — built for focus and flow.
        """
    )
    st.markdown("#### How it works")
    st.markdown(
        """
1) Use the **Word list** in the left sidebar to pick a word (or search).  
2) Click **Show Definition**, then **Mark as Learned** when you’re ready.  
3) Your **streak** (smooth line) and **lifetime progress** update automatically.  
4) **Quiz** practices only your **recently learned** words (last 10 by default).
        """
    )
    st.button("Start learning →", on_click=lambda: ss.update({"mode":"Learn"}))

# --- LEARN ---
elif ss.mode == "Learn":
    row = data.iloc[ss.index]
    st.header("Learn")
    st.subheader(f"{row['word']} ({row['part_of_speech']})")

    c1, c2, c3 = st.columns([1,1,1])

    with c1:
        if st.button("Show Definition"):
            ss.show_def = True

    with c2:
        # Mark as learned (button adds once)
        if st.button("Mark as Learned ✅"):
            learned = set(progress.get("learned", []))
            if row["word"] not in learned:
                progress["learned"].append(row["word"])
                # update recent pool (max 10)
                pool = [w for w in progress.get("recent_pool", []) if w != row["word"]]
                pool.append(row["word"])
                if len(pool) > 10:
                    pool = pool[-10:]
                progress["recent_pool"] = pool
                save_progress(progress)
                st.success("Added to learned.")
            else:
                st.info("Already marked as learned.")

    with c3:
        nxt, prev = st.columns(2)
        if nxt.button("Next ➜"):
            ss.index = (ss.index + 1) % TOTAL_WORDS
            ss.show_def = False
            st.rerun()
        if prev.button("◀ Previous"):
            ss.index = (ss.index - 1) % TOTAL_WORDS
            ss.show_def = False
            st.rerun()

    if ss.show_def:
        st.markdown("### Definition")
        st.markdown(
            f"""
            <div class="card">
              <p><strong>Meaning:</strong> {row['definition']}</p>
              <p><strong>French:</strong> {row['french']}</p>
              <p><strong>Arabic:</strong> {row['arabic']}</p>
              <p><strong>Example:</strong> {row['example']}</p>
            </div>
            """,
            unsafe_allow_html=True
        )

    st.write("")
    if st.button("Reset learned (clear)"):
        progress["learned"] = []
        progress["recent_pool"] = []
        save_progress(progress)
        st.success("Progress cleared.")

# --- QUIZ (recent 10 learned) ---
elif ss.mode == "Quiz":
    pool = progress.get("recent_pool", [])
    st.header("Quiz")
    if len(pool) < 3:
        st.info("Learn at least 3 words (up to 10) to enable the quiz from your recent words.")
    else:
        # Build question if needed
        if ss.quiz_q is None:
            correct_word = random.choice(pool)
            correct_row = data[data["word"] == correct_word].iloc[0]
            # wrong options
            others = data[data["word"] != correct_word].sample(3, random_state=random.randint(0, 99999))
            choices_df = pd.concat([others, correct_row.to_frame().T]).sample(frac=1, random_state=random.randint(0,99999))
            ss.quiz_q = correct_row
            ss.quiz_choices = choices_df["definition"].tolist()

        q = ss.quiz_q
        st.subheader(f"What does **{q['word']}** mean?")
        answer = st.radio("Choose one:", ss.quiz_choices, index=None, label_visibility="collapsed")

        colL, colR = st.columns([1,1])
        if colL.button("Submit"):
            if answer is None:
                st.warning("Pick an option.")
            else:
                ss.quiz_total += 1
                if answer == q["definition"]:
                    ss.quiz_score += 1
                    st.success("Correct! ✅")
                else:
                    st.error(f"Not quite. Correct answer: {q['definition']}")
                # next question
                ss.quiz_q = None
                ss.quiz_choices = []

        if colR.button("Reset quiz"):
            ss.quiz_q = None
            ss.quiz_choices = []
            ss.quiz_score = 0
            ss.quiz_total = 0

        st.caption(f"Score: {ss.quiz_score} / {ss.quiz_total}")

# Fallback safety
else:
    ss.mode = "Home"
    st.rerun()
