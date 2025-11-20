# Code Review AI

Automated Python code review system that detects bugs and generates fixes using AST analysis and Claude AI.

## What This Does

Code Review AI analyzes Python code to find common bugs, security issues, and code quality problems. The system uses Abstract Syntax Tree parsing to understand code structure, then applies Claude AI for semantic analysis. When bugs are found, the system generates automatic fixes and posts them as comments on GitHub Pull Requests.

## Features

- AST-based code parsing
- Automatic bug detection (unused variables, missing type hints, security risks)
- AI-powered analysis with Claude
- Automatic fix generation
- GitHub PR integration
- FastAPI REST API
- Docker deployment ready

## Tech Stack

- Python 3.11+
- Claude API (Anthropic)
- FastAPI
- PyGithub
- Docker

## Project Status

🚧 In Development - Week 4/6

Current progress:
- API Deployment
## Installation

Clone the repository:

```bash
git clone https://github.com/yourusername/code-review-ai.git
cd code-review-ai
```

Install dependencies:

```bash
pip install -r requirements.txt
```

Set up environment variables:

```bash
cp .env.example .env
# Edit .env with your API keys
```

## Configuration

Create a .env file with these variables:

```
ANTHROPIC_API_KEY=your_claude_api_key
GITHUB_TOKEN=your_github_token
GITHUB_WEBHOOK_SECRET=your_webhook_secret
```

Get your API keys:
- Claude API: https://console.anthropic.com
- GitHub Token: https://github.com/settings/tokens

## Usage

### Analyze Code Locally

```python
from src.parser import parse_code
from src.analyzer import analyze_code_quality

code = """
def calculate(x, y):
    result = x + y
    temp = 10
    return result
"""

tree = parse_code(code)
issues = analyze_code_quality(tree, code)
print(issues)
```

### Run API Server

```bash
uvicorn src.main:app --reload
```

Server runs on http://localhost:8000

API endpoints:
- POST /analyze - Analyze code
- POST /webhook/github - GitHub webhook
- GET /health - Health check

### Analyze via API

```bash
curl -X POST http://localhost:8000/analyze \
  -H "Content-Type: application/json" \
  -d '{
    "code": "def test(): x = 1",
    "auto_fix": true
  }'
```

## Architecture

```
parser.py → analyzer.py → llm_client.py → fixer.py → github_client.py
```

Each module handles one responsibility:
- parser.py: Extract code structure with AST
- analyzer.py: Detect bug patterns
- llm_client.py: Integrate Claude API
- fixer.py: Generate automatic fixes
- github_client.py: Automate GitHub reviews
- main.py: Orchestrate all modules

## Development

Run tests:

```bash
pytest tests/ -v
```

Format code:

```bash
black src/
isort src/
```

Check code quality:

```bash
flake8 src/ --max-line-length=100
```

## Docker Deployment

Build image:

```bash
docker build -t code-review-ai .
```

Run container:

```bash
docker run -p 8000:8000 --env-file .env code-review-ai
```

## GitHub Integration

1. Deploy the API to Railway or Render
2. Get your deployment URL
3. Go to GitHub repo settings
4. Add webhook:
   - Payload URL: https://your-api.com/webhook/github
   - Content type: application/json
   - Secret: your webhook secret
   - Events: Pull requests
5. Create a PR to test

The system will automatically analyze code and post review comments.

## Roadmap

Week 1 (Current):
- Core functionality
- GitHub integration
- API deployment

Week 2 (Planned):
- Support for JavaScript and TypeScript
- Custom detection rules
- Performance optimization
- CI/CD pipeline integration

## Contributing

This is a learning project. Contributions welcome.

Fork the repo, make changes, and submit a PR.

## License

MIT

## Author

Yaqine Saad

## Contact

Questions or feedback? Open an issue on GitHub.

---

Version 0.1.0 - October 2025
