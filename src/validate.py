"""Validation checks for generated workforce data."""
from pathlib import Path
import json, sqlite3
import pandas as pd
from .generator import ROOT, TABLES, load_config

def validate(data_dir=None, db_path=None):
    data_dir=Path(data_dir or ROOT/"data"/"generated")
    db_path=Path(db_path or ROOT/"database"/"workforce.db")
    results=[]
    def add(check, passed, details): results.append({"check":check,"status":"PASS" if passed else "FAIL","details":str(details)})
    dfs={name:pd.read_csv(data_dir/f"{name}.csv") for name in TABLES}
    cfg=load_config()
    add("employee_count",len(dfs["Employee"])==int(cfg["employee_count"]),len(dfs["Employee"]))
    for name,df in dfs.items():
        pk={"Employee":"employee_id","Role":"role_id","Team":"team_id","TenureSnapshot":"snapshot_id",
            "EngagementSurvey":"survey_id","WorkloadSnapshot":"workload_snapshot_id",
            "CompensationBand":"compensation_band_id","PromotionHistory":"promotion_id",
            "AttritionOutcome":"outcome_id","Intervention":"intervention_id","TransferHistory":"transfer_id"}[name]
        add(f"{name}_primary_key_unique",df[pk].notna().all() and df[pk].is_unique, f"rows={len(df)}")
    employee_ids=set(dfs["Employee"].employee_id)
    for name in ["TenureSnapshot","EngagementSurvey","WorkloadSnapshot","PromotionHistory","AttritionOutcome","Intervention","TransferHistory"]:
        missing=set(dfs[name].employee_id.dropna())-employee_ids
        add(f"{name}_employee_fk",len(missing)==0,f"invalid={len(missing)}")
    role_ids=set(dfs["Role"].role_id); team_ids=set(dfs["Team"].team_id); band_ids=set(dfs["CompensationBand"].compensation_band_id)
    add("Employee_role_fk",set(dfs["Employee"].role_id)<=role_ids,"role references")
    add("Employee_team_fk",set(dfs["Employee"].team_id)<=team_ids,"team references")
    add("Employee_compensation_fk",set(dfs["Employee"].compensation_band_id)<=band_ids,"band references")
    add("Transfer_from_team_fk",set(dfs["TransferHistory"].from_team_id)<=team_ids,"from-team references")
    add("Transfer_to_team_fk",set(dfs["TransferHistory"].to_team_id)<=team_ids,"to-team references")
    surveys=dfs["EngagementSurvey"]
    missing_ok=surveys.loc[surveys.survey_status=="MISSING","engagement_score"].isna().all()
    add("missing_survey_not_negative",missing_ok,"missing surveys remain null")
    add("engagement_score_range",surveys.engagement_score.dropna().between(0,100).all(),"0..100")
    wl=dfs["WorkloadSnapshot"]
    add("workload_nonnegative",(wl.weekly_hours>=0).all() and (wl.overtime_hours>=0).all(),"hours >= 0")
    ten=dfs["TenureSnapshot"]
    add("tenure_nonnegative",(ten.tenure_months>=0).all(),"months >= 0")
    attrition_rate=len(dfs["AttritionOutcome"])/max(1,len(dfs["Employee"]))
    add("attrition_rate_5_to_15_pct",0.05<=attrition_rate<=0.15,f"rate={attrition_rate:.4f}")
    outcome_dates=pd.to_datetime(dfs["AttritionOutcome"]["outcome_date"])
    add("outcomes_after_as_of_date",(outcome_dates>pd.Timestamp(cfg["as_of_date"])).all(),"future-horizon labels")
    add("outcomes_within_future_horizon",(outcome_dates<=pd.Timestamp(cfg["as_of_date"])+pd.Timedelta(days=int(cfg["future_horizon_days"]))).all(),"within configured horizon")
    # Temporal leakage: features must be dated on/before cutoff. Outcomes are stored separately.
    cutoff=pd.Timestamp(cfg["as_of_date"])
    for name in ["TenureSnapshot","EngagementSurvey","WorkloadSnapshot"]:
        dates=pd.to_datetime(dfs[name]["snapshot_date"] if "snapshot_date" in dfs[name] else dfs[name]["survey_date"])
        add(f"{name}_no_future_features",(dates<=cutoff).all(),f"cutoff={cutoff.date()}")
    # SQL table presence and row counts
    with sqlite3.connect(db_path) as conn:
        db_tables={r[0] for r in conn.execute("SELECT name FROM sqlite_master WHERE type='table'")}
        add("sqlite_all_tables",set(TABLES)<=db_tables,sorted(db_tables))
        fk_violations=conn.execute("PRAGMA foreign_key_check").fetchall()
        add("sqlite_foreign_key_check",len(fk_violations)==0,f"violations={len(fk_violations)}")
        for name,df in dfs.items():
            count=conn.execute(f'SELECT COUNT(*) FROM "{name}"').fetchone()[0]
            add(f"sqlite_{name}_row_count",count==len(df),f"csv={len(df)}, db={count}")
    report=pd.DataFrame(results)
    out=ROOT/"reports"/"validation_summary.csv"; out.parent.mkdir(exist_ok=True)
    report.to_csv(out,index=False)
    (ROOT/"reports"/"validation_summary.json").write_text(report.to_json(orient="records",indent=2),encoding="utf-8")
    return report
