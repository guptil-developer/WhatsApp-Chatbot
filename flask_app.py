
# A very simple Flask Hello World app for you to get started with...
import logging

from flask import Flask, render_template, request, jsonify
from config import VERIFY_TOKEN
from utils import is_valid_whatsapp_message, process_whatsapp_message

app = Flask(__name__)
app.secret_key = 'secret_key'


@app.route('/')
def index():
    return render_template('index.html')

def verify(request):
    # Parse params from the webhook verification request
    mode = request.args.get("hub.mode")
    token = request.args.get("hub.verify_token")
    challenge = request.args.get("hub.challenge")
    # Check if a token and mode were sent
    if mode and token:
        # Check the mode and token sent are correct
        if mode == "subscribe" and token == VERIFY_TOKEN:
            # Respond with 200 OK and challenge token from the request
            print("WEBHOOK_VERIFIED")
            return challenge, 200
        else:
            # Responds with '403 Forbidden' if verify tokens do not match
            print("VERIFICATION_FAILED")
            return jsonify({"status": "error", "message": "Verification failed"}), 403
    else:
        # Responds with '400 Bad Request' if verify tokens do not match
        print("MISSING_PARAMETER")
        return jsonify({"status": "error", "message": "Missing parameters"}), 400




@app.route('/webhook', methods=['GET','POST'])
def webhook():
    logging.info(f"Webhook triggered with method: {request.method}")
    if request.method == 'GET':
        # Perform verification
        return verify(request)
    elif request.method == 'POST':
        body = request.json
        logging.info(f"Received Webhook: {body}")
        if is_valid_whatsapp_message(body):
            try:
                process_whatsapp_message(body)
                return jsonify({"status": "success"})
            except Exception as e:
                logging.error(f"Error processing WhatsApp message: {e}")
                return jsonify({"status": "error", "message": str(e)}), 500
        else:
            # Ignore status updates or handle them differently
            return jsonify({"status": "success", "message": "Ignoring status update"})
    else:
        return "Method not allowed", 405  # Method not allowed for other HTTP methods


