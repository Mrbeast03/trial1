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

class User(UserMixin):
    def __init__(self, emp_id, first_name, last_name, email, photo=None):
        self.emp_id = emp_id
        self.first_name = first_name
        self.last_name = last_name
        self.email = email
        self.photo = photo

    def get_id(self):
        return str(self.emp_id)

@login_manager.user_loader
def load_user(emp_id):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT emp_id, first_name, last_name, email, photo FROM employee WHERE emp_id = %s", (emp_id,))
    user_data = cursor.fetchone()
    cursor.close()
    conn.close()

    if user_data:
        print(f"Loaded User: {user_data}")
        return User(*user_data)  # Create and return a User instance
    return None

@app.route("/", methods=["GET"])
def welcome():
    return render_template("welcome.html")

@app.route("/signin", methods=["GET", "POST"])
def signin():
    if request.method == "POST":
        data = request.get_json()
        email = data.get("email")
        password = data.get("password")

        if not email or not password:
            return jsonify({"success": False, "message": "Email and password are required!"}), 400

        try:
            conn = get_db_connection()
            if not conn:
                return jsonify({"success": False, "message": "Unable to connect to the database."}), 500

            cursor = conn.cursor()
            cursor.execute("SELECT emp_id, first_name, last_name, email, photo FROM employee WHERE email = %s AND password = %s", (email, password))
            user = cursor.fetchone()
           

            if user:
                emp_id = user[0] 
                session["email"] = email  # Store email in session
                session["emp_id"] = user[0]  # Store emp_id in session
                user_obj = User(*user)  # Create User object
                login_user(user_obj)  # Log in user using Flask-Login
                # Capture current time in 12-hour format
                checkin_time = datetime.now().strftime("%I:%M %p")  
                
                # Insert check-in time into logs table
                cursor.execute("""
                    INSERT INTO logs (emp_id, date, checkin) 
                    VALUES (%s, CURRENT_DATE, %s) 
                    ON CONFLICT (emp_id, date)
                    DO UPDATE SET checkin = EXCLUDED.checkin;
                """, (emp_id, checkin_time))

                conn.commit()
                cursor.close()
                conn.close()
                return jsonify({"success": True, "message": "Sign-in successful!"}), 200
            else:
                cursor.close()
                conn.close()
                return jsonify({"success": False, "message": "Invalid credentials!"}), 401
        except Exception as e:
            return jsonify({"success": False, "message": f"Error: {str(e)}"}), 500
    
    return render_template("signin.html")

@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        first_name = request.form.get("first_name")
        last_name = request.form.get("last_name")
        email = request.form.get("email")
        phone = request.form.get("phone")
        password = request.form.get("password")
        confirm_password = request.form.get("confirm_password")
        date_of_birth = request.form.get("date_of_birth")
        address = request.form.get("address")
        photo = request.files.get("photo")
        resume = request.files.get("resume_path")

        if not all([first_name.strip(), last_name.strip(), email.strip(), phone.strip(), password.strip(), confirm_password.strip(), date_of_birth.strip(), address.strip()]) or not (photo and resume and photo.filename.strip() and resume.filename.strip()):
            return jsonify({"success": False, "message": "Please fill in all required fields."}), 400

        if password != confirm_password:
            return jsonify({"success": False, "message": "Passwords do not match!"}), 400

        try:
            photo_filename = os.path.join(app.config["UPLOAD_FOLDER"], secure_filename(photo.filename))
            resume_filename = os.path.join(app.config["UPLOAD_FOLDER"], secure_filename(resume.filename))

            # Save the files
            photo.save(photo_filename)
            resume.save(resume_filename)

            conn = get_db_connection()
            cursor = conn.cursor()
            cursor.execute(
                """
                INSERT INTO employee (first_name, last_name, email, phone, password, date_of_birth, address, photo, resume_path)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
                """,
                (first_name, last_name, email, phone, password, date_of_birth, address, photo_filename, resume_filename),
            )
            conn.commit()
            cursor.close()
            conn.close()

            return jsonify({"success": True, "message": "Registration successful!"}), 200
        except Exception as e:
            return jsonify({"success": False, "message": "Internal Server Error. Please try again!"}), 500

    return render_template("register.html")

def get_user_profile(emp_id):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT photo FROM employee WHERE emp_id = %s", (emp_id,))
    result = cursor.fetchone()
    cursor.close()
    conn.close()
    return result[0] if result else None

@app.route('/profile_picture/<int:user_id>')
@login_required
def get_profile_picture(user_id):
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("SELECT photo FROM employee WHERE emp_id = %s", (user_id,))
    result = cur.fetchone()
    cur.close()
    conn.close()

    if result and result[0]:
        return send_file(result[0], mimetype='image/jpeg')  # If image is stored as path
    else:
        return send_file('static/default_profile.png', mimetype='image/png')  # Default image

@app.after_request
def prevent_cache(response):
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Pragma"] = "no-cache"
    response.headers["Expires"] = "0"
    return response

@app.route("/dashboard", methods=["GET"])
@login_required
def dashboard():
    if "email" not in session:  # If email not in session, force sign-in
        return redirect(url_for("signin"))
    
    emp_id = current_user.get_id()  # Use current_user to fetch the emp_id
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("SELECT first_name, last_name, email, photo FROM employee WHERE emp_id = %s", (emp_id,))
    user_data = cur.fetchone()
    cur.close()
    conn.close()
    print(f"Current User Object: {current_user}")  
    print(f"Current User: {current_user}")  # Debugging
    print(f"First Name: {current_user.first_name}, Last Name: {current_user.last_name}")  # Debugging

    user_data = {
        "name": f"{current_user.first_name} {current_user.last_name}",
        "email": current_user.email,
        "photo_url": current_user.photo if current_user.photo else "static/default.jpg",
    } 
    # if not session.get('logged_in'):  # Check if user is logged in
    #     return redirect('/signin') 
    return render_template("dashboard.html", user_name=user_data["name"])

@app.route('/employee')
def employee():
    conn = psycopg2.connect(
        dbname="HRM", user="postgres", password="mansi", host="localhost", port="5432"
    )
    cursor = conn.cursor()

    # Fetch emp_id from session
    emp_id = session.get('emp_id')  # Assuming emp_id is stored in session
    if emp_id is None:
        return "Employee ID not found in session", 400
    if "email" not in session:  # If email not in session, force sign-in
        return redirect(url_for("signin"))

    # Execute query to fetch employee details
    cursor.execute("SELECT first_name, last_name, emp_id, date_of_birth, email, address FROM employee WHERE emp_id = %s", (emp_id,))
    employee_details = cursor.fetchone()

    # Close the database connection
    cursor.close()
    conn.close()

    # Debug: Print the employee details to the console
    print(employee_details)

    # Handling the case where data might be missing
    if employee_details:
        first_name, last_name, emp_id, date_of_birth, email, address = employee_details
        profile_name = f"{first_name} {last_name}"
    else:
       profile_name, first_name, last_name, emp_id, date_of_birth, email, address = ("N/A", "N/A", "N/A", "N/A", "N/A", "N/A", "N/A")

    return render_template('employee.html',  profile_name=profile_name, first_name=first_name, last_name=last_name, emp_id=emp_id, date_of_birth=date_of_birth, email=email, address=address)

@app.route('/update_employee', methods=['POST'])
@login_required
def update_employee():
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        data = request.json

        emp_id = session.get('emp_id') or current_user.get_id()
        email = data.get("email")
        address = data.get("address")
        phone = data.get("phone")
        emergency_number = data.get("emergency_number")
        gender = data.get("gender")


        print("Received Data:", data)  # Debugging line

        if not emp_id:  # If emp_id is missing, return an error
            return jsonify({"success": False, "error": "Employee ID is required!"})

        valid_genders = {"Male", "Female", "Other"}
        if not gender or gender not in valid_genders:
            return jsonify({"error": "Invalid gender selected!"}), 400

        # Update employee details in the database
        cursor.execute("SELECT * FROM employee WHERE emp_id = %s", (emp_id,))
        existing_record = cursor.fetchone()

        

        if existing_record:
            # Update existing record
            query = """
            UPDATE employee
            SET email = %s, address = %s, phone = %s, emergency_number = %s, gender = %s
            WHERE emp_id = %s
            """
            cursor.execute(query, (email, address, phone, emergency_number, gender, emp_id))
            print("Data updated successfully!")
        else:
            # Insert new record
            query = """ 
            INSERT INTO employee (emp_id, email , address , phone , emergency_number , gender)
            VALUES (%s,%s,%s,%s,%s,%s)
            """
            cursor.execute(query, (email, address, phone, emergency_number, gender, emp_id))
            print("Data inserted successfully!")

        conn.commit() 

        return jsonify({
            "message": "Financial details stored successfully!",
            "email": email,
            "address": address,
            "phone": phone,
            "emergency_number": emergency_number,
            "gender": gender,
        }), 200

    except Exception as e:
        conn.rollback()
        print("Error:", str(e))
        return jsonify({"error": str(e)}), 500

    finally:
        cursor.close()
        conn.close()
    
@app.route("/get_employee_details", methods=["GET"])
@login_required
def get_employee_details():
    emp_id = session.get('emp_id') 
    # data = request.json
    if not emp_id:
        return jsonify({"success": False, "message": "Employee ID not found in session."}), 400

    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT email, address, phone, emergency_number, gender FROM employee WHERE emp_id = %s", (emp_id,))
        employee = cursor.fetchone()
        cursor.close()
        conn.close() 
        if employee:
            employee_data = {
                "email": employee[0],
                "address": employee[1],
                "phone": employee[2],
                "emergency_number": employee[3],
                "gender": employee[4] if employee[4] else "Not Set"
            }
            return jsonify({"success": True, "employee": employee_data})
        else:
            return jsonify({"success": False, "message": "Employee details not found."}), 404

    except Exception as e:
        print(f"Error fetching employee details: {e}")
        return jsonify({"success": False, "message": str(e)}), 500


@app.route('/store_financial_detail', methods=['POST'])
@login_required
def store_financial_detail():
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        data = request.json  # Get JSON data from frontend

        emp_id = session.get('emp_id') or current_user.get_id()

        bank_name = data.get("bank_name")
        account_number = data.get("account_number")
        ifsc_code = data.get("ifsc_code")
        account_name = data.get("account_name")
        bank_address = data.get("bank_address")
        pincode = data.get("pincode")

        print("Received Data:", emp_id, bank_name, account_number, ifsc_code, account_name, bank_address, pincode)

        # Check if financial details exist
        cursor.execute("SELECT * FROM financial_detail WHERE emp_id = %s", (emp_id,))
        existing_record = cursor.fetchone()

        if existing_record:
            # Update existing record
            query = """
            UPDATE financial_detail 
            SET bank_name=%s, account_number=%s, ifsc_code=%s, account_name=%s, bank_address=%s, pincode=%s
            WHERE emp_id=%s
            """
            cursor.execute(query, (bank_name, account_number, ifsc_code, account_name, bank_address, pincode, emp_id))
            print("Data updated successfully!")
        else:
            # Insert new record
            query = """
            INSERT INTO financial_detail (emp_id, bank_name, account_number, ifsc_code, account_name, bank_address, pincode)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
            """
            cursor.execute(query, (emp_id, bank_name, account_number, ifsc_code, account_name, bank_address, pincode))
            print("Data inserted successfully!")

        conn.commit()

        # Return the updated data
        return jsonify({
            "message": "Financial details stored successfully!",
            "bank_name": bank_name,
            "account_number": account_number,
            "ifsc_code": ifsc_code,
            "account_name": account_name,
            "bank_address": bank_address,
            "pincode": pincode
        }), 200

    except Exception as e:
        conn.rollback()
        print("Error:", str(e))
        return jsonify({"error": str(e)}), 500

    finally:
        cursor.close()
        conn.close()

@app.route('/store_skills_interests', methods=['POST'])
@login_required
def store_skills_interests():
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        data = request.json
        emp_id = session.get('emp_id') or current_user.get_id()

        skills = data.get("skills", [])
        soft_skills = data.get("soft_skills", [])
        interests = data.get("interests", [])

        print("Received Data:", emp_id, skills, soft_skills, interests)

        cursor.execute("SELECT * FROM skillsandinterest WHERE emp_id = %s", (emp_id,))
        existing_record = cursor.fetchone()

        if existing_record:
            query = """
            UPDATE skillsandinterest
            SET skills= %s, soft_skills = %s, interests = %s
            WHERE emp_id= %s
            """
            cursor.execute(query, (skills, soft_skills, interests, emp_id))
            print("✅ Skills & Interests updated successfully!")
        else:
            query = """
            INSERT INTO skillsandinterest (emp_id, skills, soft_skills, interests)
            VALUES (%s, %s, %s, %s)
            """
            cursor.execute(query, (emp_id, skills, soft_skills, interests))
            print("✅ Skills & Interests inserted successfully!")
        conn.commit()

        return jsonify({"message": "Skills and Interests stored successfully!", "skills": skills, "soft_skills": soft_skills, "interests": interests}), 200

    except Exception as e:
        conn.rollback()
        return jsonify({"error": str(e)}), 500

    finally:
        cursor.close()
        conn.close()

@app.route('/get_financial_detail', methods=['GET'])
@login_required
def get_financial_detail():
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        emp_id = session.get('emp_id') or current_user.get_id()
        
        cursor.execute("SELECT bank_name, account_number, ifsc_code, account_name, bank_address, pincode FROM financial_detail WHERE emp_id = %s", (emp_id,))
        record = cursor.fetchone()
        
        if record:
            financial_data = {
                "bank_name": record[0],
                "account_number": record[1],
                "ifsc_code": record[2],
                "account_name": record[3],
                "bank_address": record[4],
                "pincode": record[5]
            }
        else:
            financial_data = {
                "bank_name": "Not provided",
                "account_number": "Not provided",
                "ifsc_code": "Not provided",
                "account_name": "Not provided",
                "bank_address": "Not provided",
                "pincode": "Not provided"
            }

        return jsonify(financial_data), 200

    except Exception as e:
        print("Error fetching financial details:", str(e))
        return jsonify({"error": str(e)}), 500

    finally:
        cursor.close()
        conn.close()



 

@app.route('/get_skills_interests', methods=['GET'])
@login_required
def get_skills_interests():
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        emp_id = session.get('emp_id') or current_user.get_id()

        cursor.execute("SELECT skills, soft_skills, interests FROM skillsandinterest WHERE emp_id = %s", (emp_id,))
        record = cursor.fetchone()
        if record:
            skills_data = {"skills": record[0], "soft_skills": record[1], "interests": record[2]}
        else:
            skills_data = {"skills": [], "soft_skills": [], "interests": []}
        
        return jsonify(skills_data), 200


        # print("Fetched Skills Data:", skills_data)
        # return jsonify(skills_data), 200

    except Exception as e:
        print("Error fetching skills and interests:", str(e))
        return jsonify({"error": str(e)}), 500

    finally:
        cursor.close()
        conn.close() 

@app.route('/store_social_links', methods=['POST'])
@login_required
def store_social_links():
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        data = request.json
        emp_id = session.get('emp_id') or current_user.get_id()
        linkedin = data.get("linkedin")
        github = data.get("github")
        twitter = data.get("twitter")

        cursor.execute("SELECT * FROM social WHERE emp_id = %s", (emp_id,))
        existing_record = cursor.fetchone()

        if existing_record:
            cursor.execute(
                """
                UPDATE social 
                SET linkedIn=%s, github=%s, twitter=%s 
                WHERE emp_id=%s
                """, (linkedin, github, twitter, emp_id)
            )
        else:
            cursor.execute(
                """
                INSERT INTO social (emp_id, linkedin, github, twitter) 
                VALUES (%s, %s, %s, %s)
                """, (emp_id, linkedin, github, twitter)
            )
        
        conn.commit()
        return jsonify({"message": "Social links stored successfully!"}), 200
    except Exception as e:
        conn.rollback()
        return jsonify({"error": str(e)}), 500
    finally:
        cursor.close()
        conn.close()

@app.route('/get_social_links', methods=['GET'])
@login_required
def get_social_links():
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        emp_id = session.get('emp_id') or current_user.get_id()
        cursor.execute("SELECT linkedin, github, twitter FROM social WHERE emp_id = %s", (emp_id,))
        record = cursor.fetchone()

        social_data = {
            "linkedin": record[0] if record else "Not provided",
            "github": record[1] if record else "Not provided",
            "twitter": record[2] if record else "Not provided"
        }
        return jsonify(social_data), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    finally:
        cursor.close()
        conn.close()



@app.route('/leave')
@login_required
def leave():
    return render_template('leave.html')
 

@app.route('/apply_leave', methods=['GET', 'POST'])
def apply_leave():
    if "email" not in session:  # If email not in session, force sign-in
        return redirect(url_for("signin"))
    if request.method == 'GET':
        return render_template('leave.html')
    elif request.method == 'POST':
        # Ensure user is logged in (assumes emp_id is stored in session)
        emp_id = session.get('emp_id')
        if not emp_id:
            return jsonify({"error": "User not logged in"}), 401
        
        # Get form data
        slot = request.form.get('slot')
        from_date = request.form.get('from_date')
        to_date = request.form.get('to_date')
        # For multiple selection, getlist() returns a list
        apply_to_list = request.form.getlist('apply_to')
        reason = request.form.get('reason')
        
        # Convert the notify-to list to a comma-separated string
        apply_to = ", ".join(apply_to_list) if apply_to_list else "None"
        
        # Process file attachment if provided
        document_file = request.files.get('document')
        document_filename = None
        if document_file and document_file.filename != '':
            if allowed_file(document_file.filename):
                document_filename = secure_filename(document_file.filename)
                file_path = os.path.join(app.config["UPLOAD_FOLDER"], document_filename)
                document_file.save(file_path)
            else:
                return jsonify({"error": "Invalid file type for attachment"}), 400
        
        # Insert the leave application into the database
        conn = get_db_connection()
        cur = conn.cursor()
        try:
            cur.execute("""
                INSERT INTO leave_applications (emp_id, slot, start_date, end_date, apply_to, reason, document_path, status)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
            """, (emp_id, slot, from_date, to_date, apply_to, reason, document_filename, "Pending"))
            conn.commit()
        except Exception as e:
            conn.rollback()
            return jsonify({"error": "Database error: " + str(e)}), 500
        finally:
            cur.close()
            conn.close()
        
        # Return the newly added leave application data as JSON
        return jsonify({
            "message": "Leave application submitted successfully!",
            "leave_application": {
                "slot": slot,
                "start_date": from_date,
                "end_date": to_date,
                "apply_to": apply_to,
                "reason": reason,
                "document_path": f"/static/uploads/{document_filename}" if document_filename else None,
                "status": "Pending"
            }
        }), 200

@app.route('/get_leave_applications', methods=['GET'])
def get_leave_applications():
    conn = get_db_connection()
    cur = conn.cursor()
    try:
        cur.execute("""
            SELECT slot, start_date, end_date, apply_to, reason, document_path, status 
            FROM leave_applications 
            ORDER BY leave_id desc
        """)
        apps = cur.fetchall()
        print(f"Fetched {len(apps)} leave applications from the database.")
    except Exception as e:
        return jsonify({"error": "Database error: " + str(e)}), 500
    finally:
        cur.close()
        conn.close()
    
    result = []
    for app_row in apps:
        # Format dates as strings if they are date objects
        start_date = app_row[1].strftime('%Y-%m-%d') if hasattr(app_row[1], 'strftime') else app_row[1]
        end_date = app_row[2].strftime('%Y-%m-%d') if hasattr(app_row[2], 'strftime') else app_row[2]
        result.append({
            "slot": app_row[0],
            "start_date": start_date,
            "end_date": end_date,
            "apply_to": app_row[3],
            "reason": app_row[4],
            "document_path": f"/static/uploads/{app_row[5]}" if app_row[5] else None,
            "status": app_row[6]
        })
    return jsonify({"leave_applications": result})


@app.route('/invoice')
def invoice():
    if "email" not in session:  # If email not in session, force sign-in
        return redirect(url_for("signin"))
    return render_template('invoice.html')



@app.route('/upload_invoice', methods=['POST'])
def upload_invoice():
    print("Received request to upload invoice")

    # Fetch logged-in employee ID from session
    emp_id = session.get('emp_id')  # Assuming employee ID is stored in session

    if not emp_id:
        print("Employee ID not found in session")
        return jsonify({"error": "User not logged in"}), 401  # Unauthorized

    if 'invoice_doc' not in request.files:
        print("No file uploaded")
        return jsonify({"error": "No file uploaded"}), 400

    file = request.files['invoice_doc']

    if file.filename == '':
        print("No file selected")
        return jsonify({"error": "No selected file"}), 400
    if not allowed_file(file.filename):
        print("Invalid file type")
        return jsonify({"error": "Invalid file type. Allowed types: pdf, docx, doc, jpg, jpeg, png"}), 400

    filename = secure_filename(file.filename)
    file_path = os.path.join(app.config["UPLOAD_FOLDER"], filename)
    file.save(file_path)

    conn = get_db_connection()
    cur = conn.cursor()

    now = datetime.now()
    today = now.strftime('%Y-%m-%d')  # YYYY-MM-DD
    current_time = now.strftime('%H:%M:%S')  # HH:MM:SS
    month = now.month
    month_name = now.strftime('%B')  # Get full month name (e.g., "February")
    year = now.year

    try:
        cur.execute("""
            INSERT INTO invoice (emp_id, invoice_doc, date, month, year) 
            VALUES (%s, %s, %s, %s, %s)
        """, (emp_id, filename, today, month, year))

        conn.commit()
        print("Data inserted successfully")

    except Exception as e:
        print(f"Database Error: {e}")
        conn.rollback()
        return jsonify({"error": "Database error"}), 500
    finally:
        cur.close()
        conn.close()

    return jsonify({
        "message": "Invoice uploaded successfully!",
        "file_path": f"/static/uploads/{filename}",
        "date": today,
        "time": current_time,
        "month": month_name,  # Send full month name instead of number
        "year": year
    }), 200

@app.route('/get_invoices', methods=['GET'])
def get_invoices():
    conn = get_db_connection()
    cur = conn.cursor()

    cur.execute("SELECT date, month, year, invoice_doc FROM invoice ORDER BY date DESC")
    invoices = cur.fetchall()
    cur.close()
    conn.close()

    # Convert month number to month name
    result = []
    for i in invoices:
        date_str = i[0].strftime('%Y-%m-%d')  # Convert date to string
        month_number = int(i[1])
        month_name = datetime.strptime(str(month_number), "%m").strftime("%B")  # Convert to full month name
        result.append({
            "date": date_str,
            "month": month_name,  # Now it's the full month name
            "year": i[2],
            "file_path": f"/static/uploads/{i[3]}"  # Ensure correct path
        })

    return jsonify(result)


@app.route('/contact')
def contact():
    if "email" not in session:  # If email not in session, force sign-in
        return redirect(url_for("signin"))
    return render_template('contact.html')


@app.route('/expense')
def expense():
    if "email" not in session:  # If email not in session, force sign-in
        return redirect(url_for("signin"))
    return render_template('expense.html')

@app.route("/get_emp_id", methods=["GET"])
def get_emp_id():
    emp_id = session.get("emp_id")
    if emp_id:
        return jsonify({"emp_id": emp_id}), 200
    else:
        return jsonify({"error": "User not logged in"}), 401

VALID_CATEGORIES = {"travel", "medical", "food", "general"}  
@app.route("/add_expense", methods=["POST"])
def add_expense():
    try:
        emp_id = request.form.get("emp_id")
        category = request.form.get("category")
        description = request.form.get("description")
        amount = request.form.get("amount")
        file = request.files.get("proof")

        if not all([emp_id, category, description, amount]):
            return jsonify({"error": "Missing required fields"}), 400

        proof_path = "No File"
        if file:
            file_path = os.path.join(app.config["UPLOAD_FOLDER"], file.filename)
            file.save(file_path)
            proof_path = file_path

        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute(
            "INSERT INTO expense (emp_id, category, description, amount, proof) VALUES (%s, %s, %s, %s, %s) RETURNING exp_id",
            (emp_id, category, description, amount, proof_path)
        )
        exp_id = cur.fetchone()[0]
        conn.commit()
        cur.close()
        conn.close()

        return jsonify({"message": "Expense added successfully!", "exp_id": exp_id}), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500

# Fetch Expenses (GET)
@app.route("/get_expenses", methods=["GET"])
def get_expenses():
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute("SELECT category, description, amount, proof FROM expense")
        expenses = cur.fetchall()
        cur.close()
        conn.close()

        expense_list = [
            {"category": e[0], "description": e[1], "amount": e[2], "proof": e[3]}
            for e in expenses
        ]
        return jsonify(expense_list), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500
    
@app.route('/get_employees', methods=['GET'])
def get_employees():
    conn = get_db_connection()
    cur = conn.cursor()

    # Fetching name, email, phone from employee table
    # cur.execute("SELECT first_name, email, phone FROM employee")
    # employees = cur.fetchall()
    query = """
    SELECT e.first_name, e.email, e.phone, s.linkedin,  s.twitter
    FROM employee e
    LEFT JOIN social s ON e.emp_id = s.emp_id
    """
    cur.execute(query)
    employees = cur.fetchall()

    cur.close()
    conn.close()

    # Convert to JSON format
    # employee_list = [{"first_name": emp[0], "email": emp[1], "phone": emp[2]} for emp in employees]
    employee_list = [
        {
            "first_name": emp[0],
            "email": emp[1],
            "phone": emp[2],
            "linkedin": emp[3],
            # "github": emp[4],
            "twitter": emp[4],
        }
        for emp in employees
    ]
    return jsonify(employee_list)


@app.route('/attendance')
def attendance():
    return render_template('attendance.html') 

# #@app.route('/store-login-time', methods=['POST'])
def store_login_time():
    if 'emp_id' not in session:
        return jsonify({"error": "Not logged in"}), 401

    emp_id = session['emp_id']
    now = datetime.now()
    today = now.date()
    login_time = now.strftime('%H:%M:%S')

    conn = get_db_connection()
    cur = conn.cursor()

    # Store every check-in (instead of replacing the previous one)
    cur.execute("""
        INSERT INTO logs (emp_id, date, checkin, status)
        VALUES (%s, %s, %s, 'Present')
    """, (emp_id, today, login_time))

    conn.commit()
    cur.close()
    conn.close()

    return jsonify({"message": "Login time recorded", "date": str(today), "login_time": login_time})

# Store Check-out at Logout
# @app.route('/store-logout-time', methods=['POST'])
# def store_logout_time():
#     if 'emp_id' not in session:
#         return jsonify({"error": "Not logged in"}), 401

#     emp_id = session['emp_id']
#     now = datetime.now()
#     today = now.date()
#     logout_time = now.strftime('%H:%M:%S')

#     conn = get_db_connection()
#     cur = conn.cursor()

#     # Update logout time
#     cur.execute("""
#         UPDATE logs
#         SET logout_time = %s
#         WHERE emp_id = %s AND date = %s
#     """, (logout_time, emp_id, today))

#     conn.commit()
#     cur.close()
#     conn.close()

#     return jsonify({"message": "Logout time recorded", "date": str(today), "logout_time": logout_time})
@app.route('/store-logout-time', methods=['POST'])
def store_logout_time():
    if 'emp_id' not in session:
        return jsonify({"error": "Not logged in"}), 401

    emp_id = session['emp_id']
    now = datetime.now()
    today = now.date()
    logout_time = now.strftime('%H:%M:%S')  # Ensure 24-hour format

    conn = get_db_connection()
    cur = conn.cursor()

    # Update logout time
    cur.execute("""
        UPDATE logs
        SET checkout = %s
        WHERE emp_id = %s AND date = %s
    """, (logout_time, emp_id, today))

    conn.commit()
    cur.close()
    conn.close()

    return jsonify({"message": "Logout time recorded", "date": str(today), "logout_time": logout_time})


@app.route('/fetch-attendance', methods=['GET'])
def fetch_attendance():
    try:
        if 'emp_id' not in session:
            return jsonify([])  # Always return an empty list if no session

        emp_id = session['emp_id']
        conn = get_db_connection()
        cur = conn.cursor()

        # Fetch attendance records using correct column names
        cur.execute("SELECT date, checkin, checkout FROM logs WHERE emp_id = %s ORDER BY date DESC", (emp_id,))
        records = cur.fetchall()

        cur.close()
        conn.close()

        # Convert records into JSON serializable format
        attendance_data = []
        for row in records:
            date = row[0].strftime('%Y-%m-%d') if row[0] else "-"
            checkin = row[1].strftime('%H:%M:%S') if row[1] else "-"
            checkout = row[2].strftime('%H:%M:%S') if row[2] else "-"

            attendance_data.append({
                "date": date,
                "checkin": checkin,  # Renamed from login_time
                "checkout": checkout  # Renamed from logout_time
            })

        print("Fetched Attendance Data:", attendance_data)  # Debugging
        return jsonify(attendance_data)

    except Exception as e:
        print("Error fetching attendance:", str(e))
        return jsonify({"error": str(e)}), 500

# @app.route('/logout', methods=['POST'])
# def logout():
#     emp_id = session.get("emp_id")  # Keep emp_id only
#     session.clear()  # Clear session
#     session["emp_id"] = emp_id  # Preserve emp_id across sessions
#     return jsonify({"success": True, "message": "Logged out successfully!"}), 200

@app.route('/logout', methods=['POST'])
def logout():
    if 'emp_id' not in session:
        return jsonify({"success": False, "message": "User not logged in"}), 401

    emp_id = session['emp_id']
    now = datetime.now().strftime('%H:%M:%S')
    today = datetime.now().date()

    try:
        conn = get_db_connection()
        cur = conn.cursor()

        # ✅ Ensure logout is stored in the same row as the login entry
        cur.execute("""
            UPDATE logs
            SET checkout = %s
            WHERE emp_id = %s AND date = %s AND checkout IS NULL
        """, (now, emp_id, today))

        conn.commit()
        cur.close()
        conn.close()

        # Clear session after storing logout time
        session.clear()

        return jsonify({"success": True, "message": "Logged out successfully!", "logout_time": now}), 200

    except Exception as e:
        return jsonify({"success": False, "message": f"Error: {str(e)}"}), 500

@app.route('/select-meal', methods=['POST'])
def select_meal():
    try:
        data = request.json
        emp_id = session.get("emp_id")
        meal_choice = data.get("meal")  # Expecting 'Yes' or 'No'

        if not emp_id:
            return jsonify({"error": "User not authenticated"}), 401

        today_date = datetime.date.today()

        # Log data for debugging
        print(f"Meal Selection Request: emp_id={emp_id}, meal_choice={meal_choice}, date={today_date}")

        # Store meal selection in the frontend table only (not DB yet)
        return jsonify({"message": "Meal selection recorded in frontend", "meal": meal_choice}), 200

    except Exception as e:
        print(f"Error: {e}")  # Log error to Flask console
        return jsonify({"error": str(e)}), 500

@app.route('/submit-attendance', methods=['POST'])
def submit_attendance():
    try:
        data = request.json
        emp_id = session.get("emp_id")
        meal_choice = data.get("meal")  # Expecting 'Yes' or 'No'
        today_date = datetime.date.today()

        # if not emp_id:
        #     return jsonify({"error": "User not authenticated"}), 401

        # Connect to DB
        conn = psycopg2.connect("dbname=yourdb user=youruser password=yourpassword")
        cur = conn.cursor()

        # Store data in DB
        cur.execute("INSERT INTO record (emp_id, date, meal, status) "
                    "VALUES (%s, %s, %s, %s)", 
                    (emp_id, today_date, meal_choice, "pending"))
        conn.commit()
        cur.close()
        conn.close()

        return jsonify({"message": "Attendance submitted successfully"}), 200

    except Exception as e:
        print(f"Error: {e}")
        return jsonify({"error": str(e)}), 500

@app.route('/store-meal', methods=['POST'])
def store_meal():
    if 'emp_id' not in session:
        return jsonify({"error": "User not signed in"}), 403

    emp_id = session['emp_id']
    data = request.json
    meal = data.get('meal')
    today = date.today().strftime('%Y-%m-%d')

    if not meal:
        return jsonify({"error": "Meal selection is required"}), 400

    try:
        conn = get_db_connection()
        cur = conn.cursor()
        # Insert data into the `record` table
        cur.execute(
            "INSERT INTO record (emp_id, date, meal, status, type) VALUES (%s, %s, %s, %s, %s)",
            (emp_id, today, meal, "pending", "pending")
        )
        conn.commit()
        cur.close()
        conn.close()
        return jsonify({"message": "Meal data stored successfully"}), 200

    except Exception as e:
        conn.rollback()
        return jsonify({"error": str(e)}), 500

# @app.route('/fetch-today-records', methods=['GET'])
# def fetch_today_records():
#     if 'emp_id' not in session:
#         return jsonify({"error": "User not signed in"}), 403

#     emp_id = session['emp_id']
#     today = date.today().strftime('%Y-%m-%d')
    
#     cursor.execute("SELECT date, meal, status, type FROM record WHERE emp_id = %s AND date = %s", (emp_id, today))
#     records = cursor.fetchall()

#     return jsonify([{
#         "date": row[0],
#         "meal": row[1],
#         "status": row[2],
#         "type": row[3]
#     } for row in records])

@app.route('/fetch-today-records', methods=['GET'])
def fetch_today_records():
    if 'emp_id' not in session:
        return jsonify({"error": "User not signed in"}), 403

    emp_id = session['emp_id']
    today = date.today().strftime('%Y-%m-%d')

    try:
        conn = get_db_connection()
        cur = conn.cursor()
        
        cur.execute("SELECT date, meal, status, type FROM record WHERE emp_id = %s AND date = %s", (emp_id, today))
        records = cur.fetchall()
        
        conn.close()  # Close connection after fetching
        
        return jsonify([{
            "date": row[0],
            "meal": row[1],
            "status": row[2],
            "type": row[3]
        } for row in records])

    except Exception as e:
        print("Database Error:", e)  # Log error
        return jsonify({"error": str(e)}), 500
    
if __name__ == "__main__":
    app.run(debug=True)






