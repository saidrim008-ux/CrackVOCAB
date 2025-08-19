import streamlit as st
import pandas as pd
import random, json
from datetime import date, timedelta
from pathlib import Path

# ---------- Config ----------
LEARNED_LIMIT = 10               # recent learned pool for quiz
PROGRESS_FILE = Path("progress.json")
TARGET_WORDS = 100               # goal before adding the next pack

# ---------- Load data ----------
data = pd.read_csv("words.csv").dropna().reset_index(drop=True)

st.title("📘 crackVOCAB")
st.caption("Master advanced vocabulary with English–French–Arabic flashcards!")

# ---------- helpers: persistence ----------
def load_progress():
    if PROGRESS_FILE.exists():
        try:
            return json.loads(PROGRESS_FILE.read_text(encoding="utf-8"))
        except Exception:
            pass
    return {"dates": [], "mastered_idxs": []}  # dates = ["YYYY-MM-DD"]

def save_progress(p):
    PROGRESS_FILE.write_text(json.dumps(p, ensure_ascii=False, indent=2), encoding="utf-8")

progress = load_progress()

def mark_active_today():
    today = str(date.today())
    if today not in progress["dates"]:
        progress["dates"].append(today)
        save_progress(progress)

def add_mastered(idx: int):
    # lifetime mastered set (distinct words)
    if idx not in progress["mastered_idxs"]:
        progress["mastered_idxs"].append(idx)
        save_progress(progress)

# ---------- Streak utilities ----------
def consecutive_streak(dates_list):
    """Return streak length ending today."""
    if not dates_list: return 0
    s = set(dates_list)
    streak = 0
    d = date.today()
    while str(d) in s:
        streak += 1
        d -= timedelta(days=1)
    return streak

def week_flags(dates_list):
    """Return last 7 days flags [(label, did_learn: bool)]."""
    s = set(dates_list)
    out = []
    for i in range(6, -1, -1):  # Mon..Sun visual left->right (last 7 days)
        d = date.today() - timedelta(days=i)
        out.append((d.strftime("%a"), str(d) in s))
    return out

# ---------- Session state ----------
if "index" not in st.session_state:
    st.session_state.index = 0
if "learned_idxs_recent" not in st.session_state:
    st.session_state.learned_idxs_recent = []  # recent pool for quiz only
if "quiz" not in st.session_state:
    st.session_state.quiz = {"q": None, "score": 0, "num": 0}

# ---------- sidebar: streak & progress ----------
streak = consecutive_streak(progress["dates"])
flags = week_flags(progress["dates"])
mastered_count = len(progress["mastered_idxs"])

with st.sidebar:
    st.subheader("🔥 Streak")
    st.write(f"Consecutive days: **{streak}**")
    bar = min(streak, 7) / 7
    st.progress(bar, text=f"{bar*100:.0f}% of this week")

    cols = st.columns(7)
    for (lbl, ok), c in zip(flags, cols):
        c.markdown(f"**{lbl}**\n\n{'✅' if ok else '—'}")

    st.subheader("📈 Lifetime Progress")
    st.write(f"Words mastered: **{mastered_count} / {TARGET_WORDS}**")
    st.progress(min(mastered_count, TARGET_WORDS) / TARGET_WORDS)

    st.write(f"Quiz pool (recent): **{len(st.session_state.learned_idxs_recent)} / {LEARNED_LIMIT}**")
    if st.button("Clear recent quiz pool"):
        st.session_state.learned_idxs_recent = []
        st.success("Recent pool cleared.")

# ---------- internal helpers ----------
def add_recent(idx):
    if idx in st.session_state.learned_idxs_recent:
        st.session_state.learned_idxs_recent.remove(idx)
    st.session_state.learned_idxs_recent.insert(0, idx)
    st.session_state.learned_idxs_recent = st.session_state.learned_idxs_recent[:LEARNED_LIMIT]

def next_index(delta: int):
    st.session_state.index = (st.session_state.index + delta) % len(data)

def make_quiz_item(pool):
    i = random.choice(pool)
    row = data.iloc[i]
    others = pool.copy()
    others.remove(i)
    pick = random.sample(others, k=min(3, len(others))) if others else []
    choices = [row["word"]] + [data.iloc[j]["word"] for j in pick]
    random.shuffle(choices)
    correct = choices.index(row["word"])
    prompt = f'Which word matches this definition?\n\n**{row["definition"]}**'
    return {"prompt": prompt, "choices": choices, "correct": correct, "row": row}

# ---------- UI mode ----------
mode = st.radio("Mode", ["Learn", "Quiz"], horizontal=True)

# ====================== LEARN ======================
if mode == "Learn":
    row = data.iloc[st.session_state.index]
    st.subheader(f"Word: {row['word']} ({row['part_of_speech']})")

    if st.button("Show Definition"):
        st.write(f"**Definition:** {row['definition']}")
        st.write(f"**French:** {row['french']}")
        st.write(f"**Arabic:** {row['arabic']}")
        st.write(f"**Example:** {row['example']}")

    cols = st.columns(3)
    if cols[0].button("⬅️ Previous"):
        next_index(-1); st.rerun()
    if cols[1].button("Mark as Learned ✅"):
        # record activity & mastery
        mark_active_today()
        add_mastered(st.session_state.index)
        # keep a small recent pool for quizzing
        add_recent(st.session_state.index)
        st.toast("Added to learned pool + streak updated"); st.rerun()
    if cols[2].button("Next ➡️"):
        next_index(1); st.rerun()

# ====================== QUIZ ======================
else:
    pool = st.session_state.learned_idxs_recent
    if not pool:
        st.info("Your recent learned pool is empty. Go to **Learn** and mark some words ✅.")
    else:
        if st.session_state.quiz["q"] is None:
            st.session_state.quiz["q"] = make_quiz_item(pool)

        q = st.session_state.quiz["q"]
        st.subheader(f"Quiz (from your last {len(pool)} learned words) • Q{st.session_state.quiz['num'] + 1}")
        st.markdown(q["prompt"])
        choice = st.radio("Choose one:", q["choices"], index=None, key=f"q{st.session_state.quiz['num']}")

        cols = st.columns(2)
        if cols[0].button("Check"):
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
                # count a quiz interaction as activity for streak too
                mark_active_today()

        if cols[1].button("Next Question ➡️"):
            st.session_state.quiz["num"] += 1
            st.session_state.quiz["q"] = make_quiz_item(pool)
            st.rerun()

        st.info(f"Score: **{st.session_state.quiz['score']}** / {st.session_state.quiz['num']}")
