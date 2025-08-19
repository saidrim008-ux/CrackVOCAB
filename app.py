import streamlit as st
import pandas as pd
from pathlib import Path
from datetime import date

# --------------------------------
# App setup
# --------------------------------
st.set_page_config(page_title="crackVOCAB", page_icon="📘", layout="wide")

# ----- Global CSS (beige theme + components) -----
st.markdown("""
<style>
/* Beige app background + black text */
.stApp, .block-container { background: #F5E6D3 !important; color: #111 !important; }

/* Headings */
h1, h2, h3, h4, h5, h6 { color:#222 !important; }

/* Sidebar keep light (beige) */
section[data-testid="stSidebar"] { background: #F2DEBE !important; }

/* Inputs (text + search) — beige with black text */
.stTextInput > div > div > input {
  background:#FAF1E3 !important; color:#111 !important; border:1px solid #e3d2b8 !important;
}

/* Selectbox (word list) — beige, no dark tiles */
.stSelectbox > div > div, .stSelectbox > div > div > div { 
  background:#FAF1E3 !important; color:#111 !important; 
  border:1px solid #e3d2b8 !important;
}
[data-baseweb="select"] div[role="listbox"] { background:#FAF1E3 !important; }
[data-baseweb="select"] div[role="option"] { color:#111 !important; }

/* All buttons: soft sky-blue chip style */
div.stButton > button, .st-emotion-cache-19rxjzo { 
  background:#7FD6E8 !important; color:#0d1117 !important; 
  border:1px solid #54b9cf !important; border-radius:10px !important; 
  font-weight:600 !important; padding:.45rem .9rem !important;
}
div.stButton > button:hover { filter: brightness(0.97); }

/* Center main column a bit */
.block-container { padding-top: 1.2rem; }
/* Sidebar captions (muted text) -> brown */
section[data-testid="stSidebar"] p,
section[data-testid="stSidebar"] span {    color: #5C4033 !important;   /* rich brown */
}

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
    "mode": "welcome",       # welcome → home → words/quiz
    "name": "",
    "index": 0,
    "show_def": False,
    "learned": set(),        # set of words the user marked as learned
    "recent_pool": []        # last 10 learned for quiz
}
for k, v in defaults.items():
    if k not in st.session_state:
        st.session_state[k] = v

# Utility to keep selectbox synced with index
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
        # update recent pool (keep last 10)
        st.session_state.recent_pool.append(w)
        st.session_state.recent_pool = st.session_state.recent_pool[-10:]
    st.rerun()

# --------------------------------
# PAGES
# --------------------------------
def page_welcome():
    st.title("Let's master vocabulary together 💪")
    st.write("Enter your **name or nickname** to personalize your experience.")

    # Author name only on first screen
    st.markdown(
        "<p style='text-align:center; color:#5C4033; font-size:14px;'><i>Built by Rim Said</i></p>",
        unsafe_allow_html=True
    )

    # Handle username
    if "username" not in st.session_state:
        st.session_state["username"] = ""

    name = st.text_input("Enter your name or nickname", value=st.session_state["username"])

    if st.button("Go 🚀", use_container_width=False, type="primary", disabled=(not name.strip())):
        st.session_state["username"] = name
        st.session_state.mode = "home"
        st.experimental_rerun()

def sidebar_nav():
    st.sidebar.subheader("Go to")
    st.sidebar.radio(
        label="",
        options=["Home", "Words", "Quiz"],
        key="nav_choice",
        index=["Home","Words","Quiz"].index("Home" if st.session_state.mode=="home" else st.session_state.mode),
    )
    # Small stats
    st.sidebar.markdown("### 🔥 Streak")
    st.sidebar.caption("1-day streak • view last 30 days")
    st.sidebar.markdown("### 📝 Progress")
    st.sidebar.caption(f"Words mastered: {len(st.session_state.learned)} / {TOTAL}")

def page_home():
    name = st.session_state.name or "there"
    st.header(f"Hi there, {name} — welcome to crackVOCAB 👋")
    st.write(
        "crackVOCAB helps you master **advanced English vocabulary** with bilingual "
        "(English—French—Arabic) explanations — built for focus and flow."
    )

    st.subheader("How it works")
    st.markdown("""
1) Open **Words** (left sidebar), pick any word.  
2) Click **Show Definition**, then **Mark as Learned** when you’re ready.  
3) Your progress updates automatically.  
4) Use **Quiz** to practice only your **recently learned** words (last 10).
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
    # left rail: small word tools
    st.sidebar.subheader("Word list")
    st.sidebar.caption(f"Total words: {TOTAL}")

    # Word picker (selectbox shows beige now)
    options = [label_for_row(i) for i in range(TOTAL)]
    current_label = label_for_row(st.session_state.index)
    chosen = st.sidebar.selectbox("Select a word", options, index=options.index(current_label))
    if chosen != current_label:
        st.session_state.index = options.index(chosen)
        st.session_state.show_def = False

    # Main area
    row = data.iloc[st.session_state.index]
    st.header("Words")
    st.subheader(f"{row['word']} ({row['part_of_speech']})")

    # Buttons row
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

    # Mark as learned (center)
    _, mid, _ = st.columns([1,1,1])
    with mid:
        learned = row["word"] in st.session_state.learned
        label = "✅ Marked" if learned else "Mark as Learned"
        if st.button(label):
            toggle_learned()

    # Definition block
    if st.session_state.show_def:
        st.markdown("---")
        st.write(f"**Definition:** {row['definition']}")
        st.write(f"**French:** {row.get('french','')}")
        st.write(f"**Arabic:** {row.get('arabic','')}")
        ex = row.get('example','')
        if isinstance(ex, str) and ex.strip():
            st.write(f"**Example:** {ex}")

def page_quiz():
    st.header("Quiz")
    pool = list(dict.fromkeys(st.session_state.recent_pool))  # unique, keep order
    if not pool:
        st.info("Your quiz pool is empty. Learn some words first (mark as learned), then come back!")
        return
    st.write("You’ll be quizzed on **recently learned** words (last 10).")
    st.write(", ".join(pool))

# --------------------------------
# Router
# --------------------------------
    if st.session_state.mode == "welcome":
    page_welcome()
    else:
    sidebar_nav()
    # honor sidebar navigation
    dest = st.session_state.get("nav_choice", "Home")
    if dest == "Home":
        st.session_state.mode = "home"
        page_home()
    elif dest == "Words":
        st.session_state.mode = "Words"
        page_words()
    else:
        st.session_state.mode = "Quiz"
        page_quiz()
    elif mode == "Quiz":
    st.header("Quiz")
    st.write("You'll be quizzed on recently learned words (last 10).")

    # Get last 10 learned words (replace with your own list logic)
    recent_words = ["benevolent", "candid", "diligent", "elated", "alacrity", 
                    "ambivalent", "anomaly", "antithesis", "apathetic", "arduous"]

    import random

    # Pick a word to quiz
        if "quiz_index" not in st.session_state:
        st.session_state.quiz_index = 0
        random.shuffle(recent_words)  # shuffle order

        if st.session_state.quiz_index < len(recent_words):
        word = recent_words[st.session_state.quiz_index]
        
        # Example definitions (replace with your real dict or DB)
        definitions = {
            "benevolent": "kind and generous",
            "candid": "honest and straightforward",
            "diligent": "showing care and effort",
            "elated": "very happy",
            "alacrity": "cheerful readiness",
            "ambivalent": "having mixed feelings",
            "anomaly": "something unusual",
            "antithesis": "direct opposite",
            "apathetic": "showing no interest",
            "arduous": "very difficult"
        }

        correct_def = definitions[word]

        # Generate 3 random wrong answers
        wrong_defs = random.sample([v for k,v in definitions.items() if k != word], 3)
        options = wrong_defs + [correct_def]
        random.shuffle(options)

        st.subheader(f"What does **{word}** mean?")
        choice = st.radio("Choose one:", options)

        if st.button("Check Answer"):
        if choice == correct_def:
                st.success("✅ Correct!")
        else:
                st.error(f"❌ Wrong. The correct answer is: {correct_def}")

        if st.button("Next Question"):
                st.session_state.quiz_index += 1
                st.experimental_rerun()
        else:
        st.success("🎉 Quiz finished!")

