import streamlit as st
import pandas as pd
from pathlib import Path
import random

# --------------------------
# Basic Config
# --------------------------
st.set_page_config(page_title="crackVOCAB", page_icon="📘", layout="wide")

# --------------------------
# Global CSS
# --------------------------
st.markdown("""
<style>
.stApp { background-color:#F5E6D3 !important; color:#111 !important; }
section[data-testid="stSidebar"] { background-color:#F2DEBE !important; }
h1,h2,h3,h4,h5,h6 { color:#222 !important; }

/* Buttons (sky blue) */
div.stButton > button {
    background:#7FD6E8 !important;
    color:#111 !important;
    border:1px solid #54b9cf !important;
    border-radius:10px !important;
    font-weight:600 !important;
    padding:.4rem .9rem !important;
}
</style>
""", unsafe_allow_html=True)

# --------------------------
# Load Words
# --------------------------
DATA_FILE = Path("words.csv")
if not DATA_FILE.exists():
    st.error("⚠️ words.csv not found")
    st.stop()

data = pd.read_csv(DATA_FILE).dropna(subset=["word"]).drop_duplicates("word").reset_index(drop=True)
TOTAL = len(data)

# --------------------------
# Session State
# --------------------------
if "mode" not in st.session_state: st.session_state.mode = "welcome"
if "username" not in st.session_state: st.session_state.username = ""
if "index" not in st.session_state: st.session_state.index = 0
if "show_def" not in st.session_state: st.session_state.show_def = False
if "learned" not in st.session_state: st.session_state.learned = set()
if "recent_pool" not in st.session_state: st.session_state.recent_pool = []
if "quiz_index" not in st.session_state: st.session_state.quiz_index = 0

# --------------------------
# Helpers
# --------------------------
def label_for_row(i: int) -> str:
    r = data.iloc[i]
    return f"{r['word']} ({r['part_of_speech']})"

def goto_next():
    st.session_state.index = (st.session_state.index + 1) % TOTAL
    st.session_state.show_def = False
    st.experimental_rerun()

def goto_prev():
    st.session_state.index = (st.session_state.index - 1) % TOTAL
    st.session_state.show_def = False
    st.experimental_rerun()

def toggle_learned():
    w = data.iloc[st.session_state.index]["word"]
    if w in st.session_state.learned:
        st.session_state.learned.remove(w)
    else:
        st.session_state.learned.add(w)
        st.session_state.recent_pool.append(w)
        st.session_state.recent_pool = st.session_state.recent_pool[-10:]
    st.experimental_rerun()

# --------------------------
# Pages
# --------------------------
def page_welcome():
    st.title("Let's master vocabulary together 💪")
    st.write("Enter your **name or nickname** to get started.")

    st.markdown("<p style='text-align:center; color:#5C4033; font-size:14px;'>Built by Rimsaid</p>",
                unsafe_allow_html=True)

    name = st.text_input("Enter your name or nickname", value=st.session_state.username)
    if st.button("Go 🚀", disabled=not name.strip()):
        st.session_state.username = name
        st.session_state.mode = "Home"
        st.experimental_rerun()

def sidebar_nav():
    st.sidebar.title("📘 crackVOCAB")
    st.sidebar.radio("Navigation", ["Home","Words","Quiz"], key="mode")

    # streak + progress
    st.sidebar.markdown("### 🔥 Streak")
    st.sidebar.caption(f"{len(st.session_state.learned)}-day streak")
    st.sidebar.markdown("### 📝 Progress")
    st.sidebar.caption(f"Words mastered: {len(st.session_state.learned)} / {TOTAL}")

    st.sidebar.markdown("### Word list")
    options = [label_for_row(i) for i in range(TOTAL)]
    current_label = label_for_row(st.session_state.index)
    chosen = st.sidebar.selectbox("Select a word", options, index=options.index(current_label))
    if chosen != current_label:
        st.session_state.index = options.index(chosen)
        st.session_state.show_def = False

def page_home():
    st.header(f"Hi {st.session_state.username}, welcome to crackVOCAB 👋")
    st.write("Learn advanced English vocabulary with **definitions + French + Arabic**.")
    st.markdown("""
1. Go to **Words**, show definition, mark as learned.  
2. Your streak & progress update automatically.  
3. After 10 words → unlock **Quiz**.  
    """)

def page_words():
    row = data.iloc[st.session_state.index]
    st.header(f"{row['word']} ({row['part_of_speech']})")

    b1, b2, b3 = st.columns([1,1,1])
    if b1.button("Show Definition"): st.session_state.show_def = not st.session_state.show_def
    if b2.button("◀ Previous"): goto_prev()
    if b3.button("Next ▶"): goto_next()

    if st.button("Mark as Learned" if row["word"] not in st.session_state.learned else "✅ Marked"):
        toggle_learned()

    if st.session_state.show_def:
        st.markdown("---")
        st.write(f"**Definition:** {row['definition']}")
        st.write(f"**French:** {row.get('french','')}")
        st.write(f"**Arabic:** {row.get('arabic','')}")
        if isinstance(row.get("example",""), str) and row["example"].strip():
            st.write(f"**Example:** {row['example']}")

def page_quiz():
    st.header("Quiz")
    pool = st.session_state.recent_pool
    if len(pool) < 10:
        st.info("Learn at least 10 words to start the quiz.")
        return

    # Current word
    word = pool[st.session_state.quiz_index % len(pool)]
    st.subheader(f"What does **{word}** mean?")

    # Correct definition
    row = data[data["word"]==word].iloc[0]
    correct = row["definition"]

    # Options
    wrong_defs = random.sample(
        list(data.loc[data["word"]!=word,"definition"]), 3
    )
    options = wrong_defs + [correct]
    random.shuffle(options)

    choice = st.radio("Choose one:", options, key=f"quiz_{st.session_state.quiz_index}")

    if st.button("Check Answer"):
        if choice == correct:
            st.success("✅ Correct!")
        else:
            st.error(f"❌ Wrong. Correct answer: {correct}")

    if st.button("Next Question"):
        st.session_state.quiz_index += 1
        st.experimental_rerun()

# --------------------------
# Router
# --------------------------
if st.session_state.mode == "welcome":
    page_welcome()
else:
    sidebar_nav()
    if st.session_state.mode == "Home":
        page_home()
    elif st.session_state.mode == "Words":
        page_words()
    else:
        page_quiz()
