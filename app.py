import streamlit as st
import pandas as pd
import random, json
from datetime import date, timedelta
from pathlib import Path

# ===================== Config =====================
LEARNED_LIMIT = 10                 # recent pool size used by Quiz
PROGRESS_FILE = Path("progress.json")

# ===================== Data =====================
# ONE master file with ALL words (e.g., 190 rows)
data = (
    pd.read_csv("words.csv")
      .dropna()
      .drop_duplicates(subset=["word"])   # avoid exact duplicates by word
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
    # dates: list of "YYYY-MM-DD"; mastered_idxs: list of row indices
    return {"dates": [], "mastered_idxs": []}

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

def week_flags(dates_list):
    s = set(dates_list)
    out = []
    for i in range(6, -1, -1):  # last 7 days (older -> today)
        d = date.today() - timedelta(days=i)
        out.append((d.strftime("%a"), str(d) in s))
    return out

# ===================== Session =====================
if "mode" not in st.session_state:
    st.session_state.mode = "Home"  # land on intro first
if "index" not in st.session_state:
    st.session_state.index = 0
if "learned_recent" not in st.session_state:
    st.session_state.learned_recent = []  # indices for recent pool (quiz)
if "quiz" not in st.session_state:
    st.session_state.quiz = {"q": None, "score": 0, "num": 0}

# ===================== Small helpers =====================
def add_recent(idx):
    L = st.session_state.learned_recent
    if idx in L:
        L.remove(idx)
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

# ===================== UI: Title =====================
st.title("📘 crackVOCAB")

# ===================== Sidebar =====================
# Navigation
st.session_state.mode = st.sidebar.radio("Go to", ["Home", "Words", "Quiz"],
                                         index=["Home", "Words", "Quiz"].index(st.session_state.mode))

# Word list (search + picker) when not on Home
if st.session_state.mode != "Home":
    st.sidebar.markdown("### 📚 Word list")
    st.sidebar.write(f"Total words: **{TOTAL_WORDS}**")
    query = st.sidebar.text_input("Search")
    labels = [f"{w} ({p})" for w, p in zip(data["word"], data["part_of_speech"])]
    if query:
        filtered = [(i, lbl) for i, lbl in enumerate(labels) if query.lower() in lbl.lower()]
    else:
        filtered = list(enumerate(labels))

    if filtered:
        idx_opts = [i for i, _ in filtered]
        lbl_opts = [lbl for _, lbl in filtered]
        sel = st.sidebar.selectbox("Select a word", lbl_opts, index=0)
        st.session_state.index = idx_opts[lbl_opts.index(sel)]
    else:
        st.sidebar.info("No words match your search.")

# Streak + progress
with st.sidebar:
    st.markdown("---")
    streak = consecutive_streak(progress["dates"])
    st.subheader("🔥 Streak")
    st.write(f"Consecutive days: **{streak}**")
    cols7 = st.columns(7)
    for (lbl, ok), c in zip(week_flags(progress["dates"]), cols7):
        c.markdown(f"**{lbl}**\n\n{'✅' if ok else '—'}")

    mastered_count = len(progress["mastered_idxs"])
    st.subheader("📈 Progress")
    st.write(f"Words mastered: **{mastered_count} / {TOTAL_WORDS}**")
    # Avoid div-by-zero if somehow list is empty
    st.progress((mastered_count / TOTAL_WORDS) if TOTAL_WORDS else 0.0)

    st.write(f"Quiz pool (recent): **{len(st.session_state.learned_recent)} / {LEARNED_LIMIT}**")
    if st.button("Clear recent pool"):
        st.session_state.learned_recent = []
        st.success("Recent pool cleared.")

# ===================== Pages =====================
if st.session_state.mode == "Home":
    # Intro / landing page (like before)
    st.header("Welcome to crackVOCAB 👋")
    st.write(
        """
**crackVOCAB** helps you master **advanced English vocabulary** with bilingual
(English–French–Arabic) explanations.

**How it works**
1) Go to **Words** → pick any word from the list on the left (use search).
2) Click **Show Definition**, then **Mark as Learned** when you’re ready.
3) Your **daily streak** and **lifetime progress** update automatically.
4) Use **Quiz** to practice only your **recently learned** words (last 10 by default).
        """
    )
    if st.button("Start learning →"):
        st.session_state.mode = "Words"
        st.rerun()

elif st.session_state.mode == "Words":
    # Learn page
    row = data.iloc[st.session_state.index]
    st.header("Words")
    st.subheader(f"{row['word']} ({row['part_of_speech']})")

    if st.button("Show Definition"):
        st.write(f"**Definition:** {row['definition']}")
        st.write(f"**French:** {row['french']}")
        st.write(f"**Arabic:** {row['arabic']}")
        st.write(f"**Example:** {row['example']}")

    c1, c2, c3 = st.columns(3)
    if c1.button("⬅️ Previous"):
        next_index(-1); st.rerun()
    if c2.button("Mark as Learned ✅"):
        mark_active_today()
        add_mastered(st.session_state.index)
        add_recent(st.session_state.index)
        st.toast("Added to learned + streak updated"); st.rerun()
    if c3.button("Next ➡️"):
        next_index(1); st.rerun()

else:
    # Quiz page (from recent learned pool only)
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

