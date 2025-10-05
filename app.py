import os
from flask import Flask, request, jsonify, send_file, render_template
from flask_cors import CORS
from google import genai
from google.genai import types
import os
import smtplib
from email.message import EmailMessage
import json
import datetime
from flask_cors import CORS
# ... (other Flask/Gemini imports)

# ----------------------------------------------------------------------
# 1. FLASK AND GEMINI SETUP
# ----------------------------------------------------------------------

app = Flask(__name__)
# Enable CORS to allow your local HTML file to communicate with this server
CORS(app) 

# Initialize the Gemini Client. It looks for the GEMINI_API_KEY environment variable.
try:
    client = genai.Client()
except Exception as e:
    # This happens if the key is not set. Good for checking during setup.
    print(f"Error initializing Gemini client: {e}")
    client = None

# ----------------------------------------------------------------------
# 2. SYSTEM PROMPT (The "Brain" for your Portfolio Context)
# ----------------------------------------------------------------------

# Context extracted from your portfolio sections (like #about, skills, and methodology).
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

@app.route('/')
def home():
    return send_file("portfolio.html")  
--------------------------------------
# 3. API ROUTE: This is where the ML concept is applied!
# ----------------------------------------------------------------------

@app.route('/chat', methods=['POST'])
def chat():
    # Check if the Gemini client initialized successfully
    if not client:
        return jsonify({"response": "Chatbot is temporarily offline. API Key not set."}), 500

    try:
        # Get the message from the request body
        data = request.get_json()
        user_message = data.get('message')
        
        if not user_message:
            return jsonify({"response": "No message provided."}), 400

        # Configure the model to use your portfolio context
        config = types.GenerateContentConfig(
            system_instruction=PORTFOLIO_CONTEXT,
            temperature=0.5  # Lower temperature for more factual, professional answers
        )
        
        # Call the Gemini API with the user's message and your custom context
        response = client.models.generate_content(
            model='gemini-2.5-flash',
            contents=[user_message],
            config=config
        )

        # Return the AI's generated response to the frontend
        return jsonify({"response": response.text})

    except Exception as e:
        print(f"An error occurred: {e}")
        return jsonify({"response": "I apologize, an unexpected error occurred in the server."}), 500



# ----------------------------------------------------------------------
# 5. Lead Capture & Email Logic
# ----------------------------------------------------------------------

# NOTE: SENDER_EMAIL and SENDER_PASSWORD must be available in the global scope, 
# loaded from the .env file using the dotenv library (as instructed in previous steps).

def send_log_email(name, email, timestamp):
    # Retrieve the credentials from the environment variables (loaded via dotenv)
    SENDER_EMAIL = os.environ.get("SENDER_EMAIL") 
    SENDER_PASSWORD = os.environ.get("SENDER_PASSWORD")
    RECEIVER_EMAIL = SENDER_EMAIL # Assuming you send it to yourself

    if not SENDER_EMAIL or not SENDER_PASSWORD:
        print("\n🚨 ERROR: Email credentials (SENDER_EMAIL or SENDER_PASSWORD) are NOT SET in environment variables. Email log failed.\n")
        return

    msg = EmailMessage()
    msg['Subject'] = f"NEW CV VIEW LEAD: {name}"
    msg['From'] = SENDER_EMAIL
    msg['To'] = RECEIVER_EMAIL
    
    msg.set_content(f"""
    Lathashree's CV has been viewed!

    --------------------------------------
    Name: {name}
    Email: {email}
    Time: {timestamp}
    --------------------------------------
    
    This is a confirmed lead from your portfolio.
    """)

    try:
        # Use Gmail's SMTP server (change if using a different provider)
        with smtplib.SMTP_SSL('smtp.gmail.com', 465) as smtp:
            smtp.login(SENDER_EMAIL, SENDER_PASSWORD)
            smtp.send_message(msg)
        # Use a consistent print format for better logging clarity
        print(f"--- EMAIL LOG SENT SUCCESSFULLY: To {RECEIVER_EMAIL} for lead {email} ---")
        
    except smtplib.SMTPAuthenticationError:
        print("\n🚨 CRITICAL ERROR: Email Login Failed! Check your SENDER_PASSWORD (App Password) and ensure 'Less Secure App Access' is handled for your email.\n")
    except Exception as e:
        # General error during email sending
        print(f"ERROR SENDING EMAIL: {e}")


@app.route('/log_download', methods=['POST'])
def log_download():
    # Ensure all necessary imports are available (request, jsonify, datetime, os)
    # The 'app' object must be initialized globally (app = Flask(__name__)).
    
    try:
        data = request.get_json()
        name = data.get('name', 'N/A')
        email = data.get('email', 'N/A')
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        # Input Validation (Minor improvement for robustness)
        if not name or not email:
            return jsonify({"message": "Name and Email are required."}), 400

        # 1. Log to the console (for debugging/temporary check)
        print(f"--- LEAD CAPTURED --- [{timestamp}] Name: {name}, Email: {email}")

        # 2. SEND EMAIL (Creates a permanent record in your inbox)
        send_log_email(name, email, timestamp)
        
        # Return success (the JavaScript will handle opening the CV)
        return jsonify({"message": "Lead captured and email notification sent."}), 200

    except Exception as e:
        print(f"Error processing log request: {e}")
        # Return a 500 status code for internal server error
        return jsonify({"message": "Server error while processing data."}), 500


if __name__ == "__main__":
    from dotenv import load_dotenv
    import os
    load_dotenv()

    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))



