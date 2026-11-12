# Architecture and Decisions

1. Python is used for deterministic generation, validation, export and business rules.
2. NumPy Generator is initialized with a fixed seed. The same config and version produce repeatable outputs.
3. SQLite provides a local relational database without a hosted service.
4. Pandas handles tabular exports and validation summaries.
5. Streamlit is an optional local dashboard, not a required hosted service.
6. Ground-truth anomaly labels are stored separately from input features.
7. Attrition outcomes are stored separately from pre-outcome snapshots. Any future evaluation must use an explicit as-of cutoff and must not join future outcomes into feature inputs.
8. All recommendations are supportive signals requiring human review, never automatic employment decisions.

## Known limitations
- This is a synthetic demonstration, not a validated HR prediction product.
- Synthetic attrition mechanisms are illustrative and should not be interpreted as causal evidence.
- The generator uses a monthly 24-month history with quarter-plus-month snapshot IDs. Internal team transfers are stored as dated TransferHistory events and reflected in subsequent snapshots. Attrition outcomes are derived deterministically by ranking a documented risk score based on pre-outcome engagement and workload signals; the selected cohort is assigned future event dates within the configured 90-day horizon. The resulting rate is 10%, within the required 5–15% range.
- The initial schema is intentionally compact. For full effective-dated role/team many-to-many history, add explicit bridge/event tables and document cardinality before production use.
