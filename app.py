import streamlit as st
import pandas as pd
import random, json
from datetime import date, timedelta
from pathlib import Path

# ===================== App setup =====================
st.set_page_config(page_title="crackVOCAB", page_icon="📘", layout="wide")

# Global CSS (all text black, study-vibe background, rounded buttons/cards)
st.markdown(
    """
    <style>
      /* Background */
      .stApp {
        background: linear-gradient(180deg, #f6fbff 0%, #eef3ff 100%);
        color: #111 !important;
      }
      /* Force dark text everywhere */
      html, body, [class*="st-"], .stMarkdown, .stMarkdown p, .stMarkdown span {
        color: #111 !important;
      }
      /* Headings */
      h1, h2, h3, .stMarkdown h1, .stMarkdown h2 {
        font-family: ui-sans-serif, system-ui, -apple-system, "Segoe UI", Roboto, "Helvetica Neue", Arial;
        color: #111 !important;
      }
      /* Buttons */
      div.stButton > button {
        background: #2563eb;  /* blue */
        color: #fff !important;
        border: 0;
        padding: 10px 16px;
        border-radius: 12px;
        font-weight: 600;
      }
      div.stButton > button:hover { background: #1e4fbf; }
      /* Cards */
      .card {
        background: #ffffffcc;
        border: 1px solid #e6ecff;
        box-shadow: 0 8px 20px rgba(37,99,235,0.08);
        border-radius: 16px;
        padding: 1.1rem 1.2rem;
      }
      /* Sidebar */
      section[data-testid="stSidebar"] {
        background: #f7f9ff;
        border-right: 1px solid #e9efff;
        color: #111 !important;
      }
      /* Streak bar (smooth line) */
      .streak-wrap {
        background: #e5edff;
        border-radius: 999px;
        height: 10px;
        width: 100%;
        overflow: hidden;
      }
      .streak-fill {
        background: #2563eb;
        height: 100%;
        transition: width 300ms ease;
      }
      .muted { color: #5b6b7a !important; }
    </style>
    """,
    unsafe_allow_html=True
)

# ===================== Config =====================
LEARNED_LIMIT = 10                 # recent pool for Quiz
PROGRESS_FILE = Path("progress.json")
STREAK_WINDOW = 30                 # visual window for the streak bar

# ===================== Data =====================
data = (
    pd.read_csv("words.csv")
      .dropna()
      .drop_duplicates(subset=["word"])   # avoid exact duplicate words
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
    st.session_state.mode = "Welcome"   # ask for name first
if "index" not in st.session_state:
    st.session_state.index = 0
if "learned_recent" not in st.session_state:
    st.session_state.learned_recent = []  # indices for recent pool (quiz)
if "quiz" not in st.session_state:
    st.session_state.quiz = {"q": None, "score": 0, "num": 0}

# ===================== Small helpers =====================
def add_recent(idx):
    L = st.session_state.learned_recent
    if idx in L: L.remove(idx)
    L.insert(0, idx)
    st.session_state.learned_recent = L[:LEARNED_LIMIT]

def next_index(delta):
    st.session_state.index = (st.session_state.index + delta) % TOTAL_WORDS

def make_quiz_item(pool):
    i = random.choice(pool)
    row = data.iloc[i]
    others = pool.copy()
    if i in others:
        others.remove(i)
    pick = random.sample(others, k=min(3, len(others))) if others else []
    choices = [row["word"]] + [data.iloc[j]["word"] for j in pick]
    random.shuffle(choices)
    return {
        "prompt": f'Which word matches this definition?\n\n**{row["definition"]}**',
        "choices": choices,
        "correct": choices.index(row["word"]),
        "row": row,
    }

# ===================== Sidebar (hide on Welcome) =====================
if st.session_state.mode != "Welcome":
    # Navigation
    st.session_state.mode = st.sidebar.radio(
        "Go to", ["Home", "Words", "Quiz"],
        index=["Home","Words","Quiz"].index(st.session_state.mode) if st.session_state.mode in ["Home","Words","Quiz"] else 0
    )

    # Word list (not on Home)
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

    # Streak + progress
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
        if st.button("Clear recent pool"):
            st.session_state.learned_recent = []
            st.success("Recent pool cleared.")

# ===================== Pages =====================

# ---- Welcome (enter name) ----
if st.session_state.mode == "Welcome":
    st.markdown("<div class='card'>", unsafe_allow_html=True)
    st.header("Welcome to your favorite spot ✨")
    st.write("Enter your **full name** to personalize your experience.")
    default_name = progress.get("name") or ""
    name = st.text_input("Full name", value=default_name, placeholder="e.g., Youssef Said")
    if st.button("Go →"):
        clean = name.strip()
        if clean:
            progress["name"] = clean
            if not progress.get("first_seen"):
                progress["first_seen"] = str(date.today())
            save_progress(progress)
            st.session_state.mode = "Home"
            st.rerun()
        else:
            st.warning("Please enter your full name to continue.")
    st.markdown("</div>", unsafe_allow_html=True)

# ---- Home (intro) ----
elif st.session_state.mode == "Home":
    user = progress.get("name") or "there"
    st.markdown("<div class='card'>", unsafe_allow_html=True)
    st.header(f"Hi {user}, welcome to crackVOCAB 👋")
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
        next_index(-1); st.rerun()
    if c2.button("Mark as Learned ✅", help="Adds to streak, mastered list, and quiz pool"):
        mark_active_today()
        add_mastered(st.session_state.index)
        add_recent(st.session_state.index)
        st.toast("Added to learned + streak updated"); st.rerun()
    if c3.button("Next ➡️"):
        next_index(1); st.rerun()

# ---- Quiz ----
else:
    pool = st.session_state.learned_recent
    st.header("Quiz")
    if not pool:
        st.info("Your recent learned pool is empty. Go to **Words** and mark some items ✅.")
    else:
        if st.session_state.quiz["q"] is None:
            st.session_state.quiz["q"] = make_quiz_item(pool)

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
            st.session_state.quiz["q"] = make_quiz_item(pool)
            st.rerun()

        st.info(f"Score: **{st.session_state.quiz['score']}** / {st.session_state.quiz['num']}")
