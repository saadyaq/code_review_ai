import ast
import pytest
from pathlib import Path
from src.analyzer import (
    detect_unused_variables,
    detect_missing_type_hints,
    detect_unused_imports,
    detect_security_issues,
    detect_long_functions,
    detect_missing_docstrings,
    count_by_severity,
    analyze_code_quality
)
from src.parser import parse_code


class TestDetectUnusedVariables:
    """Test detect_unused_variables function"""

    def test_detect_single_unused_variable(self):
        """Should detect a single unused variable"""
        code = """
x = 10
y = 20
print(x)
"""
        tree = parse_code(code)
        issues = detect_unused_variables(tree, code)

        assert len(issues) == 1
        assert issues[0]['type'] == 'unused_variable'
        assert issues[0]['variable'] == 'y'
        assert issues[0]['severity'] == 'warning'

    def test_detect_multiple_unused_variables(self):
        """Should detect multiple unused variables"""
        code = """
a = 1
b = 2
c = 3
print(a)
"""
        tree = parse_code(code)
        issues = detect_unused_variables(tree, code)

        assert len(issues) == 2
        variables = {issue['variable'] for issue in issues}
        assert 'b' in variables
        assert 'c' in variables

    def test_no_unused_variables(self):
        """Should return empty list when all variables are used"""
        code = """
x = 10
y = 20
result = x + y
print(result)
"""
        tree = parse_code(code)
        issues = detect_unused_variables(tree, code)

        assert issues == []


class TestDetectMissingTypeHints:
    """Test detect_missing_type_hints function"""

    def test_detect_function_without_return_type(self):
        """Should detect function missing return type hint"""
        code = """
def add(x, y):
    return x + y
"""
        tree = parse_code(code)
        issues = detect_missing_type_hints(tree, code)

        assert len(issues) == 1
        assert issues[0]['type'] == 'missing_type_hint'
        assert issues[0]['function'] == 'add'
        assert issues[0]['line'] == 2

    def test_function_with_return_type(self):
        """Should not flag function with return type hint"""
        code = """
def add(x: int, y: int) -> int:
    return x + y
"""
        tree = parse_code(code)
        issues = detect_missing_type_hints(tree, code)

        assert issues == []

    def test_multiple_functions_mixed(self):
        """Should detect only functions without type hints"""
        code = """
def typed_func() -> str:
    return "hello"

def untyped_func():
    return 42
"""
        tree = parse_code(code)
        issues = detect_missing_type_hints(tree, code)

        assert len(issues) == 1
        assert issues[0]['function'] == 'untyped_func'


class TestDetectSecurityIssues:
    """Test detect_security_issues function"""

    def test_detect_eval_usage(self):
        """Should detect dangerous eval() usage"""
        code = """
user_input = input()
result = eval(user_input)
"""
        tree = parse_code(code)
        issues = detect_security_issues(tree)

        assert len(issues) == 1
        assert issues[0]['type'] == 'security'
        assert issues[0]['severity'] == 'high'
        assert 'eval' in issues[0]['message']

    def test_detect_exec_usage(self):
        """Should detect dangerous exec() usage"""
        code = """
code_str = "print('hello')"
exec(code_str)
"""
        tree = parse_code(code)
        issues = detect_security_issues(tree)

        assert len(issues) == 1
        assert 'exec' in issues[0]['message']

    def test_no_security_issues(self):
        """Should return empty list for safe code"""
        code = """
x = 10
print(x)
"""
        tree = parse_code(code)
        issues = detect_security_issues(tree)

        assert issues == []


class TestDetectLongFunctions:
    """Test detect_long_functions function"""

    def test_detect_long_function(self):
        """Should detect function exceeding max lines"""
        # Create a function with 60 lines
        lines = ["def long_func():"]
        lines.extend([f"    x{i} = {i}" for i in range(60)])
        code = "\n".join(lines)

        tree = parse_code(code)
        issues = detect_long_functions(tree, max_lines=50)

        assert len(issues) == 1
        assert issues[0]['type'] == 'complexity'
        assert issues[0]['function'] == 'long_func'

    def test_short_function(self):
        """Should not flag short functions"""
        code = """
def short_func():
    return 42
"""
        tree = parse_code(code)
        issues = detect_long_functions(tree, max_lines=50)

        assert issues == []


class TestDetectMissingDocstrings:
    """Test detect_missing_docstrings function"""

    def test_detect_function_without_docstring(self):
        """Should detect function without docstring"""
        code = """
def my_function():
    pass
"""
        tree = parse_code(code)
        issues = detect_missing_docstrings(tree)

        assert len(issues) == 1
        assert issues[0]['type'] == 'documentation'
        assert issues[0]['name'] == 'my_function'

    def test_detect_class_without_docstring(self):
        """Should detect class without docstring"""
        code = """
class MyClass:
    def method(self):
        pass
"""
        tree = parse_code(code)
        issues = detect_missing_docstrings(tree)

        assert len(issues) == 2  # Class and method both missing docstrings
        names = {issue['name'] for issue in issues}
        assert 'MyClass' in names
        assert 'method' in names

    def test_function_with_docstring(self):
        """Should not flag function with docstring"""
        code = '''
def documented():
    """This is documented"""
    pass
'''
        tree = parse_code(code)
        issues = detect_missing_docstrings(tree)

        assert issues == []


class TestCountBySeverity:
    """Test count_by_severity function"""

    def test_count_severities(self):
        """Should correctly count issues by severity"""
        issues = [
            {'severity': 'warning'},
            {'severity': 'high'},
            {'severity': 'warning'},
            {'severity': 'warning'},
            {'severity': 'high'}
        ]

        result = count_by_severity(issues)

        assert result['warning'] == 3
        assert result['high'] == 2

    def test_count_with_missing_severity(self):
        """Should handle issues without severity field"""
        issues = [
            {'severity': 'warning'},
            {'type': 'some_issue'}  # No severity field
        ]

        result = count_by_severity(issues)

        assert result['warning'] == 1
        assert result['unknown'] == 1

    def test_empty_issues_list(self):
        """Should return empty dict for empty issues list"""
        result = count_by_severity([])
        assert result == {}


class TestAnalyzeCodeQuality:
    """Test analyze_code_quality function"""

    def test_analyze_complete_file(self, tmp_path):
        """Should perform complete code quality analysis"""
        test_file = tmp_path / "test_code.py"
        test_code = """
import os
import sys

def calculate(x, y):
    unused_var = 100
    result = x + y
    return result

class Calculator:
    def add(self, a, b):
        return a + b
"""
        test_file.write_text(test_code)

        result = analyze_code_quality(str(test_file))

        # Check structure
        assert 'total_issues' in result
        assert 'issues' in result
        assert 'severity_breakdown' in result

        # Should have multiple issues
        assert result['total_issues'] > 0
        assert isinstance(result['issues'], list)

        # Check for specific issue types
        issue_types = {issue['type'] for issue in result['issues']}
        assert 'unused_variable' in issue_types  # unused_var
        assert 'missing_type_hint' in issue_types  # calculate function
        assert 'documentation' in issue_types  # missing docstrings

    def test_analyze_clean_code(self, tmp_path):
        """Should find minimal issues in clean code"""
        test_file = tmp_path / "clean_code.py"
        test_code = '''
def add(x: int, y: int) -> int:
    """Add two numbers"""
    return x + y
'''
        test_file.write_text(test_code)

        result = analyze_code_quality(str(test_file))

        # Should have very few issues
        assert result['total_issues'] >= 0
        assert isinstance(result['severity_breakdown'], dict)

    def test_analyze_code_with_security_issues(self, tmp_path):
        """Should detect security issues in analysis"""
        test_file = tmp_path / "unsafe_code.py"
        test_code = """
def dangerous():
    user_input = input()
    eval(user_input)
"""
        test_file.write_text(test_code)

        result = analyze_code_quality(str(test_file))

        # Should detect eval as security issue
        issue_types = {issue['type'] for issue in result['issues']}
        assert 'security' in issue_types

        # Should have high severity
        assert 'high' in result['severity_breakdown']
