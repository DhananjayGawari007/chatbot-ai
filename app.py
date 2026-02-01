from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
from dotenv import load_dotenv
import os
from openai import OpenAI

# 1. Load environment variables
load_dotenv()

app = Flask(__name__)
CORS(app)

# 2. Initialize Client
# Make sure OPENAI_API_KEY is exactly this name in your .env file
api_key = os.getenv("OPENAI_API_KEY")
client = OpenAI(api_key=api_key)

@app.route("/")
def home():
    return render_template("index.html")

@app.route("/chat", methods=["POST"])
def chat():
    try:
        # Get message from JSON request
        data = request.get_json()
        user_message = data.get("message")

        if not user_message:
            return jsonify({"reply": "No message received"}), 400

        # 3. Create OpenAI Completion
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                # Set the persona for Health & Wellness
                {"role": "system", "content": "You are CareNest AI, a helpful Health and Wellness assistant. Provide supportive, wellness-focused advice. Always remind users to consult a doctor for serious medical concerns."},
                {"role": "user", "content": user_message}
            ]
        )

        # 4. Extract the reply
        bot_reply = response.choices[0].message.content
        return jsonify({"reply": bot_reply})

    except Exception as e:
        # This will print the actual error in your terminal/Render logs
        print(f"ERROR: {e}")
        return jsonify({"reply": "I'm having trouble connecting to my service. Please try again later."}), 500

if __name__ == "__main__":
    # Render uses the PORT environment variable, so this is safer
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
