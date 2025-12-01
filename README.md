# 🤖 Code Review AI

Automated Python code review system powered by AST analysis and Claude AI. Automatically analyzes pull requests and provides detailed feedback on code quality, bugs, and security issues.

![Python](https://img.shields.io/badge/python-3.11+-blue.svg)
![FastAPI](https://img.shields.io/badge/FastAPI-0.104+-green.svg)
![Docker](https://img.shields.io/badge/docker-ready-blue.svg)
![License](https://img.shields.io/badge/license-MIT-green.svg)

## ✨ What This Does

Code Review AI analyzes Python code to find common bugs, security issues, and code quality problems. The system uses Abstract Syntax Tree (AST) parsing to understand code structure, then applies Claude AI for semantic analysis. When issues are found, the system automatically posts them as comments on GitHub Pull Requests.

## 🚀 Features

- **AST-based code analysis** - Deep understanding of code structure
- **Automatic bug detection**:
  - Unused variables and imports
  - Missing type hints
  - Missing docstrings
  - Security vulnerabilities (eval, exec usage)
  - Long functions (complexity detection)
- **AI-powered analysis** with Claude 3.5 Haiku
- **Automatic fix generation** with detailed diffs
- **GitHub webhook integration** - Auto-reviews on PR creation/update
- **FastAPI REST API** - Easy integration with your workflow
- **Docker deployment ready** - One-command deployment
- **Comprehensive test suite** - 58% test coverage (1,158 lines of tests)

## 📊 Project Statistics

- **Total Lines:** ~2,400 lines (Python + config)
- **Source Code:** 514 lines
- **Tests:** 1,158 lines (2.25:1 test-to-code ratio)
- **Test Coverage:** 58%
- **Files:** 21 Python files

## 🛠️ Tech Stack

- **Language:** Python 3.11+
- **AI:** Claude API (Anthropic)
- **Web Framework:** FastAPI
- **GitHub Integration:** PyGithub
- **Containerization:** Docker & Docker Compose
- **Testing:** pytest

## 📦 Installation

### Prerequisites

- Python 3.11+
- Docker (optional)
- GitHub account
- Anthropic API key

### Clone the Repository

```bash
git clone https://github.com/saadyaq/code_review_ai.git
cd code_review_ai
```

### Install Dependencies

```bash
# Create virtual environment
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### Configuration

Create a `.env` file in the root directory:

```bash
ANTHROPIC_API_KEY=your_claude_api_key_here
GITHUB_TOKEN=your_github_token_here
```

**Get your API keys:**
- Claude API: https://console.anthropic.com
- GitHub Token: https://github.com/settings/tokens (needs `repo` scope)

## 🎯 Usage

### Option 1: Analyze Code Locally

```python
from src.analyzer import analyze_code_quality

code = """
def calculate(x, y):
    unused_var = 10
    return x + y
"""

result = analyze_code_quality(code=code)
print(f"Found {result['total_issues']} issues:")
for issue in result['issues']:
    print(f"  - {issue['message']}")
```

### Option 2: Run API Server

```bash
# Start the API
uvicorn api.main:app --reload
```

Server runs on http://localhost:8000

**Interactive API docs:** http://localhost:8000/docs

### Option 3: Docker

```bash
# Using docker-compose (recommended)
docker-compose up

# Or build and run manually
docker build -t code-review-ai .
docker run -p 8000:8000 --env-file .env code-review-ai
```

## 🔌 API Endpoints

### POST `/analyze`

Analyze Python code and optionally generate fixes.

**Request:**
```json
{
  "code": "def test():\n    x = 5\n    return 10",
  "auto_fix": false
}
```

**Response:**
```json
{
  "issues": [
    {
      "type": "unused_variable",
      "severity": "warning",
      "variable": "x",
      "message": "Variable 'x' is assigned but never used"
    }
  ],
  "fixed_code": null,
  "diff": null
}
```

### POST `/webhook/github`

GitHub webhook endpoint for automatic PR reviews.

**Headers:**
- `X-GitHub-Event: pull_request`

### GET `/health`

Health check endpoint.

**Response:**
```json
{"status": "ok"}
```

## 🔗 GitHub Integration

### Setup Webhook

1. **Deploy your API** (Railway, Render, or use ngrok for testing)

2. **Get your webhook URL:**
   - Production: `https://your-api.com/webhook/github`
   - Testing (ngrok): `https://abc123.ngrok.io/webhook/github`

3. **Configure GitHub webhook:**
   - Go to: `https://github.com/YOUR_USERNAME/YOUR_REPO/settings/hooks`
   - Click "Add webhook"
   - **Payload URL:** Your webhook URL
   - **Content type:** `application/json`
   - **Events:** Select "Pull requests"
   - **Active:** ✓ Checked
   - Click "Add webhook"

4. **Test it:**
   - Create a Pull Request
   - The bot will automatically analyze Python files and post a review

### Example Review Output

When you create a PR, the bot posts:

```markdown
## 🤖 Code Review AI Analysis

**Issues Found:** 12

### Details:
⚠️ **src/example.py:15** - Function 'calculate' is missing return type hint
⚠️ **src/example.py:23** - Variable 'unused_var' is assigned but never used
🔴 **src/example.py:42** - Usage dangereux de eval()
ℹ️ **src/example.py:10** - FunctionDef 'helper' sans docstring
```

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────┐
│                   GitHub Webhook                     │
│          (Pull Request Created/Updated)              │
└──────────────────┬──────────────────────────────────┘
                   │
                   ▼
┌─────────────────────────────────────────────────────┐
│              FastAPI Application                     │
│  ┌─────────────────────────────────────────────┐   │
│  │  api/main.py      - API Routes              │   │
│  │  api/webhook.py   - GitHub Webhook Handler  │   │
│  └─────────────────────────────────────────────┘   │
└──────────────────┬──────────────────────────────────┘
                   │
                   ▼
┌─────────────────────────────────────────────────────┐
│              Core Analysis Engine                    │
│  ┌─────────────────────────────────────────────┐   │
│  │  src/analyzer.py         - AST Analysis     │   │
│  │  src/llm_client.py       - Claude AI        │   │
│  │  src/github_integration.py - GitHub API     │   │
│  └─────────────────────────────────────────────┘   │
└──────────────────┬──────────────────────────────────┘
                   │
                   ▼
┌─────────────────────────────────────────────────────┐
│                GitHub Pull Request                   │
│             (Automated Review Posted)                │
└─────────────────────────────────────────────────────┘
```

## 🧪 Testing

Run the test suite:

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=src --cov=api

# Run specific test file
pytest tests/test_analyzer.py -v
```

## 🐳 Docker Commands

```bash
# Build image
docker-compose build

# Start services
docker-compose up

# Start in background
docker-compose up -d

# View logs
docker-compose logs -f

# Stop services
docker-compose down

# Rebuild and restart
docker-compose up --build
```

## 📁 Project Structure

```
code_review_ai/
├── api/
│   ├── __init__.py
│   ├── main.py           # FastAPI app & routes
│   └── webhook.py        # GitHub webhook handler
├── src/
│   ├── __init__.py
│   ├── analyzer.py       # Code quality analysis
│   ├── llm_client.py     # Claude AI integration
│   ├── github_integration.py  # GitHub API client
│   └── parser.py         # AST parsing utilities
├── tests/
│   ├── test_analyzer.py
│   ├── test_llm_client.py
│   ├── test_api_main.py
│   └── test_api_webhook.py
├── Dockerfile
├── docker-compose.yml
├── requirements.txt
└── README.md
```

## 🎓 Detection Rules

The analyzer detects the following issues:

| Rule | Severity | Description |
|------|----------|-------------|
| **Unused Variables** | Warning | Variables assigned but never used |
| **Unused Imports** | Warning | Imported modules not referenced |
| **Missing Type Hints** | Warning | Function parameters/returns without types |
| **Missing Docstrings** | Info | Functions/classes without documentation |
| **Security Issues** | High | Dangerous functions (eval, exec) |
| **Long Functions** | Warning | Functions exceeding 50 lines |

## 🚀 Production Status

**Status:** ✅ LIVE IN PRODUCTION

**Production URL:** `https://codereviewai-production.up.railway.app`

The Code Review AI is successfully deployed and actively reviewing Python pull requests!

## 🗺️ Roadmap

### ✅ Completed
- [x] AST-based code analysis
- [x] FastAPI REST API
- [x] GitHub webhook integration
- [x] Docker deployment
- [x] Automated PR reviews
- [x] Claude AI integration
- [x] **Production deployment on Railway**
- [x] **Empty file handling and error recovery**
- [x] **Multi-repository support**

### 📋 Future Enhancements
- [ ] Support for JavaScript/TypeScript
- [ ] Custom rule configuration
- [ ] Code quality scoring system
- [ ] Web dashboard for analytics
- [ ] Integration with CI/CD pipelines
- [ ] Support for other git platforms (GitLab, Bitbucket)
- [ ] Caching system for API cost optimization
- [ ] Advanced complexity metrics

## 🤝 Contributing

Contributions are welcome! This is a learning project, but PRs for improvements are appreciated.

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📝 License

MIT License - see [LICENSE](LICENSE) file for details

## 👤 Author

**Yaqine Saad**

- GitHub: [@saadyaq](https://github.com/saadyaq)

## 🙏 Acknowledgments

- [Anthropic](https://anthropic.com) for Claude AI
- [FastAPI](https://fastapi.tiangolo.com/) for the excellent web framework
- [PyGithub](https://github.com/PyGithub/PyGithub) for GitHub API integration

## 📞 Support

Questions or feedback? Open an issue on [GitHub Issues](https://github.com/saadyaq/code_review_ai/issues)

---

## 🎯 Project Achievements

This project successfully demonstrates:
- ✅ **Full-stack development**: Python backend with FastAPI
- ✅ **AI integration**: Claude API for intelligent code analysis
- ✅ **DevOps**: Docker containerization and Railway deployment
- ✅ **GitHub integration**: Automated webhook-based PR reviews
- ✅ **Production-ready**: Error handling, logging, and reliability
- ✅ **Clean architecture**: Modular design with separation of concerns
- ✅ **Well-tested**: 58% test coverage with comprehensive test suite

**Status:** Project completed and deployed successfully!

---

**Version 1.0.0** - November 2024

