import os
import json
import google.generativeai as genai

# Ensure your .env file is loaded and GEMINI_API_KEY is available
genai.configure(api_key=os.environ.get("GEMINI_API_KEY"))

def analyze_resume_text(resume_text, job_description):
    try:
        model = genai.GenerativeModel('gemini-2.5-flash') 
        
        prompt = f"""
        You are an expert Applicant Tracking System (ATS). 
        Analyze the candidate's Resume against the provided Job Description.
        
        RESUME:
        {resume_text}
        
        JOB DESCRIPTION:
        {job_description}
        
        Evaluate the match carefully. Return your analysis STRICTLY as a valid JSON object without markdown formatting (do not use ```json).
        Use this exact schema:
        {{
            "candidate_name": "Extracted Name",
            "experience_years": 5,
            "skills": ["skill1", "skill2"],
            "matched_skills": ["matched_skill1"],
            "missing_skills": ["missing_skill1"],
            "match_score": 85
        }}
        
        Rules:
        - match_score must be an integer from 0 to 100 based on how well the candidate fits the requirements.
        - missing_skills should only list core requirements they are lacking.
        """
        
        response = model.generate_content(prompt)
        text_response = response.text.strip()
        
        # Handle the malformed JSON edge case if Gemini stubbornly includes markdown blocks
        if text_response.startswith("```"):
            text_response = text_response.strip("`").replace("json\n", "", 1).strip()
            
        return json.loads(text_response)
        
    except json.JSONDecodeError:
        # Edge Case: Malformed JSON response
        return {"error": "Failed to parse JSON. Gemini returned malformed data."}
    except Exception as e:
        # Edge Case: General AI Engine failure or quota limits
        return {"error": f"AI Engine Failure: {str(e)}"}