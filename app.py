import streamlit as st
import pandas as pd

# Load vocab data
data = pd.read_csv("words.csv")

st.title("📘 crackVOCAB")
st.write("Master advanced vocabulary with English–French–Arabic flashcards!")

# Pick a random word
word = data.sample(1).iloc[0]

st.subheader(f"Word: {word['word']} ({word['part_of_speech']})")

if st.button("Show Definition"):
    st.write(f"**Definition:** {word['definition']}")
    st.write(f"**French:** {word['french']}")
    st.write(f"**Arabic:** {word['arabic']}")
    st.write(f"**Example:** {word['example']}")
