import streamlit as st
import pandas as pd

# --- Streamlit App Title ---
st.set_page_config(page_title="Consistency Checker", layout="wide")
st.title("📊 Questionnaire Consistency & Benchmark Checker")

# --- File Uploads ---
st.markdown("Upload your questionnaire responses and optionally a benchmark dataset from last year.")
uploaded_file = st.file_uploader("📁 Upload response CSV", type=["csv"], key="responses")
benchmark_file = st.file_uploader("📁 Upload benchmark CSV (optional)", type=["csv"], key="benchmark")

# --- Settings ---
margin = st.slider("⚙️ Select tolerance margin (±)", 0, 2, 1)
benchmark_tol = st.slider("📏 Benchmark tolerance (±)", 0.0, 1.0, 0.5, step=0.1)
debug = st.checkbox("🔍 Show logic check details", value=False)

# --- Define Logical Pair Rules ---
logical_rules = {
    "B1": ["E4c", "F1"],
    "B2": ["F1", "E1", "E4", "E4c", "F2"],
    "B3a": ["E4c", "E4"],
    "B3b": ["E4c", "E4"],
    "E1": ["E4", "E4c", "F1", "F2", "F3", "F4"],
    "E4": ["F2", "F3", "F4", "F1"],
    "E4b": ["F5", "F6"],
    "E4c": ["F1"]
}

# --- Benchmark Setup ---
benchmarks = {}
if benchmark_file:
    benchmark_df = pd.read_csv(benchmark_file)
    for brand in benchmark_df["Brand"].unique():
        brand_data = benchmark_df[benchmark_df["Brand"] == brand].iloc[0]
        benchmarks[brand] = brand_data.drop("Brand").to_dict()

# --- Main Validation Function ---
def validate_row(row, logic_rules, margin, benchmarks, benchmark_tol, debug=False):
    inconsistencies = []
    recommendations = []
    benchmark_flags = []
    risk_score = 0

    brand = row["Brand"]
    row_benchmarks = benchmarks.get(brand, {})

    # Logic checks
    for source, targets in logic_rules.items():
        if source in row:
            source_val = row[source]
            for target in targets:
                if target in row:
                    target_val = row[target]
                    min_val = max(1, source_val - margin)
                    max_val = min(5, source_val + margin)
                    valid_range = list(range(min_val, max_val + 1))

                    if debug:
                        st.write(f"{source}={source_val} → checking {target}={target_val} in range {valid_range}")

                    if target_val not in valid_range:
                        inconsistencies.append(f"{source}={source_val} vs {target}={target_val}")
                        closest = max(min(source_val, 5), 1)
                        recommendations.append(f"Adjust {target} to approx {closest}")
                        risk_score += 1

    # Benchmark check
    for col, benchmark_val in row_benchmarks.items():
        if col in row:
            actual = row[col]
            if abs(actual - benchmark_val) > benchmark_tol:
                benchmark_flags.append(f"{col}: {actual} vs {benchmark_val:.2f}")
                risk_score += 1

    return pd.Series({
        "Consistency_Check": " | ".join(inconsistencies) if inconsistencies else "Consistent",
        "Recommendations": " | ".join(recommendations),
        "Benchmark_Flags": " | ".join(benchmark_flags) if benchmark_flags else "OK",
        "Risk_Score": risk_score
    })

# --- Run the Analysis ---
if uploaded_file:
    df = pd.read_csv(uploaded_file)

    with st.spinner("🔍 Checking logic and benchmarks across brands..."):
        results = df.apply(validate_row, axis=1, args=(logical_rules, margin, benchmarks, benchmark_tol, debug))
        df_result = pd.concat([df, results], axis=1)

    st.success("✅ Check completed!")
    st.subheader("📋 Results Preview")
    st.dataframe(df_result, use_container_width=True)

    # --- Download Button ---
    csv = df_result.to_csv(index=False).encode('utf-8')
    st.download_button("💾 Download Checked CSV", csv, "checked_responses.csv", "text/csv")
else:
    st.info("Please upload a response CSV to begin.")
