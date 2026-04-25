import os
import logging
from github import Github, GithubException
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class GitHubRepoCreator:
    def __init__(self, access_token: str):
        """Initialize the GitHub client with the provided access token."""
        self.github = Github(access_token)

    def create_private_repo(self, repo_name: str, description: str = "") -> None:
        """
        Create a private repository with README and Python .gitignore.
        
        Args:
            repo_name: Name of the repository to create.
            description: Optional description for the repository.
        """
        try:
            user = self.github.get_user()
            logger.info(f"Authenticated as {user.login}")

            # Create repo with README and Python .gitignore
            logger.info(f"Creating private repo '{repo_name}'...")
            repo = user.create_repo(
                name=repo_name,
                description=description,
                private=True,
                auto_init=True,              # Adds README.md
                gitignore_template="Python"  # Adds Python-specific .gitignore
            )
            logger.info(f"Repository '{repo.full_name}' created successfully.")
            print(f"Repository URL: {repo.html_url}")

        except GithubException as e:
            logger.error(f"GitHub API error: {str(e)}")
            raise Exception(f"Failed to create repository: {str(e)}")

        except Exception as e:
            logger.error(f"Unexpected error: {str(e)}")
            raise

def main():
    # Get GitHub access token from environment variables
    access_token = os.getenv("GITHUB_ACCESS_TOKEN")
    if not access_token:
        raise ValueError("GitHub access token not found in .env file")

    # Get repo name from user input
    repo_name = "people-knowledge-graph" 
    description = "To create an AI-friendly knowledge graph of people that combines professional, social, and personal insights, enabling strategic relationship building, task matching, influence, loyalty development, and safe experimentation in interactions."


    # Initialize the repo creator and create repo
    creator = GitHubRepoCreator(access_token)
    creator.create_private_repo(repo_name=repo_name, description=description)

if __name__ == "__main__":
    main()