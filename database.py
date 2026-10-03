import sqlite3
import hashlib
import json
import os
from typing import Optional, List, Dict, Any

DB_FILE = "autoinsight_history.db"

def get_db_connection() -> sqlite3.Connection:
    conn = sqlite3.connect(DB_FILE)
    conn.row_factory = sqlite3.Row
    return conn

def init_db() -> None:
    """Initializes SQLite database tables for users and analysis history."""
    with get_db_connection() as conn:
        cursor = conn.cursor()
        
        # User Authentication Table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                email TEXT UNIQUE NOT NULL,
                password_hash TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Analysis Session History Table (Isolated by user email)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS analysis_history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_email TEXT NOT NULL,
                file_name TEXT NOT NULL,
                data_summary_json TEXT NOT NULL,
                executive_report TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_email) REFERENCES users (email)
            )
        """)
        conn.commit()

def hash_password(password: str) -> str:
    """Computes SHA-256 hash of a plain text password with salt."""
    salt = "AutoInsight_Secure_Salt_2026"
    return hashlib.sha256((password + salt).encode("utf-8")).hexdigest()

def register_user(email: str, password: str) -> bool:
    """Registers a new user into SQLite database."""
    email_clean = email.strip().lower()
    pwd_hash = hash_password(password)
    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "INSERT INTO users (email, password_hash) VALUES (?, ?)",
                (email_clean, pwd_hash)
            )
            conn.commit()
            return True
    except sqlite3.IntegrityError:
        return False

def authenticate_user(email: str, password: str) -> bool:
    """Validates user credentials against stored hash."""
    email_clean = email.strip().lower()
    pwd_hash = hash_password(password)
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(
            "SELECT id FROM users WHERE email = ? AND password_hash = ?",
            (email_clean, pwd_hash)
        )
        user = cursor.fetchone()
        return user is not None

def save_analysis_history(
    user_email: str,
    file_name: str,
    data_summary: Dict[str, Any],
    executive_report: str
) -> int:
    """Saves completed dataset analysis report linked to user email."""
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(
            """
            INSERT INTO analysis_history (user_email, file_name, data_summary_json, executive_report)
            VALUES (?, ?, ?, ?)
            """,
            (
                user_email.strip().lower(),
                file_name,
                json.dumps(data_summary),
                executive_report
            )
        )
        conn.commit()
        return cursor.lastrowid

def get_user_history(user_email: str) -> List[Dict[str, Any]]:
    """Retrieves all past dataset analyses for a specific user."""
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(
            """
            SELECT id, file_name, data_summary_json, executive_report, created_at
            FROM analysis_history
            WHERE user_email = ?
            ORDER BY created_at DESC
            """,
            (user_email.strip().lower(),)
        )
        rows = cursor.fetchall()
        
        history = []
        for row in rows:
            history.append({
                "id": row["id"],
                "file_name": row["file_name"],
                "data_summary": json.loads(row["data_summary_json"]),
                "executive_report": row["executive_report"],
                "created_at": row["created_at"]
            })
        return history

# Initialize database schema upon execution
init_db()
