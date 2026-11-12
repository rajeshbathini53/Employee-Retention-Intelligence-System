from pathlib import Path
import pandas as pd
from src.generator import ROOT, generate, load_config
from src.validate import validate

def test_generated_employee_count():
    cfg=load_config()
    cfg["employee_count"]=120
    cfg["history_months"]=24
    generate(cfg, ROOT/"data"/"test_generated")
    df=pd.read_csv(ROOT/"data"/"test_generated"/"Employee.csv")
    assert len(df)==120
    assert df.employee_id.is_unique

def test_missing_survey_is_not_zero():
    cfg=load_config()
    cfg["employee_count"]=80
    generate(cfg, ROOT/"data"/"test_generated")
    df=pd.read_csv(ROOT/"data"/"test_generated"/"EngagementSurvey.csv")
    assert df.loc[df.survey_status=="MISSING","engagement_score"].isna().all()
