import streamlit as st
import pandas as pd
from pathlib import Path
import random

# ----------------------------
# App setup
# ----------------------------
st.set_page_config(page_title="crackVOCAB", page_icon="📘", layout="wide")

# ----- CSS -----
st.markdown("""
<style>
.stApp, .block-container { background: #F5E6D3 !important; color: #111 !important; }
h1, h2, h3, h4, h5, h6 { color:#222 !important; }
.stTextInput > div > div > input {
  background:#FAF1E3 !important; color:#111 !important; border:1px solid #e3d2b8 !important;
}
.stSelectbox > div > div, .stSelectbox > div > div > div { 
  background:#FAF1E3 !important; color:#111 !important; border:1px solid #e3d2b8 !important;
}
[data-baseweb="select"] div[role="listbox"] { background:#FAF1E3 !important; }
[data-baseweb="select"] div[role="option"] { color:#111 !important; }

div.stButton > button { 
  background:#7FD6E8 !important; color:#0d1117 !important; 
  border:1px solid #54b9cf !important; border-radius:10px !important; 
  font-weight:600 !important; padding:.45rem .9rem !important;
}
div.stButton > button:hover { filter: brightness(0.97); }

.navbar {
  position: fixed;
  bottom: 0;
  left: 0;
  width: 100%;
  background: #F5E6D3;
  padding: 10px;
  text-align: center;
  border-top: 1px solid #ccc;
}
</style>
""", unsafe_allow_html=True)

# ----------------------------
# Load data
# ----------------------------
DATA_FILE = Path("words.csv")
if not DATA_FILE.exists():
    st.error("words.csv not found. Please add it to continue.")
    st.stop()

data = pd.read_csv(DATA_FILE).dropna(subset=["word"]).drop_duplicates(subset=["word"]).reset_index(drop=True)
TOTAL = len(data)

# ----------------------------
# Session state
# ----------------------------
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

# ----------------------------
# Utils
# ----------------------------
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

# ----------------------------
# Pages
# ----------------------------
def page_welcome():
    st.title("Let's master vocabulary together 💪")
    st.write("Enter your **name or nickname** to personalize your experience.")

    # Author badge
    st.markdown("<p style='text-align:center; color:#5C4033; font-size:14px;'><i>Built by Rim Said</i></p>", unsafe_allow_html=True)

    name = st.text_input("Enter your name or nickname", value=st.session_state.username)

    if st.button("Go 🚀", disabled=(not name.strip())):
        st.session_state.username = name
        st.session_state.mode = "home"
        st.experimental_rerun()

def page_home():
    name = st.session_state.username or "there"
    st.header(f"Hi {name}, welcome to crackVOCAB 👋")
    st.write("crackVOCAB helps you master **advanced English vocabulary** with bilingual explanations.")
    st.subheader("How it works")
    st.markdown("""
1) Go to **Words**.  
2) Click **Show Definition** and then **Mark as Learned**.  
3) Your progress updates automatically.  
4) Use **Quiz** to practice your last 10 learned words.
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
    with c3:
        if st.button("Next ▶"):
            goto_next()

    learned = row["word"] in st.session_state.learned
    if st.button("✅ Mark as Learned" if not learned else "❌ Unmark"):
        toggle_learned()

    if st.session_state.show_def:
        st.markdown("---")
        st.write(f"**Definition:** {row['definition']}")
        st.write(f"**French:** {row.get('french','')}")
        st.write(f"**Arabic:** {row.get('arabic','')}")
        if isinstance(row.get("example",""), str) and row["example"].strip():
            st.write(f"**Example:** {row['example']}")

def page_quiz():
    st.header("Quiz 📝")

    pool = list(dict.fromkeys(st.session_state.recent_pool))
    if not pool:
        st.info("No words in your quiz pool yet. Mark some as learned first.")
        return

    if st.session_state.quiz_index >= len(pool):
        st.success("🎉 Quiz finished!")
        if st.button("Reset Quiz"):
            st.session_state.quiz_index = 0
        return

    word = pool[st.session_state.quiz_index]

    # Use real definitions if available
    definitions = {r["word"]: r["definition"] for _, r in data.iterrows()}
    correct_def = definitions.get(word, f"Definition of {word}")
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

# ----------------------------
# Router
# ----------------------------
if st.session_state.mode == "welcome":
    page_welcome()
elif st.session_state.mode == "home":
    page_home()
elif st.session_state.mode == "words":
    page_words()
elif st.session_state.mode == "quiz":
    page_quiz()

# ----------------------------
# Bottom navigation bar
# ----------------------------
st.markdown(
    """
    <div class="navbar">
        <form action="" method="get">
            <button name="nav" value="home">Home</button>
            <button name="nav" value="words">Words</button>
            <button name="nav" value="quiz">Quiz</button>
        </form>
    </div>
    """,
    unsafe_allow_html=True,
)

# Handle nav button clicks
nav = st.query_params.get("nav", None)
if nav:
    st.session_state.mode = nav
    st.experimental_rerun()
