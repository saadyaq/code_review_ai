import anthropic 
import os 
from dotenv import load_dotenv
from typing import List,Dict

load_dotenv()

client=anthropic.Anthropic(
    api_key=os.getenv("ANTHROPIC_API_KEY")
)

if client:
    print("the api key is found")

def create_analysis_prompt(code:str,issues: List[Dict])->str:
    """Create the prompt for claude"""
    issues_text = "\n".join([
        f"- Line {issue['line']}: {issue['message']}"
        for issue in issues
    ])
    
    prompt = f"""You are a Python code review expert.

Analyze this code and the automatically detected issues:

CODE:

```python
{code}
```

DETECTED ISSUES:
{issues_text}

For each issue:

1. Explain the problem in English
2. Explain why it is a problem
3. Suggest a concrete fix with code

Respond in JSON with this structure:
{{
"issues_analyzed": [
{{
"line": <number>,
"problem": "<explanation>",
"why": "<reason>",
"fix": "<corrected code>",
"severity": "low|medium|high"
}}
]
}}"""

    return prompt

