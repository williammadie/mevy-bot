import os

import streamlit as st
import pandas as pd

from mevy_bot.path_finder import PathFinder

st.title("📂 Sources connues")

# Load the CSV (you could load JSON if needed)
data_definition = PathFinder.data_definition()
manual_sources_path = os.path.join(data_definition, "manual_sources.csv")
df = pd.read_csv(manual_sources_path)

# Show table
st.write("### Liste des sources")
st.dataframe(df)

# Optional: Add a filter
filter_text = st.text_input("Chercher par nom de fichier")
if filter_text:
    df = df[df['name'].str.contains(filter_text, case=False, na=False)]
    st.write("### Filtered Files")
    st.dataframe(df)
