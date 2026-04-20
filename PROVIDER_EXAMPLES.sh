#!/bin/bash
# Example: Test AI Resume Analyzer with multiple providers

# Make sure you have set API keys in backend/.env:
#   ANTHROPIC_API_KEY=your_key_here
#   GROQ_API_KEY=your_key_here

BASE_URL="http://localhost:8000"

echo "AI Resume Analyzer - Multi-Provider Test Examples"
echo "=================================================="
echo ""

# Sample data
RESUME="Senior Software Engineer with 5 years experience in Python, JavaScript, React, Node.js, AWS, Docker, and Kubernetes."

JOB_DESC="We are looking for a Senior Developer with expertise in JavaScript, React, Node.js, AWS, and Docker. Must have 5+ years experience."

echo "Example 1: Analyze with DEFAULT provider (from environment)"
echo "---"
echo "curl -X POST $BASE_URL/api/analyze \\"
echo "  -H 'Content-Type: application/json' \\"
echo "  -d '{\"resume\": \"...\", \"job_description\": \"...\"}'"
echo ""

echo "Example 2: Analyze with CLAUDE provider (override)"
echo "---"
echo "curl -X POST $BASE_URL/api/analyze \\"
echo "  -H 'Content-Type: application/json' \\"
echo "  -d '{
    \"resume\": \"$RESUME\",
    \"job_description\": \"$JOB_DESC\",
    \"provider\": \"claude\"
  }'"
echo ""

echo "Example 3: Analyze with GROQ provider (override)"
echo "---"
echo "curl -X POST $BASE_URL/api/analyze \\"
echo "  -H 'Content-Type: application/json' \\"
echo "  -d '{
    \"resume\": \"$RESUME\",
    \"job_description\": \"$JOB_DESC\",
    \"provider\": \"groq\"
  }'"
echo ""

echo "Example 4: Batch analysis with provider"
echo "---"
echo "curl -X POST $BASE_URL/api/analyze-batch \\"
echo "  -H 'Content-Type: application/json' \\"
echo "  -d '{
    \"resumes\": [\"Resume 1...\", \"Resume 2...\"],
    \"job_description\": \"$JOB_DESC\",
    \"provider\": \"groq\"
  }'"
echo ""

echo "To switch default provider:"
echo "---"
echo "1. Edit backend/.env"
echo "2. Change LLM_PROVIDER=claude to LLM_PROVIDER=groq"
echo "3. Restart the server"
