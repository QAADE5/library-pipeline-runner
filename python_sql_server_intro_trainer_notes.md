# Trainer notes - Python meets SQL Server

**Slot:** 30 mins - **Notebook:** `python_sql_server_intro.ipynb` - **Tools:** Jupyter (VS Code optional) + SSMS side by side

**Aim:** learners see that Python and SSMS are both clients of the same SQL Server, and can create a database, a table and data from Python, then view it in SSMS.

## Before the session

- Run the whole notebook once on a learner VM.
- Confirm `pyodbc.drivers()` lists **ODBC Driver 17 for SQL Server**. If only Driver 18 is present, change `DRIVER` and add `TrustServerCertificate=yes;` to both connection strings.
- Drop `py_sandbox` afterwards so your demo starts clean.

## Timings

| Time | Part | Learning type | What happens |
|---|---|---|---|
| 0-10 | Part 1 demo | Acquisition | You run Steps 1-10 live, refreshing SSMS after each step |
| 10-20 | Part 1 + Part 2 | Practice | Learners run the cells, then make the "Make it yours" changes |
| 20-30 | Part 3 | Production | Learners build their own scenario in the empty cells |

## Key moments in the demo

| Step | Point to land | What SSMS shows |
|---|---|---|
| 2 | The connection string holds the same details as the SSMS connect box | - |
| 3 | We connect to `master` with autocommit, because `CREATE DATABASE` can't run in a transaction | Refresh Databases - `py_sandbox` appears |
| 5 | Python just sends T-SQL - nothing new from Module 2 | Refresh Tables - `dbo.products` appears |
| 6 | `?` placeholders keep data and SQL separate | `SELECT * FROM products` **waits** ("Executing query…") |
| 7 | Uncommitted changes are invisible to other clients | The waiting query finishes and shows 5 rows |
| 8 | `fetchall()` returns a list, and a `for` loop prints it | - |
| 9 | `cursor.description` gives the headers. `newline=''` stops blank lines on Windows | - |
| 10 | An open connection keeps the database "in use" | - |

**The Step 6-7 pause is the highlight.** Ask "Why is SSMS waiting?" before running Step 7.

## Common issues

| Symptom | Cause and fix |
|---|---|
| SSMS query never finishes | Python hasn't committed. Run Step 7. |
| `Data source name not found` | Wrong driver name. Check the output of Step 1. |
| `Login failed` | The VM user isn't Windows-authenticated to SQL Server, or `SERVER` is wrong. Check the SSMS connect box. |
| Can't delete the database in SSMS | A connection is still open. Run Step 10, or restart the kernel. |
| `NameError: conn` in Part 2 | The connection was closed in Step 10. Re-run Step 4. |
| Part 2 new column fails in Step 6 | The `INSERT` column list, the `?` count and the tuples all need updating. This is the intended challenge. |

## Debrief questions (if time allows)

- What's the difference between SSMS and SQL Server?
- Why did we connect to `master` first?
- What would happen in a pipeline that never calls `commit()`?
- Why use `?` placeholders rather than building the SQL with an f-string?

## Bridge to the next part

Learners have gone from **SQL Server to CSV**. Next they go the other way, taking their pipeline's CSVs into SQL Server.
