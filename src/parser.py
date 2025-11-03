
import ast 
from pathlib import Path
from typing import List, Dict

#step 

def parse_code(code: str):
    """Parse Python code string and return AST"""
    try:
        tree = ast.parse(code)
        return tree
    except SyntaxError as e:
        print(f"Syntax error: {e}")
        return None

def extract_functions(tree):
    """Extract all functions of an ast"""  
    functions=[]
    for node in ast.walk(tree):
        if isinstance(node,ast.FunctionDef):
            functions.append({
                'name':node.name,
                'line':node.lineno,
                'args':[arg.arg for arg in node.args.args],
                'docstring':ast.get_docstring(node)
            })
    return functions
def extract_classes(tree):
    """Extract all classes from an ast"""
    classes=[]
    for node in ast.walk(tree):
        if isinstance(node,ast.ClassDef):
            classes.append({
                'name':node.name,
                'line':node.lineno,
                'methods':[m.name for m in node.body if isinstance(m,ast.FunctionDef)],
                'docstring': ast.get_docstring(node)})
    return classes

def extract_imports(tree):
    """extract all import from an ast"""
    imports = []
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                imports.append(alias.name)
        elif isinstance(node, ast.ImportFrom):
            module = node.module or ''
            for alias in node.names:
                imports.append(f"{module}.{alias.name}")
    return imports

def analyze_python_file(filepath:str)-> Dict:
    """Complete analysis of the python file """
    code=Path(filepath).read_text(encoding="utf-8")
    tree=ast.parse(code)
    return {
        'functions':extract_functions(tree),
        'classes':extract_classes(tree),
        'imports':extract_imports(tree),
        'number of lines':len(code.splitlines())
    }

