from flask import Flask, render_template, request, redirect, url_for, session, jsonify, send_file, current_app
from flask_login import LoginManager, UserMixin, login_user, login_required, current_user, logout_user
import psycopg2
from werkzeug.utils import secure_filename
import os 
from datetime import datetime
import logging
# import traceback
from flask import send_from_directory
from datetime import datetime, timedelta
from datetime import date


app = Flask(__name__)
app.secret_key = 'mansi'  # For session management
app.config["SESSION_PERMANENT"] = True 

login_manager = LoginManager()
# login_manager.login_view = 'signin'
login_manager.init_app(app)

UPLOAD_FOLDER = "static/uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER

ALLOWED_EXTENSIONS = {"pdf", "jpg", "jpeg", "png", "doc", "docx"}
def allowed_file(filename):
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS
# Database configuration
db_config = {
    "host": "localhost",
    "database": "HRM",
    "user": "postgres",
    "password": "03130903",
    "port": "5432",
}

# Function to create a database connection
def get_db_connection():
    try:
        conn = psycopg2.connect(
            host=db_config["host"],
            database=db_config["database"],
            user=db_config["user"],
            password=db_config["password"],
            port=db_config["port"],
        )
        return conn
    except Exception as e:
        print(f"Database connection error: {e}")
        return None
