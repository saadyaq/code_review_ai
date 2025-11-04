import anthropic
import os
import difflib
from pathlib import Path
from src.analyzer import analyze_code_quality
from dotenv import load_dotenv
from typing import List, Dict

load_dotenv()

# Verify API key exists
api_key = os.getenv("ANTHROPIC_API_KEY")
if not api_key:
    raise ValueError("ANTHROPIC_API_KEY not found in environment variables")

client = anthropic.Anthropic(api_key=api_key)
print("✓ Claude API client initialized successfully")

def create_analysis_prompt(code:str,issues: List[Dict])->str:
    """Create the prompt for claude"""
    issues_text = "\n".join([
        f"- Line {issue.get('line', 'N/A')}: {issue['message']}"
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
    response=client.messages.create(
        model="claude-3-5-haiku-20241022",
        max_tokens=4096,
        messages=[{'role':'user','content':prompt}]
    )

    import json
    response_text=response.content[0].text
    start=response_text.find('{')
    end=response_text.rfind('}') + 1  # Find last '}' and include it
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
        model="claude-3-5-haiku-20241022",
        max_tokens=4096,
        messages=[
            {"role": "user", "content": prompt}
        ]
    )
    
    return response.content[0].text

def apply_simple_fix(code:str, line_number:int, new_line:str)->str:
    """Replace a specific line."""
    lines=code.splitlines()
    if 0 < line_number <= len(lines):
        lines[line_number - 1] = new_line
    return '\n'.join(lines)



def generate_diff(original: str, fixed: str) -> str:
    """Generate diff between original and fixed."""
    diff = difflib.unified_diff(
        original.splitlines(keepends=True),
        fixed.splitlines(keepends=True),
        fromfile='original.py',
        tofile='fixed.py'
    )
    return ''.join(diff)

def auto_fix_pipeline(filepath: str) -> Dict:
    """Complete fix pipeline"""
    # Read code and analyze
    code = Path(filepath).read_text()
    result = analyze_code_quality(filepath)
    issues = result['issues']

    
    analysis = analyze_with_claude(code, issues)

    
    fixed_code = code
    for issue in analysis['issues_analyzed']:
        if issue.get('fix'):
            fixed_code = generate_fix(fixed_code, issue)

   
    diff = generate_diff(code, fixed_code)

    return {
        'original': code,
        'fixed': fixed_code,
        'diff': diff,
        'issues_fixed': len(analysis['issues_analyzed'])
    }