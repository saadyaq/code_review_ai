import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch, MagicMock
from api.main import app

client = TestClient(app)

def test_health_check():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}

@patch("api.main.analyze_code_quality")
def test_analyze_code_no_issues(mock_analyze):
    mock_analyze.return_value = {"issues": []}
    
    payload = {"code": "print('hello')"}
    response = client.post("/analyze", json=payload)
    
    assert response.status_code == 200
    assert response.json() == {"issues": [], "fixed_code": None, "diff": None}
    mock_analyze.assert_called_once_with(code="print('hello')")

@patch("api.main.analyze_code_quality")
def test_analyze_code_with_issues(mock_analyze):
    mock_issues = [{"code": "E501", "message": "Line too long"}]
    mock_analyze.return_value = {"issues": mock_issues}
    
    payload = {"code": "long_line = 'a' * 100"}
    response = client.post("/analyze", json=payload)
    
    assert response.status_code == 200
    assert response.json() == {"issues": mock_issues, "fixed_code": None, "diff": None}

@patch("api.main.analyze_code_quality")
@patch("api.main.auto_fix_pipeline")
def test_analyze_code_with_autofix(mock_autofix, mock_analyze):
    mock_analyze.return_value = {"issues": []}
    mock_autofix.return_value = {
        "fixed": "fixed_code",
        "diff": "diff_content"
    }
    
    payload = {"code": "bad_code", "auto_fix": True}
    response = client.post("/analyze", json=payload)
    
    assert response.status_code == 200
    data = response.json()
    assert data["fixed_code"] == "fixed_code"
    assert data["diff"] == "diff_content"
    mock_autofix.assert_called_once_with(code="bad_code")

@patch("api.main.analyze_code_quality")
def test_analyze_code_syntax_error(mock_analyze):
    mock_analyze.side_effect = SyntaxError("Unexpected token")
    
    payload = {"code": "if True"}
    response = client.post("/analyze", json=payload)
    
    assert response.status_code == 400
    assert "Invalid Python syntax" in response.json()["detail"]

@patch("api.main.analyze_code_quality")
def test_analyze_code_internal_error(mock_analyze):
    mock_analyze.side_effect = Exception("Something went wrong")
    
    payload = {"code": "print('test')"}
    response = client.post("/analyze", json=payload)
    
    assert response.status_code == 500
    assert "Internal error" in response.json()["detail"]
