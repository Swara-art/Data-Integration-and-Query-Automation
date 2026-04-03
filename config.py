{
  "profiles": {

    "sqlite_local": {
      "description": "Local SQLite file — no server needed, great for testing",
      "connection_string": "sqlite:///sample.db",
      "notes": "File will be created at ./sample.db if it doesn't exist"
    },

    "postgresql": {
      "description": "PostgreSQL server",
      "connection_string": "postgresql://YOUR_USER:YOUR_PASSWORD@localhost:5432/YOUR_DB",
      "notes": "Install psycopg2: pip install psycopg2-binary"
    },

    "mysql": {
      "description": "MySQL / MariaDB server",
      "connection_string": "mysql+pymysql://YOUR_USER:YOUR_PASSWORD@localhost:3306/YOUR_DB",
      "notes": "Install pymysql: pip install pymysql"
    },

    "mongodb_local": {
      "description": "Local MongoDB instance",
      "connection_string": "mongodb://localhost:27017/YOUR_DB_NAME",
      "notes": "Requires MongoDB running locally; install pymongo: pip install pymongo"
    },

    "mongodb_atlas": {
      "description": "MongoDB Atlas cloud cluster",
      "connection_string": "mongodb+srv://YOUR_USER:YOUR_PASSWORD@cluster0.abc123.mongodb.net/YOUR_DB",
      "notes": "Get this string from Atlas UI → Connect → Drivers"
    }

  },

  "active_profile": "sqlite_local"
}