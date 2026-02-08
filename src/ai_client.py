import requests
import json
import time
from .config import GEMINI_API_KEY

class JulesAI:
    def __init__(self, api_key=None):
        self.api_key = api_key or GEMINI_API_KEY
        self.base_url = "https://generativelanguage.googleapis.com/v1beta/models/gemini-pro:generateContent"

    def generate_content(self, prompt, retries=3, backoff_factor=1):
        """
        Generates content using the Gemini API with retry logic.
        """
        if not self.api_key:
            raise ValueError("GEMINI_API_KEY is not set.")

        url = f"{self.base_url}?key={self.api_key}"
        payload = {"contents": [{"parts": [{"text": prompt}]}]}
        headers = {"Content-Type": "application/json"}

        for attempt in range(retries):
            try:
                response = requests.post(url, json=payload, headers=headers)
                response.raise_for_status()
                data = response.json()

                if 'candidates' in data and data['candidates']:
                    return data['candidates'][0]['content']['parts'][0]['text']
                else:
                    # Log warning about unexpected structure but don't retry as it's a valid response
                    return f"Error: No candidates returned. Response: {json.dumps(data)}"

            except requests.exceptions.RequestException as e:
                if attempt < retries - 1:
                    sleep_time = backoff_factor * (2 ** attempt)
                    print(f"API call failed: {e}. Retrying in {sleep_time}s...")
                    time.sleep(sleep_time)
                else:
                    return f"Error calling Gemini API after {retries} attempts: {str(e)}"
            except Exception as e:
                return f"Unexpected error: {str(e)}"
