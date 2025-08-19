import streamlit as st
import pandas as pd
import random

# ---------- Load data ----------
data = pd.read_csv("words.csv").dropna().reset_index(drop=True)

st.title("📘 crackVOCAB")
st.write("Master advanced vocabulary with English–French–Arabic flashcards!")

# ---------- Session state ----------
if "index" not in st.session_state:
    st.session_state.index = 0

if "quiz" not in st.session_state:
    st.session_state.quiz = {
        "question_i": 0,   # which question number you are on
        "score": 0,        # how many correct so far
        "current": None    # holds the current quiz payload
    }

# ---------- Helpers ----------
def next_word_index():
    st.session_state.index = (st.session_state.index + 1) % len(data)

def make_quiz_item():
    """Return a dict with: prompt, choices, correct_idx, row (the pandas row)."""
    # pick one correct row
    i = random.randrange(len(data))
    row = data.iloc[i]

    # Build choices: correct word + 3 random other words
    other_indices = list(range(len(data)))
    other_indices.remove(i)
    wrong_idx = random.sample(other_indices, k=min(3, len(other_indices)))
    choices = [row["word"]] + [data.iloc[j]["word"] for j in wrong_idx]
    random.shuffle(choices)
    correct_idx = choices.index(row["word"])

    prompt = f'Which word matches this definition?\n\n**{row["definition"]}**'
    return {"prompt": prompt, "choices": choices, "correct_idx": correct_idx, "row": row}

# ---------- Sidebar mode ----------
mode = st.sidebar.radio("Mode", ["Learn", "Quiz"])

# ====================== LEARN MODE ======================
if mode == "Learn":
    row = data.iloc[st.session_state.index]
    st.subheader(f"Word: {row['word']} ({row['part_of_speech']})")

    if st.button("Show Definition"):
        st.write(f"**Definition:** {row['definition']}")
        st.write(f"**French:** {row['french']}")
        st.write(f"**Arabic:** {row['arabic']}")
        st.write(f"**Example:** {row['example']}")

    cols = st.columns(2)
    if cols[0].button("⬅️ Previous"):
        st.session_state.index = (st.session_state.index - 1) % len(data)
        st.rerun()
    if cols[1].button("Next ➡️"):
        next_word_index()
        st.rerun()

# ====================== QUIZ MODE ======================
else:
    # prepare a question if none loaded yet
    if st.session_state.quiz["current"] is None:
        st.session_state.quiz["current"] = make_quiz_item()

    q = st.session_state.quiz["current"]
    st.subheader(f"Quiz • Question {st.session_state.quiz['question_i'] + 1}")
    st.markdown(q["prompt"])

    # show choices as radio buttons
    choice = st.radio("Choose one:", q["choices"], index=None)

    # Check answer
    if st.button("Check"):
        if choice is None:
            st.warning("Pick an answer first 🙂")
        else:
            correct = (choice == q["choices"][q["correct_idx"]])
            if correct:
                st.success("✅ Correct!")
                st.session_state.quiz["score"] += 1
            else:
                st.error(f"❌ Not quite. Correct answer: **{q['choices'][q['correct_idx']]}**")

            # Show bilingual info + example
            row = q["row"]
            with st.expander("See explanation"):
                st.write(f"**Definition:** {row['definition']}")
                st.write(f"**French:** {row['french']}")
                st.write(f"**Arabic:** {row['arabic']}")
                st.write(f"**Example:** {row['example']}")

    # Next question
    cols = st.columns(2)
    if cols[0].button("Next Question ➡️"):
        st.session_state.quiz["question_i"] += 1
        st.session_state.quiz["current"] = make_quiz_item()
        st.rerun()

    # Reset quiz
    if cols[1].button("Reset Quiz ↺"):
        st.session_state.quiz = {"question_i": 0, "score": 0, "current": make_quiz_item()}
        st.rerun()

    # Score display
    st.info(f"Score: **{st.session_state.quiz['score']}** / {st.session_state.quiz['question_i']}")
