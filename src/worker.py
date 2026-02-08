from .ai_client import JulesAI
from .config import GEMINI_API_KEY

class ServiceAgent:
    def __init__(self):
        self.ai = JulesAI(api_key=GEMINI_API_KEY)

    def execute_task(self, skill, instructions):
        """
        Executes a freelance task based on the skill and instructions using the AI.

        Args:
            skill (str): The skill category (e.g., 'Excel/SQL', 'SEO/Writing', 'Marketing').
            instructions (str): The specific project description or task instructions.

        Returns:
            str: The generated deliverable (code, article, strategy, etc.).
        """
        prompt = ""

        if "Excel" in skill or "SQL" in skill or "Python" in skill or "VBA" in skill:
            prompt = f"""
            You are an expert Automation Engineer and Data Analyst.
            Task: Generate the complete code solution for the following request.
            Skill: {skill}
            Instructions: {instructions}

            Output Requirements:
            - Provide ONLY the code block (VBA, SQL, Python) ready to copy-paste.
            - Include brief comments explaining key parts of the code.
            - Ensure the code is optimized for performance and error handling.
            """

        elif "SEO" in skill or "Writing" in skill or "Copywriting" in skill:
            prompt = f"""
            You are a Senior SEO Specialist and Content Writer.
            Task: Write a high-quality, SEO-optimized article or copy based on the request.
            Skill: {skill}
            Instructions: {instructions}

            Output Requirements:
            - Use proper H1, H2, H3 heading structure.
            - Integrate SEO keywords naturally.
            - Ensure the tone is professional and engaging.
            - Focus on 'Information Gain' and E-E-A-T principles.
            """

        elif "Marketing" in skill or "Ads" in skill:
            prompt = f"""
            You are a Digital Marketing Strategist.
            Task: Create a marketing strategy or ad copy based on the request.
            Skill: {skill}
            Instructions: {instructions}

            Output Requirements:
            - Define target audience and key messaging.
            - Provide specific Ad Copy (Headline, Primary Text, CTA).
            - Suggest campaign structure (CBO/ABO) and targeting.
            """

        else:
            # General fallback
            prompt = f"""
            You are an expert Freelancer.
            Task: Execute the following professional task to the highest standard.
            Skill: {skill}
            Instructions: {instructions}
            """

        try:
            return self.ai.generate_content(prompt)
        except Exception as e:
            return f"Error executing task: {str(e)}"
