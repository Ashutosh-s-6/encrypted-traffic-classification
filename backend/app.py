from flask import Flask, render_template, request, jsonify
from routes import routes
from groq import Groq
import os
from dotenv import load_dotenv

# =====================================================
# LOAD ENV VARIABLES
# =====================================================

load_dotenv()

# =====================================================
# FLASK APP CONFIG
# =====================================================

app = Flask(
    __name__,
    template_folder="../frontend/templates",
    static_folder="../frontend/static"
)

# Register API routes (for prediction etc.)
app.register_blueprint(routes)

# =====================================================
# GROQ API CONFIG
# =====================================================

GROQ_API_KEY = os.getenv("GROQ_API_KEY")

client = Groq(
    api_key=GROQ_API_KEY
)

# =====================================================
# PAGE ROUTES
# =====================================================

@app.route("/")
def home():
    return render_template("index.html")


@app.route("/analytics")
def analytics():
    return render_template("analytics.html")


@app.route("/about-project")
def about_project():
    return render_template("about_project.html")


@app.route("/about-dataset")
def about_dataset():
    return render_template("about_dataset.html")


@app.route('/threat_intel')
def threat_intel():
    return render_template('threat_intel.html')


@app.route("/report")
def report():
    return render_template("report.html")


# =====================================================
# AI CHAT API
# =====================================================

@app.route("/chat", methods=["POST"])
def chat():

    data = request.json
    message = data.get("message", "")

    if not message:
        return jsonify({"reply": "Please enter a question."})

    try:

        completion = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[
                {
"role": "system",
"content": """
You are an AI cybersecurity assistant for a dashboard called
'Encrypted Traffic Classification System'.

Your job is ONLY to help users understand:
• Encrypted traffic classification
• Network traffic analysis
• Cybersecurity insights
• Dataset: ISCX-VPN-NonVPN-2016
• Traffic classes: Browsing, Streaming, VoIP, Chat, Mail, P2P, File Transfer
• Machine learning models used in the dashboard

STRICT DOMAIN RULE:

If the user asks something unrelated to:
network traffic, cybersecurity, machine learning results,
or this dashboard system,

you must politely refuse.

Example response:
"I'm designed to help with encrypted traffic analysis,
cybersecurity insights, and understanding the dashboard results.
Please ask a question related to the traffic classification system."

RESPONSE STYLE RULES:

1. Adapt your response based on the user's question.

2. If the user asks a simple definition
(example: "What is P2P?" or "What is FT?")
→ give a short clear explanation.

3. If the user asks about traffic results
(example: "Explain the traffic distribution")
→ provide an analytical response.

4. If the user asks about security insights
→ explain cybersecurity implications.

5. Use bullet points when helpful, but do NOT force a fixed structure.

6. Avoid unnecessary sections for simple questions.

Respond naturally like ChatGPT or Gemini.
"""
},
                {
                    "role": "user",
                    "content": message
                }
            ],
            temperature=0.3,
            max_tokens=500
        )

        reply = completion.choices[0].message.content

    except Exception as e:

        print("Groq API Error:", e)

        reply = "⚠️ AI assistant could not generate a response."

    return jsonify({"reply": reply})


# =====================================================
# RUN SERVER
# =====================================================

if __name__ == "__main__":
    app.run(debug=True)