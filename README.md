# Library Pipeline Runner

A second library network that consumes your cleaning package.
Your code runs here unchanged - only the data is different.

## Setup

### 1. Clone this repo

```bash
git clone https://github.com/QAADE5/library-pipeline-runner.git
cd library-pipeline-runner
```

### 2. Install dependencies

```bash
pip install -r requirements.txt
```

### 3. Install your pipeline package

```bash
pip install git+https://github.com/YOUR_ORG/YOUR_REPO.git
```

### 4. Run the pipeline

```bash
python -m data_processing.run_pipeline
```

Cleaned files will appear in `data/silver/`.

### 5. Load to SQL Server

```bash
python load_to_sql.py
```

### 6. Open SSMS

Connect to `localhost` and explore the `library_warehouse` database.
