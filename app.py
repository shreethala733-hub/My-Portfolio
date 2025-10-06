import os
from flask import Flask, request, jsonify, render_template
from google import genai
from google.genai import types
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

# ✅ Get API key safely from environment variable
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

# ✅ Initialize Gemini client properly
client = None
try:
    if GEMINI_API_KEY:
        client = genai.Client(api_key=GEMINI_API_KEY)
    else:
        print("⚠️ GEMINI_API_KEY not found in environment variables.")
except Exception as e:
    print(f"❌ Error initializing Gemini client: {e}")
    client = None

@app.route("/")
def home():
    return render_template("index.html")

@app.route("/chat", methods=["POST"])
def chat():
    if not client:
        return jsonify({"response": "Chatbot is temporarily offline. Failed to initialize Gemini client."}), 200

    data = request.get_json()
    user_message = data.get("message", "")

    try:
        response = client.models.generate_content(
            model="gemini-1.5-flash",
            contents=[user_message]
        )
        return jsonify({"response": response.text})
    except Exception as e:
        print(f"❌ Error generating response: {e}")
        return jsonify({"response": "Error: Unable to get response from AI."}), 500


if __name__ == "__main__":
    app.run(debug=True)
