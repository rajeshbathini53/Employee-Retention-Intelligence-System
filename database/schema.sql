-- Logical schema reference. Runtime generator creates typed SQLite tables.
-- Every entity has an immutable primary key; dependent entities reference Employee.
CREATE TABLE IF NOT EXISTS Role(role_id TEXT PRIMARY KEY, role_name TEXT NOT NULL, job_family TEXT, level TEXT);
CREATE TABLE IF NOT EXISTS Team(team_id TEXT PRIMARY KEY, team_name TEXT NOT NULL, department TEXT);
CREATE TABLE IF NOT EXISTS CompensationBand(compensation_band_id TEXT PRIMARY KEY, band_name TEXT NOT NULL, min_salary REAL, max_salary REAL, currency TEXT);
CREATE TABLE IF NOT EXISTS Employee(employee_id TEXT PRIMARY KEY, role_id TEXT NOT NULL REFERENCES Role(role_id), team_id TEXT NOT NULL REFERENCES Team(team_id), compensation_band_id TEXT NOT NULL REFERENCES CompensationBand(compensation_band_id), hire_date DATE NOT NULL, employment_status TEXT NOT NULL, location_code TEXT, created_at DATE, synthetic_record BOOLEAN NOT NULL);
CREATE TABLE IF NOT EXISTS TenureSnapshot(snapshot_id TEXT PRIMARY KEY, employee_id TEXT NOT NULL REFERENCES Employee(employee_id), snapshot_date DATE NOT NULL, period TEXT NOT NULL, tenure_months INTEGER NOT NULL, tenure_years REAL NOT NULL, role_id TEXT REFERENCES Role(role_id), team_id TEXT REFERENCES Team(team_id));
CREATE TABLE IF NOT EXISTS EngagementSurvey(survey_id TEXT PRIMARY KEY, employee_id TEXT NOT NULL REFERENCES Employee(employee_id), survey_date DATE NOT NULL, period TEXT NOT NULL, engagement_score REAL, manager_support_score REAL, survey_status TEXT NOT NULL, missing_reason TEXT);
CREATE TABLE IF NOT EXISTS WorkloadSnapshot(workload_snapshot_id TEXT PRIMARY KEY, employee_id TEXT NOT NULL REFERENCES Employee(employee_id), snapshot_date DATE NOT NULL, weekly_hours REAL NOT NULL, overtime_hours REAL NOT NULL, capacity_utilization_pct REAL, workload_status TEXT);
CREATE TABLE IF NOT EXISTS PromotionHistory(promotion_id TEXT PRIMARY KEY, employee_id TEXT NOT NULL REFERENCES Employee(employee_id), effective_date DATE NOT NULL, from_level TEXT, to_level TEXT, reason_code TEXT);
CREATE TABLE IF NOT EXISTS AttritionOutcome(outcome_id TEXT PRIMARY KEY, employee_id TEXT NOT NULL REFERENCES Employee(employee_id), outcome_date DATE NOT NULL, outcome_type TEXT NOT NULL, future_horizon_days INTEGER, rule_version TEXT);
CREATE TABLE IF NOT EXISTS Intervention(intervention_id TEXT PRIMARY KEY, employee_id TEXT NOT NULL REFERENCES Employee(employee_id), created_date DATE NOT NULL, intervention_type TEXT NOT NULL, status TEXT NOT NULL, reason TEXT, human_review_required BOOLEAN NOT NULL);

CREATE TABLE IF NOT EXISTS TransferHistory(
 transfer_id TEXT PRIMARY KEY,
 employee_id TEXT NOT NULL REFERENCES Employee(employee_id),
 from_team_id TEXT NOT NULL REFERENCES Team(team_id),
 to_team_id TEXT NOT NULL REFERENCES Team(team_id),
 effective_date DATE NOT NULL,
 reason_code TEXT NOT NULL
);
