import os
import json
from utils import Utils
from langchain_groq import ChatGroq
from langchain_core.messages import SystemMessage, HumanMessage
from dotenv import load_dotenv
import re
# Load environment variables
load_dotenv()


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

job_title = "Quantum Computing Developer"
jd_text = """ BosonQ Psi is looking for a Quantum Computing Developer who will play a pivotal role in driving. innovation within our simulation-as-a-service (Q-SaaS) software suite, BQPhy.As part of this role, you'll collaborate extensively across teams to develop state-of-the-art quantum algorithms, leveraging languages such as Qiskit and PennyLane to enhance hybrid quantum-classical workflows

Apply now to be a part of revolutionizing computational science and pushing the boundaries of Quantum Computing and join us and shape the future of simulations for diverse industries

Responsibilities. Design, implement, and evaluate quantum algorithms tailored for machine learning, optimization, and simulation applications

Collaborate closely with researchers, engineers, and domain experts to translate intricate problem domains into efficient quantum computational workflows

Develop and optimize hybrid quantum-classical algorithms to harness the synergies between quantum and classical computing resources

Utilize quantum programming languages, libraries, and frameworks such as Qiskit, PennyLane, Cirq, or equivalent to realize quantum algorithms and applications

Lead the integration of quantum solutions into real-world applications and contribute to the evolution of scalable quantum computing infrastructure

Stay updated with the latest advancements in quantum computing, machine learning, and optimization fields, and actively participate in thought leadership within the organization and the wider scientific community

Employ familiarity with GPU technologies to enhance computational performance

Upskill other team members by conducting knowledge awareness sessions and workshops internally

Requirements. Bachelors/Masters degree in Computer Science, Physics, Mathematics, or a related field with a focus on quantum computing

Hands-on experience in designing and implementing quantum algorithms for machine learning, optimization, or simulation, preferably within a research or industry context

Proficiency in Python, quantum programming languages such as Qiskit, PennyLane, Cirq, or equivalent, along with the adaptability to work with less mainstream quantum frameworks

Strong mathematical and algorithmic prowess, accompanied by a profound understanding of quantum computing principles and quantum information theory

Demonstrated ability to collaborate effectively in cross-functional teams and take ownership of projects from inception to fruition

Exceptional communication and presentation skills, capable of elucidating complex technical concepts to both technical and non-technical stakeholders

A passion for pushing the boundaries of computational science and catalyzing impactful advancements in quantum computing

Proficiency in utilizing cloud platforms like AWS and Azure is desirable

Tech Stack. Must-have: Python, Qiskit, PennyLane, familiarity with C++. Good to have: Experience with cloud platforms (AWS, Azure),. We welcome people from all backgrounds and embrace gender diversity. We're committed to building a team that reflects the richness of the talent pool, and we encourage applications from everyone who has the skills and passion to thrive in this role
Role: Data warehouse Developer
Industry Type: Recruitment / Staffing
Department: Engineering - Software & QA
Employment Type: Full Time, Permanent
Role Category: DBA / Data warehousing
Education
UG: Any Graduate
PG: Any Postgraduate
Key Skills
mathematicspresentation skillsgpsalgorithmscommunication skillsprogrammingquantum """

file_path = "C:/Users/vaibh/OneDrive/Desktop/genai-hidevs/ResumeScorer/app/utils/ResumeVaibhav.pdf"

groq = Groq()
result = groq.generate_strict_scoring(job_title=job_title, jd_text=jd_text, file_path=file_path)
print(result)
