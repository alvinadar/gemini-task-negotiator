import streamlit as st
import google.generativeai as genai
from google import genai
import json
import os 

GOOGLE_API_KEY = "AIzaSyAftXtE0G4-hkENF4ks97g0Zu7y9563Kl4"

#genai.configure(api_key=GOOGLE_API_KEY)

#model = genai.GenerativeModel('gemini-3-flash-preview')
model = genai.Client(api_key=GOOGLE_API_KEY)



#--Logic Functions--#

#--Create an app for brain dumping to prioritize tasks--#

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
        response = model.models.generate_content(model = "gemma-3-1b-it", contents=prompt)
        cleaned_text = cleaned_text = response.text.replace("```json", "").replace("```", "").strip()
        return json.loads(cleaned_text)

    except Exception as e:
        st.error(f"Error parsing brain dump: {e}")
        return []
    
def get_recommendation(tasks, time, energy):
   """
   Sends the structured list + context to Gemini to pick a winner.
   """
   prompt = f"""
   I have these tasks: {json.dumps(tasks)}
  
   My current context:
   - Time available: {time} minutes
   - Energy level: {energy}
  
   Your Goal:
   Pick the SINGLE best task for me to do right now.
  
   Output Format:
   1. Start with "DO THIS: [Task Name]"
   2. Then provide a bulleted list of 2-3 reasons why this fits my current energy and time.
   3. Be encouraging but firm.
   """
  
   response = model.models.generate_content(model = "gemma-3-1b-it", contents=prompt)
   return response.text
  
  # --- STREAMLIT USER INTERFACE ---


st.set_page_config(page_title="Task Negotiator", page_icon="🧠")


st.title("🧠 Gemini Task Negotiator")
st.caption("Powered by Google Gemini 1.5 Flash")


# Initialize session state to keep data alive between button clicks
if 'tasks' not in st.session_state:
   st.session_state.tasks = []


# SECTION 1: BRAIN DUMP
with st.expander(" Step 1: Brain Dump (Click to Open)", expanded=not st.session_state.tasks):
   st.write("Type everything on your mind. Don't worry about formatting.")
   dump = st.text_area("Ex: 'Need to email boss, buy milk, fix the door handle...'")
  
   if st.button("Analyze Tasks"):
       if dump:
           with st.spinner("Gemini is organizing your life..."):
               st.session_state.tasks = parse_brain_dump(dump)
       else:
           st.warning("Please type something first!")


# SECTION 2: THE LIST
if st.session_state.tasks:
   st.divider()
   st.subheader(" Your Structured List")
   # Display the JSON data as a clean table
   st.table(st.session_state.tasks)


   st.divider()


   # SECTION 3: THE NEGOTIATION
   st.subheader("Step 2: What should I do NOW?")
  
   col1, col2 = st.columns(2)
   with col1:
       time_avail = st.slider("Time Available (Minutes)", 5, 120, 30)
   with col2:
       energy_level = st.select_slider("Current Energy", options=["Zombie 🧟", "Low 🔋", "Neutral 😐", "High ⚡", "God Mode 🚀"], value="Neutral 😐")
  
   if st.button("✨ Pick My Task"):
       with st.spinner("Negotiating with your brain..."):
           recommendation = get_recommendation(st.session_state.tasks, time_avail, energy_level)
           st.success("### Recommendation")
           st.markdown(recommendation)


   # Reset Button
   if st.button("Clear & Start Over"):
       st.session_state.tasks = []
       st.rerun()
  