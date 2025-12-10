from typing import Dict, List
from github import Github 
import os 

def get_github_client():
    """ Create an authentified github client"""
    token=os.getenv("GITHUB_TOKEN")
    return Github(token)

def get_pr_files(repo_name:str,pr_number:int)->List[Dict]:
    """Retrieve modified files in a PR"""
    g=get_github_client()
    repo=g.get_repo(repo_name)
    pr=repo.get_pull(pr_number)

    files=[]
    for file in pr.get_files():
        if file.filename.endswith(".py"):
            try:
                content = repo.get_contents(file.filename,ref=pr.head.ref).decoded_content.decode()
                # Skip empty files
                if content and content.strip():
                    files.append({
                        'filename':file.filename,
                        'content':content,
                        'patch':file.patch
                    })
            except Exception as e:
                # Skip files that can't be fetched (deleted files, etc.)
                print(f"Skipping {file.filename}: {e}")
                continue

    return files

def post_review_comment(repo_name:str,pr_number:int,filename:str,line:int, comment:str):
    """Post a comment about a specific line"""
    g=get_github_client()
    repo=g.get_repo(repo_name)
    pr=repo.get_pull(pr_number)
    commits=list(pr.get_commits())
    commit=commits[-1]  # Get the last commit
    pr.create_review_comment(
        body=comment,
        commit=commit,
        path=filename,
        line=line
    )

def post_complete_review(repo_name: str, pr_number: int,
                        analysis: Dict):
    """Post a complete review"""
    g = get_github_client()
    repo = g.get_repo(repo_name)
    pr = repo.get_pull(pr_number)


    body = f"""## 🤖 Code Review AI Analysis

**Issues Found:** {analysis['total_issues']}

### Details:
"""

    for issue in analysis['issues']:
        filename = issue.get('filename', 'unknown')
        line = issue.get('line', 'N/A')
        severity = issue.get('severity', 'info')
        message = issue.get('message', issue.get('description', 'No description'))

        # Emoji based on severity
        emoji = {
            'high': '🔴',
            'warning': '⚠️',
            'info': 'ℹ️'
        }.get(severity, '•')

        body += f"{emoji} **{filename}:{line}** - {message}\n"


    pr.create_review(
        body=body,
        event="COMMENT"
    )


def main():
    """Test the get_pr_files function"""
    repo_name = input("Enter repo name (format: owner/repo): ")
    pr_number = int(input("Enter PR number: "))

    print(f"\nFetching files from PR #{pr_number} in {repo_name}...")

    try:
        files = get_pr_files(repo_name, pr_number)

        print(f"\nFound {len(files)} Python file(s):\n")

        for file_info in files:
            print(f"📄 {file_info['filename']}")
            print(f"   Content length: {len(file_info['content'])} characters")
            print(f"   Has patch: {'Yes' if file_info['patch'] else 'No'}")
            print()

        if files:
            print("\n✅ Test successful! get_pr_files is working.")
        else:
            print("\n⚠️  No Python files found in this PR.")

    except Exception as e:
        print(f"\n❌ Error: {e}")


if __name__ == "__main__":
    main()