import os
import json
from utils import Utils  # Ensure this is implemented and available
from langchain_groq import ChatGroq
from langchain_core.messages import SystemMessage, HumanMessage
from dotenv import load_dotenv
import re
# Load environment variables
load_dotenv()


class Groq:
    SYSTEM_TAILORING = """
        You are a smart assistant to career advisors at HiDevs. Your task is to evaluate resumes, provide ATS optimization scores, and suggest improvements based on the given job description and title.
        Adhere to the following:
        - Ensure extracted details strictly align with job requirements.
        - Score each section independently and compute an overall score.
        - Provide actionable feedback for better alignment with the job description.
        - Also print the original content of resume before doing this and print the score 
    """

    FINAL_SCORING_PROMPT = """
        Based on the extracted JSON from the CV and the job description, perform a **strict correspondence check**.
        Guidelines for scoring:
        1. Compare **skills**, **projects**, and **work experience** directly against job requirements.
        2. Evaluate the alignment of education, certifications, and keywords with the job title and description.
        3. Deduct points for missing or irrelevant details in any section.
        4. Add weight to:
           - Quantifiable achievements.
           - STAR-methodology-based work highlights.
           - Strong alignment with job-specific keywords.

        **Output ONLY in the following JSON format:** 
            "overallScore": int,
            "alignmentFeedback": str,
            "overallMatch": str,
            "keywordMatch": {
                "matched": [str],
                "unmatched": [str]
            },
            "readabilityScore": str,
            "atsCompatibilityScore": int,
            "formatAnalysis": {
                "structure": str,
                "length": str
            },
            "impactAnalysis": {
                "impactfulPhrases": [str],
                "weakPhrases": [str]
            },
            "skillsGapAnalysis": {
                "presentSkills": [str],
                "suggestedSkills": [str]
            },
            "overallImprovementSuggestions": [str],
            "generalRecommendations": [str],
            "industrySpecificFeedback": [str]
        }
    """

    def __init__(self):
        self.llm = ChatGroq(
            temperature=0,
            groq_api_key=os.getenv("GROQ_API_KEY"),
            model="llama-3.1-70b-versatile",
        )

    def extract_json_from_cv(self, file_path):
        """Extract JSON data from the CV using utilities."""
        util = Utils()
        try:
            return util.extract_text(file_path=file_path)
        except Exception as e:
            print(f"Error extracting text from CV: {e}")
            return {}

   

    def generate_strict_scoring(self, job_title, jd_text, file_path):
        """Generate a strict correspondence scoring for the provided CV and job description."""
        try:
            # Step 1: Extract text from the CV
            cv_text = self.extract_json_from_cv(file_path)
            if not cv_text:
                return {"error": "Failed to extract text from CV."}

            # Step 2: Prepare the scoring prompt
            prompt = self.FINAL_SCORING_PROMPT
            prompt = prompt.replace("<CV_TEXT>", json.dumps(cv_text))  # Convert CV text to JSON string
            prompt = prompt.replace("<JD_TEXT>", jd_text)  # Replace with job description
            prompt = prompt.replace("<JOB_TITLE>", job_title)  # Replace with job title

            # Step 3: Invoke the LLM with the prompt
            response = self.llm.invoke(
                [
                    SystemMessage(content=self.SYSTEM_TAILORING),
                    HumanMessage(content=prompt),
                ]
            )

            # Step 4: Extract JSON from the response
            # Match the content inside the JSON block using regular expression
            json_match = re.search(r"```json\n(.*?)\n```", response.content, re.DOTALL)

            if not json_match:
                return {
                    "error": "Failed to extract JSON from LLM response.",
                    "raw_response": response.content,
                }

            json_content = json_match.group(1)

            # Step 5: Parse the JSON response
            try:
                return json.loads(json_content)
            except json.JSONDecodeError as e:
                return {
                    "error": "Failed to parse LLM response JSON.",
                    "raw_json": json_content,
                    "json_error": str(e),
                }

        except Exception as e:
            print(f"Error performing scoring: {e}")
            return {"error": str(e)}


# Example Usage
# Ensure environment variables are loaded and file paths are correct
job_title = "AI Engineer"
jd_text = """ Job description
Logistify is looking for AI Engineer to join our dynamic team and embark on a rewarding career journey.
Designing and developing AI algorithms and models to solve specific business problems
Creating and maintaining databases for storing and processing large amounts of data
Developing and deploying machine learning and deep learning models
Implementing and integrating AI solutions with existing systems and software
Analyzing and interpreting complex data sets to extract insights and drive decision-making
Collaborating with cross-functional teams to develop and deploy AI applications
Ensuring the security and privacy of data used in AI applications
Communicating and presenting technical information to non-technical stakeholders
Excellent communication skills & attention to detail
 
Role: Data Science & Machine Learning - Other
Industry Type: Legal
Department: Data Science & Analytics
Employment Type: Full Time, Permanent
Role Category: Data Science & Machine Learning
Education
UG: Any Graduate
PG: Any Postgraduate
Key Skills
image processingalgorithmspythonnatural language processingneural networksmachine learningartificial intelligencedeep learningtensorflowdata sciencecomputer visionkerastext miningopencvcommunication skillspattern recognition"""
file_path = "ResumeVaibhav.pdf"

groq = Groq()
result = groq.generate_strict_scoring(job_title=job_title, jd_text=jd_text, file_path=file_path)
print(json.dumps(result, indent=4))
