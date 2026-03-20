import os
from flask import Flask, request, jsonify, session

try:
    from google import genai
except ImportError:
    print("The 'google-genai' package is not installed.")
    exit(1)

# Ensure the API key is accessible for genai.Client()
api_key = os.environ.get("GEMINI_API_KEY", "AIzaSyBXfMy_Uhye8IQE7C8uSUBb7Sl6yQEWXMM")

app = Flask(__name__, static_folder='static')
app.secret_key = "super_secret_fitness_key_for_sessions"
client = genai.Client(api_key=api_key)

chat_sessions = {}

@app.route('/')
def serve_index():
    return app.send_static_file('index.html')

@app.route('/api/generate_plan', methods=['POST'])
def generate_plan():
    data = request.json
    metrics = data.get('metrics', {})
    uid = data.get('uid', 'anonymous')
    
    prompt = f"""
You are an expert Certified Personal Trainer and Registered Dietitian.
Based on the following user profile, create a structured, personalized fitness and diet plan.
Make it highly tailored to their specific answers. Keep it engaging, encouraging, and professional.

User Profile:
- Age, Gender, Height, Weight: {metrics.get('basic')}
- Primary Goal: {metrics.get('goal')}
- Dietary Preferences/Restrictions: {metrics.get('diet')}
- Lifestyle Activity Level: {metrics.get('activity')}
- Lifter Experience Level: {metrics.get('experience')}
- Gym Commitment/Access: {metrics.get('days')}
- Health Conditions/Injuries: {metrics.get('health')}

Provide:
1. A brief encouraging introductory message.
2. A customized Nutrition Plan (Macros, calories strategy, meal ideas based on their diet preferences).
3. A customized Workout Routine (Split, specific exercises, reps/sets based on their experience and equipment).
4. Hydration and Supplement recommendations.

Please format the response nicely with headings and line breaks, keeping it clean and easy to read.
"""
    try:
        chat = client.chats.create(model='gemini-2.5-flash')
        response = chat.send_message(prompt)
        
        chat_sessions[uid] = chat
        return jsonify({"plan": response.text})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/chat', methods=['POST'])
def chat():
    data = request.json
    message = data.get('message', '')
    uid = data.get('uid', 'anonymous')
    plan_text = data.get('plan_text', '')
    
    chat_session = chat_sessions.get(uid)
    if not chat_session:
        if not plan_text:
            return jsonify({"error": "Please generate a plan first before chatting."}), 400
        
        # Seed a new chat with the user's plan for context
        chat_session = client.chats.create(model='gemini-2.5-flash')
        chat_session.send_message(f"We generated this amazing fitness plan for me previously, just acknowledge it with 'Ready!': {plan_text}")
        chat_sessions[uid] = chat_session
        
    try:
        response = chat_session.send_message(message)
        return jsonify({"response": response.text})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(host='127.0.0.1', port=5000, debug=True)
