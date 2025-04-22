import streamlit as st
import pandas as pd
import ast

# Load the association rules CSV file
@st.cache_data
def load_rules():
    rules = pd.read_csv("../data/processed_data/association_rules.csv")

    # Convert strings to lists
    rules['antecedents'] = rules['antecedents'].apply(ast.literal_eval)
    rules['consequents'] = rules['consequents'].apply(ast.literal_eval)

    return rules

rules = load_rules()

# Streamlit app layout
st.title("Market Basket Recommendation System")
st.write("Select a product to see what other items customers often buy with it.")

# Collect all unique items from antecedents
unique_items = sorted(set(item for ant in rules['antecedents'] for item in ant))
selected_item = st.selectbox("Select a product", unique_items)

# Optional filters
min_conf = st.slider("Minimum Confidence", 0.0, 1.0, 0.5, 0.05)
min_lift = st.slider("Minimum Lift", 1.0, 20.0, 1.0, 0.5)

# Filter rules for selected item
filtered_rules = rules[
    rules['antecedents'].apply(lambda x: selected_item in x) &
    (rules['confidence'] >= min_conf) &
    (rules['lift'] >= min_lift)
]

# Remove duplicate recommendations (based on consequents)
filtered_rules = filtered_rules.sort_values(by='confidence', ascending=False)
filtered_rules['consequents_set'] = filtered_rules['consequents'].apply(lambda x: frozenset(x))
filtered_rules = filtered_rules.drop_duplicates(subset='consequents_set')

# Display recommendations
if not filtered_rules.empty:
    st.subheader(f"Recommendations for: {selected_item}")
    for _, row in filtered_rules.iterrows():
        recommended_items = ', '.join(row['consequents'])
        st.markdown(f"""
        - Buyers also bought: {recommended_items}
        - Confidence: `{row['confidence']:.2f}`
        - Lift: `{row['lift']:.2f}`
        """)
else:
    st.warning("No strong recommendations found for the selected item. Try lowering the confidence or lift thresholds.")
