import os
import google.generativeai as genai
from langchain_core.messages import SystemMessage
from dotenv import load_dotenv
import os

# Load environment variables from .env file
load_dotenv()

# Access the GOOGLE_API_KEY environment variable
google_api_key = os.getenv("GOOGLE_API_KEY")

genai.configure(api_key=google_api_key)

# Configure the model for concise responses
generation_config = {
    "temperature": 0.75,
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
chat_session = model.start_chat(
    history=[
        {"role": "user", "parts": "Please go by the name Memory Mate and by my therapist-like companion."}
    ]
)
SystemMessage("You are Memory Mate, a therapist conversational AI designed to assist users with their mental health and provide support. Treat all users kindly, regardless of their statements. Keep your responses warm, brief, and empathetic. Engage users by asking questions to maintain the conversation and offer comfort.")

# Example message with explicit brevity request
def send_message(message):
    response = chat_session.send_message(message)
    #print(response)
    return response

# Method to summarize the chat
def summarize_chat():
    summary_prompt = "Please summarize the conversation so far."
    summary_response = chat_session.send_message(summary_prompt)
    return summary_response

# Example usage
if __name__ == "__main__":
    # Send a message
    print(send_message("I'm feeling a bit down today."))
    
    # Summarize the chat
    print(summarize_chat())