import hashlib
import hmac
import logging
import os
from fastapi import APIRouter, Request, Header, HTTPException, BackgroundTasks
from src.analyzer import analyze_code_quality
from src.llm_client import analyze_with_claude
from src.github_integration import get_pr_files, post_complete_review
from .main import app

logger = logging.getLogger(__name__)

# Threshold for using Claude - use Claude if AST finds more than this many issues
CLAUDE_THRESHOLD = int(os.getenv("CLAUDE_THRESHOLD", "5"))

# Shared secret configured in the GitHub webhook settings. When set, every
# incoming payload must carry a valid X-Hub-Signature-256 header.
WEBHOOK_SECRET = os.getenv("WEBHOOK_SECRET")


def verify_signature(payload_body: bytes, signature_header: str) -> None:
    """Verify the GitHub HMAC SHA-256 signature of a webhook payload.

    Raises HTTPException(401) if verification is enabled and the signature is
    missing or invalid. If WEBHOOK_SECRET is not configured, verification is
    skipped (useful for local development).
    """
    if not WEBHOOK_SECRET:
        logger.warning("WEBHOOK_SECRET not set - skipping signature verification")
        return

    if not signature_header:
        raise HTTPException(status_code=401, detail="Missing X-Hub-Signature-256 header")

    expected = "sha256=" + hmac.new(
        WEBHOOK_SECRET.encode("utf-8"), payload_body, hashlib.sha256
    ).hexdigest()

    if not hmac.compare_digest(expected, signature_header):
        raise HTTPException(status_code=401, detail="Invalid webhook signature")

def process_pr_analysis(repo_name: str, pr_number: int, files: list):
    """Background task to analyze PR files and post review"""
    try:
        all_issues = []
        claude_used = False

        for file_info in files:
            try:
                # First pass: AST analysis
                analysis = analyze_code_quality(code=file_info["content"])
                issues = analysis['issues']

                # Smart Claude usage: only if many issues found
                if len(issues) >= CLAUDE_THRESHOLD:
                    logger.info(f"File {file_info['filename']} has {len(issues)} issues - using Claude for deep analysis")
                    try:
                        claude_analysis = analyze_with_claude(file_info["content"], issues)
                        # Enrich issues with Claude's insights
                        issues = claude_analysis.get('issues_analyzed', issues)
                        claude_used = True
                    except Exception as claude_error:
                        logger.warning(f"Claude analysis failed for {file_info['filename']}: {claude_error}, falling back to AST only")

                # Add filename context to each issue
                for issue in issues:
                    issue['filename'] = file_info['filename']
                    all_issues.append(issue)

            except Exception as e:
                logger.error(f"Error analyzing {file_info['filename']}: {e}")
                continue

        # Post complete review to GitHub
        if all_issues:
            complete_analysis = {
                'total_issues': len(all_issues),
                'issues': all_issues
            }
            post_complete_review(repo_name, pr_number, complete_analysis)
            logger.info(f"Posted review with {len(all_issues)} issues (Claude used: {claude_used})")
        else:
            logger.info("No issues found, skipping review post")

    except Exception as e:
        logger.error(f"Background analysis error for PR #{pr_number}: {e}")

async def github_webhook_handler(
    request: Request,
    background_tasks: BackgroundTasks,
    x_github_event: str = Header(None),
    x_hub_signature_256: str = Header(None)
):
    """Handle Github webhooks for pull requests."""
    try:
        # Read the raw body first so we can verify the signature over the exact
        # bytes GitHub signed, then parse JSON from those same bytes.
        body = await request.body()
        verify_signature(body, x_hub_signature_256)

        payload = await request.json()

        if x_github_event == "pull_request":
            action = payload.get("action")

            # Only process opened or updated PRs
            if action in ['opened', 'synchronize']:
                pr_number = payload['pull_request']['number']
                repo_name = payload['repository']['full_name']

                logger.info(f"Received PR #{pr_number} from {repo_name} - queuing for analysis")

                # Get modified Python files (fast operation)
                files = get_pr_files(repo_name, pr_number)

                if not files:
                    logger.info(f"No Python files found in PR #{pr_number}")
                    return {"status": "no_python_files"}

                # Queue analysis as background task - respond immediately to GitHub
                background_tasks.add_task(process_pr_analysis, repo_name, pr_number, files)

                # Return immediately (< 1 second)
                return {
                    "status": "queued",
                    "pr_number": pr_number,
                    "files_to_analyze": len(files),
                    "message": "Analysis queued and will be posted to PR when complete"
                }

        return {"status": "ignored", "event": x_github_event}

    except HTTPException:
        # Preserve intentional responses (e.g. 401 from signature verification)
        raise
    except Exception as e:
        logger.error(f"Webhook error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# Register the handler for both with and without trailing slash
@app.post("/webhook/github")
@app.post("/webhook/github/")
async def github_webhook(
    request: Request,
    background_tasks: BackgroundTasks,
    x_github_event: str = Header(None),
    x_hub_signature_256: str = Header(None)
):
    """Route wrapper for webhook handler."""
    return await github_webhook_handler(
        request, background_tasks, x_github_event, x_hub_signature_256
    )
