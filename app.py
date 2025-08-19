import streamlit as st
import pandas as pd
import random

# ---------- Config ----------
LEARNED_LIMIT = 10   # keep the last N learned words

# ---------- Load data ----------
data = pd.read_csv("words.csv").dropna().reset_index(drop=True)

st.title("📘 crackVOCAB")
st.caption("Master advanced vocabulary with English–French–Arabic flashcards!")

# ---------- Session state ----------
if "index" not in st.session_state:
    st.session_state.index = 0
if "learned_idxs" not in st.session_state:
    st.session_state.learned_idxs = []  # list of row indices (most recent first)
if "quiz" not in st.session_state:
    st.session_state.quiz = {"q": None, "score": 0, "num": 0}

# ---------- Helpers ----------
def add_learned(idx: int):
    # move idx to front; keep only LEARNED_LIMIT
    if idx in st.session_state.learned_idxs:
        st.session_state.learned_idxs.remove(idx)
    st.session_state.learned_idxs.insert(0, idx)
    st.session_state.learned_idxs = st.session_state.learned_idxs[:LEARNED_LIMIT]

def next_index(delta: int):
    st.session_state.index = (st.session_state.index + delta) % len(data)

def make_quiz_item(pool):
    """pool = list of row indices to quiz from"""
    i = random.choice(pool)
    row = data.iloc[i]

    # choices also from pool; up to 4 options
    others = pool.copy()
    others.remove(i)
    pick = random.sample(others, k=min(3, len(others))) if others else []
    choices = [row["word"]] + [data.iloc[j]["word"] for j in pick]
    random.shuffle(choices)
    correct = choices.index(row["word"])
    prompt = f'Which word matches this definition?\n\n**{row["definition"]}**'
    return {"prompt": prompt, "choices": choices, "correct": correct, "row": row}

# ---------- Sidebar ----------
mode = st.sidebar.radio("Mode", ["Learn", "Quiz"])
st.sidebar.write(f"✅ Learned pool: **{len(st.session_state.learned_idxs)} / {LEARNED_LIMIT}**")
if st.sidebar.button("Clear learned pool"):
    st.session_state.learned_idxs = []
    st.success("Learned pool cleared.")

# ====================== LEARN MODE ======================
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
        add_learned(st.session_state.index)
        st.toast("Added to learned pool"); st.rerun()
    if cols[2].button("Next ➡️"):
        next_index(1); st.rerun()

# ====================== QUIZ MODE ======================
else:
    pool = st.session_state.learned_idxs
    if not pool:
        st.info("Your learned pool is empty. Go to **Learn** mode and mark some words ✅.")
    else:
        # ensure we have a question ready
        if st.session_state.quiz["q"] is None:
            st.session_state.quiz["q"] = make_quiz_item(pool)

        q = st.session_state.quiz["q"]
        st.subheader(f"Quiz (from your {len(pool)} learned words) • Q{st.session_state.quiz['num'] + 1}")
        st.markdown(q["prompt"])

        choice = st.radio("Choose one:", q["choices"], index=None, key=f"radio_{st.session_state.quiz['num']}")

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

        if cols[1].button("Next Question ➡️"):
            st.session_state.quiz["num"] += 1
            st.session_state.quiz["q"] = make_quiz_item(pool)
            st.rerun()

        st.info(f"Score: **{st.session_state.quiz['score']}** / {st.session_state.quiz['num']}")
