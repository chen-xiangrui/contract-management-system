from flask import Flask, request
from twilio.twiml.messaging_response import MessagingResponse

app = Flask(__name__)

@app.route("/whatsapp", methods=["POST"])
def whatsapp_reply():
    """Respond to incoming WhatsApp messages with a simple text reply."""
    incoming_msg = request.form.get("Body")  # The message sent by the user
    sender = request.form.get("From")        # The sender's WhatsApp number
    
    print(f"Message from {sender}: {incoming_msg}")

    # Build response
    resp = MessagingResponse()
    resp.message("Message received.")

    return str(resp)

if __name__ == "__main__":
    print("Starting server...")
    app.run(debug=True, port=5000)
