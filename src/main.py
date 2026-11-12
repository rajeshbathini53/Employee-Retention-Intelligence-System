import argparse, json, shutil
from pathlib import Path
from .generator import generate, ROOT
from .validate import validate
from .exporter import export_sql_dump

def main():
    parser=argparse.ArgumentParser(description="Generate and validate synthetic workforce retention data.")
    parser.add_argument("--seed",type=int,default=None)
    parser.add_argument("--employees",type=int,default=None)
    parser.add_argument("--output",default=None)
    args=parser.parse_args()
    cfg=json.loads((ROOT/"config.json").read_text())
    if args.seed is not None: cfg["seed"]=args.seed
    if args.employees is not None: cfg["employee_count"]=args.employees
    out=Path(args.output) if args.output else ROOT/"data"/"generated"
    frames,manifest=generate(cfg,out)
    report=validate(out)
    export_sql_dump()
    print(json.dumps(manifest,indent=2))
    print("\nValidation summary:")
    print(report.to_string(index=False))
    if (report.status=="FAIL").any():
        raise SystemExit("Validation failed. Review reports/validation_summary.csv")
    print("\nGeneration and validation completed successfully.")

if __name__=="__main__": main()
