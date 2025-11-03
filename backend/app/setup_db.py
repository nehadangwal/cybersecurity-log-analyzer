# Create this new file in your backend directory
from __init__ import create_app, db
import os

app = create_app()

# This is a one-off command to ensure tables exist
with app.app_context():
    # Only run the create_all function
    #db.create_all() 
    print("Database tables created successfully!")