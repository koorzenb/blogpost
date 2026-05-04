"""
Script to manually create database tables
Run this if you want to create tables in PostgreSQL manually
"""
from main import app, db

with app.app_context():
    print("Creating all database tables...")
    db.create_all()
    print("✓ Tables created successfully!")
    
    # Optional: Print table names
    from sqlalchemy import inspect
    inspector = inspect(db.engine)
    tables = inspector.get_table_names()
    print(f"✓ Tables in database: {', '.join(tables)}")
