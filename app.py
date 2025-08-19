import streamlit as st
import pandas as pd
import random, json
from datetime import date
from pathlib import Path

# ---------- BASIC SETUP ----------
st.set_page_config(page_title="crackVOCAB", page_icon="📘", layout="wide")

DATA_FILE = "words.csv"
PROGRESS_FILE = Path("progress.json")

SKY = "#38bdf8"      # sky blue
SKY_HOVER = "#0ea5e9"

# ---------- GLOBAL CSS: all white, black text, sky buttons ----------
st.markdown(
    f"""
    <style>
      /* App & text: white bg, dark text */
      .stApp, html, body, [class*="st-"], .stMarkdown, .stMarkdown p, .stMarkdown span {{
        background: #ffffff !important;
        color: #111 !important;
      }}
      /* Sidebar stays white */
      [data-testid="stSidebar"] {{
        background: #ffffff !important;
      }}
      /* Inputs */
      input, textarea, select, div[data-baseweb="select"], .stDateInput input {{
        background: #ffffff !important;
        color: #111 !important;
        border: 1px solid #cfcfcf !important;
        border-radius: 10px !important;
      }}
      /* Buttons (all) */
      .stButton button {{
        background: {SKY} !important;
        color: #fff !important;
        border: none !important;
        border-radius: 12px !important;
        padding: 10px 16px !important;
        font-weight: 600 !important;
      }}
      .stButton button:hover {{ background: {SKY_HOVER} !important; }}
      /* Card */
      .card {{
        background: #ffffff;
        border: 1px solid rgba(0,0,0,0.06);
        box-shadow: 0 8px 20px rgba(0,0,0,0.06);
        border-radius: 16px;
        padding: 1.1rem 1.2rem;
      }}
      /* Streak bar */
      .streak-wrap {{ background:#eef5ff; height:10px; border-radius:999px; overflow:hidden; }}
      .streak-fill {{ background:{SKY}; height:100%; transition:width .3s ease; }}
      .muted {{ color:#5b6b7a !important; }}
      /* Welcome page background */
      .welcome-bg {{
        position: fixed; inset: 0; z-index: -1;
        background: url('bg-welcome.jpg') center/cover no-repeat;
        filter: brightness(0.9);
      }}
      .welcome-panel {{
        background: rgba(255,255,255,0.85);
        border: 1px solid rgba(0,0,0,0.06);
        border-radius: 16px;
        padding: 24px 28px;
        max-width: 680px;
      }}
    </style>
    """,
    unsafe_allow_html=True,
)

# ---------- DATA ----------
@st.cache_data
def load_words():
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

progress = load_progress()
defaults = {
    "name": "",
    "learned": [],
    "recent_pool": [],
    "streak_start": str(date.today()),
    "last_open": str(date.today()),
    "streak_days": 0,
}
for k,v in defaults.items():
    if k not in progress: progress[k] = v
save_progress(progress)

# ---------- SESSION ----------
ss = st.session_state
ss.setdefault("mode", "Home")
ss.setdefault("index", 0)
ss.setdefault("show_def", False)
ss.setdefault("quiz_q", None)
ss.setdefault("quiz_choices", [])
ss.setdefault("quiz_score", 0)
ss.setdefault("quiz_total", 0)

# ---------- STREAK (safe) ----------
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

# ---------- SIDEBAR ----------
with st.sidebar:
    st.markdown("### Go to")
    st.radio("", ["Home","Words","Quiz"], key="mode", label_visibility="collapsed")

    st.markdown("### Word list")
    st.caption(f"Total words: **{TOTAL_WORDS}**")

    search = st.text_input("Search")
    if search:
        matches = data[data["word"].str.contains(search, case=False, na=False)]
    else:
        matches = data

    sel = st.selectbox("Select a word", matches["word"].tolist() if not matches.empty else data["word"].tolist())
    try:
        ss.index = int(data.index[data["word"] == sel][0])
    except Exception:
        pass

    st.markdown("### 🔥 Streak")
    days = max(1, min(progress["streak_days"], 30))
    pct = int(days/30*100)
    st.markdown(
        f"""
        <div class="streak-wrap"><div class="streak-fill" style="width:{pct}%"></div></div>
        <div class="muted" style="margin-top:6px;">{progress["streak_days"]}-day streak • view last 30 days</div>
        """,
        unsafe_allow_html=True,
    )

    st.markdown("### ☑️ Progress")
    st.caption(f"Words mastered: **{len(progress.get('learned', []))} / {TOTAL_WORDS}**")

# ---------- PAGES ----------
# HOME (welcome with map bg)
if ss.mode == "Home":
    st.markdown('<div class="welcome-bg"></div>', unsafe_allow_html=True)
    st.title("Hi there, welcome to **crackVOCAB** 📘")
    st.write("")  # small spacer
    st.markdown('<div class="welcome-panel">', unsafe_allow_html=True)
    st.subheader("Let’s master vocabulary together 💪")
    st.write("Enter your **name or nickname** to personalize your experience.")
    name = st.text_input("Enter your name or nickname", value=progress.get("name",""))
    if name != progress.get("name",""):
        progress["name"] = name
        save_progress(progress)
        st.caption(f"Saved name: {name}")
    st.button("Go →", on_click=lambda: ss.update({"mode":"Words"}))
    st.markdown("</div>", unsafe_allow_html=True)

# WORDS (all white)
elif ss.mode == "Words":
    row = data.iloc[ss.index]
    st.header("Words")
    st.subheader(f"{row['word']} ({row['part_of_speech']})")

    c1,c2,c3 = st.columns([1,1,1])
    with c1:
        if st.button("Show Definition"):
            ss.show_def = True
    with c2:
        learned = set(progress.get("learned", []))
        already = row["word"] in learned
        marked = st.checkbox("Mark as Learned", value=already, key=f"learn_{row['word']}")
        if marked and not already:
            progress["learned"].append(row["word"])
            rp = [w for w in progress.get("recent_pool", []) if w != row["word"]]
            rp.append(row["word"])
            if len(rp) > 10: rp = rp[-10:]
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

# QUIZ (uses last 10 learned)
elif ss.mode == "Quiz":
    pool = progress.get("recent_pool", [])
    if len(pool) < 3:
        st.info("Learn at least 3 words (up to 10) to enable the quiz.")
    else:
        st.header("Quiz")
        if ss.quiz_q is None:
            correct_word = random.choice(pool)
            correct_row = data[data["word"] == correct_word].iloc[0]
            others = data[data["word"] != correct_word].sample(3, random_state=random.randint(0,9999))
            choices = pd.concat([others, correct_row.to_frame().T]).sample(frac=1, random_state=random.randint(0,9999))
            ss.quiz_q = correct_row
            ss.quiz_choices = choices["definition"].tolist()

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

        with cols[2]:
            if st.button("Reset quiz"):
                ss.quiz_q = None
                ss.quiz_choices = []
                ss.quiz_score = 0
                ss.quiz_total = 0

        st.caption(f"Score: {ss.quiz_score} / {ss.quiz_total}")
