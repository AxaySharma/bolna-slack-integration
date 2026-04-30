import os
import requests
from flask import Flask, request, jsonify
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)
SLACK_WEBHOOK_URL = os.getenv("SLACK_WEBHOOK_URL")

def notify_slack(call_data):
    # Using Slack Block Kit here to format the data nicely
    payload = {
        "blocks": [
            {
                "type": "header",
                "text": {"type": "plain_text", "text": "📞 Bolna Call Finished", "emoji": True}
            },
            {
                "type": "section",
                "fields": [
                    {"type": "mrkdwn", "text": f"*Call ID:*\n`{call_data.get('id', 'N/A')}`"},
                    {"type": "mrkdwn", "text": f"*Agent ID:*\n`{call_data.get('agent_id', 'N/A')}`"},
                    {"type": "mrkdwn", "text": f"*Duration:*\n{call_data.get('conversation_duration', 0)}s"}
                ]
            },
            {"type": "divider"},
            {
                "type": "section",
                # Bolna sends the transcript as a single formatted string
                "text": {"type": "mrkdwn", "text": f"*Transcript:*\n> {call_data.get('transcript', 'No transcript generated.')}"}
            }
        ]
    }

    try:
        res = requests.post(SLACK_WEBHOOK_URL, json=payload)
        res.raise_for_status()
        print(f"✅ Alert sent to Slack for call {call_data.get('id')}")
    except Exception as e:
        # TODO: Add proper retry logic here later.
        print(f"❌ Failed to post to Slack: {e}")

@app.route('/api/webhook/bolna', methods=['POST'])
def bolna_webhook():
    payload = request.json
    
    # Bolna updates the 'status' key directly. We only want to trigger on 'completed'
    call_status = payload.get("status")
    
    if call_status == "completed":
        
        if not SLACK_WEBHOOK_URL:
            print("Error: SLACK_WEBHOOK_URL environment variable is missing.")
            return jsonify({"error": "Configuration error"}), 500

        # Pass the raw payload directly since Bolna doesn't nest it inside a 'data' key
        notify_slack(payload)
        
        return jsonify({"status": "success"}), 200

    # Silently ignore other statuses (initiated, ringing, in-progress, etc.) to prevent spam
    return jsonify({"status": "ignored", "reason": f"Status was {call_status}"}), 200

if __name__ == '__main__':
    app.run(port=5000, debug=True)