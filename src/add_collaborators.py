import os
import logging
from typing import List
from github import Github, GithubException
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class GitHubCollaboratorManager:
    def __init__(self, access_token: str):
        """Initialize the GitHub client with the provided access token."""
        self.github = Github(access_token)
    
    def add_collaborators(
        self,
        repo_owner: str,
        repo_name: str,
        github_usernames: List[str],
        permission: str = "push"
    ) -> dict:
        """
        Add collaborators to a GitHub repository by their GitHub usernames.
        
        Args:
            repo_owner: Owner of the repository
            repo_name: Name of the repository
            github_usernames: List of GitHub usernames to add as collaborators
            permission: Permission level ("pull", "push", "admin", "maintain", "triage")
            
        Returns:
            Dictionary with results (added, pending, failed)
        """
        results = {
            "added": [],
            "pending": [],
            "failed": []
        }
        
        try:
            repo = self.github.get_repo(f"{repo_owner}/{repo_name}")
            logger.info(f"Accessing repository: {repo_owner}/{repo_name}")
            
            for username in github_usernames:
                try:
                    logger.info(f"Processing collaborator: {username}")
                    
                    # Check if user is already a collaborator
                    if repo.has_in_collaborators(username):
                        msg = f"User {username} already a collaborator"
                        logger.info(msg)
                        results["added"].append({
                            "username": username,
                            "reason": msg
                        })
                        continue
                    
                    # Add the user as a collaborator
                    repo.add_to_collaborators(username, permission)
                    logger.info(f"Added {username} as collaborator")
                    
                    # Check if the invitation is pending
                    invitations = repo.get_pending_invitations()
                    invitation_sent = any(
                        inv.invitee.login == username for inv in invitations
                    )
                    
                    if invitation_sent:
                        msg = f"Invitation sent to {username} (pending)"
                        logger.info(msg)
                        results["pending"].append({
                            "username": username,
                            "reason": msg
                        })
                    else:
                        msg = f"{username} added successfully"
                        logger.info(msg)
                        results["added"].append({
                            "username": username,
                            "reason": msg
                        })
                        
                except GithubException as e:
                    logger.error(f"Error processing {username}: {str(e)}")
                    results["failed"].append({
                        "username": username,
                        "reason": str(e)
                    })
                    
        except GithubException as e:
            logger.error(f"Repository access error: {str(e)}")
            raise Exception(f"Failed to access repository: {str(e)}")
        
        return results

def main():
    # Get GitHub access token from environment variables
    access_token = os.getenv("GITHUB_ACCESS_TOKEN")
    if not access_token:
        raise ValueError("GitHub access token not found in .env file")
    
    # Initialize the collaborator manager
    manager = GitHubCollaboratorManager(access_token)
    
    # Example usage - replace with your actual values
    repo_owner = "roopesht"
    repo_name =  "learning.ojasamirai.com" #"people-knowledge-graph"
    github_usernames = [
        "yashwanth9619"
    ]
    
    # Add collaborators
    results = manager.add_collaborators(
        repo_owner=repo_owner,
        repo_name=repo_name,
        github_usernames=github_usernames,
        permission="push"  # Can be "pull", "push", "admin", "maintain", "triage"
    )
    
    # Print results
    print("\nResults:")
    print(f"Successfully added: {len(results['added'])}")
    print(f"Pending invitations: {len(results['pending'])}")
    print(f"Failed to add: {len(results['failed'])}\n")
    
    # Print details if needed
    if results["failed"]:
        print("Failed additions:")
        for failure in results["failed"]:
            print(f"- {failure['username']}: {failure['reason']}")

if __name__ == "__main__":
    main()