# fetch("/get_financial_detail")
#     .then(response => response.json())
#     .then(data => {
#         document.getElementById("displayBankName").textContent = data.bank_name || "Not provided";
#         document.getElementById("displayAccountNumber").textContent = data.account_number || "Not provided";
#         document.getElementById("displayIFSC").textContent = data.ifsc_code || "Not provided";
#         document.getElementById("displayAccountName").textContent = data.account_name || "Not provided";
#         document.getElementById("displayBankAddress").textContent = data.bank_address || "Not provided";
#         document.getElementById("displayPincode").textContent = data.pincode || "Not provided";
#     })
# This format is used to load the updated data on ui


# function openModal(modalId) {
#     const modal = document.getElementById(modalId);
#     if (modal) {
#         modal.style.display = "block";
#         checkForm(modalId);
#     }
# } 
# this is for edit button i.e opening modal and editing the data 
 

# document.getElementById("saveFinancialButton")?.addEventListener("click", event => {
#     event.preventDefault();
#     saveChanges("financial");
# });
# this is for saving the data using button for particular feild 

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