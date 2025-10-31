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

def main ():
    file_path="/home/saadyaq/SE/Python/code_review_ai/test.py"
    parser(file_path)

if __name__=="__main__":
    main()