"""
One-time helper to load database/schema.sql and database/seed_data.sql into
MySQL using the same mysql-connector-python driver the app already uses -
no mysql.exe / PATH setup needed.

Usage:
    python setup_db.py

This is safe to re-run - schema.sql drops and recreates every table itself.
"""

import mysql.connector
from config.config import DB_CONFIG


def run_sql_file(cursor, path):
    with open(path, "r", encoding="utf-8") as f:
        lines = f.readlines()
   
    cleaned = [line for line in lines if not line.strip().startswith("--")]
    sql = "".join(cleaned)
    statements = [s.strip() for s in sql.split(";") if s.strip()]
    for stmt in statements:
        cursor.execute(stmt)


def main():
    
    conn = mysql.connector.connect(
        host=DB_CONFIG["host"],
        port=DB_CONFIG["port"],
        user=DB_CONFIG["user"],
        password=DB_CONFIG["password"],
    )
    cursor = conn.cursor()

    print("Running database/schema.sql ...")
    run_sql_file(cursor, "database/schema.sql")
    conn.commit()

    print("Running database/seed_data.sql ...")
    run_sql_file(cursor, "database/seed_data.sql")
    conn.commit()

    cursor.close()
    conn.close()
    print("Done! Database and tables are ready - you can now run main.py")
    print("Login with: admin / admin123")


if __name__ == "__main__":
    main()
