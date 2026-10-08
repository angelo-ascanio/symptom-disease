import pandas as pd
import streamlit as st

st.set_page_config(page_title="Symptom Checker", layout="centered")
st.title("🩺 Symptom to Disease Lookup")

# Load dataset
@st.cache_data
def load_data():
    return pd.read_csv("main.csv")

df = load_data()
symptoms = [col for col in df.columns if col != "prognosis"]

# Format symptom names for better UI readability (e.g., "chest_pain" -> "Chest Pain")
symptom_display_mapping = {sym: sym.replace("_", " ").title() for sym in symptoms}
display_to_symptom = {v: k for k, v in symptom_display_mapping.items()}

# Symptom selector
selected_display_symptoms = st.multiselect(
    "Select symptoms:",
    options=sorted(symptom_display_mapping.values()),
    placeholder="Search or pick symptoms...",
)

if selected_display_symptoms:
    # Map back the pretty display names to the actual dataset column names
    selected_symptoms = [display_to_symptom[sym] for sym in selected_display_symptoms]
    
    # Calculate match scores for each row
    df["match_count"] = df[selected_symptoms].sum(axis=1)
    results = df[df["match_count"] > 0][["prognosis", "match_count"]].copy()
    
    if not results.empty:
        # FIX: Deduplicate by grouping by prognosis and keeping the highest match count
        results = results.groupby("prognosis", as_index=False)["match_count"].max()
        
        # Calculate percentage match based on selected symptoms
        results["Match %"] = ((results["match_count"] / len(selected_symptoms)) * 100).round(1)
        
        # Sort results by highest match count, then alphabetically by disease name
        results = results.sort_values(by=["match_count", "prognosis"], ascending=[False, True]).reset_index(drop=True)

        st.subheader(f"Matching Results ({len(results)} distinct diseases found)")
        
        # IMPROVEMENT: Use Streamlit's Column Configuration for a much better UI
        st.dataframe(
            results,
            column_config={
                "prognosis": st.column_config.TextColumn("Disease / Prognosis"),
                "match_count": st.column_config.NumberColumn("Matched Symptoms"),
                "Match %": st.column_config.ProgressColumn(
                    "Match Percentage",
                    format="%.1f%%",
                    min_value=0,
                    max_value=100,
                ),
            },
            hide_index=True,
            use_container_width=True,
        )
    else:
        st.warning("No diseases found matching those specific symptoms. Try adding different ones.")
else:
    st.info("Select one or more symptoms above to see possible matches.")
