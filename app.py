import os
import google.generativeai as genai
from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)
CORS(app)

# Setup Gemini
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
model = genai.GenerativeModel('gemini-1.5-flash')

@app.route("/")
def home():
    return render_template("index.html")

@app.route("/chat", methods=["POST"])
def chat():
    try:
        user_message = request.json.get("message")
        
        # System instructions for Health & Wellness
        prompt = f"System: You are CareNest AI, a health and wellness assistant. Provide supportive advice. User: {user_message}"
        
        response = model.generate_content(prompt)
        
        return jsonify({"reply": response.text})
    except Exception as e:
        print(f"ERROR: {e}")
        return jsonify({"reply": "I'm having trouble connecting right now."}), 500

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
