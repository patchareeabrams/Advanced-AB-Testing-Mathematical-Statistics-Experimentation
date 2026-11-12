"""Create a SQLite database from the CSV for SQL analysis."""
from pathlib import Path
import sqlite3
import pandas as pd
root = Path(__file__).resolve().parents[1]
df = pd.read_csv(root / "data" / "experiment.csv")
with sqlite3.connect(root / "data" / "experiment.db") as conn:
    df.to_sql("experiment", conn, if_exists="replace", index=False)
    print(pd.read_sql_query("SELECT variant, COUNT(*) AS users, AVG(converted) AS conversion_rate FROM experiment GROUP BY variant", conn))
