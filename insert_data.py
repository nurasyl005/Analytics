import pandas as pd
from sqlalchemy import create_engine

# ✅ Step 1: Create the DB engine (connection)
engine = create_engine("postgresql://alimbeknurasyl@localhost/screen_time_db")

# ✅ Step 2: Read the CSV
df = pd.read_csv("/Users/alimbeknurasyl/Desktop/projects/Analytics/screen_time.csv")

# ✅ Step 3: Clean column names
df.columns = ['age', 'gender', 'screen_time_type', 'day_type', 'avg_screen_time', 'sample_size']

# ✅ Step 4: Insert into database
df.to_sql("screen_time", engine, if_exists="replace", index=False)

print("✅ Data inserted successfully into PostgreSQL!")