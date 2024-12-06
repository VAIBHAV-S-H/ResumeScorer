import os
import json
from langchain_groq import ChatGroq
from langchain_core.messages import SystemMessage, HumanMessage
from dotenv import load_dotenv
from PyPDF2 import PdfReader  
load_dotenv()

class Utils:
    def __init__(self):
        pass  # No need for initialization as PyPDF2 does not require API keys or configurations

    def extract_text(self, file_path):
        try:
            # Initialize a PDF reader
            reader = PdfReader(file_path)
            text_content = []

            # Extract text from each page
            for page in reader.pages:
                if page.extract_text():
                    text_content.append(page.extract_text())

            return "\n".join(text_content)
        except Exception as e:
            print(f"Error reading PDF: {e}")
            return ""
   


class Groq:
    SYSTEM_TAILORING = """
        You are a smart assistant for a Job recruitment process. Your task is to evaluate resumes, provide ATS optimization scores, 
        and suggest improvements based on the given job description and title.
        Adhere to the following:
        - Ensure extracted details strictly align with job requirements.
        - Score each section independently and compute an overall score strictly.
        - Provide actionable feedback for better alignment with the job description.
    """
    JSON_EXTRACT_PROMPT = """
        Given the text extracted from a resume, create a JSON object by organizing the information into the following sections:

        1. Personal Information: Include details like name, contact information, and address.
        2. Education: List educational qualifications, institutions, degrees, and graduation dates.
        3. Skills: Include technical and non-technical skills.
        4. Experience: Provide details about previous work experience, job roles, companies, and durations.
        5. Certifications: List any relevant certifications, along with issuing organizations and dates.
        6. Additional Sections: Include any other relevant sections such as projects, volunteer work, publications, etc.

        The output should be in JSON format, with each section properly labeled and containing relevant data.
        Here is the extracted resume text:
        <CV_TEXT>
        NO PREAMBLE and no inclusion of ```
    """
    FINAL_SCORING_PROMPT = """
        Job Title:
        <JOB_TITLE>
        
        Job Description:
        <JD_TEXT>
        
        Here is the extracted JSON object: 
        <JSON_TEXT>
        
        Perform a correct correspondence check between the content extracted from the JSON and the job description. 
        Use the following guidelines to evaluate and score the match:

        Evaluation Guidelines
        Skills, Projects, and Work Experience

        Directly compare these sections against job requirements for alignment.
        Deduct points for missing, irrelevant, or misaligned details.
        Education, Certifications, and Keywords

        Assess how well these aspects align with the job title and description.
        Pay special attention to job-specific keywords.
        Achievements and Highlights

        Add weight for quantifiable achievements and highlights following the STAR (Situation, Task, Action, Result) methodology.
        Keywords and Job-Specific Alignment

        Evaluate the presence and relevance of keywords that are essential for the role.
        Output Requirements:
        Return the evaluation strictly in the following JSON format:
        {
            "overallScore": int,                  // Overall score for the candidate’s match
            "alignmentFeedback": str,            // Feedback on the alignment of the candidate's profile with the job description
            "overallMatch": str,                 // Overall summary of the match (e.g., "Strong", "Moderate", "Weak")
            "keywordMatch": {
                "matched": [str],                // List of matched keywords
                "unmatched": [str]               // List of missing keywords
            },
            "readabilityScore": str,             // Assessment of the resume's readability (e.g., "High", "Moderate", "Low")
            "atsCompatibilityScore": int,        // Score based on ATS (Applicant Tracking System) compatibility
            "formatAnalysis": {
                "structure": str,                // Feedback on structure (e.g., "Well-organized", "Needs improvement")
                "length": str                    // Assessment of resume length (e.g., "Optimal", "Too short", "Too long")
            },
            "impactAnalysis": {
                "impactfulPhrases": [str],       // List of impactful phrases found in the resume
                "weakPhrases": [str]             // List of weak or generic phrases to avoid
            },
            "skillsGapAnalysis": {
                "presentSkills": [str],          // List of skills present in the candidate’s profile
                "suggestedSkills": [str]         // List of additional skills that could strengthen the profile
            },
            "overallImprovementSuggestions": [str (example)], // Suggestions for improving the profile
            "generalRecommendations": [str (example)],    // General advice for the candidate
            "industrySpecificFeedback": [str (example)]   // Recommendations tailored to the industry or role
        }
        Evaluation Guidelines:  

        Skills, Projects, and Work Experience:  
        - Directly compare these sections against job requirements for alignment.  
        - Prioritize relevant experience in reverse chronological order.  
        - Deduct points for missing, irrelevant, or misaligned details.  
        - Award points for impactful, quantifiable achievements using metrics (e.g., percentages, dollar amounts).  

        Education, Certifications, and Keywords:  
        - Evaluate alignment with the job title and description.  
        - Highlight professional certifications and degrees.  
        - Pay special attention to job-specific keywords and technical terms.  
        - Deduct points for irrelevant or missing certifications required for the role.  

        Achievements and Highlights:  
        - Focus on quantifiable results following the STAR (Situation, Task, Action, Result) methodology.  
        - Deduct points for vague or overly generic phrases.  

        Keywords and Job-Specific Alignment:  
        - Evaluate the presence and relevance of keywords essential for the role.  
        - Score higher for strategic use of role-specific and industry-standard terminology.  

        Readability and ATS Compatibility:  
        - Ensure the format is clean, structured, and ATS-compatible (avoid images, tables, or non-standard fonts).  
        - Deduct points for excessive or inconsistent formatting.  

        Resume Formatting:  
        - Evaluate the structure for clarity, readability, and organization (e.g., clear headers, bullet points).  
        - Length: Ensure the resume is concise and within one or two pages.  

        Language, Grammar, and Professionalism:  
        - Deduct points for spelling or grammar errors.  
        - Evaluate tone for professionalism and clarity.
          
        Scoring Priorities:
        Deduct points for missing critical job qualifications or misaligned content.
        Add weight for:
            Quantifiable accomplishments.
            Clear STAR-based highlights.
            Strong use of relevant keywords.
        Note:
        - Ensure the feedback is actionable and highlights both strengths and areas for improvement.
        - Do not hesitate to be brutally honest when you score the resume.
        - Do not be considerate to the candidate's feelings 
        - Score can be any number which is apt to the resume.
        - Be brutally strict.
        NO PREAMBLE and no inclusion of ```
    """

    def __init__(self):
        self.llm = ChatGroq(
            temperature=0,
            groq_api_key="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",
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
        
        # Step 1: Extract text from the CV
        cv_text = self.extract_json_from_cv(file_path)
        if not cv_text:
            return {"error": "Failed to extract text from CV."}

        # Step 2: Prepare the scoring prompt
        prompt = self.JSON_EXTRACT_PROMPT
        prompt = prompt.replace("<CV_TEXT>", json.dumps(cv_text))  # Convert CV text to JSON string
        
        # Step 3: Invoke the LLM with the prompt
        response = self.llm.invoke(
            [
                HumanMessage(content=prompt),
            ]
        )
        json_text = response.content
        prompt = self.FINAL_SCORING_PROMPT
        prompt = prompt.replace("<JSON_TEXT>", json_text)
        prompt = prompt.replace("<JD_TEXT>", jd_text)  # Replace with job description
        prompt = prompt.replace("<JOB_TITLE>", job_title)  # Replace with job title
        response = self.llm.invoke(
            [
                SystemMessage(content=self.SYSTEM_TAILORING),
                HumanMessage(content=prompt),
            ]
        )
        return response.content


