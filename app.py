# app.py  —  crackVOCAB (all-beige version)
# -----------------------------------------
import streamlit as st
import pandas as pd
import random, json
from datetime import date, timedelta
from pathlib import Path

# ---------- THEME (all beige, text black) ----------
BEIGE_BG   = "#F3E6D8"   # main background
BEIGE_UI   = "#E6D2BB"   # components / cards / buttons (slightly deeper)
BEIGE_DARK = "#D9C3A8"   # button hover / accents
TEXT_BLACK = "#222222"

st.set_page_config(page_title="crackVOCAB", page_icon="📘", layout="wide")

st.markdown(f"""
<style>
/* Global bg + text */
.stApp {{
  background: {BEIGE_BG} !important;
  color: {TEXT_BLACK} !important;
}}
/* Sidebar same beige */
section[data-testid="stSidebar"] {{
  background: {BEIGE_BG} !important;
  color: {TEXT_BLACK} !important;
  border-right: 1px solid rgba(0,0,0,0.06);
}}
/* Buttons (beige, bold) */
div.stButton > button {{
  background: {BEIGE_UI} !important;
  color: {TEXT_BLACK} !important;
  border: 1px solid rgba(0,0,0,0.10) !important;
  border-radius: 10px !important;
  font-weight: 700 !important;
}}
div.stButton > button:hover {{
  background: {BEIGE_DARK} !important;
}}
/* Select boxes / inputs to match beige */
.stSelectbox, .stTextInput, .stRadio, .stMultiSelect, .stNumberInput {{
  background: {BEIGE_UI} !important;
  border-radius: 10px !important;
  padding: 4px 6px !important;
}}
/* Card style for definition */
.card {{
  background: {BEIGE_UI};
  border: 1px solid rgba(0,0,0,0.10);
  border-radius: 12px;
  padding: 14px 16px;
}}
/* Slim horizontal streak bar */
.streak-rail {{
  width: 100%; height: 8px;
  background: rgba(0,0,0,0.12);
  border-radius: 999px; overflow: hidden;
}}
.streak-fill {{
  height: 100%;
  background: {BEIGE_DARK};
}}
/* Tiny caption tone */
.small-muted {{ opacity: 0.7; font-size: 0.9rem; }}
</style>
""", unsafe_allow_html=True)

# ---------- DATA ----------
DATA_FILE = Path("words.csv")
if not DATA_FILE.exists():
    st.error("words.csv not found in repo root.")
    st.stop()

data = (
    pd.read_csv(DATA_FILE)
      .dropna(subset=["word"])
      .drop_duplicates(subset=["word"])
      .reset_index(drop=True)
)
TOTAL_WORDS = len(data)

# ---------- PERSISTENCE ----------
PROGRESS_FILE = Path("progress.json")

def load_progress():
    if PROGRESS_FILE.exists():
        try:
            return json.loads(PROGRESS_FILE.read_text(encoding="utf-8"))
        except Exception:
            return {}
    return {}

def save_progress(p):
    PROGRESS_FILE.write_text(json.dumps(p, ensure_ascii=False, indent=2), encoding="utf-8")

progress = load_progress()
progress.setdefault("name", "")
progress.setdefault("learned", [])       # list of words
progress.setdefault("recent_pool", [])   # last 10 learned words (for quiz)
progress.setdefault("last_open", str(date.today()))
progress.setdefault("streak_days", 0)    # consecutive days learning (app opened)
progress.setdefault("opened_dates", [])  # list of YYYY-MM-DD strings you opened the app

# Streak update (count daily opens as learning habit)
today = date.today()
opened_set = set(progress.get("opened_dates", []))
if str(today) not in opened_set:
    # check if yesterday was opened to keep streak
    yesterday = today - timedelta(days=1)
    if str(yesterday) in opened_set:
        progress["streak_days"] = int(progress.get("streak_days", 0)) + 1
    else:
        progress["streak_days"] = 1
    progress["opened_dates"].append(str(today))
    save_progress(progress)

# ---------- SESSION STATE ----------
ss = st.session_state
ss.setdefault("mode", "Home")      # "Home", "Words", "Quiz"
ss.setdefault("index", 0)
ss.setdefault("show_def", False)
ss.setdefault("quiz_q", None)
ss.setdefault("quiz_choices", [])
ss.setdefault("quiz_score", 0)
ss.setdefault("quiz_total", 0)

# If no name yet, always keep user on welcome input
if not progress.get("name"):
    ss.mode = "Welcome"

# ---------- SIDEBAR ----------
with st.sidebar:
    st.markdown("### Go to")
    if st.button("Home"):
        ss.mode = "Home"
        ss.show_def = False
    if st.button("Words"):
        ss.mode = "Words"
        ss.show_def = False
    if st.button("Quiz"):
        ss.mode = "Quiz"
        ss.quiz_q = None
        ss.quiz_choices = []

    st.markdown("### Word list")
    st.caption(f"Total words: {TOTAL_WORDS}")
    search = st.text_input("Search")
    choices = data["word"].tolist()
    if search:
        choices = [w for w in choices if search.lower() in w.lower()]
    current = data.iloc[ss.index]["word"]
    sel = st.selectbox("Select a word", choices, index=choices.index(current) if current in choices else 0)
    if sel != current:
        ss.index = data.index[data["word"] == sel][0]
        ss.show_def = False

    st.markdown("### 🔥 Streak")
    st.caption("Consecutive days learning")
    # streak bar is capped at 30 visually
    streak_days = int(progress.get("streak_days", 0))
    pct = max(0, min(100, int(100 * (streak_days / 30))))
    st.markdown(f"""
      <div class="streak-rail"><div class="streak-fill" style="width:{pct}%"></div></div>
      <div class="small-muted">{streak_days} day(s)</div>
    """, unsafe_allow_html=True)

    st.markdown("### 📈 Progress")
    learned_count = len(progress.get("learned", []))
    st.caption(f"Words mastered: {learned_count} / {TOTAL_WORDS}")

# ---------- PAGES ----------
mode = ss.mode

# WELCOME: name input (first screen, beige)
if mode == "Welcome":
    st.title("Let’s master vocabulary together 💪")
    st.write("Enter your **name or nickname** to personalize your experience.")
    name = st.text_input("Enter your name or nickname", value=progress.get("name",""))
    if name != progress.get("name",""):
        progress["name"] = name
        save_progress(progress)
        st.caption(f"Saved name: {name}")
    st.button("Go →", on_click=lambda: ss.update({"mode":"Home"}))

# HOME: intro after name
elif mode == "Home":
    nm = progress.get("name", "").strip() or "friend"
    st.title(f"Hi there, {nm}, welcome to **crackVOCAB** 📘")
    st.markdown(
        """
        crackVOCAB helps you master **advanced English vocabulary** with bilingual
        (English–French–Arabic) explanations — built for focus and flow.
        """)
    st.markdown("#### How it works")
    st.markdown(
        """
        1) Open **Words** (left sidebar), pick any word (search or scroll).  
        2) Click **Show Definition**, then **Mark as Learned** when you’re ready.  
        3) Your **streak** (smooth line) and **lifetime progress** update automatically.  
        4) Use **Quiz** to practice only your **recently learned** words (last 10 by default).
        """
    )
    st.button("Start learning →", on_click=lambda: ss.update({"mode":"Words"}))

# WORDS: flashcards
elif mode == "Words":
    row = data.iloc[ss.index]
    st.header("Words")
    st.subheader(f"{row['word']} ({row['part_of_speech']})")

    c1, c2, c3 = st.columns([1,1,1])
    with c1:
        if st.button("Show Definition"):
            ss.show_def = True

    with c2:
        learned = set(progress.get("learned", []))
        already = row["word"] in learned
        # Make the checkbox label clearly visible
        marked = st.checkbox("Mark as Learned", value=already, key=f"learn_{row['word']}")
        if marked and not already:
            # add to learned + recent pool (for Quiz)
            L = progress.get("learned", [])
            L.append(row["word"])
            progress["learned"] = sorted(list(set(L)))
            rp = [w for w in progress.get("recent_pool", []) if w != row["word"]]
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
            ss.index = (ss.index + 1) % TOTAL_WORDS
            ss.show_def = False
        st.write("")
        if st.button("◀ Previous"):
            ss.index = (ss.index - 1) % TOTAL_WORDS
            ss.show_def = False

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
            unsafe_allow_html=True,
        )

    st.write("")
    if st.button("Reset learned (clear)"):
        progress["learned"] = []
        progress["recent_pool"] = []
        save_progress(progress)
        st.success("Progress cleared.")

# QUIZ: only recently learned (last 10)
elif mode == "Quiz":
    pool = progress.get("recent_pool", [])
    if len(pool) < 3:
        st.header("Quiz")
        st.info("Learn at least 3 words (up to 10) to enable the quiz from your recent words.")
    else:
        st.header("Quiz")
        if ss.quiz_q is None:
            correct_word = random.choice(pool)
            correct_row = data[data["word"] == correct_word].iloc[0]
            # 3 other options
            others = data[data["word"] != correct_word].sample(3, random_state=random.randint(0,9999))
            choices_df = pd.concat([others, correct_row.to_frame().T]).sample(frac=1, random_state=random.randint(0,9999))
            ss.quiz_q = correct_row
            ss.quiz_choices = choices_df["definition"].tolist()

        q = ss.quiz_q
        st.markdown(f"**What does _{q['word']}_ mean?**")
        answer = st.radio("Choose the correct definition:", ss.quiz_choices, index=None, label_visibility="collapsed")

        cols = st.columns([1,1,1])
        if cols[0].button("Submit"):
            if answer is None:
                st.warning("Pick an option.")
            else:
                ss.quiz_total += 1
                if answer == q["definition"]:
                    ss.quiz_score += 1
                    st.success("Correct! ✅")
                else:
                    st.error(f"Not quite. Correct answer: {q['definition']}")
                ss.quiz_q = None
                ss.quiz_choices = []

        with cols[2]:
            if st.button("Reset quiz"):
                ss.quiz_q = None
                ss.quiz_choices = []
                ss.quiz_score = 0
                ss.quiz_total = 0

        st.caption(f"Score: {ss.quiz_score} / {ss.quiz_total}")

# Fallback
else:
    ss.mode = "Home"
    st.experimental_rerun()  # safe fallback (Streamlit still supports it)
