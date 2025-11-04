"""
Demo script to test the LLM client with Claude API
This script demonstrates the complete code review and fix pipeline
"""

import os
from pathlib import Path
from src.llm_client import (
    create_analysis_prompt,
    analyze_with_claude,
    generate_fix,
    apply_simple_fix,
    generate_diff,
    auto_fix_pipeline
)
from src.analyzer import analyze_code_quality


# Mock code with intentional issues for testing
MOCK_CODE_WITH_ISSUES = '''
def calculate_total(items):
    total = 0
    tax_rate = 0.1
    unused_var = 100
    for item in items:
        total += item
    return total

def process_data(data):
    result = []
    for d in data:
        result.append(d * 2)
    return result

class Calculator:
    def add(self, a, b):
        return a + b

    def subtract(self, a, b):
        temp = 0
        return a - b
'''


def demo_prompt_creation():
    """Demo: Creating analysis prompts"""
    print("\n" + "=" * 70)
    print("DEMO 1: Creating Analysis Prompt")
    print("=" * 70)

    issues = [
        {'line': 5, 'message': "Variable 'unused_var' is assigned but never used", 'severity': 'warning'},
        {'line': 2, 'message': "Function 'calculate_total' is missing return type hint", 'severity': 'warning'},
        {'line': 10, 'message': "Function 'process_data' is missing return type hint", 'severity': 'warning'}
    ]

    prompt = create_analysis_prompt(MOCK_CODE_WITH_ISSUES, issues)

    print("\n📝 Generated Prompt Preview (first 500 chars):")
    print("-" * 70)
    print(prompt[:500] + "...")
    print("\n✓ Prompt created successfully")


def demo_simple_fix():
    """Demo: Applying simple line fixes"""
    print("\n" + "=" * 70)
    print("DEMO 2: Applying Simple Fix")
    print("=" * 70)

    code = "line1\nline2_old\nline3"
    print("\n📄 Original code:")
    print(code)

    fixed = apply_simple_fix(code, 2, "line2_fixed")
    print("\n✅ Fixed code:")
    print(fixed)


def demo_diff_generation():
    """Demo: Generating diffs"""
    print("\n" + "=" * 70)
    print("DEMO 3: Generating Diff")
    print("=" * 70)

    original = """def old_function(x):
    temp = 10
    return x"""

    fixed = """def old_function(x: int) -> int:
    '''Calculate something with x'''
    return x"""

    diff = generate_diff(original, fixed)

    print("\n📊 Unified Diff:")
    print("-" * 70)
    print(diff if diff else "(no changes)")


def demo_analyze_with_api():
    """Demo: Analyze code with Claude API (requires API key)"""
    print("\n" + "=" * 70)
    print("DEMO 4: Analyzing with Claude API")
    print("=" * 70)

    # Check if API key is available
    if not os.getenv("ANTHROPIC_API_KEY"):
        print("\n⚠️  SKIPPED: ANTHROPIC_API_KEY not found in environment")
        print("   Set your API key in .env to run this demo")
        return

    try:
        print("\n🤖 Calling Claude API...")

        issues = [
            {'line': 5, 'message': "Variable 'unused_var' is assigned but never used"},
            {'line': 2, 'message': "Function 'calculate_total' is missing type hints"}
        ]

        analysis = analyze_with_claude(MOCK_CODE_WITH_ISSUES, issues)

        print("\n✅ Claude API Response:")
        print("-" * 70)
        print(f"Issues analyzed: {len(analysis.get('issues_analyzed', []))}")

        for idx, issue in enumerate(analysis.get('issues_analyzed', []), 1):
            print(f"\n  Issue {idx}:")
            print(f"    Line: {issue.get('line', 'N/A')}")
            print(f"    Problem: {issue.get('problem', 'N/A')[:60]}...")
            print(f"    Severity: {issue.get('severity', 'N/A')}")

    except Exception as e:
        print(f"\n❌ Error calling Claude API: {e}")
        print("   Make sure your API key is valid and you have credits")


def demo_generate_fix():
    """Demo: Generate fix with Claude API (requires API key)"""
    print("\n" + "=" * 70)
    print("DEMO 5: Generating Fix with Claude")
    print("=" * 70)

    if not os.getenv("ANTHROPIC_API_KEY"):
        print("\n⚠️  SKIPPED: ANTHROPIC_API_KEY not found in environment")
        return

    try:
        print("\n🤖 Generating fix with Claude...")

        simple_code = "def test(): pass"
        issue = {'line': 1, 'message': 'Missing docstring and type hints'}

        fixed_code = generate_fix(simple_code, issue)

        print("\n📄 Original:")
        print(simple_code)
        print("\n✅ Fixed:")
        print(fixed_code[:200] + ("..." if len(fixed_code) > 200 else ""))

    except Exception as e:
        print(f"\n❌ Error generating fix: {e}")


def demo_full_pipeline():
    """Demo: Complete auto-fix pipeline (requires API key)"""
    print("\n" + "=" * 70)
    print("DEMO 6: Complete Auto-Fix Pipeline")
    print("=" * 70)

    if not os.getenv("ANTHROPIC_API_KEY"):
        print("\n⚠️  SKIPPED: ANTHROPIC_API_KEY not found in environment")
        print("   This demo requires Claude API access")
        return

    # Create a temporary test file
    test_file = Path("temp_test_file.py")

    try:
        print("\n📝 Creating temporary test file...")
        test_file.write_text(MOCK_CODE_WITH_ISSUES)

        print("🔍 Running complete pipeline...")
        result = auto_fix_pipeline(str(test_file))

        print("\n✅ Pipeline Results:")
        print("-" * 70)
        print(f"Issues fixed: {result['issues_fixed']}")
        print(f"\n📊 Diff (first 300 chars):")
        print(result['diff'][:300] + ("..." if len(result['diff']) > 300 else ""))

    except Exception as e:
        print(f"\n❌ Error in pipeline: {e}")
    finally:
        # Cleanup
        if test_file.exists():
            test_file.unlink()
            print("\n🧹 Cleaned up temporary file")


def demo_local_analysis():
    """Demo: Local analysis without API (always works)"""
    print("\n" + "=" * 70)
    print("DEMO 7: Local Analysis (No API Required)")
    print("=" * 70)

    # Create temporary file
    test_file = Path("temp_local_test.py")

    try:
        test_file.write_text(MOCK_CODE_WITH_ISSUES)

        print("\n🔍 Analyzing code locally...")
        result = analyze_code_quality(str(test_file))

        print("\n✅ Local Analysis Results:")
        print("-" * 70)
        print(f"Total issues: {result['total_issues']}")
        print(f"Severity breakdown: {result['severity_breakdown']}")

        print("\n📋 Issues found:")
        for idx, issue in enumerate(result['issues'][:5], 1):
            print(f"  {idx}. [{issue.get('severity', 'unknown').upper()}] "
                  f"Line {issue.get('line', 'N/A')}: {issue['message']}")

        if result['total_issues'] > 5:
            print(f"  ... and {result['total_issues'] - 5} more")

    finally:
        if test_file.exists():
            test_file.unlink()


def main():
    """Run all demos"""
    print("\n" + "=" * 70)
    print("   🚀 LLM CLIENT DEMO - Code Review AI")
    print("=" * 70)
    print("\nThis demo showcases the code analysis and auto-fix capabilities")
    print("Some demos require Claude API access (set ANTHROPIC_API_KEY in .env)")

    # Run demos
    demo_prompt_creation()
    demo_simple_fix()
    demo_diff_generation()
    demo_local_analysis()

    # API-dependent demos
    demo_analyze_with_api()
    demo_generate_fix()
    demo_full_pipeline()

    print("\n" + "=" * 70)
    print("   ✅ DEMO COMPLETE")
    print("=" * 70)
    print("\n💡 Tips:")
    print("  - Set ANTHROPIC_API_KEY in .env to enable API demos")
    print("  - Check tests/test_llm_client.py for unit tests")
    print("  - Use auto_fix_pipeline() for complete code fixes")
    print("\n")


if __name__ == "__main__":
    main()
