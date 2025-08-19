import streamlit as st
import pandas as pd
from pathlib import Path
import random

# -------------------------
# App setup
# -------------------------
st.set_page_config(page_title="crackVOCAB", page_icon="📘", layout="wide")

# -------------------------
# Load Data
# -------------------------
DATA_FILE = Path("words.csv")
if not DATA_FILE.exists():
    st.error("words.csv not found. Please add it to continue.")
    st.stop()

data = pd.read_csv(DATA_FILE).dropna(subset=["word"]).drop_duplicates(subset=["word"]).reset_index(drop=True)
TOTAL = len(data)

# -------------------------
# Session State Defaults
# -------------------------
if "mode" not in st.session_state:
    st.session_state.mode = "welcome"
if "username" not in st.session_state:
    st.session_state.username = ""
if "index" not in st.session_state:
    st.session_state.index = 0
if "show_def" not in st.session_state:
    st.session_state.show_def = False
if "learned" not in st.session_state:
    st.session_state.learned = set()
if "recent_pool" not in st.session_state:
    st.session_state.recent_pool = []
if "quiz_index" not in st.session_state:
    st.session_state.quiz_index = 0

# -------------------------
# Utility
# -------------------------
def label_for_row(i: int) -> str:
    r = data.iloc[i]
    return f"{r['word']} ({r['part_of_speech']})"

def goto_next():
    st.session_state.index = (st.session_state.index + 1) % TOTAL
    st.session_state.show_def = False

def goto_prev():
    st.session_state.index = (st.session_state.index - 1) % TOTAL
    st.session_state.show_def = False

def toggle_learned():
    w = data.iloc[st.session_state.index]["word"]
    if w in st.session_state.learned:
        st.session_state.learned.remove(w)
    else:
        st.session_state.learned.add(w)
        st.session_state.recent_pool.append(w)
        st.session_state.recent_pool = st.session_state.recent_pool[-10:]

# -------------------------
# Pages
# -------------------------
def page_welcome():
    st.title("Let's master vocabulary together 💪")
    st.write("Enter your **name or nickname** to personalize your experience.")

    # Author name only here
    st.markdown("<p style='text-align:center; color:#5C4033; font-size:14px;'><i>Built by Reem Saeed</i></p>", unsafe_allow_html=True)

    name = st.text_input("Enter your name or nickname", value=st.session_state.username)

    if st.button("Go 🚀", disabled=(not name.strip())):
        st.session_state.username = name
        st.session_state.mode = "home"
        st.experimental_rerun()

def sidebar_nav():
    st.sidebar.subheader("Navigation")
    dest = st.sidebar.radio("", ["Home", "Words"])
    return dest

def page_home():
    st.header(f"Hi {st.session_state.username}, welcome to crackVOCAB 👋")
    st.write("This app helps you master **advanced English vocabulary** with bilingual explanations.")
    st.subheader("How it works")
    st.markdown("""
1. Go to **Words** in the sidebar.  
2. Click **Show Definition** and mark words as learned.  
3. Your learned words are tracked.  
4. At the bottom of **Words**, practice with a quiz on your recent words.
""")

def page_words():
    st.header("Words")
    options = [label_for_row(i) for i in range(TOTAL)]
    current_label = label_for_row(st.session_state.index)
    chosen = st.selectbox("Select a word", options, index=options.index(current_label))
    if chosen != current_label:
        st.session_state.index = options.index(chosen)
        st.session_state.show_def = False

    row = data.iloc[st.session_state.index]
    st.subheader(f"{row['word']} ({row['part_of_speech']})")

    c1, c2, c3 = st.columns(3)
    with c1:
        if st.button("Show Definition"):
            st.session_state.show_def = not st.session_state.show_def
    with c2:
        if st.button("◀ Previous"):
            goto_prev()
            st.experimental_rerun()
    with c3:
        if st.button("Next ▶"):
            goto_next()
            st.experimental_rerun()

    learned = row["word"] in st.session_state.learned
    if st.button("✅ Mark as Learned" if not learned else "❌ Unmark"):
        toggle_learned()
        st.experimental_rerun()

    if st.session_state.show_def:
        st.markdown("---")
        st.write(f"**Definition:** {row['definition']}")
        st.write(f"**French:** {row.get('french','')}")
        st.write(f"**Arabic:** {row.get('arabic','')}")
        if isinstance(row.get("example",""), str) and row["example"].strip():
            st.write(f"**Example:** {row['example']}")

    # ---------------- QUIZ SECTION ----------------
    st.markdown("---")
    st.subheader("Quick Quiz 📝")

    pool = list(dict.fromkeys(st.session_state.recent_pool))  # unique, keep order
    if not pool:
        st.info("No words in your quiz pool yet. Mark some as learned first.")
        return

    # Pick current quiz word
    if st.session_state.quiz_index >= len(pool):
        st.success("🎉 Quiz finished! Reset to try again.")
        if st.button("Reset Quiz"):
            st.session_state.quiz_index = 0
        return

    word = pool[st.session_state.quiz_index]

    # Example dictionary (replace with real definitions from CSV if available)
    definitions = {
        w: f"Definition of {w}" for w in pool
    }

    correct_def = definitions[word]
    wrong_defs = random.sample([v for k, v in definitions.items() if k != word], min(3, len(definitions)-1))
    options = wrong_defs + [correct_def]
    random.shuffle(options)

    st.write(f"What does **{word}** mean?")
    choice = st.radio("Choose one:", options, key=f"quiz_{st.session_state.quiz_index}")

    if st.button("Check Answer"):
        if choice == correct_def:
            st.success("✅ Correct!")
        else:
            st.error(f"❌ Wrong. The correct answer is: {correct_def}")

    if st.button("Next Question"):
        st.session_state.quiz_index += 1
        st.experimental_rerun()

# -------------------------
# Router
# -------------------------
if st.session_state.mode == "welcome":
    page_welcome()
else:
    dest = sidebar_nav()
    if dest == "Home":
        page_home()
    elif dest == "Words":
        page_words()
