# 🚀 AI Resume Analyzer

A modern, AI-powered web application that analyzes resumes against job descriptions and provides detailed insights and suggestions for improvement.

## ✨ Features

- **Resume Analysis**: Compare your resume with job descriptions using AI
- **PDF Upload**: Upload PDF resumes and extract text automatically
- **Skill Matching**: See which skills match and which are missing
- **AI Chat Assistant (Knight)**: Get career advice from an AI-powered chatbot
- **Beautiful UI**: Modern, animated, and responsive design
- **Real-time Analysis**: Get instant feedback on your resume

## 🎯 Key Capabilities

✅ Match percentage calculation  
✅ Matched and missing skills identification  
✅ Weak sections detection  
✅ Improved resume summary generation  
✅ Actionable suggestions for improvement  
✅ Interactive chat with AI assistant  
✅ PDF resume extraction  
✅ Session-based conversation history  

## 🛠️ Tech Stack

**Frontend:**
- HTML5, CSS3, JavaScript
- Font Awesome Icons
- Modern Glassmorphism Design
- Responsive Layout

**Backend:**
- FastAPI (Python)
- Uvicorn
- Claude AI / Groq API
- PDF Text Extraction

## 📋 Prerequisites

- Python 3.8+
- pip (Python package manager)
- Either Claude API key OR Groq API key

## 🚀 Quick Start

### 1. Clone the Repository
```bash
git clone https://github.com/yourusername/ai-resume-analyzer.git
cd ai-resume-analyzer/backend
```

### 2. Create Virtual Environment
```bash
# Windows
python -m venv venv
venv\Scripts\activate

# macOS/Linux
python3 -m venv venv
source venv/bin/activate
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. Setup Environment Variables
Create a `.env` file in the `backend` directory:

```env
# LLM Provider Selection (claude or groq)
LLM_PROVIDER=groq

# Groq API Configuration
GROQ_API_KEY=your_groq_api_key_here

# OR Anthropic API Configuration
# ANTHROPIC_API_KEY=your_claude_api_key_here

# FastAPI Configuration
DEBUG=true
HOST=127.0.0.1
PORT=8888
```

### 5. Run the Application
```bash
python run.py
```

The application will be available at `http://localhost:8888`

## 📁 Project Structure

```
ai-resume-analyzer/
├── backend/
│   ├── app/
│   │   ├── main.py                 # FastAPI app setup
│   │   ├── api/
│   │   │   └── routes.py           # API endpoints
│   │   └── services/
│   │       ├── analyzer.py         # Resume analysis logic
│   │       ├── chat_manager.py     # Chat session management
│   │       ├── conversation.py     # Conversation handling
│   │       ├── pdf_extractor.py    # PDF text extraction
│   │       └── provider_factory.py # LLM provider setup
│   ├── run.py                      # Entry point
│   ├── requirements.txt            # Python dependencies
│   └── .env.example               # Example environment file
├── index_simple.html              # Main UI (modern design)
├── index_backup.html              # Backup UI
└── README.md                       # This file
```

## 🔌 API Endpoints

### Analysis Endpoints
- `POST /api/analyze` - Analyze single resume
- `POST /api/analyze-batch` - Analyze multiple resumes
- `GET /api/results/{analysis_id}` - Get cached analysis

### File Upload
- `POST /api/upload-resume` - Upload and extract PDF resume

### Chat Endpoints
- `POST /api/chat/start` - Start new chat session
- `POST /api/chat/message` - Send message to Knight AI
- `GET /api/chat/history/{session_id}` - Get chat history
- `DELETE /api/chat/{session_id}` - Delete chat session

### Health Check
- `GET /api/health` - Server health status

## 🎨 Frontend Features

### Welcome Screen
- Beautiful "Namaste" greeting
- Animated introduction sequence
- Smooth transitions to main app

### Main Interface
- Tab-based navigation
- Resume and job description input
- PDF file upload with automatic extraction
- Real-time analysis results

### Results Display
- Match percentage with visual indicator
- Matched and missing skills visualization
- Weak sections identification
- Improvement suggestions
- AI-generated improved summary

### Knight AI Assistant
- Floating widget in bottom-right corner
- Real-time chat interface
- Session-based conversation history
- Career advice and guidance

## 🎯 Usage Example

1. **Open the Application**
   - Navigate to `http://localhost:8888`
   - See the beautiful Namaste welcome screen
   - Wait for auto-transition to main app

2. **Analyze Resume**
   - Upload a PDF or paste resume text
   - Paste job description
   - Click "Analyze Resume"
   - View detailed analysis and suggestions

3. **Chat with Knight**
   - Click the Knight icon (bottom-right)
   - Ask career-related questions
   - Get AI-powered advice

## 🔐 Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `LLM_PROVIDER` | AI provider (claude/groq) | groq |
| `GROQ_API_KEY` | Groq API key | - |
| `ANTHROPIC_API_KEY` | Claude API key | - |
| `HOST` | Server host | 127.0.0.1 |
| `PORT` | Server port | 8888 |
| `DEBUG` | Debug mode | true |

## 🚀 Deployment

### Deploy to Heroku
```bash
heroku create your-app-name
git push heroku main
```

### Deploy to Railway
Connect your GitHub repo to Railway and it will auto-detect the Python app.

### Deploy to Render
1. Connect your GitHub repo
2. Create Web Service
3. Build Command: `pip install -r requirements.txt`
4. Start Command: `python run.py`

## 📝 License

This project is licensed under the MIT License.

## 🤝 Contributing

Contributions are welcome! Feel free to submit a Pull Request.

## 🎉 Acknowledgments

- Built with FastAPI
- AI powered by Claude/Groq
- UI inspired by modern design trends
- Icons from Font Awesome

---

**Made with ❤️**
