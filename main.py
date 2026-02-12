import streamlit as st
from google import genai # Use the new SDK specifically
import json
import os 


try:
    GOOGLE_API_KEY = GOOGLE_API_KEY = st.secrets["GOOGLE_API_KEY"]
except FileNotFoundError:
    # Fallback for local testing if you have an .env file or just want to paste it temporarily (don't commit this!)
    GOOGLE_API_KEY = "YOUR_API_KEY_HERE_ONLY_FOR_LOCAL_TESTING" 

# Initialize the client using the safe key
client = genai.Client(api_key=GOOGLE_API_KEY)

# --- Logic Functions ---

def parse_brain_dump(text_input):
    sys_instruction = """
    You are a task extractor. Analyze the input text and output a JSON list of tasks.
    Each task must have:
    - "task": The task name
    - "time_min": Estimated minutes (integer)
    - "energy": Energy level (Low, Neutral, High)
    
    Example Input: "Buy milk and email boss"
    Example Output: [{"task": "Buy milk", "time_min": 15, "energy": "Low"}, {"task": "Email Boss", "time_min": 5, "energy": "High"}]
    
    Return ONLY raw JSON.
    """

    prompt = f"{sys_instruction}\n\n{text_input}"

    try:
        # UPDATED: Use the 'client' variable we created above
        response = client.models.generate_content(model="gemini-2.0-flash", contents=prompt)
        # Note: I changed the model to 'gemini-2.0-flash' or 'gemini-1.5-flash' 
        # because 'gemma-3-1b-it' might not be available via the API yet depending on your region/access.
        
        cleaned_text = response.text.replace("```json", "").replace("```", "").strip()
        return json.loads(cleaned_text)

    except Exception as e:
        st.error(f"Error parsing brain dump: {e}")
        return []

def get_recommendation(tasks, time, energy):
   prompt = f"""
   I have these tasks: {json.dumps(tasks)}
   My current context: Time: {time} min, Energy: {energy}
   Goal: Pick the SINGLE best task.
   """
   # UPDATED: Use the 'client' variable
   response = client.models.generate_content(model="gemini-2.0-flash", contents=prompt)
   return response.text

