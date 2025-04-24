import os
import google.generativeai as genai

# Set the API key (ensure it's set securely)
if "GEMINI_API_KEY" not in os.environ:
    os.environ["GEMINI_API_KEY"] = "AIzaSyAd5ZK7H9O65y1VBuoj3OT9Fs3SKcnbDGI"

genai.configure(api_key=os.environ["GEMINI_API_KEY"])

# Configure the model for concise responses
generation_config = {
    "temperature": 0.5, 
    "top_p": 0.9,        
    "top_k": 30,         
    "max_output_tokens": 200,  
    "response_mime_type": "text/plain",
}

# Initialize the fine-tuned model
model = genai.GenerativeModel(
    model_name="tunedModels/limitedrowsdataset-ufb2lccvub1p",
    generation_config=generation_config,
)

# Start chat with system-level instruction
chat_session = model.start_chat(history=[
    {"role": "user", "parts": ["Keep responses simple yet compassionate. At most 3 sentences. Avoid unnecessary details."]}
])

# Example message with explicit brevity request
def send_message(message):
    response = chat_session.send_message(message)
    print(response)
    return response

