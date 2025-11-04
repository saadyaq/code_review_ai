"""
Test file to demonstrate the code analyzer capabilities
This file intentionally contains various code quality issues
"""

import math
import os  # Unused import
import sys  # Unused import

class Circle:
    """A circle class - Good docstring!"""
    def __init__(self, radius):
        self.radius = radius

    def area(self):
        """Calculate the area"""
        return math.pi * self.radius ** 2

    def circumference(self):
        # Missing docstring
        unused_variable = 10  # Unused variable
        return 2 * math.pi * self.radius


def calculate_something(x, y):
    # Missing type hints and docstring
    temp = 5  # Unused variable
    another_unused = 100  # Another unused variable
    result = x + y
    return result


def dangerous_function():
    # Security issue: using eval
    user_input = "2 + 2"
    result = eval(user_input)
    return result


class Rectangle:
    # Missing docstring for class
    def __init__(self, width, height):
        self.width = width
        self.height = height

    def area(self):
        # Missing docstring
        return self.width * self.height


# Test the analyzer
if __name__ == "__main__":
    from src.parser import parse_code
    from src.analyzer import analyze_code_quality
    from pathlib import Path
    import json

    print("=" * 60)
    print("CODE QUALITY ANALYSIS REPORT")
    print("=" * 60)

    # Analyze this file
    result = analyze_code_quality(__file__)

    print(f"\n📊 Total Issues Found: {result['total_issues']}")
    print(f"\n📈 Severity Breakdown:")
    for severity, count in result['severity_breakdown'].items():
        print(f"   {severity.upper()}: {count}")

    print(f"\n🔍 Detailed Issues:\n")

    # Group issues by type
    issues_by_type = {}
    for issue in result['issues']:
        issue_type = issue['type']
        if issue_type not in issues_by_type:
            issues_by_type[issue_type] = []
        issues_by_type[issue_type].append(issue)

    # Print issues grouped by type
    for issue_type, issues in issues_by_type.items():
        print(f"\n{issue_type.upper().replace('_', ' ')}:")
        for issue in issues:
            line = issue.get('line', 'N/A')
            message = issue['message']
            severity = issue.get('severity', 'unknown')
            print(f"   [{severity.upper()}] Line {line}: {message}")

    print("\n" + "=" * 60)
    print("Analysis complete!")
    print("=" * 60)
