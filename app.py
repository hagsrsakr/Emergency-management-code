from pathlib import Path
import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(page_title="Real CAD + AI + SHAP + MILP", layout="wide")
st.title("Real CAD + AI + SHAP + MILP — Stage 2")
st.caption("Real public operational data; AI prediction; SHAP explanation; constraint-aware assignment")

tabs=st.tabs(["Data","AI","SHAP","Decision","Statistics","Scalability","Research Notes"])

with tabs[0]:
    st.header("Real CAD provenance")
    p=Path("data/sf_cad_prepared.csv")
    if p.exists():
        d=pd.read_csv(p)
        st.metric("Prepared CAD rows",f"{len(d):,}")
        if "final_priority" in d:
            st.bar_chart(d.final_priority.astype(str).value_counts())
        st.dataframe(d.head(50),use_container_width=True)
    else: st.warning("Run scripts/01_download_sf_cad.py and scripts/02_prepare_real_data.py")

with tabs[1]:
    st.header("AI situation understanding")
    p=Path("outputs/model_validation.csv")
    if p.exists(): st.dataframe(pd.read_csv(p),use_container_width=True)
    else: st.info("Run scripts/03_validate_and_select_models.py")

with tabs[2]:
    st.header("SHAP — Why did the AI predict this?")
    for prefix,title in [("priority","Operational Priority"),("response","Response Time")]:
        p=Path(f"outputs/shap/{prefix}_global_importance.csv")
        if p.exists():
            g=pd.read_csv(p).head(20).sort_values("mean_abs_shap")
            st.subheader(title)
            fig=px.bar(g,x="mean_abs_shap",y="feature",orientation="h")
            st.plotly_chart(fig,use_container_width=True)
            loc=Path(f"outputs/shap/{prefix}_local_first_case.csv")
            if loc.exists(): st.dataframe(pd.read_csv(loc).head(20),use_container_width=True)
        else: st.info(f"Run scripts/06_run_shap.py for {title}")

with tabs[3]:
    st.header("AI + MILP final decision")
    p=Path("data/incident_resource_scored.csv")
    if p.exists():
        pairs=pd.read_csv(p)
        incidents=sorted(pairs.incident_id.astype(str).unique())
        choice=st.selectbox("Incident",incidents)
        g=pairs[pairs.incident_id.astype(str)==choice].copy().sort_values("predicted_response_min")
        st.write("Predicted priority:",g.predicted_priority.iloc[0])
        st.dataframe(g[["resource_id","unit_type","station_area","empirical_response_min","predicted_response_min","predicted_priority","priority_penalty"]],use_container_width=True)
    else: st.info("Run scripts/04_build_incident_resource_matrix.py and 05_score_pairs_with_ai.py")

with tabs[4]:
    p=Path("outputs/strategy_statistical_tests.csv")
    if p.exists(): st.dataframe(pd.read_csv(p),use_container_width=True)
    else: st.info("Run scripts/08_statistical_tests.py")

with tabs[5]:
    p=Path("outputs/scalability_results.csv")
    if p.exists():
        d=pd.read_csv(p); st.dataframe(d,use_container_width=True)
        st.plotly_chart(px.line(d,x="incidents",y="runtime_sec",markers=True),use_container_width=True)
    else: st.info("Run scripts/09_scalability.py")

with tabs[6]:
    st.markdown("""
### Research interpretation
AI = situation understanding and prediction.

SHAP = feature-level explanation of the AI prediction.

MILP = constraint-aware allocation using the empirically reconstructed Incident × Resource matrix.

The public CAD dataset contains operational priority rather than a clinical diagnosis. Any Egyptian manuscript version should call this **operational priority** unless a validated medical/triage label is available.

Traffic is not fabricated: the AI+Traffic strategy runs only when a real traffic layer is supplied.
""")
