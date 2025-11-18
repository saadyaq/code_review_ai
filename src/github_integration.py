from github import Github 
import os 

def get_github_client():
    """ Create an authentified github client"""
    token=os.getenv("GITHUB_TOKEN")
    return Github(token)