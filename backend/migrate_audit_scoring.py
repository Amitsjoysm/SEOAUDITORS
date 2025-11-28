"""Migration script to add scoring columns to audits table"""
import sqlite3
import os

db_path = os.path.join(os.path.dirname(__file__), 'mjseo.db')

conn = sqlite3.connect(db_path)
cursor = conn.cursor()

try:
    # Try to add columns (will fail if they already exist)
    try:
        cursor.execute("ALTER TABLE audits ADD COLUMN potential_score FLOAT")
        print("✓ Added potential_score column")
    except sqlite3.OperationalError as e:
        if 'duplicate column' in str(e).lower():
            print("✓ potential_score column already exists")
        else:
            raise
    
    try:
        cursor.execute("ALTER TABLE audits ADD COLUMN score_grade VARCHAR")
        print("✓ Added score_grade column")
    except sqlite3.OperationalError as e:
        if 'duplicate column' in str(e).lower():
            print("✓ score_grade column already exists")
        else:
            raise
    
    try:
        cursor.execute("ALTER TABLE audits ADD COLUMN score_interpretation TEXT")
        print("✓ Added score_interpretation column")
    except sqlite3.OperationalError as e:
        if 'duplicate column' in str(e).lower():
            print("✓ score_interpretation column already exists")
        else:
            raise
    
    try:
        cursor.execute("ALTER TABLE audits ADD COLUMN category_scores JSON")
        print("✓ Added category_scores column")
    except sqlite3.OperationalError as e:
        if 'duplicate column' in str(e).lower():
            print("✓ category_scores column already exists")
        else:
            raise
    
    try:
        cursor.execute("ALTER TABLE audits ADD COLUMN analytics_summary JSON")
        print("✓ Added analytics_summary column")
    except sqlite3.OperationalError as e:
        if 'duplicate column' in str(e).lower():
            print("✓ analytics_summary column already exists")
        else:
            raise
    
    conn.commit()
    print("\n✅ Database migration completed successfully!")
    
except Exception as e:
    conn.rollback()
    print(f"\n❌ Migration failed: {e}")
    raise

finally:
    conn.close()
