import pytest
from unittest.mock import Mock, patch, MagicMock
from src.llm_client import (
    create_analysis_prompt,
    apply_simple_fix,
    generate_diff
)


class TestCreateAnalysisPrompt:
    """Test create_analysis_prompt function"""

    def test_creates_prompt_with_issues(self):
        """Should create a well-formatted prompt with issues"""
        code = "def test(): pass"
        issues = [
            {'line': 1, 'message': 'Missing docstring'},
            {'line': 1, 'message': 'Missing type hint'}
        ]

        prompt = create_analysis_prompt(code, issues)

        assert "Python code review expert" in prompt
        assert "def test(): pass" in prompt
        assert "Line 1: Missing docstring" in prompt
        assert "Line 1: Missing type hint" in prompt

    def test_handles_issues_without_line_number(self):
        """Should handle issues without line number"""
        code = "x = 10"
        issues = [
            {'message': 'Unused variable', 'variable': 'x'}
        ]

        prompt = create_analysis_prompt(code, issues)

        assert "Line N/A: Unused variable" in prompt

    def test_empty_issues_list(self):
        """Should handle empty issues list"""
        code = "def clean_code(): pass"
        issues = []

        prompt = create_analysis_prompt(code, issues)

        assert "def clean_code(): pass" in prompt
        assert "DETECTED ISSUES:" in prompt


class TestApplySimpleFix:
    """Test apply_simple_fix function"""

    def test_replace_single_line(self):
        """Should replace a specific line"""
        code = "line1\nline2\nline3"
        result = apply_simple_fix(code, 2, "new_line2")

        assert result == "line1\nnew_line2\nline3"

    def test_replace_first_line(self):
        """Should replace first line"""
        code = "line1\nline2\nline3"
        result = apply_simple_fix(code, 1, "new_line1")

        assert result == "new_line1\nline2\nline3"

    def test_replace_last_line(self):
        """Should replace last line"""
        code = "line1\nline2\nline3"
        result = apply_simple_fix(code, 3, "new_line3")

        assert result == "line1\nline2\nnew_line3"

    def test_invalid_line_number_too_high(self):
        """Should not modify code if line number is too high"""
        code = "line1\nline2"
        result = apply_simple_fix(code, 10, "new_line")

        assert result == code

    def test_invalid_line_number_zero(self):
        """Should not modify code if line number is zero"""
        code = "line1\nline2"
        result = apply_simple_fix(code, 0, "new_line")

        assert result == code

    def test_invalid_line_number_negative(self):
        """Should not modify code if line number is negative"""
        code = "line1\nline2"
        result = apply_simple_fix(code, -1, "new_line")

        assert result == code


class TestGenerateDiff:
    """Test generate_diff function"""

    def test_generate_diff_with_changes(self):
        """Should generate unified diff"""
        original = "def old():\n    pass"
        fixed = "def new():\n    pass"

        diff = generate_diff(original, fixed)

        assert "---" in diff
        assert "+++" in diff
        assert "-def old():" in diff
        assert "+def new():" in diff

    def test_generate_diff_no_changes(self):
        """Should return empty diff when no changes"""
        code = "def same():\n    pass"
        diff = generate_diff(code, code)

        assert diff == ""

    def test_generate_diff_multiple_changes(self):
        """Should handle multiple line changes"""
        original = "line1\nline2\nline3"
        fixed = "line1\nmodified\nline3\nline4"

        diff = generate_diff(original, fixed)

        assert "-line2" in diff
        assert "+modified" in diff
        assert "+line4" in diff


class TestAnalyzeWithClaudeMocked:
    """Test analyze_with_claude with mocked API calls"""

    @patch('src.llm_client.client')
    def test_analyze_with_claude_success(self, mock_client):
        """Should successfully analyze code with Claude"""
        # Mock response
        mock_response = Mock()
        mock_response.content = [Mock(text='{"issues_analyzed": [{"line": 1, "problem": "test", "why": "reason", "fix": "solution", "severity": "low"}]}')]
        mock_client.messages.create.return_value = mock_response

        from src.llm_client import analyze_with_claude

        code = "def test(): pass"
        issues = [{'line': 1, 'message': 'Missing docstring'}]

        result = analyze_with_claude(code, issues)

        # Verify API was called
        mock_client.messages.create.assert_called_once()
        assert 'issues_analyzed' in result
        assert len(result['issues_analyzed']) == 1

    @patch('src.llm_client.client')
    def test_analyze_with_claude_handles_json_in_text(self, mock_client):
        """Should extract JSON from text response"""
        # Mock response with surrounding text
        mock_response = Mock()
        mock_response.content = [Mock(text='Here is the analysis:\n{"issues_analyzed": []}\nDone.')]
        mock_client.messages.create.return_value = mock_response

        from src.llm_client import analyze_with_claude

        code = "x = 10"
        issues = []

        result = analyze_with_claude(code, issues)

        assert 'issues_analyzed' in result
        assert result['issues_analyzed'] == []


class TestGenerateFixMocked:
    """Test generate_fix with mocked API calls"""

    @patch('src.llm_client.client')
    def test_generate_fix_returns_code(self, mock_client):
        """Should generate fixed code"""
        mock_response = Mock()
        mock_response.content = [Mock(text='def fixed():\n    """Fixed function"""\n    pass')]
        mock_client.messages.create.return_value = mock_response

        from src.llm_client import generate_fix

        code = "def test(): pass"
        issue = {'line': 1, 'message': 'Missing docstring'}

        result = generate_fix(code, issue)

        assert 'def fixed():' in result
        assert 'Fixed function' in result


class TestAutoFixPipelineMocked:
    """Test auto_fix_pipeline with mocked dependencies"""

    @patch('src.llm_client.analyze_with_claude')
    @patch('src.llm_client.analyze_code_quality')
    @patch('src.llm_client.generate_fix')
    @patch('src.llm_client.Path')
    def test_auto_fix_pipeline_complete(self, mock_path, mock_generate_fix, mock_analyze_quality, mock_analyze_claude):
        """Should run complete auto-fix pipeline"""
        # Setup mocks
        original_code = "def test(): pass"
        fixed_code = "def test():\n    '''Test function'''\n    pass"

        mock_path.return_value.read_text.return_value = original_code
        mock_analyze_quality.return_value = {
            'issues': [{'line': 1, 'message': 'Missing docstring'}]
        }
        mock_analyze_claude.return_value = {
            'issues_analyzed': [
                {'line': 1, 'fix': 'Add docstring', 'problem': 'Missing docstring'}
            ]
        }
        mock_generate_fix.return_value = fixed_code

        from src.llm_client import auto_fix_pipeline

        result = auto_fix_pipeline('test.py')

        # Verify structure
        assert 'original' in result
        assert 'fixed' in result
        assert 'diff' in result
        assert 'issues_fixed' in result
        assert result['issues_fixed'] == 1

    @patch('src.llm_client.analyze_with_claude')
    @patch('src.llm_client.analyze_code_quality')
    @patch('src.llm_client.Path')
    def test_auto_fix_pipeline_no_issues(self, mock_path, mock_analyze_quality, mock_analyze_claude):
        """Should handle code with no issues"""
        clean_code = "def clean():\n    '''Clean function'''\n    pass"

        mock_path.return_value.read_text.return_value = clean_code
        mock_analyze_quality.return_value = {'issues': []}
        mock_analyze_claude.return_value = {'issues_analyzed': []}

        from src.llm_client import auto_fix_pipeline

        result = auto_fix_pipeline('clean.py')

        assert result['original'] == result['fixed']
        assert result['issues_fixed'] == 0
        assert result['diff'] == ''


class TestIntegrationWithoutAPI:
    """Integration tests without actual API calls"""

    def test_full_workflow_structure(self):
        """Test the structure of the complete workflow"""
        code = """
def calculate(x, y):
    temp = 10
    return x + y
"""
        issues = [
            {'line': 2, 'message': 'Missing type hints'},
            {'line': 3, 'message': 'Unused variable temp'}
        ]

        # Test prompt creation
        prompt = create_analysis_prompt(code, issues)
        assert all(keyword in prompt for keyword in ['CODE:', 'DETECTED ISSUES:', 'JSON'])

        # Test simple fix
        fixed = apply_simple_fix(code, 3, "    # temp removed")
        assert "# temp removed" in fixed

        # Test diff generation
        diff = generate_diff(code, fixed)
        assert len(diff) > 0
