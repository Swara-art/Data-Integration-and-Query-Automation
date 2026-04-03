import sqlite3
import os
 
DB_PATH = "sample.db"

CREATE_DEPARTMENTS = """
CREATE TABLE IF NOT EXISTS departments (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    name        TEXT    NOT NULL,
    location    TEXT    NOT NULL,
    budget      REAL    NOT NULL
);
"""
 
CREATE_EMPLOYEES = """
CREATE TABLE IF NOT EXISTS employees (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    name        TEXT    NOT NULL,
    email       TEXT    UNIQUE NOT NULL,
    dept_id     INTEGER REFERENCES departments(id),
    salary      REAL    NOT NULL,
    join_date   TEXT    NOT NULL,
    is_active   INTEGER DEFAULT 1    -- SQLite uses 1/0 for booleans
);
"""
 
CREATE_PRODUCTS = """
CREATE TABLE IF NOT EXISTS products (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    name        TEXT    NOT NULL,
    category    TEXT    NOT NULL,
    price       REAL    NOT NULL,
    stock       INTEGER NOT NULL,
    supplier    TEXT
);
"""
 
# ── Sample data ───────────────────────────────────────────────────
DEPARTMENTS = [
    ("Engineering",  "Pune",      1500000.00),
    ("Marketing",    "Mumbai",     800000.00),
    ("HR",           "Bangalore",  500000.00),
    ("Sales",        "Delhi",     1200000.00),
]
 
EMPLOYEES = [
    ("Aarav Shah",      "aarav@example.com",   1, 95000, "2021-03-15", 1),
    ("Priya Mehta",     "priya@example.com",   2, 72000, "2020-07-01", 1),
    ("Rohan Kulkarni",  "rohan@example.com",   1, 88000, "2022-01-20", 1),
    ("Sneha Patil",     "sneha@example.com",   3, 65000, "2019-11-05", 1),
    ("Vikram Nair",     "vikram@example.com",  4, 78000, "2023-06-10", 1),
    ("Ananya Iyer",     "ananya@example.com",  1, 102000,"2018-04-22", 1),
    ("Karan Joshi",     "karan@example.com",   2, 68000, "2021-09-30", 0),
    ("Meera Reddy",     "meera@example.com",   4, 85000, "2020-02-14", 1),
]
 
PRODUCTS = [
    ("Laptop Pro 15",     "Electronics",   89999, 45,  "TechCorp"),
    ("Wireless Mouse",    "Accessories",    1299,  200, "PeriphHub"),
    ("Standing Desk",     "Furniture",     24999,  30, "OfficePlus"),
    ("Monitor 27inch",    "Electronics",   32999,  60, "ViewMax"),
    ("Noise Cancel Earphones", "Audio",    15999, 150, "SoundWave"),
    ("USB-C Hub",         "Accessories",    3499,  90, "PeriphHub"),
    ("Ergonomic Chair",   "Furniture",     18999,  20, "OfficePlus"),
]
 
 
def create_sample_db():
    if os.path.exists(DB_PATH):
        print(f"{DB_PATH} already exists. Deleting and recreating...")
        os.remove(DB_PATH)
 
    print(f"🔨 Creating {DB_PATH}...")

    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()

    cur.execute(CREATE_DEPARTMENTS)
    cur.execute(CREATE_EMPLOYEES)
    cur.execute(CREATE_PRODUCTS)

    cur.executemany("INSERT INTO departments (name, location, budget) VALUES (?,?,?)", DEPARTMENTS)
    cur.executemany(
        "INSERT INTO employees (name, email, dept_id, salary, join_date, is_active) VALUES (?,?,?,?,?,?)",
        EMPLOYEES
    )
    cur.executemany(
        "INSERT INTO products (name, category, price, stock, supplier) VALUES (?,?,?,?,?)",
        PRODUCTS
    )
 
    conn.commit()
    conn.close()
 
    print(f"✅ Sample database created: {DB_PATH}")
    print(f"   Tables: departments ({len(DEPARTMENTS)} rows)")
    print(f"           employees   ({len(EMPLOYEES)} rows)")
    print(f"           products    ({len(PRODUCTS)} rows)")
    print(f"\n▶  Now run: python db_connector.py")
    print(f"   Use connection string: sqlite:///sample.db")
 
 
if __name__ == "__main__":
    create_sample_db()