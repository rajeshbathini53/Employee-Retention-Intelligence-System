# Data Dictionary

All data is synthetic. Identifiers are deterministic and immutable. Dates use ISO-8601 (`YYYY-MM-DD`).

| Entity | Primary key | Important fields | Rules |
|---|---|---|---|
| Employee | employee_id | role_id, team_id, hire_date, employment_status | role/team/band references must exist |
| Role | role_id | role_name, job_family, level | controlled role master |
| Team | team_id | team_name, department | controlled team master |
| TenureSnapshot | snapshot_id | employee_id, snapshot_date, tenure_months, period | derived from hire date and snapshot date |
| EngagementSurvey | survey_id | employee_id, survey_date, engagement_score, survey_status | missing scores remain NULL, never converted to zero |
| WorkloadSnapshot | workload_snapshot_id | employee_id, snapshot_date, weekly_hours, overtime_hours | derived metrics reconciled to source hours |
| CompensationBand | compensation_band_id | min_salary, max_salary, currency | synthetic bands only; no individual salary |
| PromotionHistory | promotion_id | employee_id, effective_date, from_level, to_level | chronological event history |
| AttritionOutcome | outcome_id | employee_id, outcome_date, outcome_type | future outcome label; excluded from pre-outcome features |
| Intervention | intervention_id | employee_id, created_date, intervention_type, reason | supportive workflow; human review required |

## Relationships
- Role 1:N Employee; Team 1:N Employee; CompensationBand 1:N Employee.
- Employee 1:N TenureSnapshot, EngagementSurvey, WorkloadSnapshot, PromotionHistory, AttritionOutcome, Intervention.
- Historical role/team changes should be represented as dated events/snapshots, not destructive overwrites.
- A future production extension may add explicit EmployeeTeamHistory and EmployeeRoleHistory bridge/event tables if multiple concurrent assignments are required.
\nSnapshot IDs use `SNAP-<employee-id>-<YYYY>Q<quarter>M<month>` to preserve the requested quarter-based convention while remaining unique for monthly records.\n
| TransferHistory | transfer_id | employee_id, from_team_id, to_team_id, effective_date, reason_code | records internal team transfers as dated events; both teams must exist |
