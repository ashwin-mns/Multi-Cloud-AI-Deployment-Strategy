import streamlit as st
import pandas as pd
import plotly.express as px
import time
import os
import json

st.set_page_config(page_title="Multi-Cloud AI Monitor", layout="wide")

st.title("🌐 Multi-Cloud AI Deployment Monitoring Dashboard")
st.markdown("""
This dashboard compares the performance and estimated costs of the same AI model deployed across 
**AWS SageMaker**, **GCP Vertex AI**, and **Azure AI Studio**.
""")

# Load Org Config
config_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'config', 'org_config.json')
try:
    with open(config_path, 'r') as f:
        config = json.load(f)
    orgs = list(config['organizations'].keys())
except FileNotFoundError:
    orgs = ["default"]

# Sidebar settings
st.sidebar.header("Navigation")
selected_org = st.sidebar.selectbox("Select Organization", orgs)
page = st.sidebar.radio("Go to", ["Dashboard", "Raw Data", "About"])

# Load Data
@st.cache_data(ttl=1)
def load_data():
    if os.path.exists("benchmark_results.csv"):
        df = pd.read_csv("benchmark_results.csv")
        # Ensure numeric columns are correct
        df["Total Latency (ms)"] = pd.to_numeric(df["Total Latency (ms)"], errors='coerce')
        df["Processing Time (ms)"] = pd.to_numeric(df["Processing Time (ms)"], errors='coerce')
        return df
    return pd.DataFrame()

df = load_data()

if page == "Dashboard":
    if not df.empty:
        # Aggregate metrics
        metrics_df = df.groupby("Provider").agg({
            "Total Latency (ms)": "mean",
            "Processing Time (ms)": "mean"
        }).reset_index()
        
        # Add mock cost data for comparison
        cost_mapping = {"AWS SageMaker": 0.15, "GCP Vertex AI": 0.12, "Azure AI Studio": 0.18}
        metrics_df["Cost per 1k Req ($)"] = metrics_df["Provider"].map(cost_mapping)

        # Top Metrics Row
        best_latency = metrics_df.loc[metrics_df["Total Latency (ms)"].idxmin()]
        best_cost = metrics_df.loc[metrics_df["Cost per 1k Req ($)"].idxmin()]

        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Fastest Provider", best_latency["Provider"], f"{best_latency['Total Latency (ms)']:.1f}ms")
        with col2:
            st.metric("Cheapest Provider", best_cost["Provider"], f"${best_cost['Cost per 1k Req ($)']:.2f}")
        with col3:
            st.metric("Average Latency", f"{metrics_df['Total Latency (ms)'].mean():.1f}ms")

        st.divider()

        # Visualization Row
        col_left, col_right = st.columns(2)

        with col_left:
            st.subheader("Latency Comparison (ms)")
            fig_latency = px.bar(metrics_df, x="Provider", y="Total Latency (ms)", 
                                 color="Provider", title="Mean Inference Latency",
                                 color_discrete_sequence=px.colors.qualitative.Prism)
            st.plotly_chart(fig_latency, use_container_width=True)

        with col_right:
            st.subheader("Cost-Performance Efficiency")
            # Lower is better for both, so we use 1/Latency * 1/Cost for a "Value" metric
            metrics_df["Value Score"] = 1 / (metrics_df["Total Latency (ms)"] * metrics_df["Cost per 1k Req ($)"])
            fig_value = px.scatter(metrics_df, x="Total Latency (ms)", y="Cost per 1k Req ($)",
                                  size="Value Score", color="Provider", text="Provider",
                                  title="Cost vs Latency Trade-off")
            st.plotly_chart(fig_value, use_container_width=True)

        st.divider()

        # Detailed Table
        st.subheader("Comparative Metrics Summary")
        st.dataframe(metrics_df.style.highlight_min(subset=["Total Latency (ms)", "Cost per 1k Req ($)"], color='#d4edda'), use_container_width=True)
    else:
        st.warning("No benchmark data found. Please run `monitor/benchmark.py` first.")

elif page == "Raw Data":
    st.subheader("Raw Benchmark Results")
    if not df.empty:
        st.dataframe(df, use_container_width=True)
    else:
        st.warning("No data available.")

st.info("💡 Tip: Use the Multi-Cloud AI Deployment pipelines to update your models and then re-run benchmarks to see updated stats.")
