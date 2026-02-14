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
        response = client.models.generate_content(model="gemma-3-1b-it", contents=prompt)
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
   response = client.models.generate_content(model="gemma-3-1b-it", contents=prompt)
   return response.text


# Create the streamlite app
st.set_page_config(page_title="Task Negotiatior",page_icon="🧠") 

st.title("🧠 Germini Task Negotiator")
st.caption("Power by Google Germini gemma-3-1b-it")

# Initialize session state to keep data alive between button clicks

if 'tasks' not in st.session_state:
    st.session_state.tasks = []

#SECTION 1 : BRAIN DUMP 
with st.expander("Step 1 :Brain Dump (Click to Open)", expanded = not st.session_state.tasks):
    st.write("Type everything on your mind.Dont worry about formatting.")
    dump = st.text_area("Ex: 'Need to email boss, buy milk, fix the door handle...'")
    if st.button("Analyze Task"):
        if dump:
            with st.spinner("Germini is organizing your life...."):
                st.session_state.task = parse_brain_dump(dump)
        else:
            st.warning("Please type something first!")
if st.session_state.tasks:
    st.devider()
    st.subheader("Your Sturctured List")
    #Display the JSON data as a clean table 
    st.table(st.session_state.task)

    st.devider()

# SECTION 3: THE NEGOTIATION
st.subheader("Step 2 : What should I do NOW ?")
col1,col2 = st.columns(2)
with col1:
    time_avail = st.slider("Time Available (Minutes)",5,120,30)
with col2:
    energy_level = st.select_slider("Current Energy",
 options=["Zombie 🧟", "Low 🔋", "Neutral 😐", "High ⚡", "God Mode 🚀"], value="Neutral 😐")
if st.button("✨ Pick My Task"):
    with st.spinner("Negotiating with your brain....."):
        recommendation = get_recommendation(st.session_state.task,time_avail,energy_level)
        st.success("###Recomendation")
        st.markdown(recommendation)

if st.button("Clear & Start Over"):
    st.session_state.task = []
    st.rerun()
