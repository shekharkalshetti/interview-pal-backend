from flask import Blueprint, request, jsonify
from app.services.interview_service import interview_controller

interview_bp = Blueprint('interview', __name__)


@interview_bp.route('/generate-questions', methods=['POST'])
def api_generate_questions():
    """API endpoint to generate interview questions."""
    try:
        # Get request data
        data = request.json

        if not data or 'user_id' not in data or 'job_description' not in data:
            return jsonify({"error": "Missing required fields: user_id and job_description"}), 400

        user_id = data['user_id']
        job_description: str = data['job_description']

        # Fetch resume
        resume_text: str = interview_controller.fetch_resume(user_id)

        if resume_text is None:
            return jsonify({"error": f"No resume found for user_id: {user_id}"}), 404

        # Generate questions
        questions = interview_controller.generate_interview_questions(
            resume_text, job_description)

        # Return the questions
        return jsonify(questions)

    except Exception as e:
        return jsonify({"error": str(e)}), 500


@interview_bp.route('/feedback', methods=['POST'])
def feedback():
    """API endpoint to generate feedback for interview results."""
    try:
        # Get request data
        data = request.json

        if not data or 'answers' not in data or 'questions' not in data:
            return jsonify({"error": "Missing required fields: answers and questions"}), 400

        answers = data['answers']
        questions = data['questions']
        job_description = data.get('job_description', '')  # Optional field

        # Generate feedback using LLM
        feedback = interview_controller.generate_feedback(
            questions, answers, job_description)

        # Return the feedback
        return jsonify(feedback)

    except Exception as e:
        return jsonify({"error": str(e)}), 500
