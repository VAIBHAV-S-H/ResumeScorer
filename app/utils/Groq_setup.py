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

    def map_to_template(self):
        pass

    def render_latex(self):
        pass


class Groq:
    SYSTEM_TAILORING = """
        You are a smart assistant to career advisors at HiDevs. Your task is to evaluate resumes, provide ATS optimization scores, 
        and suggest improvements based on the given job description and title.
        Adhere to the following:
        - Ensure extracted details strictly align with job requirements.
        - Score each section independently and compute an overall score.
        - Provide actionable feedback for better alignment with the job description.
        - Also print the original content of resume before doing this and print the score 
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
        
        Perform a strict correspondence check between the content extracted from the JSON and the job description. Use the following guidelines to evaluate and score the match.

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
        Output Requirements
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
            "overallImprovementSuggestions": [str], // Suggestions for improving the profile
            "generalRecommendations": [str],    // General advice for the candidate
            "industrySpecificFeedback": [str]   // Recommendations tailored to the industry or role
        }
        Scoring Priorities:
        Deduct points for missing critical job qualifications or misaligned content.
        Add weight for:
            Quantifiable accomplishments.
            Clear STAR-based highlights.
            Strong use of relevant keywords.
        Note:
        Ensure the feedback is actionable and highlights both strengths and areas for improvement.
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

# job_title = "Mineral Processing Engineer"
# jd_text = """ Job description

# Experience in mineral processing equipment i.e. size reduction (Crushers, Grinding Mills), Dewatering (Thickeners, Filters), Gravity separation (Cyclones, Spiral classifier), Magnetic Separation (Low, Medium & High Intensity), Flotation cells, Slurry pumps etc. Should have good Knowledge of plant layout including utilities and should have the expertise of layout optimization based on the plant requirement.
# Experience in the field of basic and detail design in mineral processing plant and equipment (Iron ore, Lead-Zinc, Copper, Precious metals, Coal washeries etc). Should be able to provide the required water and air requirements and other utilities along with calculations for the Plant.
# Preparation of Process design Basis, Mass Balance, Process Flow Diagrams based on the test work and the Material characteristic provided by the customer., Piping & Instrumentation diagrams and selection of suitable material of construction.
# Preparation of bought out equipment duty condition/data sheets, Assist/evaluation of sizing and selection of equipment. Provide assistance with process inputs for piping, valves, electrical and instrumentation in Generation of Plant P&IDs.
# Assist in Plant layouts, sectional drawings and floor plans with load details; GA and manufacturing drawings; technological & support structures; Piping routing in 2D and 3D tools. Should be able to relate Mechanical, civil& Instrumentation requirements in conjunction with process.
# Executing commissioning activities at various stages like, pre-commissioning, cold & hot commissioning, capacity ramp up and performance testing.
# Process stabilization at customer site, Participating in Performance guarantees tests, technical warranty claim or customer complain handling. Should have knowledge of coning & quartering of samples, sieve analysis etc. Related to test work.
# Ensure that the work complies with relevant specification/standards, tolerances and ensure the material of constructions for the service and good for intended application.
# Knowledge of relevant safety requirements and design standards (Indian, European, America and International) & codes.
# Knowledge/exposure to material handling i.e. conveyor, feeders, silo/stockpile design; Utility system i.e. water, compressor air etc along with capacity calculations.
# Collaborate and partner with internal departments including Project, Proposal, Procurement, Field Service etc. Oversee improvement of engineering tools & data base.
# Support and ensure optimum scheduling for engineering, attend review meetings, and provide necessary reporting on a regular basis.
# Resolve engineering problems and concerns and work closely with client representatives to ensure problem resolution, give timely feedback, taking actions on eventual deviations.
# Ensure engineering tasks are delivered on time, on cost and on the quality and performance.
# Should be available to move frequently at customer sites for clarifications and meetings related to plant and process for providing assistance to sales and proposals.

# Role: Process Engineer
# Industry Type: Metals & Mining
# Department: Production, Manufacturing & Engineering
# Employment Type: Full Time, Permanent
# Role Category: Engineering
# Education
# UG: B.Tech/B.E. in Chemical, Mineral
# PG: M.Tech in Mineral
# Key Skills
# Skills highlighted with *  are preferred keyskills
# Mineral ProcessingMathcadProcess Engineering """

# file_path = "C:/Users/vaibh/OneDrive/Desktop/genai-hidevs/ResumeScorer/app/utils/ResumeVaibhav.pdf"

# groq = Groq()
# result = groq.generate_strict_scoring(job_title=job_title, jd_text=jd_text, file_path=file_path)
# print(result)
