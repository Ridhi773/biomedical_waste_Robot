"""
Handles the MySQL connection for the whole app.
Uses a single shared connection (simple singleton), matching a desktop-app scale project.
"""

import mysql.connector
from mysql.connector import Error
from config.config import DB_CONFIG

_connection = None


def get_connection():
    """Return a live MySQL connection, opening one if needed."""
    global _connection
    if _connection is None or not _connection.is_connected():
        try:
            _connection = mysql.connector.connect(
                host=DB_CONFIG["host"],
                port=DB_CONFIG["port"],
                user=DB_CONFIG["user"],
                password=DB_CONFIG["password"],
                database=DB_CONFIG["database"],
            )
        except Error as e:
            raise ConnectionError(f"Could not connect to MySQL: {e}")
    return _connection


def execute_query(query, params=None, fetch=False, fetchone=False):
    """
    Run a query and optionally fetch results.
    fetch=True     -> returns list of dict rows
    fetchone=True  -> returns a single dict row (or None)
    otherwise      -> commits and returns the cursor.lastrowid (for INSERTs)
    """
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    try:
        cursor.execute(query, params or ())
        if fetch:
            return cursor.fetchall()
        if fetchone:
            return cursor.fetchone()
        conn.commit()
        return cursor.lastrowid
    finally:
        cursor.close()


def close_connection():
    global _connection
    if _connection is not None and _connection.is_connected():
        _connection.close()
        _connection = None
