import streamlit as st
import pandas as pd
import random
import datetime

# Load words
words_df = pd.read_csv("words.csv")

# App configuration
st.set_page_config(page_title="CrackVOCAB", page_icon="📘", layout="wide")

# Initialize session state
if "mode" not in st.session_state:
    st.session_state.mode = "home"
if "learned_words" not in st.session_state:
    st.session_state.learned_words = []
if "streak" not in st.session_state:
    st.session_state.streak = 0
if "last_study_date" not in st.session_state:
    st.session_state.last_study_date = None

# Sidebar navigation
st.sidebar.title("Go to")
if st.sidebar.button("Home"):
    st.session_state.mode = "home"
if st.sidebar.button("Words"):
    st.session_state.mode = "words"
if st.sidebar.button("Quiz"):
    st.session_state.mode = "quiz"

# Track streak
def update_streak():
    today = datetime.date.today()
    if st.session_state.last_study_date is None:
        st.session_state.streak = 1
    else:
        delta = (today - st.session_state.last_study_date).days
        if delta == 1:
            st.session_state.streak += 1
        elif delta > 1:
            st.session_state.streak = 1
    st.session_state.last_study_date = today

# HOME PAGE
if st.session_state.mode == "home":
    st.title("Hi, welcome to CrackVOCAB 👋")
    st.markdown("### Let's master our vocabulary together")
    st.caption("Built by **Rimsaid**")  # author credit only here

    st.write("CrackVOCAB helps you master advanced English vocabulary with bilingual explanations.")
    st.subheader("How it works")
    st.markdown("""
    1. Open **Words**, pick any word.  
    2. Click **Show Definition**, then **Mark as Learned**.  
    3. Progress updates automatically.  
    4. Use **Quiz** to test your last learned words.  
    """)

    st.metric("🔥 Streak", f"{st.session_state.streak} days")
    st.metric("📊 Progress", f"{len(st.session_state.learned_words)} / {len(words_df)} words mastered")

# WORDS PAGE
elif st.session_state.mode == "words":
    st.header("Words 📖")

    word_list = words_df["word"].tolist()
    choice = st.selectbox("Select a word", word_list)

    if st.button("Show Definition"):
        definition = words_df.loc[words_df["word"] == choice, "definition"].values[0]
        st.info(definition)

        if st.button("Mark as Learned"):
            if choice not in st.session_state.learned_words:
                st.session_state.learned_words.append(choice)
                update_streak()
                st.success(f"'{choice}' added to your learned words!")

    st.write("### Your Progress")
    st.progress(len(st.session_state.learned_words) / len(words_df))

# QUIZ PAGE
elif st.session_state.mode == "quiz":
    st.header("Quiz 📝")

    if len(st.session_state.learned_words) == 0:
        st.info("No words in your quiz pool yet. Mark some words as learned first.")
    else:
        word = random.choice(st.session_state.learned_words)
        correct_def = words_df.loc[words_df["word"] == word, "definition"].values[0]

        st.write(f"**What does '{word}' mean?**")

        # Multiple-choice (1 correct + 3 random)
        options = [correct_def]
        wrong_defs = words_df.loc[words_df["word"] != word, "definition"].sample(3).tolist()
        options.extend(wrong_defs)
        random.shuffle(options)

        choice = st.radio("Choose the correct definition:", options)

        if st.button("Submit"):
            if choice == correct_def:
                st.success("✅ Correct!")
            else:
                st.error(f"❌ Wrong! The correct answer is: {correct_def}")
