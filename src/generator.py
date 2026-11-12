"""Deterministic synthetic workforce data generator for the YottaFlex challenge."""
from __future__ import annotations
import json, sqlite3, hashlib
from pathlib import Path
from datetime import date, timedelta
import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
TABLES = [
    "Employee", "Role", "Team", "TenureSnapshot", "EngagementSurvey",
    "WorkloadSnapshot", "CompensationBand", "PromotionHistory",
    "AttritionOutcome", "Intervention", "TransferHistory"
]

def load_config(path=ROOT / "config.json"):
    return json.loads(Path(path).read_text(encoding="utf-8"))

def _id(prefix: str, n: int, width: int = 6) -> str:
    return f"{prefix}-{n:0{width}d}"

def generate(config=None, output_dir=None):
    cfg = config or load_config()
    out = Path(output_dir or ROOT / "data" / "generated")
    gt_dir = ROOT / "data" / "ground_truth"
    out.mkdir(parents=True, exist_ok=True); gt_dir.mkdir(parents=True, exist_ok=True)

    seed = int(cfg["seed"])
    rng = np.random.default_rng(seed)
    n = int(cfg["employee_count"])
    months = int(cfg["history_months"])
    end = pd.Timestamp(cfg["as_of_date"])
    start = (end - pd.DateOffset(months=months-1)).replace(day=1)
    month_starts = pd.date_range(start=start, end=end, freq="MS")
    # Ensure exactly the requested history length.
    if len(month_starts) > months:
        month_starts = month_starts[-months:]
    elif len(month_starts) < months:
        month_starts = pd.date_range(end=end.replace(day=1), periods=months, freq="MS")

    roles = [
        {"role_id":"ROLE-0001","role_name":"Software Engineer","job_family":"Engineering","level":"L2"},
        {"role_id":"ROLE-0002","role_name":"Senior Engineer","job_family":"Engineering","level":"L3"},
        {"role_id":"ROLE-0003","role_name":"Data Analyst","job_family":"Analytics","level":"L2"},
        {"role_id":"ROLE-0004","role_name":"Product Manager","job_family":"Product","level":"L3"},
        {"role_id":"ROLE-0005","role_name":"HR Specialist","job_family":"People","level":"L2"},
        {"role_id":"ROLE-0006","role_name":"Operations Associate","job_family":"Operations","level":"L1"},
        {"role_id":"ROLE-0007","role_name":"QA Engineer","job_family":"Engineering","level":"L2"},
        {"role_id":"ROLE-0008","role_name":"Engineering Manager","job_family":"Engineering","level":"L4"},
    ]
    teams = [
        {"team_id":"TEAM-0001","team_name":"Platform","department":"Engineering"},
        {"team_id":"TEAM-0002","team_name":"Data","department":"Analytics"},
        {"team_id":"TEAM-0003","team_name":"Product","department":"Product"},
        {"team_id":"TEAM-0004","team_name":"People Operations","department":"People"},
        {"team_id":"TEAM-0005","team_name":"Business Operations","department":"Operations"},
    ]
    bands = [
        {"compensation_band_id":"BAND-0001","band_name":"Band 1","min_salary":30000,"max_salary":49999,"currency":"USD"},
        {"compensation_band_id":"BAND-0002","band_name":"Band 2","min_salary":50000,"max_salary":74999,"currency":"USD"},
        {"compensation_band_id":"BAND-0003","band_name":"Band 3","min_salary":75000,"max_salary":99999,"currency":"USD"},
        {"compensation_band_id":"BAND-0004","band_name":"Band 4","min_salary":100000,"max_salary":139999,"currency":"USD"},
        {"compensation_band_id":"BAND-0005","band_name":"Band 5","min_salary":140000,"max_salary":200000,"currency":"USD"},
    ]
    pd.DataFrame(roles).to_csv(out/"Role.csv", index=False)
    pd.DataFrame(teams).to_csv(out/"Team.csv", index=False)
    pd.DataFrame(bands).to_csv(out/"CompensationBand.csv", index=False)

    employees=[]; tenure=[]; surveys=[]; workloads=[]; promotions=[]; outcomes=[]; interventions=[]; transfers=[]
    gt_anomalies=[]
    role_ids=[r["role_id"] for r in roles]
    team_ids=[t["team_id"] for t in teams]
    band_ids=[b["compensation_band_id"] for b in bands]
    # Generate baseline profile signals first; attrition labels are derived from a documented,
    # deterministic rule over pre-outcome signals rather than independent random labels.
    baseline_engagement=np.clip(rng.normal(72,13,size=n),20,98)
    baseline_workload=np.clip(rng.normal(40,7,size=n),20,65)
    attrition_rate=0.10  # within the required 5-15% range
    risk_scores=(0.60*((100-baseline_engagement)/100.0) +
                 0.40*(np.maximum(baseline_workload-40,0)/40.0))
    exit_count=max(1,int(round(n*attrition_rate)))
    ranked=np.argsort(-risk_scores,kind="stable")
    exit_indices=set(ranked[:exit_count].tolist())
    anomaly_indices=set(rng.choice(n, size=min(4,n), replace=False).tolist())

    for i in range(n):
        emp_id=_id("EMP",i+1)
        hire_date=(start - pd.Timedelta(days=int(rng.integers(30, 365*8)))).date()
        role_idx=int(rng.integers(0,len(roles)))
        team_idx=int(rng.integers(0,len(teams)))
        band_idx=int(rng.integers(0,len(bands)))
        base_eng=float(np.clip(rng.normal(72,13),20,98))
        base_load=float(np.clip(rng.normal(40,7),20,65))
        is_exit=i in exit_indices
        transfer_month=None
        original_team=team_ids[team_idx]
        destination_team=original_team
        if rng.random() < 0.12 and months > 8:
            transfer_month=int(rng.integers(6,months))
            choices=[t for t in team_ids if t != original_team]
            destination_team=str(rng.choice(choices))
            transfers.append({"transfer_id":_id("TRF",len(transfers)+1),
                "employee_id":emp_id,"from_team_id":original_team,"to_team_id":destination_team,
                "effective_date":str(month_starts[transfer_month].date()),
                "reason_code":"INTERNAL_MOBILITY"})
        employees.append({
            "employee_id":emp_id, "role_id":role_ids[role_idx], "team_id":destination_team,
            "compensation_band_id":band_ids[band_idx], "hire_date":str(hire_date),
            "employment_status":"ACTIVE",
            "location_code":f"LOC-{int(rng.integers(1,6)):02d}",
            "created_at":str(start.date()), "synthetic_record":True
        })
        promo_months=[]
        if rng.random()<0.22:
            promo_months=[int(rng.integers(6,max(7,months)))]
        for pm in promo_months:
            if pm < months:
                promotions.append({"promotion_id":_id("PROM",len(promotions)+1),"employee_id":emp_id,
                    "effective_date":str(month_starts[pm].date()),"from_level":roles[role_idx]["level"],
                    "to_level":roles[min(role_idx+1,len(roles)-1)]["level"],"reason_code":"CAREER_PROGRESSION"})
        exit_month=int(rng.integers(max(1,months-3),months)) if is_exit else None
        for m, dt in enumerate(month_starts):
            if dt > end: continue
            quarter=f"{dt.year}Q{((dt.month-1)//3)+1}"
            # Underlying engagement/workload trajectory; only pre-outcome values become features.
            load=float(np.clip(base_load + (8 if is_exit and exit_month is not None and m>=exit_month-3 else 0) + rng.normal(0,5),15,80))
            engagement=float(np.clip(base_eng - (12 if is_exit and exit_month is not None and m>=exit_month-3 else 0) + rng.normal(0,6),0,100))
            tenure_months=max(0,(dt.year-hire_date.year)*12+dt.month-hire_date.month)
            snap_id=f"SNAP-{emp_id}-{quarter}M{dt.month:02d}"
            snapshot_team=destination_team if transfer_month is not None and m>=transfer_month else original_team
            tenure.append({"snapshot_id":snap_id,"employee_id":emp_id,"snapshot_date":str(dt.date()),
                "period":quarter,"tenure_months":tenure_months,"tenure_years":round(tenure_months/12,2),
                "role_id":role_ids[role_idx],"team_id":snapshot_team})
            workloads.append({"workload_snapshot_id":f"WS-{emp_id}-{dt.strftime('%Y%m')}",
                "employee_id":emp_id,"snapshot_date":str(dt.date()),"weekly_hours":round(load,1),
                "overtime_hours":round(max(0,load-40),1),"capacity_utilization_pct":round(float(np.clip(load/45*100,20,160)),1),
                "workload_status":"HIGH" if load>=50 else "NORMAL"})
            if rng.random() >= float(cfg["survey_missing_rate"]):
                surveys.append({"survey_id":_id("SURV",len(surveys)+1),"employee_id":emp_id,
                    "survey_date":str(dt.date()),"period":quarter,"engagement_score":round(engagement,1),
                    "manager_support_score":round(float(np.clip(engagement+rng.normal(0,10),0,100)),1),
                    "survey_status":"COMPLETED","missing_reason":None})
            else:
                surveys.append({"survey_id":_id("SURV",len(surveys)+1),"employee_id":emp_id,
                    "survey_date":str(dt.date()),"period":quarter,"engagement_score":None,
                    "manager_support_score":None,"survey_status":"MISSING","missing_reason":"NOT_SUBMITTED"})
        if is_exit:
            event_date=(end + pd.Timedelta(days=int(rng.integers(1,int(cfg["future_horizon_days"])+1)))).date()
            outcomes.append({"outcome_id":f"OUT-{emp_id}-{end.year}","employee_id":emp_id,
                "outcome_date":str(event_date),"outcome_type":"VOLUNTARY_ATTRITION",
                "future_horizon_days":int(cfg["future_horizon_days"]),"rule_version":"retention-rules-v1"})
        # Intervention records are supportive and are not treated as employment decisions.
        if base_eng < 65 or base_load > 47:
            interventions.append({"intervention_id":_id("INT",len(interventions)+1),
                "employee_id":emp_id,"created_date":str(end.date()),
                "intervention_type":"SUPPORTIVE_CHECK_IN" if base_eng<65 else "WORKLOAD_REVIEW",
                "status":"PLANNED","reason":"LOW_ENGAGEMENT" if base_eng<65 else "HIGH_WORKLOAD",
                "human_review_required":True})

    frames={
        "Employee":pd.DataFrame(employees), "Role":pd.DataFrame(roles), "Team":pd.DataFrame(teams),
        "TenureSnapshot":pd.DataFrame(tenure), "EngagementSurvey":pd.DataFrame(surveys),
        "WorkloadSnapshot":pd.DataFrame(workloads), "CompensationBand":pd.DataFrame(bands),
        "PromotionHistory":pd.DataFrame(promotions, columns=["promotion_id","employee_id","effective_date","from_level","to_level","reason_code"]),
        "AttritionOutcome":pd.DataFrame(outcomes, columns=["outcome_id","employee_id","outcome_date","outcome_type","future_horizon_days","rule_version"]),
        "Intervention":pd.DataFrame(interventions, columns=["intervention_id","employee_id","created_date","intervention_type","status","reason","human_review_required"]),
        "TransferHistory":pd.DataFrame(transfers, columns=["transfer_id","employee_id","from_team_id","to_team_id","effective_date","reason_code"])
    }
    # Labelled anomalies are stored separately and never silently corrupt baseline tables.
    anomaly_specs=[
        ("FUTURE_INFORMATION_LEAKAGE","Feature timestamp occurs after prediction cutoff; must be excluded from model features."),
        ("MISSING_SURVEY_AS_NEGATIVE","Missing survey is represented as missing, not a zero/negative engagement score."),
        ("OUTCOME_DATE_INCONSISTENCY","Ground-truth case where outcome label conflicts with termination/event date."),
        ("UNEXPLAINED_INDIVIDUAL_SCORE","A score without explanation/human review must be flagged.")
    ]
    for idx,(issue,desc) in enumerate(anomaly_specs):
        emp_idx=sorted(anomaly_indices)[idx]
        gt_anomalies.append({"case_id":f"ANOM-{idx+1:03d}","employee_id":_id("EMP",emp_idx+1),
            "issue_type":issue,"ground_truth_label":"FLAG","expected_action":desc,
            "observed_condition":{
                "FUTURE_INFORMATION_LEAKAGE":"feature_event_date_after_prediction_cutoff",
                "MISSING_SURVEY_AS_NEGATIVE":"survey_status=MISSING and score=NULL",
                "OUTCOME_DATE_INCONSISTENCY":"label=VOLUNTARY_ATTRITION with contradictory event date",
                "UNEXPLAINED_INDIVIDUAL_SCORE":"score has no explanation and no human review"
            }[issue],
            "feature_cutoff_date":str(end.date()),
            "is_input_feature":False})
    for name,df in frames.items():
        df.to_csv(out/f"{name}.csv",index=False)
        df.to_json(out/f"{name}.json",orient="records",indent=2,date_format="iso")
    pd.DataFrame(gt_anomalies).to_csv(gt_dir/"ground_truth_anomalies.csv",index=False)
    pd.DataFrame(gt_anomalies).to_json(gt_dir/"ground_truth_anomalies.json",orient="records",indent=2)
    _write_database(frames, ROOT/"database"/"workforce.db")
    manifest={"seed":seed,"employee_count":n,"history_months":months,
        "snapshot_months":len(month_starts),"as_of_date":str(end.date()),
        "actual_attrition_rate":round(len(outcomes)/n,4),"table_row_counts":{k:int(len(v)) for k,v in frames.items()},
        "generator_version":"1.0.0"}
    (ROOT/"reports"/"generation_manifest.json").write_text(json.dumps(manifest,indent=2),encoding="utf-8")
    return frames,manifest

def _write_database(frames, db_path):
    db_path=Path(db_path); db_path.parent.mkdir(parents=True,exist_ok=True)
    if db_path.exists(): db_path.unlink()
    schema_path=ROOT/"database"/"schema.sql"
    with sqlite3.connect(db_path) as conn:
        conn.execute("PRAGMA foreign_keys=ON")
        conn.executescript(schema_path.read_text(encoding="utf-8"))
        order=["Role","Team","CompensationBand","Employee","TenureSnapshot",
               "EngagementSurvey","WorkloadSnapshot","PromotionHistory",
               "AttritionOutcome","Intervention","TransferHistory"]
        for name in order:
            frames[name].to_sql(name,conn,index=False,if_exists="append")
        for table,col in [("TenureSnapshot","employee_id"),("EngagementSurvey","employee_id"),
                          ("WorkloadSnapshot","employee_id"),("PromotionHistory","employee_id"),
                          ("AttritionOutcome","employee_id"),("Intervention","employee_id")]:
            conn.execute(f'CREATE INDEX IF NOT EXISTS idx_{table.lower()}_employee ON "{table}"("{col}")')
        conn.commit()

def checksum_file(path):
    h=hashlib.sha256()
    with open(path,"rb") as f:
        for chunk in iter(lambda:f.read(1024*1024),b""): h.update(chunk)
    return h.hexdigest()
