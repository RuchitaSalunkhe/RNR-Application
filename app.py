from flask import Flask, render_template, request, jsonify
import pandas as pd
import os
import datetime
import time
import pythoncom
import win32com.client

app = Flask(__name__)

# Path to shared folder
SHARED_FOLDER = r"D:\Emp_rewards\shared_folder"
EXCEL_FILE = os.path.join(SHARED_FOLDER, "data.xlsx")

# Ensure Excel file exists
if not os.path.exists(EXCEL_FILE):
    df = pd.DataFrame(columns=[
        "SrNo", "FormId", "SubmitDate", "Department", "ProjectName", "RewardsType", "Category", 
        "EmployeeCode", "EmployeeName", "MobileNumber", "Email", "NominatedByName", "NominatedByEmail",
         "Achievement", "NumberofNominee"
    ])
    df.to_excel(EXCEL_FILE, index=False)

def close_excel_file():
    try:
        pythoncom.CoInitialize()  # Initialize COM
        excel = win32com.client.Dispatch("Excel.Application")
        for wb in excel.Workbooks:
            if "data.xlsx" in wb.Name.lower():  # Check if our file is open
                wb.Close(SaveChanges=True)  # Save & close the workbook
                print("Excel file closed successfully.")
                break
        excel.Quit()
    except Exception as e:
        print(f"Error closing Excel: {e}")
    finally:
        pythoncom.CoUninitialize()  # Uninitialize COM
        
@app.route("/")
def index():
    return render_template("index.html")


@app.route("/submit", methods=["POST"])
def submit():
    try:
        close_excel_file()
        time.sleep(2)  # W
        # Get form data
        department = request.form["department"]
        project_name = request.form["projectname"]
        rewards_type = request.form["rewardstype"]
        category = request.form["category"]
        nominated_by_name = request.form["nominatedbyname"]
        nominated_by_email = request.form["nominatedby"]
        achievement = request.form["achievement"]
        num_nominees = int(request.form.get("numberofnominees", 1))
        
        employee_codes = request.form.getlist("employeecode[]")
        employee_names = request.form.getlist("employeename[]")
        mobile_numbers = request.form.getlist("mobilenumber[]")
        emails = request.form.getlist("email[]")

        # Validate inputs
        if not department or not category or not nominated_by_email:
            return jsonify({"message": "Required fields are missing!"}), 400

        if len(employee_codes) != num_nominees:
            return jsonify({"message": "Mismatch in number of nominees!"}), 400

        # Read existing data
        df = pd.read_excel(EXCEL_FILE)

        # Get the next SrNo
        sr_no = len(df) + 1
        
        # Generate FormId
        form_id = f"RNR{sr_no:04d}"

        # Keep FormId same for all nominees if category is "Team"
        if category == "Team":
            form_id = f"RNR{sr_no:04d}"  # Use first SrNo FormId

        submit_date = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        # Append new data
        for i in range(num_nominees):
            df = pd.concat([df, pd.DataFrame([{
                "SrNo": sr_no + i,  # Increment SrNo for each nominee
                "FormId": form_id,  # Keep same FormId if category is "Team"
                "SubmitDate": submit_date,
                "Department": department,
                "ProjectName": project_name,
                "RewardsType": rewards_type,
                "Category": category,
                "EmployeeCode": employee_codes[i],
                "EmployeeName": employee_names[i],
                "MobileNumber": mobile_numbers[i],
                "Email": emails[i],
                "NominatedByName": nominated_by_name,
                "NominatedByEmail": nominated_by_email,
                "Achievement": achievement,
                "NumberofNominee": num_nominees
            }])], ignore_index=True)

        # Save to Excel
        df.to_excel(EXCEL_FILE, index=False)

        return jsonify({"message": "Form submitted successfully!"})

    except Exception as e:
        return jsonify({"message": f"Error: {str(e)}"}), 500
    
if __name__ == "__main__":
    app.run(debug=True)
