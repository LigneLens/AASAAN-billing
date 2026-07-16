from fastapi import FastAPI, Request, Response
import requests

app = FastAPI()

VERIFY_TOKEN = "bharat_erp_secret_123"
PHONE_NUMBER_ID = "1177923822074684" 
WHATSAPP_TOKEN = "PASTE_YOUR_NEW_TOKEN_HERE" 

# This creates a single door named "/webhook" that handles EVERYTHING
@app.api_route("/webhook", methods=["GET", "POST"])
async def webhook_handler(request: Request):
    
    # 1. If Meta is checking if the door is open (GET request)
    if request.method == "GET":
        mode = request.query_params.get("hub.mode")
        token = request.query_params.get("hub.verify_token")
        challenge = request.query_params.get("hub.challenge")

        if mode == "subscribe" and token == VERIFY_TOKEN:
            print("Meta successfully connected!")
            return Response(content=challenge, status_code=200)
        return Response(status_code=403)
        
    # 2. If Meta is delivering a WhatsApp message (POST request)
    elif request.method == "POST":
        try:
            body = await request.json()
            print("--- INCOMING DATA ---", body) # Prints to your Render logs
            
            # Dig into the data to find the message
            entry = body.get("entry", [])[0]
            changes = entry.get("changes", [])[0]
            value = changes.get("value", {})
            
            if "messages" in value:
                message = value["messages"][0]
                sender_phone = message["from"]
                received_text = message.get("text", {}).get("body", "")
                
                print(f"Message received from {sender_phone}: {received_text}")
                
                # Formulate and send the reply
                reply_text = f"Vanakkam! I am your Retail Bot. You said: '{received_text}'"
                send_whatsapp_reply(sender_phone, reply_text)
                
        except Exception as e:
            print("Error reading message:", e)
            
        # Tell Meta "We got it!" so they don't keep trying
        return {"status": "success"}

def send_whatsapp_reply(recipient_phone, text_to_send):
    """Sends the actual reply back to the user's phone"""
    url = f"https://graph.facebook.com/v19.0/{PHONE_NUMBER_ID}/messages"
    headers = {
        "Authorization": f"Bearer {WHATSAPP_TOKEN}",
        "Content-Type": "application/json"
    }
    payload = {
        "messaging_product": "whatsapp",
        "to": recipient_phone,
        "type": "text",
        "text": {"body": text_to_send}
    }
    requests.post(url, headers=headers, json=payload)
    print("Reply successfully sent!")