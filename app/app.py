from fastapi import FastAPI, File, UploadFile, Form, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
import shutil
import os
from utils.Groq_setup import Groq  # Importing Groq class from utils/Groq_setup.py

# Initialize FastAPI app
app = FastAPI()

# Serve static files for styles, images, etc.
app.mount("/static", StaticFiles(directory="static"), name="static")

# Set up Jinja2 templates
templates = Jinja2Templates(directory="templates")

# Initialize the Groq object
groq = Groq()

@app.get("/", response_class=HTMLResponse)
async def get_resume_scorer(request: Request):
    """
    Render the scorer.html template for the homepage.
    """
    return templates.TemplateResponse("scorer.html", {"request": request})

@app.post("/score_resume/", response_class=HTMLResponse)
async def score_resume(
    request: Request,
    job_title: str = Form(...),
    job_description: str = Form(...),
    resume_file: UploadFile = File(...),
):
    """
    Handle resume scoring requests.
    """
    # Save the uploaded file temporarily
    temp_file_path = f"temp_{resume_file.filename}"
    try:
        with open(temp_file_path, "wb") as buffer:
            shutil.copyfileobj(resume_file.file, buffer)

        # Call the Groq object for scoring
        result = groq.generate_strict_scoring(
            job_title=job_title, jd_text=job_description, file_path=temp_file_path
        )
    except Exception as e:
        # Handle errors gracefully
        error_message = f"An error occurred while processing the file: {str(e)}"
        return templates.TemplateResponse(
            "error.html",
            {"request": request, "error_message": error_message},
        )
    finally:
        # Clean up: Delete the temporary file after processing or in case of error
        if os.path.exists(temp_file_path):
            os.remove(temp_file_path)

    # Render results in the results.html template
    return templates.TemplateResponse(
        "results.html",
        {"request": request, "result": result, "job_title": job_title},
    )
