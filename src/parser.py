"""
input: python file 
output : parsed file 
step 0: imports
step 1: load file 
step 2 : parse file 
step 3 : save parsed file 

"""

import ast 
from pathlib import Path

#step 

def parser(file_path):
    """Parse file structure """
    try: 
        file_path=Path(file_path).read_text(encoding="utf-8")
        tree=ast.parse(file_path)
        return tree
    except SyntaxError as e:
        print(f"Syntax error {e}")
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
    """Extract all classes from an ast"""


def main():
    parser()

if __name__=="__main__":
    main()