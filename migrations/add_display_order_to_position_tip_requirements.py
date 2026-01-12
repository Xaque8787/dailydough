from sqlalchemy import text
from app.database import engine

def migrate():
    with engine.connect() as conn:
        conn.execute(text("""
            ALTER TABLE position_tip_requirements
            ADD COLUMN IF NOT EXISTS display_order INTEGER DEFAULT 0;
        """))
        conn.commit()
        print("Added display_order column to position_tip_requirements table")

if __name__ == "__main__":
    migrate()
