from pathlib import Path
import pandas as pd
import streamlit as st
import plotly.express as px

ROOT=Path(__file__).resolve().parents[1]
DATA=ROOT/"data"/"generated"
st.set_page_config(page_title="Workforce Retention Intelligence",layout="wide")
st.title("Employee Retention Intelligence")
st.caption("Synthetic data demonstration. Outputs are supportive signals, not employment decisions.")
required=["Employee","Role","Team","EngagementSurvey","WorkloadSnapshot","Intervention","AttritionOutcome"]
if not (DATA/"Employee.csv").exists():
    st.warning("Data not generated yet. Run: python -m src.main")
    st.stop()
dfs={n:pd.read_csv(DATA/f"{n}.csv") for n in required}
employees=dfs["Employee"]
surveys=dfs["EngagementSurvey"]
workloads=dfs["WorkloadSnapshot"]
interventions=dfs["Intervention"]
outcomes=dfs["AttritionOutcome"]
c1,c2,c3,c4=st.columns(4)
c1.metric("Synthetic employees",f"{len(employees):,}")
c2.metric("Voluntary outcomes",f"{len(outcomes):,}")
c3.metric("Interventions planned",f"{len(interventions):,}")
c4.metric("Survey completion",f"{(surveys.survey_status=='COMPLETED').mean()*100:.1f}%")
st.subheader("Engagement distribution")
completed=surveys[surveys.engagement_score.notna()]
if not completed.empty:
    st.plotly_chart(px.histogram(completed,x="engagement_score",nbins=20,title="Engagement scores (synthetic)"),use_container_width=True)
st.subheader("Workload by status")
st.plotly_chart(px.histogram(workloads,x="weekly_hours",color="workload_status",title="Weekly workload hours"),use_container_width=True)
st.subheader("Supportive interventions")
st.dataframe(interventions.head(100),use_container_width=True)
st.info("Do not use these synthetic scores to make employment decisions. Human review and context are required.")
