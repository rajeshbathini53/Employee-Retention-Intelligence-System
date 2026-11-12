# Employee Retention Intelligence System

A Python-based synthetic workforce data generation, validation, and analytics application with an interactive dashboard for exploring employee engagement, workload, tenure, and retention-related insights.


## Project Overview

The Employee Retention Intelligence System is designed to generate and analyze synthetic workforce data to demonstrate how employee engagement, workload patterns, tenure, and historical workforce events can support employee retention analysis.

The application generates structured employee datasets, validates data integrity, stores information in an SQLite database, and provides an interactive dashboard for visualizing workforce trends.

## Key Features

- Generates synthetic workforce data for 10,000 employees.
- Creates 24 months of longitudinal employee records.
- Includes a separate 90-day future voluntary attrition outcome horizon.
- Supports 10 core entities and an additional TransferHistory event table.
- Exports datasets in CSV and JSON formats.
- Stores structured data in an SQLite database.
- Generates separately labelled anomaly ground truth.
- Performs data integrity and temporal validation.
- Exports SQL seed scripts.
- Provides an interactive Streamlit dashboard.
- Visualizes engagement and workload distributions.
- Displays supportive employee retention interventions.
- Includes automated testing using Pytest.
- Supports deterministic data generation using a configurable random seed.

## Technology Stack

| Component                 |       Technology      |
-----------------------------------------------------
| Programming Language      |       Python 3.12     |
| Data Processing           |       Pandas          |
| Numerical Computing       |       NumPy           |
| Frontend / Dashboard      |       Streamlit       |
| Data Visualization        |       Plotly          |
| Database                  |       SQLite          |
| Query Language            |       SQL             |
| Testing                   |       Pytest          |
| Excel Support             |       OpenPyXL        |
-----------------------------------------------------

## Project Architecture

The application follows a Python-based data generation and analytics workflow.

1. **Data Generation:** Python, NumPy, and Pandas generate synthetic workforce records.
2. **Data Validation:** Validation logic checks data integrity, relationships, and temporal constraints.
3. **Data Storage:** Generated datasets are exported as CSV and JSON files and stored in SQLite.
4. **Dashboard:** Streamlit provides the interactive user interface, while Plotly displays workforce visualizations.
5. **Testing:** Pytest executes automated checks against important project requirements.

## Project Structure

employee_retention_intelligence/
│
├── dashboard/
│   └── app.py
│
├── data/
│   ├── exports/
│   ├── generated/
│   ├── ground_truth/
│   └── test_generated/
│
├── database/
│   ├── schema.sql
│   └── workforce.db
│
├── docs/
│   ├── architecture.md
│   ├── data_dictionary.md
│   └── data_dictionary.xlsx
│
├── reports/
│   ├── build_log.txt
│   ├── generation_manifest.json
│   ├── test_log.txt
│   ├── validation_summary.csv
│   ├── validation_summary.json
│   └── verification_summary.json
│
├── src/
│   ├── generator.py
│   ├── main.py
│   └── validate.py
│
├── tests/
│   └── test_project.py
│
├── config.json
├── PROJECT_MANIFEST.json
├── README.md
└── requirements.txt


## Installation and Setup

### Prerequisites

- Python 3.10 or later
- pip
- Git

### 1. Clone the Repository

git clone YOUR_GITHUB_REPOSITORY_URL
cd employee_retention_intelligence


### 2. Create a Virtual Environment

python -m venv .venv

### 3. Activate the Environment

**Windows:**

.venv\Scripts\activate

**macOS / Linux:**

source .venv/bin/activate

### 4. Install Dependencies

python -m pip install -r requirements.txt

## Running the Application

### 1. Generate Workforce Data and Validate

python -m src.main

This command executes the main data generation and validation workflow.

It generates employee datasets, exports CSV and JSON files, creates the SQLite database, and produces validation reports.

### 2. Launch the Dashboard

python -m streamlit run dashboard/app.py

Open the local URL displayed in the terminal.

Usually:

http://localhost:8501

### 3. Run Automated Tests

python -m pytest tests -v

## Sample Project Results

The completed local execution generated the following results:

| Metric                    |       Result          |
|---------------------------------------------------
| Synthetic Employees       |       10,000          |
| Historical Period         |       24 months       |
| TenureSnapshot Records    |       240,000         |
| EngagementSurvey Records  |       240,000         |
| WorkloadSnapshot Records  |       240,000         |
| AttritionOutcome Records  |       1,000           |
| Planned Interventions     |       3,947           |
| TransferHistory Records   |       1,223           |
| Survey Completion         |       88%             |
-----------------------------------------------------

These figures represent the generated synthetic dataset and observed dashboard output.

## Database

The application uses **SQLite** for local structured data storage.

**Database file:**

database/workforce.db

**Database schema:**

database/schema.sql

The database contains 11 tables:

1. Employee
2. Role
3. Team
4. TenureSnapshot
5. EngagementSurvey
6. WorkloadSnapshot
7. CompensationBand
8. PromotionHistory
9. AttritionOutcome
10. Intervention
11. TransferHistory

SQL is used to define database tables, relationships, and data storage structures.

## Generated Outputs

| Location                  |       Description             |
|-------------------------------------------------------------
| `data/generated/`         |    Generated entity datasets in CSV and JSON formats |
| `data/ground_truth/`      |    Labelled anomaly ground-truth datasets |
| `data/test_generated/`    |    Test-generated datasets |
| `data/exports/`           |    SQL seed export |
| `database/workforce.db`   |    SQLite database |
| `reports/`                |    Generation, validation, testing, and verification reports |
| `docs/`                   |    Architecture and data dictionary documentation |

## Testing and Verification

The automated test suite was executed successfully.

**Test Results:**

test_generated_employee_count PASSED
