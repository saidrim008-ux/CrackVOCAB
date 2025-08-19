import streamlit as st
import pandas as pd

# Load vocab data
data = pd.read_csv("words.csv")

st.title("📘 crackVOCAB")
st.write("Master advanced vocabulary with English–French–Arabic flashcards!")

# Initialize session state
if "index" not in st.session_state:
    st.session_state.index = 0

# Get current word
word = data.iloc[st.session_state.index]

# Show the word
st.subheader(f"Word: {word['word']} ({word['part_of_speech']})")

# Button to show definition
if st.button("Show Definition"):
    st.write(f"**Definition:** {word['definition']}")
    st.write(f"**French:** {word['french']}")
    st.write(f"**Arabic:** {word['arabic']}")
    st.write(f"**Example:** {word['example']}")

# Button to go to next word
if st.button("Next Word ➡️"):
    st.session_state.index = (st.session_state.index + 1) % len(data)
    st.experimental_rerun()
