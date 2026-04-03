from pymongo import MongoClient
from datetime import datetime

MONGO_URI = "mongodb://localhost:27017"
DB_NAME   = "sample_nosql_db"


CUSTOMERS = [
    {
        "name": "Aarav Shah",
        "email": "aarav@example.com",
        "age": 29,
        "city": "Pune",
        "is_premium": True,
        "tags": ["tech", "gadgets"]
    },
    {
        "name": "Priya Mehta",
        "email": "priya@example.com",
        "age": 34,
        "city": "Mumbai",
        "is_premium": False,
        "tags": ["fashion", "travel"]
    },
    {
        "name": "Rohan Kulkarni",
        "email": "rohan@example.com",
        "age": 27,
        "city": "Bangalore",
        "is_premium": True,
        "tags": ["gaming", "tech"]
    },
    {
        "name": "Sneha Patil",
        "email": "sneha@example.com",
        "age": 31,
        "city": "Delhi",
        "is_premium": False,
        "tags": ["books", "music"]
    },
]

ORDERS = [
    {
        "order_id": "ORD-001",
        "customer_email": "aarav@example.com",
        "product": "Laptop Pro 15",
        "quantity": 1,
        "total": 89999,
        "status": "delivered",
        "ordered_at": "2024-01-15"
    },
    {
        "order_id": "ORD-002",
        "customer_email": "priya@example.com",
        "product": "Wireless Mouse",
        "quantity": 2,
        "total": 2598,
        "status": "shipped",
        "ordered_at": "2024-02-20"
    },
    {
        "order_id": "ORD-003",
        "customer_email": "rohan@example.com",
        "product": "Noise Cancel Earphones",
        "quantity": 1,
        "total": 15999,
        "status": "processing",
        "ordered_at": "2024-03-05"
    },
]

INVENTORY = [
    {"sku": "TECH-001", "name": "Laptop Pro 15",    "stock": 45, "warehouse": "Pune",   "reorder_at": 10},
    {"sku": "ACC-001",  "name": "Wireless Mouse",   "stock": 200,"warehouse": "Mumbai", "reorder_at": 50},
    {"sku": "AUD-001",  "name": "Earphones NC",     "stock": 150,"warehouse": "Pune",   "reorder_at": 30},
]


def seed_mongodb():
    print(f"Connecting to MongoDB at {MONGO_URI}...")
    try:
        client = MongoClient(MONGO_URI)
        client.admin.command("ping")
        print("Connected!")
    except Exception as e:
        print(f"Could not connect: {e}")
        print("Make sure MongoDB is running: mongod --dbpath /data/db")
        return

    db = client[DB_NAME]

    # Drop existing collections to start fresh
    for col in ["customers", "orders", "inventory"]:
        db[col].drop()

    db.customers.insert_many(CUSTOMERS)
    db.orders.insert_many(ORDERS)
    db.inventory.insert_many(INVENTORY)

    print(f"\nMongoDB seeded: database='{DB_NAME}'")
    print(f"   Collections: customers ({len(CUSTOMERS)} docs)")
    print(f"               orders    ({len(ORDERS)} docs)")
    print(f"               inventory ({len(INVENTORY)} docs)")
    print(f"\n▶  Now run: python db_connector.py")
    print(f"   Use connection string: mongodb://localhost:27017/{DB_NAME}")

    client.close()


if __name__ == "__main__":
    seed_mongodb()