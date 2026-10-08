import pandas as pd
import streamlit as st

st.set_page_config(page_title="Symptom Checker", layout="centered")
st.title("🩺 Symptom to Disease Lookup")

# Load dataset
@st.cache_data
def load_data():
    return pd.read_csv("main_cleaned_fix.csv")

df = load_data()
symptoms = [col for col in df.columns if col != "prognosis"]

# Symptom selector
selected_symptoms = st.multiselect(
    "Select symptoms:",
    options=sorted(symptoms),
    placeholder="Search or pick symptoms...",
)

if selected_symptoms:
    # Calculate match scores for each disease
    df["match_count"] = df[selected_symptoms].sum(axis=1)
    results = df[df["match_count"] > 0][["prognosis", "match_count"]].copy()
    
    # Calculate percentage match based on selected symptoms
    results["Match %"] = ((results["match_count"] / len(selected_symptoms)) * 100).round(1)
    results = results.sort_values(by="match_count", ascending=False).reset_index(drop=True)
    results.columns = ["Disease / Prognosis", "Matched Symptoms", "Match Percentage"]

    st.subheader(f"Matching Results ({len(results)} found)")
    st.dataframe(results, use_container_width=True)
else:
    st.info("Select one or more symptoms above to see possible matches.")
