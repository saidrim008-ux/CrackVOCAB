import streamlit as st
import random

# -------------------------
# WELCOME PAGE
# -------------------------
def page_welcome():
    st.markdown(
        "<h1 style='text-align: center; color: beige;'>Let's Master Our Vocabulary Together</h1>",
        unsafe_allow_html=True
    )
    st.markdown(
        "<p style='text-align: center;'>By Reem Saeed</p>",
        unsafe_allow_html=True
    )

    # Ask user for their name
    name = st.text_input("Enter your name or nickname:")
    if st.button("Go"):
        if name.strip() != "":
            st.session_state.name = name
            st.session_state.mode = "home"


# -------------------------
# HOME PAGE
# -------------------------
def page_home():
    st.header(f"Hi {st.session_state.name}, welcome to CrackVOCAB 👋")
    st.write("CrackVOCAB helps you master advanced English vocabulary with bilingual (English–French–Arabic) explanations.")


# -------------------------
# WORDS PAGE
# -------------------------
def page_words():
    st.header("Words")
    st.write("Pick a word and learn its definition.")

    # Example word list
    words = ["abate (verb)", "benevolent (adj)", "candid (adj)", "diligent (adj)"]
    choice = st.selectbox("Select a word", words)

    if st.button("Show Definition"):
        st.write(f"Definition of {choice} will appear here (link to CSV).")


# -------------------------
# QUIZ PAGE
# -------------------------
def page_quiz():
    st.header("Quiz")
    st.write("You'll be quizzed on recently learned words.")

    # Example recent words (replace with real data from CSV/session)
    recent_words = ["benevolent", "candid", "diligent", "elated"]

    if not recent_words:
        st.info("No recent words to quiz. Learn some words first!")
        return

    # Pick a random word
    word = random.choice(recent_words)

    # Example fake choices (replace with real definitions)
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


# -------------------------
# MAIN APP
# -------------------------
def main():
    if "mode" not in st.session_state:
        st.session_state.mode = "welcome"
        st.session_state.name = ""

    if st.session_state.mode == "welcome":
        page_welcome()
    else:
        # Sidebar navigation
        dest = st.sidebar.radio("Go to", ["Home", "Words", "Quiz"])

        if dest == "Home":
            st.session_state.mode = "home"
            page_home()
        elif dest == "Words":
            st.session_state.mode = "words"
            page_words()
        elif dest == "Quiz":
            st.session_state.mode = "quiz"
            page_quiz()


if __name__ == "__main__":
    main()
