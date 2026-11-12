from pathlib import Path
import sqlite3
from .generator import ROOT, TABLES

def export_sql_dump(db_path=None, output_path=None):
    db_path=Path(db_path or ROOT/"database"/"workforce.db")
    output_path=Path(output_path or ROOT/"data"/"exports"/"workforce_seed.sql")
    output_path.parent.mkdir(parents=True,exist_ok=True)
    with sqlite3.connect(db_path) as conn:
        lines=["-- Synthetic workforce database seed dump"]
        for table in TABLES:
            rows=conn.execute(f'SELECT * FROM "{table}"').fetchall()
            cols=[d[1] for d in conn.execute(f'PRAGMA table_info("{table}")').fetchall()]
            lines.append(f"-- {table}: {len(rows)} rows")
            for row in rows:
                vals=[]
                for v in row:
                    if v is None: vals.append("NULL")
                    elif isinstance(v,(int,float)): vals.append(str(v))
                    else: vals.append("'" + str(v).replace("'","''") + "'")
                lines.append(f'INSERT INTO "{table}" ({",".join(chr(34)+c+chr(34) for c in cols)}) VALUES ({",".join(vals)});')
        output_path.write_text("\n".join(lines),encoding="utf-8")
    return output_path
