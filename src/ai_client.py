import os
import requests
import json
from groq import Groq
from src.proposal_generator import generate_proposal as template_generator

class AIClient:
    def __init__(self):
        self.groq_api_key = os.getenv("GROQ_API_KEY")
        self.gemini_api_key = os.getenv("GEMINI_API_KEY")
        self.hf_token = os.getenv("HF_TOKEN")

        self.groq_client = Groq(api_key=self.groq_api_key) if self.groq_api_key else None

    def _call_groq(self, prompt):
        if not self.groq_client: return None
        try:
            completion = self.groq_client.chat.completions.create(
                model="llama3-70b-8192",
                messages=[{"role": "user", "content": prompt}],
                temperature=0.7,
            )
            return completion.choices[0].message.content
        except Exception as e:
            print(f"Groq Error: {e}")
            return None

    def _call_gemini(self, prompt):
        if not self.gemini_api_key: return None
        url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-pro:generateContent?key={self.gemini_api_key}"
        payload = {"contents": [{"parts": [{"text": prompt}]}]}
        try:
            response = requests.post(url, json=payload)
            response.raise_for_status()
            data = response.json()
            if 'candidates' in data and data['candidates']:
                return data['candidates'][0]['content']['parts'][0]['text']
            return None
        except Exception as e:
            print(f"Gemini Error: {e}")
            return None

    def _call_huggingface(self, prompt):
        if not self.hf_token: return None
        API_URL = "https://api-inference.huggingface.co/models/meta-llama/Meta-Llama-3.1-8B-Instruct"
        headers = {"Authorization": f"Bearer {self.hf_token}"}
        try:
            response = requests.post(API_URL, headers=headers, json={"inputs": prompt})
            if response.status_code == 200:
                return response.json()[0]['generated_text']
            return None
        except Exception as e:
            print(f"HF Error: {e}")
            return None

    def generate(self, project_desc, platform):
        prompt = f"""
        Act as Jules, a Senior Proposals Architect.
        Analyze this project from {platform}: '{project_desc}'
        Using the following arsenal:
        - Video: Pipeline Veo 3 + Nano Banana (4K Fidelity) + ElevenLabs (Sound Design).
        - Traffic: CAPI (Conversions API) + GTM Server-Side + Advanced Attribution Strategy.
        - SEO: GEO (Generative Engine Optimization) + AEO (Answer Engine Optimization) + Knowledge Graph @graph.
        - Content: Nugget Technique (Answer-First) + Information Gain (E-E-A-T).

        Generate a killer proposal in English. Focus on solving pain points.
        Return ONLY the proposal text.
        """

        # Try Groq
        print("Attempting Groq...")
        res = self._call_groq(prompt)
        if res: return res

        # Try Gemini
        print("Groq failed or key missing. Attempting Gemini...")
        res = self._call_gemini(prompt)
        if res: return res

        # Try HF
        print("Gemini failed or key missing. Attempting Hugging Face...")
        res = self._call_huggingface(prompt)
        if res: return res

        # Fallback to Template
        print("AI failed. Using Template...")
        return template_generator(platform, project_desc)
