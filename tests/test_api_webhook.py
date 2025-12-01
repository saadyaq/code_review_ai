import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch, AsyncMock, MagicMock
from api.main import app

client = TestClient(app)

@pytest.fixture
def mock_github_payload():
    return {
        "action": "opened",
        "pull_request": {
            "number": 123,
        },
        "repository": {
            "full_name": "user/repo"
        }
    }

@patch("api.webhook.get_pr_files")
@patch("api.webhook.analyze_code_quality")
@patch("api.webhook.post_complete_review")
def test_github_webhook_opened_pr(mock_post_review, mock_analyze, mock_get_files, mock_github_payload):
    # Setup mocks
    mock_get_files.return_value = [
        {"filename": "test.py", "content": "print('hello')"}
    ]
    mock_analyze.return_value = {
        "issues": [{"code": "E1", "message": "Issue 1"}]
    }
    
    headers = {"X-GitHub-Event": "pull_request"}
    response = client.post("/webhook/github", json=mock_github_payload, headers=headers)
    
    assert response.status_code == 200
    assert response.json()["status"] == "analyzed"
    assert response.json()["issues_found"] == 1
    
    mock_get_files.assert_called_once_with("user/repo", 123)
    mock_analyze.assert_called_once()
    mock_post_review.assert_called_once()

@patch("api.webhook.get_pr_files")
def test_github_webhook_no_python_files(mock_get_files, mock_github_payload):
    mock_get_files.return_value = []
    
    headers = {"X-GitHub-Event": "pull_request"}
    response = client.post("/webhook/github", json=mock_github_payload, headers=headers)
    
    assert response.status_code == 200
    assert response.json()["status"] == "no_python_files"

def test_github_webhook_ignored_event(mock_github_payload):
    headers = {"X-GitHub-Event": "push"}
    response = client.post("/webhook/github", json=mock_github_payload, headers=headers)
    
    assert response.status_code == 200
    assert response.json()["status"] == "ignored"

@patch("api.webhook.get_pr_files")
@patch("api.webhook.analyze_code_quality")
@patch("api.webhook.post_complete_review")
def test_github_webhook_no_issues(mock_post_review, mock_analyze, mock_get_files, mock_github_payload):
    mock_get_files.return_value = [
        {"filename": "good.py", "content": "pass"}
    ]
    mock_analyze.return_value = {"issues": []}
    
    headers = {"X-GitHub-Event": "pull_request"}
    response = client.post("/webhook/github", json=mock_github_payload, headers=headers)
    
    assert response.status_code == 200
    assert response.json()["issues_found"] == 0
    
    mock_post_review.assert_not_called()

@patch("api.webhook.get_pr_files")
def test_github_webhook_error(mock_get_files, mock_github_payload):
    mock_get_files.side_effect = Exception("GitHub API Error")
    
    headers = {"X-GitHub-Event": "pull_request"}
    response = client.post("/webhook/github", json=mock_github_payload, headers=headers)
    
    assert response.status_code == 500
    assert "GitHub API Error" in response.json()["detail"]
