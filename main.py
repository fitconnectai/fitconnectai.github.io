#!/home/arjav/myenv/bin/python
import time
import sys
import os

# Set your API key so you don't have to export it every time
os.environ["GEMINI_API_KEY"] = "AIzaSyBXfMy_Uhye8IQE7C8uSUBb7Sl6yQEWXMM"

try:
    from google import genai
except ImportError:
    print("The 'google-genai' package is not installed. Please install it using: pip install google-genai")
    sys.exit(1)

def print_slow(text, delay=0.03):
    """Prints text slowly to give a conversational feel."""
    for char in text:
        sys.stdout.write(char)
        sys.stdout.flush()
        time.sleep(delay)
    print()

def get_input(prompt):
    print_slow(prompt, 0.015)
    return input("> ")

def generate_plan(metrics):
    print_slow("\nAnalyzing your profile and generating your custom plan using AI...", 0.04)
    time.sleep(1)
    
    api_key = os.environ.get("GEMINI_API_KEY")
    if not api_key:
        print("\n[Error] GEMINI_API_KEY environment variable not found.")
        print("Please set your API key first to use the AI generator:")
        print("export GEMINI_API_KEY='your-api-key-here'")
        sys.exit(1)
        
    try:
        client = genai.Client()
        
        prompt = f"""
You are an expert Certified Personal Trainer and Registered Dietitian.
Based on the following user profile, create a structured, personalized fitness and diet plan.
Make it highly tailored to their specific answers. Keep it engaging, encouraging, and professional.

User Profile:
- Basic Metrics: {metrics.get('basic')}
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

Do not use markdown blocks formatting, just plain text with simple headers and dashes. Add spacing between sections.
"""
        response = client.models.generate_content(
            model='gemini-2.5-flash',
            contents=prompt,
        )
        
        plan = f"""
=========================================================
          YOUR AI-GENERATED FITNESS & DIET PLAN
=========================================================

{response.text}

=========================================================
Disclaimer: Please consult a doctor before starting any new 
fitness or diet regimen, especially given your health 
status/injuries: {metrics.get('health', 'None reported')}
=========================================================
"""
        print_slow(plan, 0.005)
    except Exception as e:
        print(f"\n[Error] Failed to generate plan using AI: {e}")
        sys.exit(1)

def main():
    print_slow("Hello! Welcome to your personalized fitness journey.")
    print_slow("As your dedicated Certified Personal Trainer and Registered Dietitian, I am here to help you achieve your goals.")
    print("\nBefore we dive in, please answer a few questions so I can tailor your plan:\n")
    
    try:
        metrics = {}
        
        metrics['basic'] = get_input("1. Basic Metrics: What is your age, gender, height, and current weight?")
        metrics['goal'] = get_input("2. Primary Goal: What is your main objective? (e.g., Fat loss, muscle hypertrophy, strength gain, endurance, or maintenance)")
        metrics['diet'] = get_input("3. Dietary Preferences & Restrictions: Do you have specific preferences (vegan, keto, etc.) or allergies?")
        metrics['activity'] = get_input("4. Activity Level: Outside the gym, how active is your daily lifestyle? (e.g., Sedentary desk job, active)")
        
        print_slow("5. Gym Experience & Access:", 0.015)
        metrics['experience'] = get_input("   - Are you a beginner, intermediate, or advanced lifter?")
        metrics['days'] = get_input("   - How many days a week can you commit to the gym? Do you have full gym access?")
        
        metrics['health'] = get_input("6. Health & Injuries: Do you have any past/current injuries or medical conditions I should know about?")
        
        generate_plan(metrics)
    except KeyboardInterrupt:
        print("\n\nSession cancelled. See you next time!")
        sys.exit(0)

if __name__ == "__main__":
    main()
