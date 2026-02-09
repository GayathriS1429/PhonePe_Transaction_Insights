import pandas as pd
from db_config import get_connection

# -----------------------------------
# Helper function to load CSV to MySQL
# -----------------------------------
def load_csv_to_mysql(csv_path, table_name, columns):
    df = pd.read_csv(csv_path)

    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("USE phonepe_db")

    placeholders = ", ".join(["%s"] * len(columns))
    column_names = ", ".join(columns)

    insert_query = f"""
    INSERT INTO {table_name} ({column_names})
    VALUES ({placeholders})
    """

    for _, row in df.iterrows():
        cursor.execute(insert_query, tuple(row[col] for col in columns))

    conn.commit()
    cursor.close()
    conn.close()

    print(f"✅ Loaded data into {table_name}")


# -----------------------------------
# AGGREGATED TABLES
# -----------------------------------

load_csv_to_mysql(
    "dataframes/aggregated_transaction.csv",
    "aggregated_transaction",
    ["State", "Year", "Quarter", "Transaction_Type",
     "Transaction_Count", "Transaction_Amount"]
)

load_csv_to_mysql(
    "dataframes/aggregated_insurance.csv",
    "aggregated_insurance",
    ["State", "Year", "Quarter",
     "Insurance_Count", "Insurance_Amount"]
)

load_csv_to_mysql(
    "dataframes/aggregated_user.csv",
    "aggregated_user",
    ["State", "Year", "Quarter",
     "User_Device", "User_Count", "User_Share"]
)

# -----------------------------------
# MAP TABLES
# -----------------------------------

load_csv_to_mysql(
    "dataframes/map_transaction.csv",
    "map_transaction",
    ["State", "Year", "Quarter",
     "District", "Transaction_Count", "Transaction_Amount"]
)

load_csv_to_mysql(
    "dataframes/map_insurance.csv",
    "map_insurance",
    ["State", "Year", "Quarter",
     "District", "Insurance_Count", "Insurance_Amount"]
)

load_csv_to_mysql(
    "dataframes/map_user.csv",
    "map_user",
    ["State", "Year", "Quarter",
     "District", "User_Count"]
)

# -----------------------------------
# TOP TABLES
# -----------------------------------

load_csv_to_mysql(
    "dataframes/top_transaction.csv",
    "top_transaction",
    ["State", "Year", "Quarter",
     "District", "Transaction_Count", "Transaction_Amount"]
)

load_csv_to_mysql(
    "dataframes/top_insurance.csv",
    "top_insurance",
    ["State", "Year", "Quarter",
     "District", "Insurance_Count", "Insurance_Amount"]
)

load_csv_to_mysql(
    "dataframes/top_user.csv",
    "top_user",
    ["State", "Year", "Quarter",
     "District", "Registered_Users"]
)

print("🎉 ALL CSV FILES LOADED SUCCESSFULLY INTO MYSQL")
