from app.config.supabase_client import supabase
from supabase.client import Client
import requests
import os
import json


def call_llm_api(messages, temperature=0.7, max_tokens=-1):
    """Make a call to the local LLM API."""
    try:
        payload = {
            "model": "qwen2.5-1.5b-instruct",
            "messages": messages,
            "temperature": temperature,
            "max_tokens": max_tokens,
            "stream": False
        }

        headers = {
            "Content-Type": "application/json"
        }

        response = requests.post(os.environ.get(
            'LLM_API_URL'), json=payload, headers=headers)

        if response.status_code == 200:
            return response.json()["choices"][0]["message"]["content"]
        else:
            raise Exception(
                f"LLM API returned status code {response.status_code}")
    except Exception as e:
        raise Exception(f"Failed to call LLM API: {str(e)}")


class InterviewService:
    def __init__(self, supabase_client: Client):
        self.supabase = supabase_client

    @staticmethod
    def fetch_resume(user_id):
        """Fetch user's resume from Supabase."""
        try:
            response = supabase.table("resumes").select(
                "content").eq("user_id", user_id).limit(1).execute()

            if response.data and len(response.data) > 0:
                return response.data[0]["content"]
            else:
                return None
        except Exception as e:
            raise Exception(f"Failed to fetch resume: {str(e)}")

    @staticmethod
    def generate_interview_questions(resume_text, job_description):
        """Generate interview questions based on resume and job description."""
        # Create the system prompt for the LLM
        system_prompt = """You are an expert technical interviewer for student and entry-level positions.
    Your task is to generate 8 targeted interview questions based on the candidate's resume and the job description.

    1. CORE TECHNICAL QUESTIONS (3): Ask about fundamental technical skills needed for the job, but phrase them in a friendly, straightforward way. Use simple English and avoid overly formal language.

    2. PROJECT-RELATED QUESTIONS (3): Reference specific projects from their resume, and ask about them as if you're genuinely curious. These should feel like natural follow-up questions a real interviewer might ask after glancing at their resume.

    3. BEHAVIORAL QUESTIONS (2): Make these sound like actual conversations, not rigid HR templates. Use relaxed phrasing like "Tell me about a time when..." or "How do you usually handle..." 

    - Write like you talk! Use contractions, simple words, and casual phrasing
    - Add a touch of humor where appropriate (nothing too cheesy)
    - Keep questions short and clear - no corporate jargon or complex sentences
    - Sound interested and curious about their experiences
    - Make technical questions less intimidating by using everyday language
    - Phrase questions in a way that invites storytelling, not just short answers

    Return the questions in the following JSON format:
    {
        "questions": [
            {
                "id": 1,
                "question": "question text here",
                "type": "technical|behavioral|project",
            },
            ...
        ]
    }
    
    Only return valid JSON, with no additional text before or after.
    """

        # Create the prompt with resume and job description
        user_prompt = f"""Please generate interview questions based on the following:
        
        RESUME:
        {resume_text}
        
        JOB DESCRIPTION:
        {job_description}
        """

        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ]

        # Call the LLM API
        response = call_llm_api(messages, temperature=0.7)

        # Parse the response as JSON
        try:
            # Find JSON in the response (in case there's any extra text)
            json_start = response.find('{')
            json_end = response.rfind('}') + 1

            if json_start >= 0 and json_end > json_start:
                json_str = response[json_start:json_end]
                return json.loads(json_str)
            else:
                raise ValueError("No JSON found in the response")
        except Exception as e:
            raise Exception(f"Failed to parse LLM response: {str(e)}")

    @staticmethod
    def generate_feedback(questions, answers, job_description):
        """Generate feedback using LLM based on questions and answers."""
        # Create the system prompt for the LLM
        system_prompt = """You are a senior technical interviewer and career coach with high standards.
        Your task is to critically evaluate a candidate's interview responses and provide honest, direct feedback.
        
        Be rigorous in your assessment. Candidates need honest feedback to improve, so don't sugarcoat your evaluation.
        Assume most entry-level candidates will score between 4-6 out of 10, with 8+ reserved only for truly exceptional answers.
        
        For each question and answer pair, provide:
        1. A realistic score out of 10 (be conservative - a score of 6 should be considered good, 8+ should be rare)
        2. Direct, specific feedback highlighting weaknesses before strengths
        3. Clear, actionable improvement suggestions with concrete examples of what would make a better answer
        
        Then provide an overall evaluation with:
        1. An accurate overall score out of 10 (again, be critical)
        2. Brief acknowledgment of strengths
        3. Detailed critique of major weaknesses, being specific about shortcomings
        4. Precise, actionable improvement advice that would significantly elevate their interview performance
        
        Be direct and straightforward - don't soften criticism with excessive positivity. Focus on substance over style.
        For students or entry-level candidates, be constructive but honest about how they compare to industry expectations.
        
        Return the feedback in the following JSON format:
        {
            "question_feedback": [
                {
                    "question_id": 1,
                    "score": 5,
                    "feedback": "detailed critical feedback here",
                    "improvement_suggestions": "specific suggestions here"
                },
                ...
            ],
            "overall_feedback": {
                "overall_score": 5,
                "strengths": "brief summary of strengths",
                "improvement_areas": "detailed critique of weak areas",
                "preparation_advice": "specific advice for future interviews"
            }
        }
        
        Only return valid JSON, with no additional text before or after.
        """

        # Create the prompt with questions, answers and job description
        qa_pairs = []
        for q in questions:
            question_id = q['id']
            question_text = q['question']
            question_type = q['type']
            answer = answers.get(str(question_id), "No answer provided")

            qa_pairs.append(
                f"Question ID: {question_id}\nQuestion Type: {question_type}\nQuestion: {question_text}\nAnswer: {answer}\n")

        user_prompt = f"""Please evaluate the following interview responses:
        
        JOB DESCRIPTION:
        {job_description}
        
        QUESTIONS AND ANSWERS:
        {''.join(qa_pairs)}
        """

        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ]

        # Call the LLM API
        response = call_llm_api(messages, temperature=0.5)

        # Parse the response as JSON
        try:
            # Find JSON in the response (in case there's any extra text)
            json_start = response.find('{')
            json_end = response.rfind('}') + 1

            if json_start >= 0 and json_end > json_start:
                json_str = response[json_start:json_end]
                return json.loads(json_str)
            else:
                raise ValueError("No JSON found in the LLM response")
        except Exception as e:
            print(f"Error parsing LLM response: {str(e)}")
            print(f"Raw response: {response}")
            # Return a basic error structure if parsing fails
            return {
                "error": "Failed to generate structured feedback",
                "raw_feedback": response
            }


interview_controller = InterviewService(supabase)
