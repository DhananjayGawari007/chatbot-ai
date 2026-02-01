import os
import google.generativeai as genai
from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)
CORS(app)

# Ensure the key is loaded
api_key = os.getenv("GEMINI_API_KEY")
genai.configure(api_key=api_key)

# Initialize the model at the top level (no spaces at the start of these lines)
model = genai.GenerativeModel(model_name='gemini-1.5-flash')

@app.route("/")
def home():
    return render_template("index.html")

@app.route("/chat", methods=["POST"])
def chat():
    try:
        data = request.get_json()
        user_message = data.get("message")
        
        if not user_message:
            return jsonify({"reply": "I didn't receive a message."}), 400

        # System instructions included in the prompt
        prompt = (
            "You are CareNest AI, a helpful Health and Wellness assistant. "
            "Provide supportive advice. User: " + user_message
        )
        
        response = model.generate_content(prompt)
        
        if response.text:
            return jsonify({"reply": response.text})
        else:
            return jsonify({"reply": "I'm sorry, I cannot answer that. How else can I help?"})

    except Exception as e:
        print(f"DETAILED ERROR: {e}")
        return jsonify({"reply": "Connection Error. Please check logs."}), 500

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
