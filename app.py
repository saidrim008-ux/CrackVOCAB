import streamlit as st
import pandas as pd
from pathlib import Path
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
# Session state defaults
# --------------------------------
defaults = {
    "mode": "welcome",
    "username": "",
    "index": 0,
    "show_def": False,
    "learned": set(),
    "recent_pool": [],
    "quiz_index": 0,
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
    st.write("Enter your **name or nickname** to personalize your experience.")

    # Author badge
    st.markdown(
        "<p style='text-align:center; color:#5C4033; font-size:14px;'><i>Built by Rim Said</i></p>",
        unsafe_allow_html=True
    )

    name = st.text_input("Enter your name or nickname", value=st.session_state["username"])

    if st.button("Go 🚀", disabled=(not name.strip())):
        st.session_state["username"] = name
        st.session_state.mode = "home"
        st.rerun()

def sidebar_nav():
    st.sidebar.subheader("Go to")
    st.session_state.mode = st.sidebar.radio(
        label="",
        options=["home", "Words", "Quiz"],
        index=["home", "Words", "Quiz"].index(st.session_state.mode if st.session_state.mode in ["home","Words","Quiz"] else "home"),
    )
    st.sidebar.markdown("### 🔥 Streak")
    st.sidebar.caption("1-day streak • view last 30 days")
    st.sidebar.markdown("### 📝 Progress")
    st.sidebar.caption(f"Words mastered: {len(st.session_state.learned)} / {TOTAL}")

def page_home():
    name = st.session_state.username or "there"
    st.header(f"Hi {name}, welcome to crackVOCAB 👋")
    st.write("crackVOCAB helps you master advanced English vocabulary with bilingual explanations.")
    st.subheader("How it works")
    st.markdown("""
1) Go to **Words**.  
2) Click **Show Definition**, then **Mark as Learned**.  
3) Your progress updates.  
4) Use **Quiz** to practice recently learned words.
""")

def page_words():
    st.sidebar.subheader("Word list")
    options = [label_for_row(i) for i in range(TOTAL)]
    current_label = label_for_row(st.session_state.index)
    chosen = st.sidebar.selectbox("Select a word", options, index=options.index(current_label))
    if chosen != current_label:
        st.session_state.index = options.index(chosen)
        st.session_state.show_def = False

    row = data.iloc[st.session_state.index]
    st.header(f"{row['word']} ({row['part_of_speech']})")

    b1, b2, b3 = st.columns(3)
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
        if "french" in row: st.write(f"**French:** {row['french']}")
        if "arabic" in row: st.write(f"**Arabic:** {row['arabic']}")
        if "example" in row and isinstance(row["example"], str):
            st.write(f"**Example:** {row['example']}")

def page_quiz():
    st.header("Quiz")
    pool = list(dict.fromkeys(st.session_state.recent_pool))
    if not pool:
        st.info("Learn some words first to unlock the quiz.")
        return

    if st.session_state.quiz_index >= len(pool):
        st.success("🎉 Quiz finished!")
        if st.button("Restart Quiz"):
            st.session_state.quiz_index = 0
        return

    word = pool[st.session_state.quiz_index]
    row = data[data["word"] == word].iloc[0]
    correct_def = row["definition"]

    # 3 wrong options
    wrong_defs = data[data["word"] != word]["definition"].sample(min(3, len(data)-1)).tolist()
    options = wrong_defs + [correct_def]
    random.shuffle(options)

    st.subheader(f"What does **{word}** mean?")
    choice = st.radio("Choose one:", options)

    if st.button("Check Answer"):
        if choice == correct_def:
            st.success("✅ Correct!")
        else:
            st.error(f"❌ Wrong. Correct answer: {correct_def}")

    if st.button("Next Question"):
        st.session_state.quiz_index += 1
        st.rerun()

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
