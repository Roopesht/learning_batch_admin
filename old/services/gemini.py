import requests
import os
from dotenv import load_dotenv

load_dotenv()
api_key = os.getenv("GEMINI_API_KEY", "")

def get_response(system_message: str, user_message: str, model="gemini-2.0-flash") -> str:
    """
    Sends messages to Google Gemini API and returns the model's response.
    system_message: context for Gemini
    user_message: actual text to rephrase or process
    """
    url = f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent?key={api_key}"
    headers = {"Content-Type": "application/json"}
    payload = {
        "contents": [
            {
                "role": "user",
                "parts": [
                    {"text": f"{system_message}\n\nUser: {user_message}"}
                ]
            }
        ]
    }

    response = requests.post(url, headers=headers, json=payload)
    response.raise_for_status()
    data = response.json()
    return data["candidates"][0]["content"]["parts"][0]["text"]
