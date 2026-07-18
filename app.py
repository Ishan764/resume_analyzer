import os
import json
from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
from core.parser import extract_text_from_pdf
from core.ai_engine import analyze_resume_text

app = Flask(__name__)
CORS(app) # <-- CORS is enabled and app is only declared ONCE!

# --- 1. System Configuration ---
UPLOAD_FOLDER = 'uploads'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# Configure the local SQLite database
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///candidates.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# --- 2. Initialize Database ---
db = SQLAlchemy(app)

# --- 3. Define the Database Schema ---
class Candidate(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    experience_years = db.Column(db.Integer)
    # Databases don't easily store Python lists, so we store the skills as a JSON string
    skills = db.Column(db.Text) 
    job_description = db.Column(db.Text)
    match_score = db.Column(db.Integer)
    missing_skills = db.Column(db.Text)

# --- 4. The API Routing Engine ---
@app.route('/analyze', methods=['POST'])
def analyze_resume():
    if 'file' not in request.files:
        return jsonify({"error": "No file part in the request"}), 400
        
    file = request.files['file']
    
    job_description = request.form.get('job_description', '').strip()
    if not job_description:
        return jsonify({"error": "Missing job_description. Please provide the job details to match against."}), 400
    
    if file.filename == '':
        return jsonify({"error": "No selected file"}), 400

    if file and file.filename.endswith('.pdf'):
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
        file.save(file_path)
        
        try:
            # Phase 2: Extract text
            raw_text = extract_text_from_pdf(file_path)
            if not raw_text or len(raw_text.strip()) < 10:
                return jsonify({"error": "PDF is empty or unparseable. Please upload a valid text-based PDF."}), 400
            
            # Phase 3: AI Analysis (Now passing the job description!)
            ai_analysis = analyze_resume_text(raw_text, job_description)
            
            if "error" in ai_analysis:
                return jsonify(ai_analysis), 500

            # Phase 4: Save strictly to Database
            new_candidate = Candidate(
                name=ai_analysis.get("candidate_name", "Unknown"),
                experience_years=ai_analysis.get("experience_years", 0),
                skills=json.dumps(ai_analysis.get("skills", [])),
                job_description=job_description,
                match_score=ai_analysis.get("match_score", 0),
                missing_skills=json.dumps(ai_analysis.get("missing_skills", []))
            )
            db.session.add(new_candidate)
            db.session.commit()
            
            return jsonify({
                "status": "Success",
                "message": "Resume analyzed and permanently saved to database!",
                "database_id": new_candidate.id,
                "analysis": ai_analysis
            }), 200
            
        except Exception as e:
            return jsonify({"error": f"Server processing pipeline broken: {str(e)}"}), 500
        
    return jsonify({"error": "Invalid file architecture. Only PDF inputs allowed."}), 400

@app.route('/candidates', methods=['GET'])
def get_candidates():
    """
    Retrieves all analyzed candidates from the database and returns them.
    """
    try:
        # Pull every record out of the Candidate table
        all_candidates = Candidate.query.all()
        
        # Serialize the database rows into a clean Python list of dictionaries
        results = []
        for candidate in all_candidates:
            results.append({
                "id": candidate.id,
                "name": candidate.name,
                "experience_years": candidate.experience_years,
                # Convert the JSON string back into a true Python list for the API response
                "skills": json.loads(candidate.skills) if candidate.skills else [],
                "match_score": candidate.match_score,
                "missing_skills": json.loads(candidate.missing_skills) if candidate.missing_skills else []
            })
            
        return jsonify({
            "status": "Success",
            "total_candidates": len(results),
            "candidates": results
        }), 200
        
    except Exception as e:
        return jsonify({"error": f"Failed to retrieve database records: {str(e)}"}), 500

if __name__ == '__main__':
    # Automatically build the database file and tables before booting
    with app.app_context():
        db.create_all()
    app.run(debug=True, port=5001)