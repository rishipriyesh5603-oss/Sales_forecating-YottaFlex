from pathlib import Path
import sys
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
import streamlit as st
import pandas as pd
import plotly.express as px
from src.config import DATA_DIR
from src.generator import generate_dataset
from src.validation import validate_dataset
from src.forecasting import forecast, scenario_comparison

st.set_page_config(page_title="YottaFlex | Sales Forecast",page_icon="📈",layout="wide")
st.title("📈 YottaFlex AI — Sales Booking Forecast")
st.caption("Synthetic CRM data • Snapshot-safe forecasts • Scenario uncertainty")
if not (DATA_DIR/"opportunities.csv").exists():
    with st.spinner("Generating baseline dataset..."): generate_dataset(DATA_DIR)
with st.sidebar:
    st.header("Forecast controls")
    scenario=st.selectbox("Scenario",["base","downside","upside"],index=0)
    slippage=st.slider("Slippage rate",0.0,0.6,0.15,0.05)
    st.caption("Scenario multipliers: downside 0.80×, base 1.00×, upside 1.15×.")
    if st.button("Run data validation"):
        try:
            v=validate_dataset(DATA_DIR)
            st.success(f"Validation passed. {len(v['metrics'])} tables checked.")
        except Exception as e: st.error(str(e))
snap=pd.read_csv(DATA_DIR/"forecast_snapshots.csv")
latest=snap[snap.snapshot_date==snap.snapshot_date.max()]
r=forecast(latest,scenario,slippage_rate=slippage)
c1,c2,c3,c4=st.columns(4)
c1.metric("Opportunities",f"{r['opportunity_count']:,}")
c2.metric("Gross pipeline",f"${r['gross_pipeline_usd']:,.0f}")
c3.metric("Weighted forecast",f"${r['weighted_bookings_usd']:,.0f}")
c4.metric("Expected wins",f"{r['expected_wins']:,.1f}")
st.subheader("Scenario comparison")
comp=scenario_comparison(latest,slippage)
st.plotly_chart(px.bar(comp,x="scenario",y="weighted_bookings_usd",color="scenario",
    title="Expected bookings by scenario",labels={"weighted_bookings_usd":"USD"}),use_container_width=True)
left,right=st.columns(2)
with left:
    st.subheader("Forecast by stage")
    stage_df=pd.DataFrame(list(r["by_stage"].items()),columns=["stage","forecast_usd"])
    st.plotly_chart(px.bar(stage_df,x="stage",y="forecast_usd"),use_container_width=True)
with right:
    st.subheader("Forecast by territory")
    terr_df=pd.DataFrame(list(r["by_territory"].items()),columns=["territory","forecast_usd"])
    st.plotly_chart(px.pie(terr_df,names="territory",values="forecast_usd"),use_container_width=True)
st.subheader("Opportunity-level forecast sample")
detail=r["detail"][["opportunity_id","stage","amount_usd","opportunity_age_days",
                    "activity_count_to_date","forecast_probability","scenario_weighted_usd"]]
st.dataframe(detail.head(100),use_container_width=True)
st.download_button("Download forecast CSV",detail.to_csv(index=False).encode(),
                   "forecast_detail.csv","text/csv")
with st.expander("Methodology and limitations"):
    st.markdown("""
    - Forecast uses only fields available at each snapshot date; final outcomes and ground-truth labels are excluded.
    - Stage probability is adjusted for opportunity age, recent activity, close-date timing and scenario assumptions.
    - USD conversion assumptions: USD=1.00, EUR=1.08, INR=0.012.
    - Scenario multipliers: downside=0.80, base=1.00, upside=1.15.
    - This is a transparent rule-based baseline, not a trained production model. Replace assumptions with calibrated historical conversion rates when real CRM outcomes are available.
    """)
