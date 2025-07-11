import PyPDF2
from docx import Document


class PDFService:
    @staticmethod
    def extract_text(file_stream, file_type):
        text = ""
        if file_type == 'application/pdf':
            pdf_reader = PyPDF2.PdfReader(file_stream)
            for page in pdf_reader.pages:
                text += page.extract_text()
        elif file_type == 'application/vnd.openxmlformats-officedocument.wordprocessingml.document':
            doc = Document(file_stream)
            for para in doc.paragraphs:
                text += para.text + '\n'
        return text.strip()

    @staticmethod
    def get_file_extension(content_type):
        if content_type == 'application/pdf':
            return '.pdf'
        elif content_type == 'application/vnd.openxmlformats-officedocument.wordprocessingml.document':
            return '.docx'
        return ''
