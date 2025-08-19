# app.py — crackVOCAB (final drop-in)

import streamlit as st
import pandas as pd
import random, json
from datetime import date
from pathlib import Path

# =============== CONFIG / COLORS ===============
RUST = "#d99072"           # light rust (sidebar)
BEIGE = "#e3b896"          # beige (Home + Words background)
SKY  = "#38bdf8"           # sky blue buttons
SKY_HOVER = "#0ea5e9"

st.set_page_config(page_title="crackVOCAB", page_icon="📘", layout="wide")

# =============== GLOBAL CSS ====================
st.markdown(
    f"""
    <style>
      /* Sidebar bg */
      [data-testid="stSidebar"] {{
        background-color: {RUST} !important;
      }}

      /* Default text dark */
      html, body, .stApp, [class*="st-"], .stMarkdown, .stMarkdown p, .stMarkdown span {{
        color: #111 !important;
      }}

      /* Inputs */
      input, textarea, select, div[data-baseweb="select"], .stDateInput input {{
        background: #fff !important;
        color: #111 !important;
        border: 1px solid #cfcfcf !important;
        border-radius: 10px !important;
      }}

      /* All buttons */
      .stButton button {{
        background: {SKY} !important;
        color: #fff !important;
        border: none !important;
        border-radius: 12px !important;
        padding: 10px 16px !important;
        font-weight: 600 !important;
      }}
      .stButton button:hover {{ background: {SKY_HOVER} !important; }}

      /* Checkbox label + tint */
      .stCheckbox > label, .stCheckbox > label span {{ color:#111 !important; }}
      .stCheckbox input {{ accent-color: {SKY} !important; }}

      /* Card */
      .card {{
        background: #ffffffcc;
        border: 1px solid rgba(0,0,0,0.06);
        box-shadow: 0 8px 20px rgba(0,0,0,0.06);
        border-radius: 16px;
        padding: 1.1rem 1.2rem;
      }}

      /* Streak bar */
      .streak-wrap {{ background:#e5edff; height:10px; border-radius:999px; overflow:hidden; }}
      .streak-fill {{ background:{SKY}; height:100%; transition:width .3s ease; }}
      .muted {{ color:#5b6b7a !important; }}
    </style>
    """,
    unsafe_allow_html=True,
)

# Helpers to set page background color (Home/Words should be beige)
def set_page_bg_color(color: str):
    st.markdown(
        f"<style>.stApp{{background:{color} !important;}}</style>",
        unsafe_allow_html=True
    )

# =============== DATA / STORAGE ===============
DATA_FILE = "words.csv"               # your master list (190+ rows)
PROGRESS_FILE = Path("progress.json") # local progress

@st.cache_data
def load_words():
    df = pd.read_csv(DATA_FILE).dropna(subset=["word"]).drop_duplicates(subset=["word"]).reset_index(drop=True)
    # normalize expected columns
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

# Normalize progress keys so old files never break
progress = load_progress()
defaults = {
    "name": "",
    "learned": [],
    "recent_pool": [],
    "streak_start": str(date.today()),
    "last_open": str(date.today()),
    "streak_days": 0,
}
for k, v in defaults.items():
    if k not in progress:
        progress[k] = v
save_progress(progress)

# =============== SESSION STATE ===============
if "mode" not in st.session_state:
    st.session_state.mode = "Home"
if "index" not in st.session_state:
    st.session_state.index = 0
if "show_def" not in st.session_state:
    st.session_state.show_def = False
if "quiz_q" not in st.session_state:
    st.session_state.quiz_q = None
if "quiz_choices" not in st.session_state:
    st.session_state.quiz_choices = []
if "quiz_score" not in st.session_state:
    st.session_state.quiz_score = 0
if "quiz_total" not in st.session_state:
    st.session_state.quiz_total = 0

# =============== STREAK (SAFE) ===============
today = date.today()
progress.setdefault("last_open", str(today))
progress.setdefault("streak_days", 0)
last_open = date.fromisoformat(progress["last_open"])

if today > last_open:
    if (today - last_open).days == 1:
        progress["streak_days"] += 1
    else:
        progress["streak_days"] = 1
    progress["last_open"] = str(today)
    save_progress(progress)
elif progress["streak_days"] == 0:
    progress["streak_days"] = 1
    progress["last_open"] = str(today)
    save_progress(progress)

# =============== SIDEBAR ===============
with st.sidebar:
    st.markdown("### Go to")
    st.radio(
        label="",
        options=["Home", "Words", "Quiz"],
        index=["Home","Words","Quiz"].index(st.session_state.mode),
        key="mode",
        label_visibility="collapsed",
    )

    st.markdown("### Word list")
    st.caption(f"Total words: **{TOTAL_WORDS}**")

    search = st.text_input("Search")
    if search:
        matches = data[data["word"].str.contains(search, case=False, na=False)]
    else:
        matches = data

    sel = st.selectbox("Select a word", matches["word"].tolist() if not matches.empty else data["word"].tolist())
    try:
        st.session_state.index = int(data.index[data["word"] == sel][0])
    except Exception:
        pass

    st.markdown("### 🔥 Streak")
    days = max(1, min(progress["streak_days"], 30))
    pct = int(days / 30 * 100)
    st.markdown(
        f"""
        <div class="streak-wrap"><div class="streak-fill" style="width:{pct}%"></div></div>
        <div class="muted" style="margin-top:6px;">{progress["streak_days"]}-day streak • view last 30 days</div>
        """,
        unsafe_allow_html=True,
    )

    st.markdown("### ☑️ Progress")
    st.caption(f"Words mastered: **{len(progress.get('learned', []))} / {TOTAL_WORDS}**")

# =============== PAGES =======================

# ---------- HOME ----------
if st.session_state.mode == "Home":
    set_page_bg_color(BEIGE)

    st.title("Hi there, welcome to **crackVOCAB** 📘")
    st.write("Master **advanced English vocabulary** with bilingual (English–French–Arabic) explanations. Built for focus and flow.")

    st.subheader("Let’s master vocabulary together 💪")
    name = st.text_input("Enter your name or nickname", value=progress.get("name",""))
    if name != progress.get("name",""):
        progress["name"] = name
        save_progress(progress)
        st.caption(f"Saved name: {name}")

    st.button("Start learning →", on_click=lambda: st.session_state.update({"mode":"Words"}))

    st.markdown("---")
    st.markdown(
        """
        **How it works**  
        1) Open **Words** (left sidebar), pick any word (search or scroll).  
        2) Click **Show Definition**, then **Mark as Learned** when you’re ready.  
        3) Your **streak** (smooth line) and **lifetime progress** update automatically.  
        4) Use **Quiz** to practice only your **recently learned** words (last 10).
        """
    )

# ---------- WORDS ----------
elif st.session_state.mode == "Words":
    set_page_bg_color(BEIGE)

    row = data.iloc[st.session_state.index]

    st.header("Words")
    st.subheader(f"{row['word']} ({row['part_of_speech']})")

    c1, c2, c3 = st.columns([1,1,1])

    with c1:
        if st.button("Show Definition"):
            st.session_state.show_def = True

    with c2:
        learned_set = set(progress.get("learned", []))
        already = row["word"] in learned_set
        marked = st.checkbox("Mark as Learned", value=already, key=f"learn_{row['word']}")
        if marked and not already:
            progress["learned"].append(row["word"])
            rp = progress.get("recent_pool", [])
            rp = [w for w in rp if w != row["word"]]
            rp.append(row["word"])
            if len(rp) > 10:
                rp = rp[-10:]
            progress["recent_pool"] = rp
            save_progress(progress)
        elif not marked and already:
            progress["learned"] = [w for w in progress["learned"] if w != row["word"]]
            progress["recent_pool"] = [w for w in progress.get("recent_pool", []) if w != row["word"]]
            save_progress(progress)

    with c3:
        if st.button("Next ➜"):
            st.session_state.index = (st.session_state.index + 1) % TOTAL_WORDS
            st.session_state.show_def = False
        st.write("")
        if st.button("◀ Previous"):
            st.session_state.index = (st.session_state.index - 1) % TOTAL_WORDS
            st.session_state.show_def = False

    if st.session_state.show_def:
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
            unsafe_allow_html=True,
        )

    st.write("")
    if st.button("Reset learned (clear)"):
        progress["learned"] = []
        progress["recent_pool"] = []
        save_progress(progress)
        st.success("Progress cleared.")

# ---------- QUIZ ----------
elif st.session_state.mode == "Quiz":
    pool = progress.get("recent_pool", [])
    if len(pool) < 3:
        st.info("Learn at least 3 words (up to 10) to enable the quiz.")
    else:
        st.header("Quiz")
        if st.session_state.quiz_q is None:
            correct_word = random.choice(pool)
            correct_row = data[data["word"] == correct_word].iloc[0]
            # 3 wrong choices
            others = data[data["word"] != correct_word].sample(3, random_state=random.randint(0, 9999))
            choices = pd.concat([others, correct_row.to_frame().T]).sample(frac=1, random_state=random.randint(0, 9999))
            st.session_state.quiz_q = correct_row
            st.session_state.quiz_choices = choices["definition"].tolist()

        q = st.session_state.quiz_q
        st.markdown(f"**What does _{q['word']}_ mean?**")

        answer = st.radio("Choose the correct definition:", st.session_state.quiz_choices, index=None, label_visibility="collapsed")

        cols = st.columns([1,1,1])
        if cols[0].button("Submit"):
            if answer is None:
                st.warning("Pick an option.")
            else:
                st.session_state.quiz_total += 1
                if answer == q["definition"]:
                    st.session_state.quiz_score += 1
                    st.success("Correct! ✅")
                else:
                    st.error(f"Not quite. Correct answer: {q['definition']}")
                st.session_state.quiz_q = None  # next question

        with cols[2]:
            if st.button("Reset quiz"):
                st.session_state.quiz_q = None
                st.session_state.quiz_choices = []
                st.session_state.quiz_score = 0
                st.session_state.quiz_total = 0

        st.caption(f"Score: {st.session_state.quiz_score} / {st.session_state.quiz_total}")
