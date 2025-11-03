import ast
from pathlib import Path
from typing import List, Dict



def declare_unused_variables(tree, code: str) -> List[Dict]:
    """Detect unused variables in the code"""
    assigned = set()
    used = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Assign):
            for target in node.targets:
                if isinstance(target, ast.Name):
                    assigned.add(target.id)
        elif isinstance(node, ast.Name):
            if isinstance(node.ctx, ast.Load):
                used.add(node.id)
    unused = assigned - used

    
    issues = []
    for var in unused:
        issues.append({
            'type': 'unused_variable',
            'severity': 'warning',
            'variable': var,
            'message': f"Variable '{var}' is assigned but never used"
        })
    return issues


def detect_missing_type_hints(tree, code: str) -> List[Dict]:
    """Detect functions missing type hints"""
    issues = []
    for node in ast.walk(tree):
        if isinstance(node, ast.FunctionDef):
            
            if node.returns is None:
                issues.append({
                    'type': 'missing_type_hint',
                    'severity': 'warning',
                    'line': node.lineno,
                    'function': node.name,
                    'message': f"Function '{node.name}' is missing return type hint"
                })
    return issues

