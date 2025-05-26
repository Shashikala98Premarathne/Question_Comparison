{
 "cells": [
  {
   "cell_type": "code",
   "execution_count": 1,
   "id": "1a0de756",
   "metadata": {},
   "outputs": [
    {
     "name": "stderr",
     "output_type": "stream",
     "text": [
      "2025-05-26 19:52:38.236 \n",
      "  \u001b[33m\u001b[1mWarning:\u001b[0m to view this Streamlit app on a browser, run it with the following\n",
      "  command:\n",
      "\n",
      "    streamlit run /Users/shashinimashi/Library/Python/3.11/lib/python/site-packages/ipykernel_launcher.py [ARGUMENTS]\n"
     ]
    }
   ],
   "source": [
    "import streamlit as st\n",
    "import pandas as pd\n",
    "\n",
    "# --- Streamlit App Title ---\n",
    "st.set_page_config(page_title=\"Consistency Checker\", layout=\"wide\")\n",
    "st.title(\"📊 Questionnaire Consistency Checker\")\n",
    "st.markdown(\"\"\"\n",
    "Upload a questionnaire response file (CSV), set a tolerance margin, and this tool will validate the consistency between related questions.\n",
    "\"\"\")\n",
    "\n",
    "# --- File Upload ---\n",
    "uploaded_file = st.file_uploader(\"📁 Upload your CSV file\", type=[\"csv\"])\n",
    "\n",
    "# --- Margin Input ---\n",
    "margin = st.slider(\"⚙️ Select tolerance margin (±)\", 0, 2, 1)\n",
    "\n",
    "# --- Define Consistency Rules ---\n",
    "rules = {\n",
    "    (\"Q1_Satisfaction\", \"Q2_Preference\"): {\n",
    "        5: [4, 5], 4: [3, 4, 5], 3: [2, 3, 4], 2: [1, 2, 3], 1: [1, 2]\n",
    "    },\n",
    "    (\"Q1_Satisfaction\", \"Q3_Recommend\"): {\n",
    "        5: [4, 5], 4: [3, 4, 5], 3: [2, 3, 4], 2: [1, 2, 3], 1: [1, 2]\n",
    "    },\n",
    "    (\"Q2_Preference\", \"Q4_Repurchase\"): {\n",
    "        5: [4, 5], 4: [3, 4, 5], 3: [2, 3, 4], 2: [1, 2, 3], 1: [1, 2]\n",
    "    },\n",
    "}\n",
    "\n",
    "# --- Consistency Checker Function ---\n",
    "def check_consistency_with_margin(row, rules, margin):\n",
    "    inconsistencies = []\n",
    "    recommendations = []\n",
    "\n",
    "    for (q1, q2), mapping in rules.items():\n",
    "        if q1 not in row or q2 not in row:\n",
    "            continue\n",
    "\n",
    "        q1_val = row[q1]\n",
    "        q2_val = row[q2]\n",
    "\n",
    "        valid = mapping.get(q1_val, [])\n",
    "        margin_range = list(range(max(1, min(valid) - margin), min(5, max(valid) + margin) + 1))\n",
    "\n",
    "        if q2_val not in margin_range:\n",
    "            inconsistencies.append(f\"{q1}={q1_val} vs {q2}={q2_val}\")\n",
    "            closest = min(valid, key=lambda x: abs(x - q2_val)) if valid else q2_val\n",
    "            recommendations.append(f\"Adjust {q2} to {closest}\")\n",
    "        else:\n",
    "            recommendations.append(f\"{q2} OK for {q1}={q1_val}\")\n",
    "\n",
    "    return pd.Series({\n",
    "        \"Consistency_Check\": \" | \".join(inconsistencies) if inconsistencies else \"Consistent\",\n",
    "        \"Recommendations\": \" | \".join(recommendations)\n",
    "    })\n",
    "\n",
    "# --- Processing ---\n",
    "if uploaded_file:\n",
    "    df = pd.read_csv(uploaded_file)\n",
    "\n",
    "    with st.spinner(\"🔍 Checking consistency...\"):\n",
    "        results = df.apply(check_consistency_with_margin, axis=1, args=(rules, margin))\n",
    "        df_result = pd.concat([df, results], axis=1)\n",
    "\n",
    "    st.success(\"✅ Consistency check completed!\")\n",
    "    st.subheader(\"📋 Results Preview\")\n",
    "    st.dataframe(df_result, use_container_width=True)\n",
    "\n",
    "    # --- Download Button ---\n",
    "    csv = df_result.to_csv(index=False).encode('utf-8')\n",
    "    st.download_button(\"💾 Download Checked CSV\", csv, \"checked_responses.csv\", \"text/csv\")\n",
    "else:\n",
    "    st.info(\"Please upload a CSV file to begin.\")\n"
   ]
  }
 ],
 "metadata": {
  "kernelspec": {
   "display_name": "Python 3",
   "language": "python",
   "name": "python3"
  },
  "language_info": {
   "codemirror_mode": {
    "name": "ipython",
    "version": 3
   },
   "file_extension": ".py",
   "mimetype": "text/x-python",
   "name": "python",
   "nbconvert_exporter": "python",
   "pygments_lexer": "ipython3",
   "version": "3.11.6"
  }
 },
 "nbformat": 4,
 "nbformat_minor": 5
}
