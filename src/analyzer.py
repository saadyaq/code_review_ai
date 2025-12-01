import ast
from pathlib import Path
from typing import List, Dict



def detect_unused_variables(tree, code: str) -> List[Dict]:
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

def detect_unused_imports(tree, code: str):
    """Detect unused imports"""
    imports = set()
    used = set()

    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                name = alias.asname or alias.name.split('.')[0]
                imports.add(name)
        elif isinstance(node, ast.ImportFrom):
            for alias in node.names:
                name = alias.asname or alias.name.split('.')[0]
                imports.add(name)

    for node in ast.walk(tree):
        if isinstance(node, ast.Name):
            used.add(node.id)

    unused = imports - used
    issues = []
    for imp in unused:
        issues.append({
            'type': 'unused_import',
            'severity': 'warning',
            'import': imp,
            'message': f"Import '{imp}' is imported but never used"
        })
    return issues

def detect_security_issues(tree):
    """detect security issues"""
    issues=[]
    for node in ast.walk(tree):
        #Detect eval() and exec()
        if isinstance(node, ast.Call):
            if isinstance(node.func, ast.Name):
                if node.func.id in ['eval', 'exec']:
                    issues.append({
                        'type': 'security',
                        'severity': 'high',
                        'line': node.lineno,
                        'message': f"Usage dangereux de {node.func.id}()"
                    })
    return issues

def detect_long_functions(tree,max_lines=50):
    """Detect long functions"""
    issues=[]

    for node in ast.walk(tree):
        if isinstance(node,ast.FunctionDef):
            if hasattr(node,'end_lineno'):
                lines=node.end_lineno-node.lineno
                if lines>max_lines:
                    issues.append({
                        'type': 'complexity',
                        'line': node.lineno,
                        'function': node.name,
                        'message': f"Fonction {node.name} trop longue ({lines} lignes)"
                    })
    
    return issues

def detect_missing_docstrings(tree):
    """Detect functions/classes without docstrings"""
    issues=[]
    for node in ast.walk(tree):
        if isinstance(node, (ast.FunctionDef, ast.ClassDef)):
            if not ast.get_docstring(node):
                issues.append({
                    'type': 'documentation',
                    'line': node.lineno,
                    'name': node.name,
                    'message': f"{node.__class__.__name__} '{node.name}' sans docstring"
                })
    
    return issues

def count_by_severity(issues: List[Dict]) -> Dict[str, int]:
    """Count issues by severity level"""
    severity_counts = {}
    for issue in issues:
        severity = issue.get('severity', 'unknown')
        severity_counts[severity] = severity_counts.get(severity, 0) + 1
    return severity_counts

def analyze_code_quality(code: str = None, filepath: str = None) -> Dict:
    """Complete analysis of the code

    Args:
        code: Python code as string (optional if filepath is provided)
        filepath: Path to Python file (optional if code is provided)

    Returns:
        Dict with analysis results
    """
    if filepath:
        code = Path(filepath).read_text(encoding='utf-8')
    elif not code:
        raise ValueError("Either 'code' or 'filepath' must be provided")

    tree = ast.parse(code)

    all_issues = []
    all_issues.extend(detect_unused_variables(tree, code))
    all_issues.extend(detect_missing_type_hints(tree, code))
    all_issues.extend(detect_unused_imports(tree, code))
    all_issues.extend(detect_security_issues(tree))
    all_issues.extend(detect_long_functions(tree))
    all_issues.extend(detect_missing_docstrings(tree))

    return {
        'total_issues': len(all_issues),
        'issues': all_issues,
        'severity_breakdown': count_by_severity(all_issues)
    }