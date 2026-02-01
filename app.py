import os
import google.generativeai as genai
from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)
CORS(app)

# 1. Setup API Key
api_key = os.getenv("GEMINI_API_KEY")
genai.configure(api_key=api_key)

# 2. Setup the Model with safety filters disabled
# This prevents the bot from crashing when it gives wellness advice
model = genai.GenerativeModel(
    model_name='gemini-1.5-flash',
    safety_settings=[
        {"category": "HARM_CATEGORY_HARASSMENT", "threshold": "BLOCK_NONE"},
        {"category": "HARM_CATEGORY_HATE_SPEECH", "threshold": "BLOCK_NONE"},
        {"category": "HARM_CATEGORY_SEXUALLY_EXPLICIT", "threshold": "BLOCK_NONE"},
        {"category": "HARM_CATEGORY_DANGEROUS_CONTENT", "threshold": "BLOCK_NONE"},
    ]
)

@app.route("/")
def home():
    return render_template("index.html")

@app.route("/chat", methods=["POST"])
def chat():
    try:
        data = request.get_json()
        user_message = data.get("message")
        
        if not user_message:
            return jsonify({"reply": "Empty message."}), 400

        prompt = "User: " + user_message + "\nAssistant: Provide helpful wellness advice."
        
        response = model.generate_content(prompt)
        
        # 3. Safe way to check for a response
        if response.candidates and response.candidates[0].content.parts:
            return jsonify({"reply": response.text})
        else:
            return jsonify({"reply": "I'm sorry, I can't answer that. Please ask something else."})

    except Exception as e:
        # This print is for YOU to see in the Render "Logs" tab
        print(f"DETAILED ERROR: {e}")
        return jsonify({"reply": f"Error: {str(e)}"}), 500

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
