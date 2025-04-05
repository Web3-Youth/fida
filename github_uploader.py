#!/usr/bin/env python3
import os
import argparse
from pathlib import Path
from github import Github
from github import GithubException
from tqdm import tqdm
from dotenv import load_dotenv
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class GitHubUploader:
    def __init__(self, token=None):
        """Initialize the GitHub uploader with authentication."""
        load_dotenv()
        self.token = token or os.getenv('GITHUB_TOKEN')
        if not self.token:
            raise ValueError("GitHub token not provided. Set GITHUB_TOKEN environment variable or pass it as an argument.")
        self.github = Github(self.token)
        self.user = self.github.get_user()

    def should_exclude_file(self, file_path):
        """Check if a file should be excluded from upload."""
        # List of directories to exclude
        excluded_dirs = {
            'node_modules',
            'dist',
            '.git',
            '__pycache__',
            'venv',
            'env'
        }
        
        # List of file patterns to exclude
        excluded_patterns = {
            '.env',
            'package-lock.json',
            '.pyc',
            '.pyo',
            '.pyd',
            '.so',
            '.dll',
            '.dylib',
            '.log',
            '.tmp',
            '.temp',
            '.DS_Store',
            'Thumbs.db'
        }

        # Check if path contains excluded directory
        parts = Path(file_path).parts
        if any(excluded_dir in parts for excluded_dir in excluded_dirs):
            return True

        # Check if file matches excluded patterns
        if any(file_path.endswith(pattern) for pattern in excluded_patterns):
            return True

        return False

    def get_repo(self, repo_name):
        """Get an existing repository."""
        try:
            return self.user.get_repo(repo_name)
        except GithubException as e:
            logger.error(f"Failed to get repository: {e}")
            raise

    def create_repo(self, repo_name, description="", private=False):
        """Create a new GitHub repository."""
        try:
            repo = self.user.create_repo(
                name=repo_name,
                description=description,
                private=private
            )
            logger.info(f"Created repository: {repo.full_name}")
            return repo
        except GithubException as e:
            logger.error(f"Failed to create repository: {e}")
            raise

    def upload_directory(self, repo_name, local_path, branch="main", commit_message="Initial commit"):
        """Upload a local directory to GitHub repository."""
        try:
            # Get the repository
            repo = self.get_repo(repo_name)
            
            # Get all files in the directory
            files_to_upload = []
            for root, _, files in os.walk(local_path):
                for file in files:
                    file_path = os.path.join(root, file)
                    relative_path = os.path.relpath(file_path, local_path)
                    
                    # Skip excluded files
                    if self.should_exclude_file(relative_path):
                        logger.info(f"Skipping excluded file: {relative_path}")
                        continue
                        
                    files_to_upload.append((file_path, relative_path))

            logger.info(f"Found {len(files_to_upload)} files to upload")

            # Upload files with progress bar
            with tqdm(total=len(files_to_upload), desc="Uploading files") as pbar:
                for file_path, relative_path in files_to_upload:
                    try:
                        with open(file_path, 'rb') as file:
                            content = file.read()
                        
                        # Create or update file in repository
                        try:
                            contents = repo.get_contents(relative_path, ref=branch)
                            repo.update_file(
                                path=relative_path,
                                message=f"Update {relative_path}",
                                content=content,
                                sha=contents.sha,
                                branch=branch
                            )
                            logger.info(f"Updated file: {relative_path}")
                        except GithubException as e:
                            if e.status == 404:  # File doesn't exist
                                repo.create_file(
                                    path=relative_path,
                                    message=f"Add {relative_path}",
                                    content=content,
                                    branch=branch
                                )
                                logger.info(f"Created file: {relative_path}")
                            else:
                                logger.error(f"Error with file {relative_path}: {e}")
                                raise
                        
                        pbar.update(1)
                    except Exception as e:
                        logger.error(f"Failed to upload {relative_path}: {e}")
                        continue

            logger.info("Upload completed successfully!")
            return True
        except GithubException as e:
            logger.error(f"Failed to upload directory: {e}")
            raise
        except Exception as e:
            logger.error(f"Unexpected error during upload: {e}")
            raise

    def update_readme(self, repo_name, content, branch="main"):
        """Update the README.md file in the repository."""
        try:
            repo = self.get_repo(repo_name)
            try:
                contents = repo.get_contents("README.md", ref=branch)
                repo.update_file(
                    path="README.md",
                    message="Update README.md",
                    content=content,
                    sha=contents.sha,
                    branch=branch
                )
            except GithubException as e:
                if e.status == 404:  # File doesn't exist
                    repo.create_file(
                        path="README.md",
                        message="Create README.md",
                        content=content,
                        branch=branch
                    )
                else:
                    raise
            logger.info("README.md updated successfully!")
        except GithubException as e:
            logger.error(f"Failed to update README.md: {e}")
            raise

def main():
    parser = argparse.ArgumentParser(description='GitHub Repository Uploader')
    parser.add_argument('--token', help='GitHub personal access token')
    parser.add_argument('--repo', required=True, help='Repository name')
    parser.add_argument('--path', required=True, help='Local directory path to upload')
    parser.add_argument('--branch', default='main', help='Branch name (default: main)')
    parser.add_argument('--message', default='Initial commit', help='Commit message')
    parser.add_argument('--description', default='', help='Repository description')
    parser.add_argument('--private', action='store_true', help='Make repository private')
    parser.add_argument('--create', action='store_true', help='Create new repository')
    
    args = parser.parse_args()

    try:
        uploader = GitHubUploader(token=args.token)
        
        if args.create:
            try:
                repo = uploader.create_repo(
                    args.repo,
                    description=args.description,
                    private=args.private
                )
            except GithubException as e:
                if "name already exists" in str(e):
                    logger.info(f"Repository {args.repo} already exists. Uploading files...")
                else:
                    raise
        else:
            repo = args.repo

        # Upload directory
        uploader.upload_directory(
            args.repo,
            args.path,
            branch=args.branch,
            commit_message=args.message
        )

        # Create/update README.md
        readme_content = f"# {args.repo}\n\n{args.description}\n\nThis repository was automatically uploaded using GitHub Uploader."
        uploader.update_readme(args.repo, readme_content, branch=args.branch)

    except Exception as e:
        logger.error(f"An error occurred: {e}")
        return 1

    return 0

if __name__ == "__main__":
    exit(main()) 