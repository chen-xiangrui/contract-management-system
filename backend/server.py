from flask import Flask, request, send_from_directory
from twilio.twiml.messaging_response import MessagingResponse
import os
from werkzeug.utils import secure_filename

app = Flask(__name__)
STORAGE_DIR = os.path.join(os.path.dirname(__file__), 'storage')
os.makedirs(STORAGE_DIR, exist_ok=True)

@app.route("/whatsapp", methods=["POST"])
def whatsapp_reply():
    incoming_msg = request.form.get("Body")
    sender = request.form.get("From")
    print(f"Message from {sender}: {incoming_msg}")
    resp = MessagingResponse()

    # Feature 1: Welcome message
    if not incoming_msg or incoming_msg.strip().lower() == 'start':
        resp.message("CMS System is ready to use. Enter '?' for help.")
        return str(resp)

    msg_lower = incoming_msg.strip().lower()

    # Feature 2: Help message
    if msg_lower == '?':
        help_text = ("Allowable instructions:\n"
                     "? form request\n"
                     "? form submit\n"
                     "? report\n"
                     "form request, <project_id>\n"
                     "form submit, timesheet (attach file)\n"
                     "report, <project_id>, weekly/monthly/year\n")
        resp.message(help_text)
        return str(resp)

    # Feature 3: Help for form request
    if msg_lower == '? form request':
        resp.message("Form request, <project_id>")
        return str(resp)

    # Feature 4: Form request
    if msg_lower.startswith('form request'):
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
    if msg_lower == '? form submit':
        resp.message("Form submit, filename, *attach file")
        return str(resp)

    # Feature 6: Form submit with attachment
    if msg_lower.startswith('form submit'):
        num_media = int(request.form.get('NumMedia', 0))
        filename = None
        if num_media > 0:
            media_url = request.form.get('MediaUrl0')
            media_type = request.form.get('MediaContentType0')
            filename = secure_filename(request.form.get('Body', 'timesheet')) + '.docx'
            file_path = os.path.join(STORAGE_DIR, filename)
            # Download and save the file (simulate)
            # In real use, download from media_url
            with open(file_path, 'wb') as f:
                f.write(b"Received file content (mock)")
            resp.message(f"Received Timesheet/User/Project/Version. File saved as {filename}.")
            return str(resp)
        else:
            resp.message("No attachment found. Please attach a file.")
            return str(resp)

    # Feature 7: Help for report
    if msg_lower == '? report':
        resp.message("Report, <project_id>, weekly/monthly/year")
        return str(resp)

    # Feature 8: Report request
    if msg_lower.startswith('report'):
        parts = incoming_msg.split(',')
        if len(parts) == 3:
            project_id = parts[1].strip()
            period = parts[2].strip()
            # Simulate report file
            if project_id == 'P1234':
                report_path = os.path.join(STORAGE_DIR, f"report_{project_id}_{period}.pdf")
                if not os.path.exists(report_path):
                    with open(report_path, 'wb') as f:
                        f.write(b"Mock report for project P1234, period: " + period.encode())
                msg = resp.message(f"Report for project {project_id}, period {period} attached.")
                msg.media(request.url_root + f"storage/report_{project_id}_{period}.pdf")
                return str(resp)
            else:
                resp.message("Illegal request: no access or project ID does not exist.")
                return str(resp)
        else:
            resp.message("Invalid format. Use: Report, <project_id>, weekly/monthly/year")
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
