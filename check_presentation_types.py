#!/usr/bin/env python3

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'backend'))

from app.db.session import SessionLocal
from sqlalchemy import text

db = SessionLocal()
try:
    # Check if table exists and get all assignments
    result = db.execute(text("SELECT * FROM presentation_assignments"))
    rows = result.fetchall()
    if rows:
        print("Found presentation assignments:")
        for row in rows:
            print(f"ID: {row[0]}, Title: {row[3]}, Student ID: {row[1]}, Assigned by: {row[2]}")
    else:
        print("No presentation assignments found")
except Exception as e:
    print(f"Error accessing presentation_assignments table: {e}")
    # Check if table exists
    try:
        result = db.execute(text("SELECT tablename FROM pg_tables WHERE tablename = 'presentation_assignments'"))
        if result.fetchone():
            print("Table exists but may be empty")
        else:
            print("Table does not exist")
    except Exception as e2:
        print(f"Error checking table existence: {e2}")
finally:
    db.close()