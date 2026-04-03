import csv
import json
import os
import re
import sys
from abc import ABC, abstractmethod  # ABC = Abstract Base Class
from urllib.parse import urlparse
from sqlalchemy import create_engine, text, inspect
import pymongo
 
import pandas as pd

class DBConnector(ABC):
    def __init__(self, connection_string: str):
        self.connection_string = connection_string
        self.connection = None
        
    @abstractmethod
    def connect(self):
        pass
    
    @abstractmethod
    def list_tables_or_collections(self) -> list:
        pass
 
    @abstractmethod
    def fetch_data(self, table_or_collection: str, filters: dict = None) -> pd.DataFrame:
        pass
 
    @abstractmethod
    def close(self):
        pass
 
    def export_to_csv(self, df: pd.DataFrame, output_path: str):
        df.to_csv(output_path, index=False, encoding="utf-8")
        print(f"Data exported to: {output_path}")
        print(f"Rows: {len(df)} | Columns: {len(df.columns)}")
        
class SQLConnector(DBConnector):
    def connect(self):
        try:
            self.engine     = create_engine(self.connection_string)
            self.connection = self.engine.connect()
            self.inspector  = inspect(self.engine)
            self._text      = text
 
            print(f"SQL connection established.")
        except Exception as e:
            print(f"SQL Connection failed: {e}")
            raise
 
    def list_tables_or_collections(self) -> list:
        tables = self.inspector.get_table_names()
        return tables
 
    def fetch_data(self, table_or_collection: str, filters: dict = None) -> pd.DataFrame:
        query  = f'SELECT * FROM "{table_or_collection}"'
        params = {}

        if filters:
            conditions = [f'"{col}" = :{col}' for col in filters]
            query  += " WHERE " + " AND ".join(conditions)
            params  = dict(filters)   # copy — don't mutate the caller's dict

        result  = self.connection.execute(self._text(query), params)
        columns = list(result.keys())     # column names from DB schema
        rows    = result.fetchall()       # list of tuples, one per row

        return pd.DataFrame(rows, columns=columns)

    def close(self):
        if self.connection:
            self.connection.close()
 
        
    
class MongoDBConnector(DBConnector):
    def connect(self):
            try:
                self.client = pymongo.MongoClient(self.connection_string)
                self.client.admin.command("ping")
                parsed = urlparse(self.connection_string)
                db_name = parsed.path.lstrip("/")
    
                if not db_name:
                    raise ValueError("Database name must be included in the connection string. e.g. .../mydb")

                self.db = self.client[db_name]
                self.connection = self.db  
    
                print(f"MongoDB connected to database: '{db_name}'")
            except Exception as e:
                print(f"MongoDB connection failed: {e}")
                raise
    
    def list_tables_or_collections(self) -> list:
            return self.db.list_collection_names()
    
    def fetch_data(self, table_or_collection: str, filters: dict = None) -> pd.DataFrame:
            collection = self.db[table_or_collection]
            query_filter = filters if filters else {}
    
            print(f"MongoDB query on '{table_or_collection}' with filter: {query_filter}")
    
            documents = list(collection.find(query_filter))
    
            if not documents:
                print("No documents found.")
                return pd.DataFrame()

            for doc in documents:
                doc.pop("_id", None)
    
            df = pd.json_normalize(documents)
            return df
    
    def close(self):
            if self.client:
                self.client.close()
                print("MongoDB connection closed.")

class MongoDBConnector(DBConnector):
    def __init__(self, connection_string: str):
        super().__init__(connection_string)

    def connect(self):
        self.client = pymongo.MongoClient(self.connection_string)
        self.client.admin.command("ping")           # verify it's alive

        parsed  = urlparse(self.connection_string)
        db_name = parsed.path.lstrip("/")

        if not db_name:
            raise ValueError("Add DB name to URI: mongodb://host:27017/mydb")

        self.db         = self.client[db_name]
        self.connection = self.db
        
    def list_tables_or_collections(self) -> list:
        return self.db.list_collection_names()
    
    def fetch_data(self, table_or_collection: str, filters: dict = None) -> pd.DataFrame:
        collection    = self.db[table_or_collection]
        query_filter  = filters if filters else {}

        documents = list(collection.find(query_filter))  

        if not documents:
            return pd.DataFrame()

        for doc in documents:
            doc.pop("_id", None)                          

        return pd.json_normalize(documents)               

    def close(self):
        if self.client:
            self.client.close()

def get_connector(connection_string: str) -> DBConnector:
    cs = connection_string.strip().lower()
 
    if cs.startswith("mongodb"):
        print("Detected: MongoDB (NoSQL)")
        return MongoDBConnector(connection_string)
    elif cs.startswith("sqlite") or cs.startswith("postgresql") or cs.startswith("mysql"):
        print("Detected: SQL Database (SQLAlchemy)")
        return SQLConnector(connection_string)
    else:
        raise ValueError(
            f"Unsupported connection string prefix.\n"
            f"Supported: sqlite://, postgresql://, mysql://, mongodb://, mongodb+srv://"
        )
        
def parse_filter_input(raw: str) -> dict:
    raw = raw.strip()
    if not raw:
        return {}
 
    # Try JSON format first
    try:
        return json.loads(raw)
    except json.JSONDecodeError:
        pass
 
    # Try simple key=value,key=value format
    result = {}
    for pair in raw.split(","):
        if "=" in pair:
            k, v = pair.split("=", 1)
            k, v = k.strip(), v.strip()
            # Try to cast to int or float if possible
            try:
                v = int(v)
            except ValueError:
                try:
                    v = float(v)
                except ValueError:
                    pass  # Keep as string
            result[k] = v
    return result
 
 
def main():
    print("\n" + "=" * 60)
    print("DB Query Automation Tool")
    print("   Supports: SQLite, PostgreSQL, MySQL, MongoDB")
    print("=" * 60)

    print("\nSTEP 1: Enter your database connection string")
    print("   Examples:")
    print("     SQLite    : sqlite:///sample.db")
    print("     PostgreSQL: postgresql://user:pass@localhost:5432/mydb")
    print("     MySQL     : mysql+pymysql://user:pass@localhost:3306/mydb")
    print("     MongoDB   : mongodb://user:pass@localhost:27017/mydb")
    print("     MongoDB Atlas: mongodb+srv://user:pass@cluster.mongodb.net/mydb")
 
    conn_str = input("\n  > Connection string: ").strip()
    if not conn_str:
        print("No connection string provided. Exiting.")
        sys.exit(1)
 
    # ── Step 2: Connect ─────────────────────────────────────────────
    print("\nSTEP 2: Connecting...")
    try:
        connector = get_connector(conn_str)
        connector.connect()
    except Exception as e:
        print(f"Could not connect: {e}")
        sys.exit(1)
 
    # ── Step 3: List available tables/collections ────────────────────
    print("\nSTEP 3: Available tables / collections:")
    try:
        tables = connector.list_tables_or_collections()
        if not tables:
            print("No tables or collections found in this database.")
            connector.close()
            sys.exit(0)
 
        for i, t in enumerate(tables, 1):
            print(f"     [{i}] {t}")
    except Exception as e:
        print(f"Could not list tables: {e}")
        connector.close()
        sys.exit(1)

    print("\nSTEP 4: Which table/collection do you want to fetch?")
    print("   (Enter name exactly, or press Enter to fetch ALL)")
    choice = input("  > ").strip()
 
    selected = [choice] if choice else tables
 
    filters = {}
    if choice:
        print("\nSTEP 5: Optional filters (press Enter to skip)")
        print("   JSON format  : {\"age\": 25, \"city\": \"Pune\"}")
        print("   Simple format: age=25,city=Pune")
        raw_filter = input("  > Filter: ").strip()
        filters = parse_filter_input(raw_filter)
        if filters:
            print(f"     Applied filter: {filters}")

    print("\nSTEP 6: Fetching data and exporting to CSV...\n")
    os.makedirs("output", exist_ok=True)
 
    for table in selected:
        print(f"Processing: {table}")
        try:
            df = connector.fetch_data(table, filters if len(selected) == 1 else {})
 
            if df.empty:
                print(f"No data found in '{table}'\n")
                continue

            safe_name = re.sub(r"[^\w\-_]", "_", table)
            output_path = os.path.join("output", f"{safe_name}.csv")
 
            connector.export_to_csv(df, output_path)
 
            print(f"\n     Preview (first 3 rows):")
            print(df.head(3).to_string(index=False))
            print()
 
        except Exception as e:
            print(f"Error fetching '{table}': {e}\n")
 
    connector.close()
    print("\n✅ Done! Check the 'output/' folder for your CSV files.")
    print("=" * 60 + "\n")
 
if __name__ == "__main__":
    main()
            
    