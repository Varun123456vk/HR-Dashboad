import streamlit as st
import pandas as pd
import plotly.express as px

# -------------------------
# PAGE CONFIG
# -------------------------
st.set_page_config(page_title="HR Attrition Dashboard", layout="wide")
st.title("📊 HR Attrition Dashboard")

# -------------------------
# LOAD DATA
# -------------------------
@st.cache_data
def load_data():
    df = pd.read_excel("HR Attrition.xlsx", sheet_name="Cleaned Data")
    # normalize column names: strip spaces + lowercase
    df.columns = df.columns.str.strip().str.lower()
    return df

df = load_data()

# Show columns once for debugging (uncomment to inspect)
# st.write("Columns:", df.columns.tolist())

# -------------------------
# FIND ATTRITION COLUMN (ROBUST)
# -------------------------
# Try to find any column that contains the word "attrition"
attrition_candidates = [c for c in df.columns if "attrition" in c]

if len(attrition_candidates) == 0:
    st.error("❌ No column related to 'attrition' found. Check the column list above.")
    st.stop()

# Pick the best match (first one)
attrition_col = attrition_candidates[0]

st.write(f"✅ Using column: {attrition_col}")

# Create flag safely
df["attrition_flag"] = df[attrition_col].astype(str).str.lower().apply(
    lambda x: 1 if "yes" in x else 0
)

# -------------------------
# SAFE COLUMN FINDER
# -------------------------
def find_col(keyword):
    # Prefer exact match first, then partial match
    exact = [c for c in df.columns if c == keyword]
    if exact:
        return exact[0]
    matches = [c for c in df.columns if keyword in c]
    return matches[0] if matches else None

dept_col = find_col("department")
gender_col = find_col("gender")
role_col = find_col("job role")
salary_col = find_col("monthly income")
age_col = find_col("age")

# Validate critical columns
for name, col in {
    "Department": dept_col,
    "Gender": gender_col,
    "JobRole": role_col
}.items():
    if col is None:
        st.error(f"❌ Column related to '{name}' not found")
        st.stop()

# -------------------------
# SIDEBAR FILTERS
# -------------------------
st.sidebar.header("Filters")

dept = st.sidebar.multiselect("Department", df[dept_col].unique(), default=df[dept_col].unique())
gender = st.sidebar.multiselect("Gender", df[gender_col].unique(), default=df[gender_col].unique())
role = st.sidebar.multiselect("Job Role", df[role_col].unique(), default=df[role_col].unique())

filtered_df = df[
    (df[dept_col].isin(dept)) &
    (df[gender_col].isin(gender)) &
    (df[role_col].isin(role))
]

# -------------------------
# KPIs
# -------------------------
total_emp = len(filtered_df)
attrition_count = filtered_df["attrition_flag"].sum()
attrition_rate = (attrition_count / total_emp) * 100 if total_emp else 0

avg_salary = filtered_df[salary_col].mean() if salary_col else 0

c1, c2, c3, c4 = st.columns(4)
c1.metric("Total Employees", total_emp)
c2.metric("Attrition Count", int(attrition_count))
c3.metric("Attrition Rate", f"{attrition_rate:.2f}%")
c4.metric("Avg Salary", f"₹{avg_salary:,.0f}" if salary_col else "N/A")

# -------------------------
# CHARTS
# -------------------------
fig1 = px.bar(filtered_df, x=dept_col, y="attrition_flag", color=dept_col, title="Attrition by Department")
fig2 = px.pie(filtered_df, names=gender_col, values="attrition_flag", title="Attrition by Gender")

col1, col2 = st.columns(2)
col1.plotly_chart(fig1, width="stretch")
col2.plotly_chart(fig2, width="stretch")

if salary_col:
    fig3 = px.box(filtered_df, x=attrition_col, y=salary_col, title="Salary vs Attrition")
    st.plotly_chart(fig3, width="stretch")

if age_col:
    fig4 = px.histogram(filtered_df, x=age_col, color=attrition_col, title="Age Distribution")
    st.plotly_chart(fig4, width="stretch")

fig5 = px.bar(filtered_df, x=role_col, y="attrition_flag", color=role_col, title="Attrition by Job Role")
st.plotly_chart(fig5, width="stretch")

# -------------------------
# DATA TABLE
# -------------------------
st.subheader("Filtered Data")
st.dataframe(filtered_df)