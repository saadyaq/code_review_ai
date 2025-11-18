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
            files.append({
                'filename':file.filename,
                'content':repo.get_contents(file.filename,ref=pr.head.ref).decoded_content.decode(),
                'patch':file.patch
            })

    return files



def main():
    """Test the get_pr_files function"""
    # Example: Replace with a real repo and PR number
    # repo_name = "username/repo-name"
    # pr_number = 1

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