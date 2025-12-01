import ast
import pytest
from pathlib import Path
from src.parser import (
    parse_code,
    extract_functions,
    extract_classes,
    extract_imports,
    analyze_python_file
)


class TestParseCode:
    """Test parse_code function"""

    def test_parse_valid_code(self):
        """Should parse valid Python code"""
        code = "def hello(): pass"
        tree = parse_code(code)
        assert tree is not None
        assert isinstance(tree, ast.AST)

    def test_parse_invalid_code(self):
        """Should return None for invalid syntax"""
        code = "def hello(: pass"
        tree = parse_code(code)
        assert tree is None

    def test_parse_empty_code(self):
        """Should parse empty code"""
        code = ""
        tree = parse_code(code)
        assert tree is not None


class TestExtractFunctions:
    """Test extract_functions function"""

    def test_extract_single_function(self):
        """Should extract single function"""
        code = """
def greet(name):
    '''Say hello'''
    return f"Hello {name}"
"""
        tree = parse_code(code)
        functions = extract_functions(tree)

        assert len(functions) == 1
        assert functions[0]['name'] == 'greet'
        assert functions[0]['args'] == ['name']
        assert 'Say hello' in functions[0]['docstring']
        assert functions[0]['line'] == 2

    def test_extract_multiple_functions(self):
        """Should extract multiple functions"""
        code = """
def func1():
    pass

def func2(x, y):
    pass
"""
        tree = parse_code(code)
        functions = extract_functions(tree)

        assert len(functions) == 2
        assert functions[0]['name'] == 'func1'
        assert functions[1]['name'] == 'func2'
        assert functions[1]['args'] == ['x', 'y']

    def test_extract_no_functions(self):
        """Should return empty list when no functions"""
        code = "x = 10"
        tree = parse_code(code)
        functions = extract_functions(tree)

        assert functions == []

    def test_function_without_docstring(self):
        """Should handle functions without docstrings"""
        code = "def test(): pass"
        tree = parse_code(code)
        functions = extract_functions(tree)

        assert functions[0]['docstring'] is None


class TestExtractClasses:
    """Test extract_classes function"""

    def test_extract_single_class(self):
        """Should extract single class"""
        code = """
class MyClass:
    '''A test class'''
    def method1(self):
        pass

    def method2(self):
        pass
"""
        tree = parse_code(code)
        classes = extract_classes(tree)

        assert len(classes) == 1
        assert classes[0]['name'] == 'MyClass'
        assert classes[0]['methods'] == ['method1', 'method2']
        assert 'A test class' in classes[0]['docstring']
        assert classes[0]['line'] == 2

    def test_extract_multiple_classes(self):
        """Should extract multiple classes"""
        code = """
class Class1:
    pass

class Class2:
    def method(self):
        pass
"""
        tree = parse_code(code)
        classes = extract_classes(tree)

        assert len(classes) == 2
        assert classes[0]['name'] == 'Class1'
        assert classes[1]['name'] == 'Class2'

    def test_extract_no_classes(self):
        """Should return empty list when no classes"""
        code = "x = 10"
        tree = parse_code(code)
        classes = extract_classes(tree)

        assert classes == []

    def test_class_without_methods(self):
        """Should handle classes without methods"""
        code = "class Empty: pass"
        tree = parse_code(code)
        classes = extract_classes(tree)

        assert classes[0]['methods'] == []


class TestExtractImports:
    """Test extract_imports function"""

    def test_extract_simple_import(self):
        """Should extract simple imports"""
        code = """
import os
import sys
"""
        tree = parse_code(code)
        imports = extract_imports(tree)

        assert 'os' in imports
        assert 'sys' in imports

    def test_extract_from_import(self):
        """Should extract from imports"""
        code = """
from pathlib import Path
from typing import List, Dict
"""
        tree = parse_code(code)
        imports = extract_imports(tree)

        assert 'pathlib.Path' in imports
        assert 'typing.List' in imports
        assert 'typing.Dict' in imports

    def test_extract_mixed_imports(self):
        """Should extract mixed import styles"""
        code = """
import ast
from collections import defaultdict
"""
        tree = parse_code(code)
        imports = extract_imports(tree)

        assert 'ast' in imports
        assert 'collections.defaultdict' in imports

    def test_extract_no_imports(self):
        """Should return empty list when no imports"""
        code = "x = 10"
        tree = parse_code(code)
        imports = extract_imports(tree)

        assert imports == []


class TestAnalyzePythonFile:
    """Test analyze_python_file function"""

    def test_analyze_complete_file(self, tmp_path):
        """Should analyze a complete Python file"""
        # Create a temporary test file
        test_file = tmp_path / "test_script.py"
        test_code = """
import os
from pathlib import Path

class Calculator:
    '''A simple calculator'''
    def add(self, x, y):
        return x + y

    def subtract(self, x, y):
        return x - y

def main():
    '''Main function'''
    calc = Calculator()
    result = calc.add(5, 3)
    print(result)
"""
        test_file.write_text(test_code)

        # Analyze the file
        result = analyze_python_file(str(test_file))

        # Assertions
        assert 'functions' in result
        assert 'classes' in result
        assert 'imports' in result
        assert 'number of lines' in result

        assert len(result['functions']) == 3  # add, subtract, main
        assert len(result['classes']) == 1  # Calculator
        assert len(result['imports']) == 2  # os, pathlib.Path
        assert result['number of lines'] > 0

    def test_analyze_empty_file(self, tmp_path):
        """Should handle empty files"""
        test_file = tmp_path / "empty.py"
        test_file.write_text("")

        result = analyze_python_file(str(test_file))

        assert result['functions'] == []
        assert result['classes'] == []
        assert result['imports'] == []
        assert result['number of lines'] == 0  # Empty file has 0 lines

    def test_analyze_file_structure(self, tmp_path):
        """Should return correct structure"""
        test_file = tmp_path / "simple.py"
        test_file.write_text("def test(): pass")

        result = analyze_python_file(str(test_file))

        assert isinstance(result, dict)
        assert isinstance(result['functions'], list)
        assert isinstance(result['classes'], list)
        assert isinstance(result['imports'], list)
        assert isinstance(result['number of lines'], int)

#I'm here to test the github webhook

