from flask import Blueprint, request, jsonify
from ..services.pdf_service import PDFService
from app.config.supabase_client import supabase
import uuid
from datetime import datetime
import io

resume_bp = Blueprint('resume', __name__)


@resume_bp.route('/<user_id>', methods=['GET'])
def get_resume(user_id):
    try:
        result = supabase.table('resumes').select(
            '*').eq('user_id', user_id).execute()

        if not result.data:
            return jsonify({'error': 'Resume not found'}), 404

        return jsonify({'data': result.data[0]}), 200

    except Exception as e:
        return jsonify({'error': str(e)}), 500


@resume_bp.route('', methods=['POST'])
def upload_resume():
    try:
        if 'file' not in request.files:
            return jsonify({'error': 'No file provided'}), 400

        file = request.files['file']
        user_id = request.headers.get('X-User-Id')

        if not user_id:
            return jsonify({'error': 'User ID is required'}), 400

        if file.filename == '':
            return jsonify({'error': 'No file selected'}), 400

        # Check file type
        if file.content_type not in ['application/pdf',
                                     'application/vnd.openxmlformats-officedocument.wordprocessingml.document']:
            return jsonify({'error': 'Invalid file type'}), 400

        # Generate unique filename
        file_extension = PDFService.get_file_extension(file.content_type)
        file_name = f"{user_id}{file_extension}"

        # Save file to memory for both text extraction and upload
        file_content = file.read()
        text_content = PDFService.extract_text(
            io.BytesIO(file_content), file.content_type)

        # Upload file to Supabase Storage
        supabase.storage.from_('resumes').upload(
            file_name,
            file_content,
            {'content-type': file.content_type}
        )

        # Get the public URL
        file_url = supabase.storage.from_('resumes').get_public_url(file_name)

        # Check if user already has a resume
        existing_resume = supabase.table('resumes').select(
            '*').eq('user_id', user_id).execute()

        resume_data = {
            'user_id': user_id,
            'content': text_content,
            'filename': file.filename,
            'file_url': file_url,
            'updated_at': datetime.utcnow().isoformat()
        }

        if existing_resume.data:
            # Update existing resume
            result = supabase.table('resumes').update(
                resume_data).eq('user_id', user_id).execute()
        else:
            # Create new resume
            resume_data['id'] = str(uuid.uuid4())
            resume_data['created_at'] = resume_data['updated_at']
            result = supabase.table('resumes').insert(resume_data).execute()

        return jsonify({
            'message': 'Resume uploaded successfully',
            'data': {
                **result.data[0],
                'file_url': file_url
            }
        }), 200

    except Exception as e:
        return jsonify({'error': str(e)}), 500


@resume_bp.route('/<user_id>', methods=['DELETE'])
def delete_resume(user_id):
    try:
        # Get the resume data first
        result = supabase.table('resumes').select(
            '*').eq('user_id', user_id).execute()

        if result.data:
            # Delete from storage
            file_extension = '.pdf' if result.data[0]['filename'].endswith(
                '.pdf') else '.docx'
            file_name = f"{user_id}{file_extension}"

            try:
                supabase.storage.from_('resumes').remove([file_name])
            except Exception as e:
                print(f"Error deleting file from storage: {str(e)}")

            # Delete from database
            supabase.table('resumes').delete().eq('user_id', user_id).execute()

        return jsonify({'message': 'Resume deleted successfully'}), 200

    except Exception as e:
        return jsonify({'error': str(e)}), 500
