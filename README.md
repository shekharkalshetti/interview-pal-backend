# Interview Pal

A modern AI-powered interview preparation platform that helps candidates practice for job interviews with personalized questions based on their resume and target job descriptions.

## 🚀 Features

- **AI-Generated Questions**: Automatically generates technical, behavioral, and project-based interview questions
- **Resume Analysis**: Analyzes uploaded resumes to create targeted interview questions
- **Job Description Matching**: Tailors questions based on specific job requirements
- **Interactive Chat Interface**: Real-time chat experience for practicing interviews
- **Instant Feedback**: AI-powered feedback on interview responses
- **Progress Tracking**: Monitor interview performance and improvement areas
- **Responsive Design**: Works seamlessly on desktop and mobile devices
- **User Authentication**: Secure user management with Supabase

## 🏗️ Architecture

- **Framework**: Flask (Python)
- **Database**: Supabase (PostgreSQL)
- **AI Integration**: Local LLM API (Qwen2.5-1.5B-Instruct)
- **Authentication**: Supabase Auth
- **File Processing**: PDF resume parsing

## 📋 Prerequisites

- **Python 3.8+** (for backend)
- **Node.js 18+** (for frontend)
- **Supabase Account** (for database and auth)
- **Local LLM API** (Qwen2.5-1.5B-Instruct or compatible)

## 🛠️ Installation & Setup

### 1. Clone the Repository

```bash
git clone https://github.com/shekharkalshetti/interview-pal-backend
cd interview-pal
```

### 2. Backend Setup

```bash
cd interview-pal-backend

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Set up environment variables
cp .env.example .env
```

Configure your `.env` file:

```env
SUPABASE_URL=your_supabase_url
SUPABASE_KEY=your_supabase_anon_key
LLM_API_URL=http://localhost:11434/v1/chat/completions
```

Configure your `.env.local` file:

```env
VITE_SUPABASE_URL=your_supabase_url
VITE_SUPABASE_ANON_KEY=your_supabase_anon_key
VITE_API_BASE_URL=http://localhost:5000
```

### 3. Database Setup

Create the following tables in your Supabase database:

```sql
-- Users table (handled by Supabase Auth)

-- Resumes table
CREATE TABLE resumes (
  id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
  user_id UUID REFERENCES auth.users(id) ON DELETE CASCADE,
  content TEXT NOT NULL,
  filename VARCHAR(255),
  created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
  updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Interviews table (optional for tracking)
CREATE TABLE interviews (
  id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
  user_id UUID REFERENCES auth.users(id) ON DELETE CASCADE,
  job_description TEXT,
  questions JSONB,
  answers JSONB,
  feedback JSONB,
  score INTEGER,
  created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);
```

### 4. LLM Setup

Install and run a local LLM (using Ollama as example):

```bash
# Install Ollama
curl -fsSL https://ollama.ai/install.sh | sh

# Pull the model
ollama pull qwen2.5:1.5b-instruct

# Run the model with OpenAI-compatible API
ollama serve
```

## 🚀 Running the Application

### Start Backend

```bash
cd interview-pal-backend
source venv/bin/activate  # On Windows: venv\Scripts\activate
python app.py
# Backend runs on http://localhost:5000
```

## 🔧 API Endpoints

### Interview Endpoints

- `POST /api/interview/generate-questions` - Generate interview questions
- `POST /api/interview/feedback` - Get feedback on interview responses

### Resume Endpoints

- `POST /api/resume/upload` - Upload and parse resume
- `GET /api/resume/:userId` - Get user's resume

## 🎯 Usage

1. **Sign Up/Login**: Create an account or login using Supabase Auth
2. **Upload Resume**: Upload your resume in PDF format
3. **Add Job Description**: Paste the job description you're applying for
4. **Generate Questions**: AI generates personalized interview questions
5. **Practice Interview**: Use the chat interface to answer questions
6. **Get Feedback**: Receive AI-powered feedback on your responses
7. **Track Progress**: Monitor your improvement over time

## 🙏 Acknowledgments

- [Supabase](https://supabase.com) for backend infrastructure
- [Radix UI](https://www.radix-ui.com) for accessible UI components
- [TanStack](https://tanstack.com) for routing and state management
- [Qwen2.5](https://qwenlm.github.io) for the local LLM model
