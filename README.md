# 🗄️ DB Query Automation Tool

> **Database Integration & Query Automation**
> A Python CLI tool that connects to SQL and NoSQL databases, lets you browse and filter tables/collections, and exports results to CSV — zero manual querying required.

![Python](https://img.shields.io/badge/Python-3.8+-3776AB?style=flat&logo=python&logoColor=white)
![SQLAlchemy](https://img.shields.io/badge/SQLAlchemy-2.0+-D71F00?style=flat)
![MongoDB](https://img.shields.io/badge/MongoDB-pymongo-47A248?style=flat&logo=mongodb&logoColor=white)
![pandas](https://img.shields.io/badge/pandas-CSV%20Export-150458?style=flat&logo=pandas&logoColor=white)
![License](https://img.shields.io/badge/license-MIT-green?style=flat)

---

## 📋 Table of Contents

- [Overview](#-overview)
- [Features](#-features)
- [Project Structure](#-project-structure)
- [Quick Start](#-quick-start)
- [Connection Strings](#-connection-strings)
- [Usage Walkthrough](#-usage-walkthrough)
- [Filter Syntax](#-filter-syntax)
- [Output Format](#-output-format)
- [Architecture](#-architecture)
- [Dependencies](#-dependencies)
- [Troubleshooting](#-troubleshooting)
- [Extending the Tool](#-extending-the-tool)

---

## 🔍 Overview

Manually extracting data from databases is slow and requires technical expertise. This tool solves that by giving you an **interactive CLI** that handles the connection, discovery, filtering, and export automatically.

Supports:
- **SQL** → SQLite, PostgreSQL, MySQL (via SQLAlchemy)
- **NoSQL** → MongoDB, MongoDB Atlas (via pymongo)

---

## ✨ Features

| Feature | Details |
|---|---|
| **Auto-detection** | Reads your connection string prefix and picks the right driver |
| **Table/collection browser** | Lists everything available in the database |
| **Selective fetch** | Choose one table/collection, or export all at once |
| **Parameterized filters** | WHERE clauses (SQL) and query docs (MongoDB) — injection-safe |
| **CSV export** | One `.csv` file per table/collection, headers from schema |
| **Nested doc flattening** | MongoDB `{"address": {"city": "Pune"}}` → `address.city` column |

---

## 📁 Project Structure

```
db_query_tool/
├── db_connector.py          ← Main script (run this)
├── create_sample_db.py      ← Generates test SQLite DB with 3 tables
├── create_sample_mongo.py   ← Seeds test MongoDB with 3 collections
├── db_config.json           ← Connection string templates & reference
├── requirements.txt         ← Python dependencies
├── README.md                ← You are here
└── output/                  ← CSV exports land here (auto-created)
```

---

## 🚀 Quick Start

### 1. Clone and install

```bash
git clone https://github.com/your-username/db-query-tool.git
cd db-query-tool
pip install -r requirements.txt
```

### 2. Create sample test data *(optional — skip if you have a real DB)*

```bash
# SQLite — no server needed, creates sample.db locally
python create_sample_db.py

# MongoDB — requires a running MongoDB instance
python create_sample_mongo.py
```

### 3. Run

```bash
python db_connector.py
```

> **No server? No problem.** Use `sqlite:///sample.db` as your connection string — SQLite is built into Python and requires zero setup.

---

## 🔌 Connection Strings

The tool auto-detects the database type from the URI prefix.

| Database | Connection String |
|---|---|
| **SQLite** | `sqlite:///filename.db` |
| **PostgreSQL** | `postgresql://user:password@host:5432/dbname` |
| **MySQL** | `mysql+pymysql://user:password@host:3306/dbname` |
| **MongoDB (local)** | `mongodb://localhost:27017/dbname` |
| **MongoDB Atlas** | `mongodb+srv://user:password@cluster.mongodb.net/dbname` |

---

## 🖥️ Usage Walkthrough

```
============================================================
   🗄️  DB Query Automation Tool
   Supports: SQLite, PostgreSQL, MySQL, MongoDB
============================================================

📌 STEP 1: Enter your database connection string
  > Connection string: sqlite:///sample.db

📌 STEP 2: Connecting...
  🔍 Detected: SQL Database (SQLAlchemy)
  ✅ SQL connection established.

📌 STEP 3: Available tables / collections:
     [1] departments
     [2] employees
     [3] products

📌 STEP 4: Which table/collection do you want to fetch?
  > employees

📌 STEP 5: Optional filters (press Enter to skip)
  > dept_id=1

  📋 Executing SQL: SELECT * FROM "employees" WHERE "dept_id" = :dept_id
  ✅ Data exported to: output/employees.csv
     Rows: 3 | Columns: 7

     Preview (first 3 rows):
 id           name               email  dept_id    salary   join_date
  1     Aarav Shah   aarav@example.com        1   95000.0  2021-03-15
  3 Rohan Kulkarni  rohan@example.com        1   88000.0  2022-01-20
  6    Ananya Iyer  ananya@example.com       1  102000.0  2018-04-22

  🔒 SQL connection closed.

✅ Done! Check the 'output/' folder for your CSV files.
```

---

## 🔎 Filter Syntax

Filters narrow which rows (SQL) or documents (MongoDB) are returned. They're optional — skip to fetch everything.

### JSON format *(works for both SQL and MongoDB)*

```json
{"age": 30}
{"dept_id": 1, "is_active": 1}
```

### Simple `key=value` format *(SQL and basic MongoDB equality)*

```
age=30
dept_id=1,is_active=1
```

### MongoDB operators *(JSON format only)*

```json
{"age": {"$gt": 25}}
{"city": {"$in": ["Pune", "Mumbai"]}}
{"is_premium": true}
```

---

## 📄 Output Format

Each table or collection is saved as a separate `.csv` in `output/`:

```
output/
├── departments.csv
├── employees.csv
└── products.csv
```

Column headers come directly from the database schema.

**SQL example — `output/employees.csv`:**

```csv
id,name,email,dept_id,salary,join_date,is_active
1,Aarav Shah,aarav@example.com,1,95000.0,2021-03-15,1
3,Rohan Kulkarni,rohan@example.com,1,88000.0,2022-01-20,1
```

**MongoDB nested document flattening:**

```
{"name": "Aarav", "address": {"city": "Pune", "zip": "411001"}}

→  CSV columns:  name | address.city | address.zip
```

---

## 🏗️ Architecture

### Class hierarchy

```
DBConnector (Abstract Base Class)
├── connect()                      ← abstract
├── list_tables_or_collections()   ← abstract
├── fetch_data(table, filters)     ← abstract
├── close()                        ← abstract
└── export_to_csv(df, path)        ← shared (defined once)
      │
      ├── SQLConnector
      │     Driver: SQLAlchemy
      │     connect()   → create_engine() + inspect()
      │     list...()   → inspector.get_table_names()
      │     fetch_data() → text() + parameterized execute()
      │     close()     → connection.close()
      │
      └── MongoDBConnector
            Driver: pymongo
            connect()   → MongoClient() + ping
            list...()   → list_collection_names()
            fetch_data() → find() + json_normalize()
            close()     → client.close()
```

### Key design concepts

**Abstract Base Class** — `DBConnector` is a contract. Any new DB type must implement the 4 abstract methods. The export and CLI logic work automatically for any connector.

**Factory Pattern** — `get_connector(connection_string)` reads the URI prefix and returns the right class. The caller never imports `SQLConnector` or `MongoDBConnector` directly.

**Parameterized queries** — prevents SQL injection:

```python
# ❌ DANGEROUS
f"SELECT * FROM users WHERE id = {user_input}"

# ✅ SAFE — SQLAlchemy escapes before sending to DB
"SELECT * FROM users WHERE id = :id"
```

**MongoDB has no injection risk** — queries are Python dicts serialized as BSON (binary), never string-interpolated into a query language.

---

## 📦 Dependencies

```
pandas>=2.0.0        # DataFrame handling + .to_csv() export
sqlalchemy>=2.0.0    # Universal SQL engine (SQLite, PostgreSQL, MySQL)
pymysql>=1.1.0       # MySQL driver used by SQLAlchemy
psycopg2-binary>=2.9.0   # PostgreSQL driver (pre-compiled binary)
pymongo>=4.6.0       # Official MongoDB Python driver
```

Install all at once:

```bash
pip install -r requirements.txt
```

---

## 🛠️ Troubleshooting

| Problem | Fix |
|---|---|
| `ModuleNotFoundError: pymongo` | `pip install pymongo` |
| `ModuleNotFoundError: sqlalchemy` | `pip install sqlalchemy` |
| `Connection refused` (PostgreSQL/MySQL) | Make sure the DB server is running on the correct port |
| `Authentication failed` | Check username and password in your connection string |
| `Database not found` (MongoDB) | Include DB name in URI: `mongodb://host:27017/mydb` |
| Empty CSV exported | Your filter returned no rows — try without a filter first |
| `_id` column missing (MongoDB) | Expected — ObjectId is dropped as it can't be CSV-serialized |

---

## 🔧 Extending the Tool

Adding a new database type takes 3 steps:

**1. Create a class inheriting from `DBConnector`**

```python
class CassandraConnector(DBConnector):
    def connect(self): ...
    def list_tables_or_collections(self): ...
    def fetch_data(self, table, filters=None): ...
    def close(self): ...
```

**2. Add detection logic in `get_connector()`**

```python
elif cs.startswith("cassandra://"):
    return CassandraConnector(connection_string)
```

**3. Done.** Export, preview, and CLI logic work automatically.

---

## 🔒 Security Notes

> ⚠️ **Never commit `db_config.json` with real credentials to version control.** Add it to `.gitignore` and use environment variables or a secrets manager for production deployments.

- SQL injection prevented via SQLAlchemy's `:placeholder` parameterized queries
- MongoDB queries are BSON-serialized — no string interpolation, no injection surface
- Credentials live only in `db_config.json` — keep it out of git

---

## 📄 License

MIT License — see [LICENSE](LICENSE) for details.
