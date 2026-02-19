import os
from groq import Groq
from dotenv import load_dotenv

load_dotenv()

try:
    client = Groq(api_key=os.environ.get("GROQ_API_KEY"))
    models = client.models.list()
    print("Available Models:")
    for model in models.data:
        print(model.id)
except Exception as e:
    print(f"Error listing models: {e}")
