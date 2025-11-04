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

def analyze_with_claude(code:str, issues:List[Dict])->Dict:
    """Code analysis with claude"""
    prompt=create_analysis_prompt(code,issues)
    response=client.message.create(
        model="claude-haiku-4-5",
        max_tokens=4096,
        messages=[{'role':'user','content':prompt}]
    )

    import json 
    response_text=response.content[0].text
    start=response_text.find('{')
    end=response_text.find('}')
    json_text=response_text[start:end]
    return json.loads(json_text)

def generate_fix(code:str, issue:Dict) ->str:
    """Generate a fix for a specific issue"""
    prompt = f"""Tu es un expert Python. Corrige ce problème:

CODE ORIGINAL:
```python
{code}
```

PROBLÈME (ligne {issue['line']}):
{issue['message']}

Réponds UNIQUEMENT avec le code corrigé complet, sans explication.
"""

    response = client.messages.create(
        model="claude-haiku-4-5",
        max_tokens=4096,
        messages=[
            {"role": "user", "content": prompt}
        ]
    )
    
    return response.content[0].text
