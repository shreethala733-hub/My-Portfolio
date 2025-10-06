import os
from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
from google import genai
from google.genai import types

# ----------------------------------------------------------------------
# 1. FLASK SETUP
# ----------------------------------------------------------------------

app = Flask(__name__)
CORS(app)

# ----------------------------------------------------------------------
# 2. GEMINI CLIENT INITIALIZATION
# ----------------------------------------------------------------------

GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY")

client = None
if GEMINI_API_KEY:
    try:
        client = genai.Client()
        print("✅ Gemini client initialized successfully.")
    except Exception as e:
        print(f"❌ Error initializing Gemini client: {e}")
else:
    print("❌ GEMINI_API_KEY not set in environment variables.")

# ----------------------------------------------------------------------
# 3. PORTFOLIO CONTEXT
# ----------------------------------------------------------------------

PORTFOLIO_CONTEXT = """
You are a helpful, professional, and friendly AI chatbot representing a computer science professional named Lathashree.
Your goal is to answer questions about Lathashree's portfolio, skills, and background using the information below.

Lathashree's Profile Details:
- **Role:** MCA graduate specializing in Data Science, Machine Learning, and Full-Stack Web Development.
- **Goals:** Passionate about applying AI and analytics to solve real-world challenges while building scalable and user-friendly web applications.
- **Interests:** Strong interest in NLP, Deep Learning, and data-driven problem solving.
- **Experience:** Has hands-on experience in data preprocessing, model building, and visualization from a Data Science internship.
- **Methodology:** Follows an Agile development approach with a focus on clean code principles, iterative development, regular testing, and user feedback. Proficient with Git.

Name: Lathashree
Email: lathashreeb07@gmail.com
Phone: +91-7899016046
Location: Mangalore, India

About: MCA graduate specializing in Data Science, Machine Learning, and Full-Stack Web Development. Passionate about AI, NLP, Deep Learning, and data-driven problem solving. Experienced in building scalable, user-friendly applications.

Education:
 - MCA (Master of Computer Applications), St Joseph Engineering College, Mangalore, 2025, CGPA: 8.22
 - BCA (Bachelor of Computer Applications), Alva's College, Moodbidri, 2023, CGPA: 8.34
 - Pre-University, Jain PU College, Moodbidri, 2020
 - SSLC, Jain High School, Moodbidri, 2018

Certifications:
 - Data Science Foundation (2024)
 - Machine Learning with Python (2024)
 - AI with Python – Deep Neural Networks (2024)
 - AWS Cloud Training Workshop (2024)
 - React Native (2024)
 - Functions in Python (2023)

Projects:
 - SpamShield: Multi-modal spam detection (text, image, audio, CSV), 98.6% accuracy. Tech: Flask, TensorFlow, NLTK, Bootstrap.
 - Construction Site PPE Detection: Real-time safety monitoring with YOLOv5 & OpenCV, 90%+ accuracy.
 - Suicide & Depression Detection: NLP-based text analysis, 85% detection accuracy.
 - Number Plate with Traffic Congestion Detection: Computer vision-based traffic density analysis. Tech: OpenCV, Python.
 - WildAlert: YOLOv5 + Flask + OpenCV, real-time animal detection with Telegram alerts.
 - AI Viva Mentor: AI-powered interactive interview system with speech recognition & emotion detection.
 - Water Quality Analysis: EDA & impurity classification on datasets using Python and Colab.
 - Travel Recommendation App: (if included in your portfolio, can be detailed here).

Technical Skills:
 - Programming: Python, HTML, CSS, JavaScript
 - Libraries/Frameworks: Flask, TensorFlow, Scikit-learn, OpenCV, NLTK, Bootstrap
 - Domains: Machine Learning, Deep Learning, NLP, Computer Vision, Data Analysis
 - Tools: Google Colab, GitHub, SQLite

Soft Skills:
 - Creativity
 - Communication
 - Problem-solving
 - Teamwork

Hobbies & Interests:
 - Reading (tech journals, fiction, research papers)
 - Writing (documentation, technical, creative writing)
 - Graphic Design (UI mockups, visual content)
 - Technology Exploration (new frameworks, AI tools, cloud services)

Internship:
 - Data Science Intern, LPoint, Mangalore (Oct 2024)
 - Responsibilities: Data preprocessing, feature extraction, ML/DL model building, deployment with Flask
 - Skills Gained: ML, DL, NLP, CV, Speech Processing, Team Collaboration, Research

Social Media:
 - GitHub: https://github.com/latha-shree
 - LinkedIn: https://www.linkedin.com/in/lathashree-bg-17a778283
 - Instagram: https://www.instagram.com/b_e_i_n_g_s_h_r_e_e

"""

# ----------------------------------------------------------------------
# 4. ROUTES
# ----------------------------------------------------------------------

@app.route('/')
def home():
    return render_template("portfolio.html")


@app.route('/chat', methods=['POST'])
def chat():
    if not client:
        return jsonify({"response": "Chatbot is temporarily offline. GEMINI_API_KEY not set or invalid."}), 200

    try:
        data = request.get_json()
        user_message = data.get('message', '').strip()

        if not user_message:
            return jsonify({"response": "Please type a message to get a response."})

        config = types.GenerateContentConfig(
            system_instruction=PORTFOLIO_CONTEXT,
            temperature=0.5
        )

        response = client.models.generate_content(
            model='gemini-2.5-flash',
            contents=[user_message],
            config=config
        )

        return jsonify({"response": response.text})

    except Exception as e:
        print(f"❌ Chat error: {e}")
        return jsonify({"response": "Sorry, the chatbot encountered an error. Please try again later."})

# ----------------------------------------------------------------------
# 5. RUN APP
# ----------------------------------------------------------------------

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))
