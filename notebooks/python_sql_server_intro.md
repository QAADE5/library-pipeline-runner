# Python meets SQL Server

In Module 2 you worked with SQL Server through **SSMS**. Today **Python** talks to the same SQL Server.

SSMS and Python are both *clients*. Neither one *is* the database - they are two windows onto the same server. So anything Python creates, SSMS can see.

```
   SSMS  ───┐
            ├──►  SQL Server (localhost)  ──►  your databases
  Python ───┘
```

**In this notebook you will use Python to:**

1. Connect to SQL Server
2. Create a database
3. Create a table
4. Insert some data
5. Read the data back
6. Save it to a CSV file

**Before you start:** open SSMS and connect to `localhost` with Windows Authentication. Keep it open next to this notebook - you will check SSMS after each step.

Run each cell in order with **Shift + Enter**.

---
# Part 1 - Follow along

## Step 1: Import the libraries

- `pyodbc` lets Python talk to SQL Server
- `csv` is built into Python and writes CSV files

The last line lists the database drivers on your machine. Look for **ODBC Driver 17 for SQL Server** in the output.


```python
import pyodbc
import csv

print(pyodbc.drivers())
```

## Step 2: The connection details

Python needs the same information you type into the SSMS **Connect to Server** box:

| SSMS connect box | Python connection string |
|---|---|
| Server name | `SERVER=localhost` |
| Authentication: Windows Authentication | `Trusted_Connection=yes` |
| Options > Connect to database | `DATABASE=...` |

We need two connection strings:

- one to `master` - the system database we use to create *new* databases
- one to *our* database, `py_sandbox`


```python
SERVER = 'localhost'
DATABASE = 'py_sandbox'
DRIVER = '{ODBC Driver 17 for SQL Server}'

master_conn_str = f'DRIVER={DRIVER};SERVER={SERVER};DATABASE=master;Trusted_Connection=yes;'
db_conn_str = f'DRIVER={DRIVER};SERVER={SERVER};DATABASE={DATABASE};Trusted_Connection=yes;'

print(master_conn_str)
print(db_conn_str)
```

## Step 3: Create the database

Notice three things:

- We connect to `master`, because our database doesn't exist yet
- `autocommit=True` - `CREATE DATABASE` is not allowed inside a transaction, so each statement must be saved straight away
- `IF NOT EXISTS` - the cell is safe to run again without an error

**Check SSMS:** in Object Explorer, right-click **Databases** > **Refresh**. You should see `py_sandbox`.


```python
master_conn = pyodbc.connect(master_conn_str, autocommit=True)

master_conn.execute(f'''
    IF NOT EXISTS (SELECT name FROM sys.databases WHERE name = '{DATABASE}')
        CREATE DATABASE [{DATABASE}]
''')

master_conn.close()
print(f'Database ready: {DATABASE}')
```

## Step 4: Connect to our database

This time we connect to `py_sandbox` itself, **without** autocommit.

That means our changes sit in a *transaction* until we choose to save them with `commit()`. Remember this - it matters in Step 6.

A **cursor** is the object we send SQL through.


```python
conn = pyodbc.connect(db_conn_str)
cursor = conn.cursor()

print(f'Connected to {DATABASE}')
```

## Step 5: Create a table

This is plain T-SQL - exactly what you would type in SSMS. Python just sends it to the server.

`DROP TABLE IF EXISTS` removes any old copy first, so this cell is safe to run again.

**Check SSMS:** expand `py_sandbox` > **Tables** and refresh. You should see `dbo.products`.


```python
cursor.execute('''
    DROP TABLE IF EXISTS products;

    CREATE TABLE products (
        product_id    INT            PRIMARY KEY,
        product_name  NVARCHAR(100)  NOT NULL,
        category      NVARCHAR(50),
        price         DECIMAL(8, 2),
        in_stock      BIT
    );
''')
conn.commit()

print('Table created: products')
```

## Step 6: Insert some data

Python values go into the SQL through `?` placeholders. Each `?` is filled, in order, from a row of `products`. This is called a **parameterised query** - it keeps data and SQL separate.

The cell starts with `DELETE FROM products` so it is safe to run again without duplicate key errors.

**We have NOT committed yet.**

**Check SSMS:** open a New Query on `py_sandbox` and run:

```sql
SELECT * FROM products;
```

What happens? Leave that query running and move on to Step 7.


```python
products = [
    (1, 'Wireless mouse',       'Accessories', 19.99,  1),
    (2, 'USB-C hub',            'Accessories', 34.50,  1),
    (3, '27-inch monitor',      'Displays',    229.00, 0),
    (4, 'Mechanical keyboard',  'Accessories', 89.95,  1),
    (5, 'Laptop stand',         'Furniture',   42.00,  1),
]

cursor.execute('DELETE FROM products')

cursor.executemany(
    'INSERT INTO products (product_id, product_name, category, price, in_stock) VALUES (?, ?, ?, ?, ?)',
    products
)

print(f'{len(products)} rows inserted - but NOT committed yet')
```

## Step 7: Commit

Your SSMS query was **waiting**. SQL Server won't show anyone else rows that haven't been saved yet, so SSMS waits for Python to finish its transaction.

Run the cell below and watch SSMS - the query finishes straight away and your rows appear.


```python
conn.commit()

print('Committed - check SSMS now')
```

## Step 8: Read the data back

`fetchall()` returns a **list** of rows. We loop through it with a `for` loop.

Each row lets you use the column names, for example `row.product_name`.


```python
cursor.execute('SELECT product_id, product_name, category, price, in_stock FROM products ORDER BY product_id')
rows = cursor.fetchall()

print(f'{len(rows)} rows returned\n')

for row in rows:
    print(f'{row.product_id:>3}  {row.product_name:<22} {row.category:<12} £{row.price:>7.2f}')
```

## Step 9: Save to a CSV file

`cursor.description` tells us the column names from the last query - we use them as the CSV header row.

`newline=''` stops Windows adding blank lines between rows.

The file `products.csv` is saved in the same folder as this notebook.


```python
cursor.execute('SELECT product_id, product_name, category, price, in_stock FROM products ORDER BY product_id')
rows = cursor.fetchall()
headers = [column[0] for column in cursor.description]

with open('products.csv', 'w', newline='', encoding='utf-8') as f:
    writer = csv.writer(f)
    writer.writerow(headers)
    writer.writerows(rows)

print(f'Saved {len(rows)} rows to products.csv')
```

## Step 10: Close the connection

Always close your connection when you're finished. An open connection keeps the database **in use**, which stops you deleting it from SSMS.


```python
cursor.close()
conn.close()

print('Connection closed')
```

---
# Part 2 - Make it yours

Now change the code and run it again. Check SSMS after each change.

1. In **Step 6**, add a sixth product to the list. Re-run Steps 4, 6 and 7. Does SSMS show 6 rows?
2. Change the price of one product. Re-run Steps 4, 6 and 7, then Step 8.
3. In **Step 5**, add a new column such as `supplier NVARCHAR(50)`. What else do you need to change to make Steps 6 and 8 work?
4. Re-run Step 9 and open `products.csv`. Does it match what SSMS shows?

**Tip:** after Step 10 the connection is closed. To carry on, re-run Step 4 first.

---
# Part 3 - On your own

Create your own scenario - for example a gym, a café, a football league, or something from your workplace. Use the cells below.

All the code you need is in Part 1. Copy it, then change it.

1. **Create your own database** - give it a new name
2. **Create a table** of your own design - at least 4 columns with suitable data types and a primary key
3. **Insert some rows** - at least 5 - then commit
4. **Select the rows** and print them with a `for` loop
5. **Save the results** to a CSV file
6. **Close** your connection

Check SSMS after each step.

**Stretch:**

- Open your CSV and check it against SSMS
- Add a `WHERE` or `ORDER BY` to your `SELECT` and save a second CSV
- Add a second table to your database


```python
# 1. Connection details and create your database
```


```python
# 2. Connect to your database and create your table
```


```python
# 3. Insert your rows - then commit
```


```python
# 4. Select your rows and print them with a for loop
```


```python
# 5. Save your results to a CSV file
```


```python
# 6. Close your connection
```
