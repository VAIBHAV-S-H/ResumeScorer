from fastapi import FastAPI, File, Form, UploadFile
from fastapi.responses import JSONResponse
from PyPDF2 import PdfReader
from dotenv import load_dotenv
from langchain_groq import ChatGroq
import re
import os

# Load environment variables
load_dotenv()

# Initialize FastAPI app
app = FastAPI()

# Initialize the Groq API client directly (without proxy)
groq_api_key = "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" 
groq_client = ChatGroq(
    temperature=0.2,
    groq_api_key=groq_api_key,
    model="llama-3.1-70b-versatile"  # Adjust the model name as needed
)

def generate_completion(prompt):
    """
    Generate a response using the Groq LLM.
    """
    try:
        # Generate the response using the Groq API
        response = groq_client.invoke(prompt)
        
        # Return the content of the response if available
        return response.content.strip() if response and hasattr(response, "content") else "No content returned"
    except Exception as e:
        return f"Error: {str(e)}"

@app.post("/upload-resume/")
async def upload_resume(
    resume: UploadFile,
    job_description: str = Form(...),
    extra_prompt: str = Form(""),
):
    """
    Endpoint to evaluate the resume against a job description.
    """
    try:
        # Extract text from the uploaded resume
        pdf_reader = PdfReader(resume.file)
        resume_text = " ".join([page.extract_text() for page in pdf_reader.pages])

        # Work Experience Extraction Prompt
        work_exp_prompt = f"Extract work experience and skills from this resume: {resume_text}."
        work_experience = generate_completion(work_exp_prompt)

        # JD Scoring Prompt
        jd_prompt = f"""
            Evaluate this JD: {job_description} against the resume: {work_experience}. 
            Additional instructions: {extra_prompt}.
            Provide the following analysis:
            1. Overall Score (out of 100).
            2. Readability Score (out of 100).
            3. ATS Compatibility Score (out of 100).
            4. Keyword Match (Matched Keywords, Missing Keywords).
            5. Skills Gap Analysis (Present Skills, Suggested Skills).
            6. Format Analysis (Structure, Length).
            7. Impact Analysis (Impactful Phrases, Weak Phrases).
            8. Overall Improvement Suggestions.
        """
        jd_score_response = generate_completion(jd_prompt)

        # Extract details from the response using regex
        sections = {
            "overall_score": re.search(r"Overall Score:\s*(\d+)", jd_score_response),
            "readability_score": re.search(r"Readability Score:\s*(\d+)", jd_score_response),
            "ats_score": re.search(r"ATS Compatibility Score:\s*(\d+)", jd_score_response),
            "keyword_match": re.search(r"Matched Keywords:\s*(.+?)\n", jd_score_response),
            "missing_keywords": re.search(r"Missing Keywords:\s*(.+?)\n", jd_score_response),
            "skills_gap_present": re.search(r"Present Skills:\s*(.+?)\n", jd_score_response),
            "skills_gap_suggested": re.search(r"Suggested Skills:\s*(.+?)\n", jd_score_response),
            "format_analysis": re.search(r"Format Analysis:\s*(.+?)\n", jd_score_response),
            "impact_phrases": re.search(r"Impactful Phrases:\s*(.+?)\n", jd_score_response),
            "weak_phrases": re.search(r"Weak Phrases:\s*(.+?)\n", jd_score_response),
            "improvement_suggestions": re.search(r"Overall Improvement Suggestions:\s*(.+?)\n", jd_score_response),
        }

        # Parse and clean the extracted sections
        result = {key: (match.group(1).strip() if match else "N/A") for key, match in sections.items()}

        # Return structured data along with feedback
        return JSONResponse(
            content={
                "feedback": jd_score_response,
                "structured_analysis": result,
                "metrics": {
                    "overall_score": int(result["overall_score"]),
                    "readability_score": int(result["readability_score"]),
                    "ats_score": int(result["ats_score"]),
                }
            },
            status_code=200,
        )
    except Exception as e:
        return JSONResponse(content={"error": str(e)}, status_code=500)

# To run the FastAPI server using Uvicorn:
# uvicorn backend.app:app --reload
