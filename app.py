import streamlit as st
import pandas as pd
from pathlib import Path
from datetime import date
import random

# --------------------------------
# App setup
# --------------------------------
st.set_page_config(page_title="crackVOCAB", page_icon="📘", layout="wide")

# ----- Global CSS (beige theme + components) -----
st.markdown("""
<style>
.stApp, .block-container { background: #F5E6D3 !important; color: #111 !important; }
h1, h2, h3, h4, h5, h6 { color:#222 !important; }
section[data-testid="stSidebar"] { background: #F2DEBE !important; }
.stTextInput > div > div > input {
  background:#FAF1E3 !important; color:#111 !important; border:1px solid #e3d2b8 !important;
}
.stSelectbox > div > div, .stSelectbox > div > div > div { 
  background:#FAF1E3 !important; color:#111 !important; 
  border:1px solid #e3d2b8 !important;
}
[data-baseweb="select"] div[role="listbox"] { background:#FAF1E3 !important; }
[data-baseweb="select"] div[role="option"] { color:#111 !important; }
div.stButton > button { 
  background:#7FD6E8 !important; color:#0d1117 !important; 
  border:1px solid #54b9cf !important; border-radius:10px !important; 
  font-weight:600 !important; padding:.45rem .9rem !important;
}
div.stButton > button:hover { filter: brightness(0.97); }
.block-container { padding-top: 1.2rem; }
section[data-testid="stSidebar"] p,
section[data-testid="stSidebar"] span { color: #5C4033 !important; }
</style>
""", unsafe_allow_html=True)

# --------------------------------
# Load data
# --------------------------------
DATA_FILE = Path("words.csv")
if not DATA_FILE.exists():
    st.error("words.csv not found in the repo. Please add it to continue.")
    st.stop()

data = (
    pd.read_csv(DATA_FILE)
      .dropna(subset=["word"])
      .drop_duplicates(subset=["word"])
      .reset_index(drop=True)
)
TOTAL = len(data)

# --------------------------------
# Session state (defaults)
# --------------------------------
defaults = {
    "mode": "welcome",
    "username": "",
    "index": 0,
    "show_def": False,
    "learned": set(),
    "recent_pool": [],
    "quiz_index": 0
}
for k, v in defaults.items():
    if k not in st.session_state:
        st.session_state[k] = v

# --------------------------------
# Helpers
# --------------------------------
def label_for_row(i: int) -> str:
    r = data.iloc[i]
    return f"{r['word']} ({r['part_of_speech']})"

def goto_next():
    st.session_state.index = (st.session_state.index + 1) % TOTAL
    st.session_state.show_def = False
    st.rerun()

def goto_prev():
    st.session_state.index = (st.session_state.index - 1) % TOTAL
    st.session_state.show_def = False
    st.rerun()

def toggle_learned():
    w = data.iloc[st.session_state.index]["word"]
    if w in st.session_state.learned:
        st.session_state.learned.remove(w)
    else:
        st.session_state.learned.add(w)
        st.session_state.recent_pool.append(w)
        st.session_state.recent_pool = st.session_state.recent_pool[-10:]
    st.rerun()

# --------------------------------
# Pages
# --------------------------------
def page_welcome():
    st.title("Let's master vocabulary together 💪")

    st.markdown(
        "<p style='text-align:center; color:#5C4033; font-size:14px;'><i>Built by Rim Said</i></p>",
        unsafe_allow_html=True
    )

    name = st.text_input("Enter your name or nickname", value=st.session_state.username)
    if st.button("Go 🚀", disabled=(not name.strip())):
        st.session_state.username = name
        st.session_state.mode = "home"
        st.experimental_rerun()

def sidebar_nav():
    st.sidebar.subheader("Go to")
    st.sidebar.radio(
        label="",
        options=["Home", "Words", "Quiz"],
        key="nav_choice",
        index=["Home","Words","Quiz"].index(
            "Home" if st.session_state.mode=="home" else st.session_state.mode
        ),
    )
    st.sidebar.markdown("### 🔥 Streak")
    st.sidebar.caption("1-day streak • view last 30 days")
    st.sidebar.markdown("### 📝 Progress")
    st.sidebar.caption(f"Words mastered: {len(st.session_state.learned)} / {TOTAL}")

def page_home():
    name = st.session_state.username or "there"
    st.header(f"Hi {name}, welcome to crackVOCAB 👋")
    st.write(
        "crackVOCAB helps you master **advanced English vocabulary** with bilingual "
        "(English—French—Arabic) explanations."
    )

    st.subheader("How it works")
    st.markdown("""
1) Open **Words**, pick any word.  
2) Click **Show Definition**, then **Mark as Learned**.  
3) Progress updates automatically.  
4) Use **Quiz** to test your last 10 learned words.
""")

    c1, c2 = st.columns([1,1])
    with c1:
        if st.button("Start learning ➜"):
            st.session_state.mode = "Words"
            st.rerun()
    with c2:
        if st.button("Clear recent pool"):
            st.session_state.recent_pool = []
            st.rerun()

def page_words():
    st.sidebar.subheader("Word list")
    st.sidebar.caption(f"Total words: {TOTAL}")

    options = [label_for_row(i) for i in range(TOTAL)]
    current_label = label_for_row(st.session_state.index)
    chosen = st.sidebar.selectbox("Select a word", options, index=options.index(current_label))
    if chosen != current_label:
        st.session_state.index = options.index(chosen)
        st.session_state.show_def = False

    row = data.iloc[st.session_state.index]
    st.header("Words")
    st.subheader(f"{row['word']} ({row['part_of_speech']})")

    b1, b2, b3 = st.columns([1,1,1])
    with b1:
        if st.button("Show Definition"):
            st.session_state.show_def = not st.session_state.show_def
    with b2:
        if st.button("◀ Previous"):
            goto_prev()
    with b3:
        if st.button("Next ▶"):
            goto_next()

    _, mid, _ = st.columns([1,1,1])
    with mid:
        learned = row["word"] in st.session_state.learned
        label = "✅ Marked" if learned else "Mark as Learned"
        if st.button(label):
            toggle_learned()

    if st.session_state.show_def:
        st.markdown("---")
        st.write(f"**Definition:** {row['definition']}")
        st.write(f"**French:** {row.get('french','')}")
        st.write(f"**Arabic:** {row.get('arabic','')}")
        ex = row.get('example','')
        if isinstance(ex, str) and ex.strip():
            st.write(f"**Example:** {ex}")

# -------------------------
# QUIZ PAGE
# -------------------------
def page_quiz():
    import random
    st.header("Quiz")
    st.write("You'll be quizzed on recently learned words.")

    # Example recent words (replace with your list or session data)
    recent_words = ["benevolent", "candid", "diligent", "elated", 
                    "ambivalent", "anomaly", "antithesis", "apathetic"]

    if not recent_words:
        st.info("No recent words to quiz. Learn some words first!")
        return

    # Pick a random word
    word = random.choice(recent_words)

    # Example fake choices (you should load definitions from your CSV)
    choices = [
        f"Definition of {word} (correct)",
        "Some wrong definition",
        "Another wrong definition",
        "Yet another wrong definition"
    ]
    random.shuffle(choices)

    st.subheader(f"What does **{word}** mean?")
    answer = st.radio("Choose one:", choices)

    if st.button("Submit"):
        if answer.startswith("Definition of"):
            st.success("✅ Correct!")
        else:
            st.error("❌ Wrong, try again.")

# --------------------------------
# Router
# --------------------------------
if st.session_state.mode == "welcome":
    page_welcome()
else:
    sidebar_nav()
    if st.session_state.mode == "home":
        page_home()
    elif st.session_state.mode == "Words":
        page_words()
    elif st.session_state.mode == "Quiz":
        page_quiz()
