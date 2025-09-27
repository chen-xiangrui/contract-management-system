from flask import Flask, request, send_from_directory
from twilio.twiml.messaging_response import MessagingResponse
import os
from werkzeug.utils import secure_filename
import datetime

app = Flask(__name__)
STORAGE_DIR = os.path.join(os.path.dirname(__file__), 'storage')
os.makedirs(STORAGE_DIR, exist_ok=True)

@app.route("/whatsapp", methods=["POST"])
def whatsapp_reply():
    incoming_msg = request.form.get("Body")
    sender = request.form.get("From")
    print(f"Message from {sender}: {incoming_msg}")
    resp = MessagingResponse()
    
    # Custom welcome for Twilio Sandbox join message
    if incoming_msg and incoming_msg.strip().lower().startswith("join"):
        resp.message("CMS System is ready to use. Enter '?' for help.")
        return str(resp)

    msg_lower = incoming_msg.strip().lower()

    # Feature 2: Help message
    if msg_lower == '?':
        help_text = ("Available instructions:\n"
                     "    - Request Timesheet\n"
                     "    - Submit Timesheet\n"
                     "    - Request Report\n"
                     "\n"
                     "Type \"? <instruction>\" for help")
        resp.message(help_text)
        return str(resp)

    # Feature 3: Help for form request
    if msg_lower == '? request timesheet':
        resp.message("Request Timesheet, <project_id>")
        return str(resp)

    # Feature 4: Form request
    if msg_lower.startswith('request timesheet'):
        parts = incoming_msg.split(',')
        if len(parts) == 2:
            project_id = parts[1].strip()
            # Simulate access check and project existence
            # For demo, allow only P1234
            if project_id == 'P1234':
                # Simulate sending a pre-filled form (Word doc)
                form_path = os.path.join(STORAGE_DIR, f"timesheet_{project_id}.docx")
                # If file doesn't exist, create a dummy file
                if not os.path.exists(form_path):
                    with open(form_path, 'wb') as f:
                        f.write(b"Mock timesheet for project P1234")
                msg = resp.message(f"Form for project {project_id} attached.")
                msg.media(request.url_root + f"storage/timesheet_{project_id}.docx")
                return str(resp)
            else:
                resp.message("Illegal request: no access or project ID does not exist.")
                return str(resp)
        else:
            resp.message("Invalid format. Use: Form request, <project_id>")
            return str(resp)

    # Feature 5: Help for form submit
    if msg_lower == '? submit timesheet':
        resp.message("[Attach timesheet and send] *Filename not important")
        return str(resp)

    # Feature 6: Timesheet submit with only docx attachment, no text
    num_media = int(request.form.get('NumMedia', 0))
    if num_media > 0 and not incoming_msg.strip():
        media_type = request.form.get('MediaContentType0', '')
        if media_type == 'application/vnd.openxmlformats-officedocument.wordprocessingml.document':
            # Hardcode filename
            filename = "timesheet_P1234.docx"
            file_path = os.path.join(STORAGE_DIR, filename)
            # Save the file (simulate, in real use download from media_url)
            with open(file_path, 'wb') as f:
                f.write(b"Received file content (mock)")
            
            # Version tracking
            version_file = os.path.join(STORAGE_DIR, "version_timesheet_P1234.txt")
            version = 1
            if os.path.exists(version_file):
                with open(version_file, 'r') as vf:
                    try:
                        version = int(vf.read().strip()) + 1
                    except Exception:
                        version = 1
            with open(version_file, 'w') as vf:
                vf.write(str(version))
            
            # Current date timestamp
            timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            resp.message(f"Received timesheet for George, P1234, {timestamp}, Version {version}.")
            return str(resp)
        else:
            resp.message("Only .docx timesheet files are accepted.")
            return str(resp)

    # Feature 7: Help for report
    if msg_lower == '? request report':
        resp.message("Report, <project_id>, weekly/monthly/<year>: To request report for <project_id>.")
        return str(resp)

    # Feature 8: Report request
    if msg_lower.startswith('report'):
        parts = incoming_msg.split(',')
        if len(parts) == 3:
            project_id = parts[1].strip()
            period = parts[2].strip()
            # Check if period is a year (4 digits)
            if project_id == 'P1234':
                if period.isdigit() and len(period) == 4:
                    # Yearly report: report_<project_id>_<year>.pdf
                    report_filename = f"report_{project_id}_{period}.pdf"
                elif period.lower() == "monthly":
                    report_filename = f"report_{project_id}_monthly.pdf"
                elif period.lower() == "weekly":
                    report_filename = f"report_{project_id}_weekly.pdf"
                else:
                    resp.message("Invalid period. Use weekly, monthly, or a 4-digit year.")
                    return str(resp)
                report_path = os.path.join(STORAGE_DIR, report_filename)
                if not os.path.exists(report_path):
                    with open(report_path, 'wb') as f:
                        f.write(b"Mock report for project P1234, period: " + period.encode())
                msg = resp.message(f"Report for project {project_id}, period {period} attached.")
                msg.media(request.url_root + f"storage/{report_filename}")
                return str(resp)
            else:
                resp.message("Illegal request: no access or project ID does not exist.")
                return str(resp)
        else:
            resp.message("Invalid format. Use: Report, <project_id>, weekly/monthly/<year>")
            return str(resp)

    # Default response
    resp.message("Unrecognized command. Enter '?' for help.")
    return str(resp)

@app.route('/storage/<filename>')
def serve_storage_file(filename):
    return send_from_directory(STORAGE_DIR, filename)

if __name__ == "__main__":
    print("Starting server...")
    app.run(debug=True, port=5000)
