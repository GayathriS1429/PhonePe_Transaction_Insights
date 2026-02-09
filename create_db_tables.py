from db_config import get_connection

conn = get_connection()
cursor = conn.cursor()

# -------------------------------
# Create Database
# -------------------------------
cursor.execute("CREATE DATABASE IF NOT EXISTS phonepe_db")
cursor.execute("USE phonepe_db")

# -------------------------------
# AGGREGATED TABLES
# -------------------------------

# aggregated_transaction
cursor.execute("""
CREATE TABLE IF NOT EXISTS aggregated_transaction (
    State VARCHAR(100),
    Year INT,
    Quarter INT,
    Transaction_Type VARCHAR(100),
    Transaction_Count BIGINT,
    Transaction_Amount DOUBLE
)
""")

# aggregated_insurance
cursor.execute("""
CREATE TABLE IF NOT EXISTS aggregated_insurance (
    State VARCHAR(100),
    Year INT,
    Quarter INT,
    Insurance_Count BIGINT,
    Insurance_Amount DOUBLE
)
""")

# aggregated_user
cursor.execute("""
CREATE TABLE IF NOT EXISTS aggregated_user (
    State VARCHAR(100),
    Year INT,
    Quarter INT,
    User_Device VARCHAR(100),
    User_Count BIGINT,
    User_Share DOUBLE
)
""")

# -------------------------------
# MAP TABLES
# -------------------------------

# map_transaction
cursor.execute("""
CREATE TABLE IF NOT EXISTS map_transaction (
    State VARCHAR(100),
    Year INT,
    Quarter INT,
    District VARCHAR(100),
    Transaction_Count BIGINT,
    Transaction_Amount DOUBLE
)
""")

# map_insurance
cursor.execute("""
CREATE TABLE IF NOT EXISTS map_insurance (
    State VARCHAR(100),
    Year INT,
    Quarter INT,
    District VARCHAR(100),
    Insurance_Count BIGINT,
    Insurance_Amount DOUBLE
)
""")

# map_user
cursor.execute("""
CREATE TABLE IF NOT EXISTS map_user (
    State VARCHAR(100),
    Year INT,
    Quarter INT,
    District VARCHAR(100),
    User_Count BIGINT
)
""")

# -------------------------------
# TOP TABLES
# -------------------------------

# top_transaction
cursor.execute("""
CREATE TABLE IF NOT EXISTS top_transaction (
    State VARCHAR(100),
    Year INT,
    Quarter INT,
    District VARCHAR(100),
    Transaction_Count BIGINT,
    Transaction_Amount DOUBLE
)
""")

# top_insurance
cursor.execute("""
CREATE TABLE IF NOT EXISTS top_insurance (
    State VARCHAR(100),
    Year INT,
    Quarter INT,
    District VARCHAR(100),
    Insurance_Count BIGINT,
    Insurance_Amount DOUBLE
)
""")

# top_user
cursor.execute("""
CREATE TABLE IF NOT EXISTS top_user (
    State VARCHAR(100),
    Year INT,
    Quarter INT,
    District VARCHAR(100),
    Registered_Users BIGINT
)
""")

# -------------------------------
# Commit & Close
# -------------------------------
conn.commit()
cursor.close()
conn.close()

print("✅ phonepe_db and all 9 tables created successfully")
