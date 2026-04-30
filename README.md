# Bolna to Slack Webhook Integration

A lightweight Python/Flask service that listens for Bolna webhook payloads and routes completed call data (ID, Agent, Duration, Transcript) to a designated Slack channel via Block Kit.

## Setup Instructions

**1. Environment Preparation**
Requires Python 3.8+. It is recommended to run this within a virtual environment.

    python -m venv venv
    source venv/bin/activate  # On Windows use: venv\Scripts\activate
    pip install -r requirements.txt

**2. Configuration**
Copy the example environment file:

    cp .env.example .env

Note: Open the `.env` file and replace the placeholder with your actual Slack Incoming Webhook URL.

**3. Running the Server**
Start the local Flask server (defaults to port 5000):

    python app.py

**4. Testing with Bolna**
- Expose the local server to the internet using ngrok: 
  `ngrok http 5000`
- Copy the secure ngrok URL (e.g., `https://1234-abcd.ngrok-free.app`).
- In your Bolna Agent's webhook settings, paste the URL and append the endpoint path: 
  `https://<your-ngrok-url>.ngrok-free.app/api/webhook/bolna`
- Trigger a test call. The Slack alert will fire automatically once the Bolna payload status updates to `completed`.

## Design Decisions & Notes

- **Direct Payload Parsing:** Bolna currently sends the call object directly in the root payload rather than nesting it under standard `event` or `data` keys. This endpoint extracts keys directly from the root and explicitly filters for `"status": "completed"` to prevent duplicate alerts during the call lifecycle.
- **Slack Block Kit:** Used Block Kit over standard text attachments to ensure better readability, data separation, and visual structure in the Slack channel.
- **Future Improvements:** Right now, the app waits for Slack to respond before it replies to Bolna. In a real production environment, I'd move the Slack API call to a background worker (like a basic Redis queue). That way, if Slack's API is running slow, it won't cause the Bolna webhook to time out, and we can safely retry failed messages.