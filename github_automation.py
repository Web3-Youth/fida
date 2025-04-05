#!/usr/bin/env python3
import os
import argparse
from pathlib import Path
from github import Github
from github import GithubException
from tqdm import tqdm
from dotenv import load_dotenv
import logging
from rich.console import Console
from rich.panel import Panel
from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn, TaskProgressColumn
from rich.table import Table
from rich.markdown import Markdown
from rich.prompt import Prompt, Confirm, IntPrompt
import pyfiglet
from datetime import datetime
import json
import re
import subprocess
import sys
from path_helper import PathHelper

# Configure rich console
console = Console()

class ConfigManager:
    def __init__(self, config_file="config.json"):
        self.config_file = config_file
        self.config = self.load_config()

    def load_config(self):
        """Load configuration from file."""
        if os.path.exists(self.config_file):
            with open(self.config_file, 'r') as f:
                return json.load(f)
        return self.create_default_config()

    def create_default_config(self):
        """Create default configuration file."""
        default_config = {
            "default_settings": {
                "branch": "main",
                "private": False,
                "auto_init": True,
                "excluded_dirs": [
                    "node_modules", "dist", ".git", "__pycache__", "venv", "env",
                    ".idea", ".vscode", "build", "coverage", ".next"
                ],
                "excluded_patterns": [
                    ".env", "package-lock.json", ".pyc", ".pyo", ".pyd",
                    ".so", ".dll", ".dylib", ".log", ".tmp", ".temp",
                    ".DS_Store", "Thumbs.db", ".swp", ".swo", "*.pyc"
                ],
                "readme_template": {
                    "features": [
                        "Automated repository management",
                        "Professional README generation",
                        "File upload with progress tracking",
                        "Customizable repository settings"
                    ],
                    "license": "MIT License",
                    "contact": {
                        "name": "Your Name",
                        "twitter": "@yourtwitter"
                    }
                }
            },
            "user_settings": {
                "github_token": "",
                "default_username": "",
                "default_email": "",
                "preferred_editor": "code"
            }
        }
        self.save_config(default_config)
        return default_config

    def save_config(self, config=None):
        """Save configuration to file."""
        if config:
            self.config = config
        with open(self.config_file, 'w') as f:
            json.dump(self.config, f, indent=4)

    def update_user_settings(self, settings):
        """Update user settings in configuration."""
        self.config["user_settings"].update(settings)
        self.save_config()

    def get_setting(self, section, key):
        """Get a specific setting from configuration."""
        return self.config[section].get(key)

class GitHubAutomation:
    def __init__(self, token=None):
        """Initialize the GitHub automation tool with authentication."""
        self.config_manager = ConfigManager()
        load_dotenv()
        self.token = token or os.getenv('GITHUB_TOKEN') or self.config_manager.get_setting('user_settings', 'github_token')
        if not self.token:
            self.setup_initial_config()
        self.github = Github(self.token)
        self.user = self.github.get_user()
        self.console = Console()

    def setup_initial_config(self):
        """Setup initial configuration interactively."""
        self.console.print("[bold yellow]Welcome to GitHub Automation Tool![/bold yellow]")
        self.console.print("Let's set up your configuration first.\n")

        token = Prompt.ask("[cyan]Enter your GitHub Personal Access Token[/cyan]")
        username = Prompt.ask("[cyan]Enter your GitHub username[/cyan]")
        email = Prompt.ask("[cyan]Enter your GitHub email[/cyan]")
        editor = Prompt.ask("[cyan]Enter your preferred code editor command[/cyan]", default="code")

        self.config_manager.update_user_settings({
            "github_token": token,
            "default_username": username,
            "default_email": email,
            "preferred_editor": editor
        })

        self.token = token
        self.console.print("\n[green]✓ Configuration saved successfully![/green]\n")

    def interactive_repo_creation(self):
        """Interactive repository creation process."""
        self.console.print("[bold cyan]Let's create a new repository![/bold cyan]\n")
        
        repo_name = Prompt.ask("[cyan]Enter repository name[/cyan]")
        # Clean repository name
        repo_name = re.sub(r'[^a-zA-Z0-9-]', '-', repo_name).lower()
        self.console.print(f"[yellow]Note: Repository name will be: {repo_name}[/yellow]")
        
        description = Prompt.ask("[cyan]Enter repository description[/cyan]")
        private = Confirm.ask("[cyan]Make repository private?[/cyan]", default=False)
        
        features = []
        self.console.print("\n[cyan]Enter repository features (press Enter twice to finish):[/cyan]")
        while True:
            feature = Prompt.ask("Feature")
            if not feature:
                break
            features.append(feature)

        return {
            "repo_name": repo_name,
            "description": description,
            "private": private,
            "features": features
        }

    def interactive_file_upload(self):
        """Interactive file upload process."""
        self.console.print("\n[bold cyan]Let's upload your project![/bold cyan]\n")
        
        # Use the PathHelper to select directory
        path = PathHelper.select_directory()
        if not path:
            return None

        branch = Prompt.ask("[cyan]Enter branch name[/cyan]", default="main")
        # Clean branch name
        branch = re.sub(r'[^a-zA-Z0-9-]', '-', branch).lower()
        self.console.print(f"[yellow]Note: Branch name will be: {branch}[/yellow]")
        
        message = Prompt.ask("[cyan]Enter commit message[/cyan]", default="Initial commit")

        return {
            "path": path,
            "branch": branch,
            "message": message
        }

    def edit_readme(self, content):
        """Open README content in editor for editing."""
        temp_file = "README_TEMP.md"
        with open(temp_file, "w", encoding="utf-8") as f:
            f.write(content)

        editor = self.config_manager.get_setting('user_settings', 'preferred_editor')
        
        # Try to find a suitable editor
        editors = [
            editor,  # User's preferred editor
            "notepad",  # Windows default
            "notepad.exe",  # Windows default (full path)
            "code",  # VS Code
            "code.cmd",  # VS Code (Windows)
            "nano",  # Unix default
            "vim",  # Common Unix editor
            "vi"  # Most basic Unix editor
        ]

        for editor_cmd in editors:
            try:
                if os.name == 'nt':  # Windows
                    subprocess.run([editor_cmd, temp_file], shell=True)
                else:  # Unix-like
                    subprocess.run([editor_cmd, temp_file])
                break
            except (FileNotFoundError, subprocess.SubprocessError):
                continue
        else:
            self.console.print("[yellow]No suitable editor found. Opening in default text editor...[/yellow]")
            if os.name == 'nt':  # Windows
                os.startfile(temp_file)
            else:  # Unix-like
                subprocess.run(['xdg-open', temp_file])

        input("\nPress Enter when you're done editing the README...")

        with open(temp_file, "r", encoding="utf-8") as f:
            edited_content = f.read()

        os.remove(temp_file)
        return edited_content

    def print_banner(self):
        """Print a colorful banner for the tool."""
        banner = pyfiglet.figlet_format("GitHub Automator", font="slant")
        self.console.print(Panel.fit(banner, style="bold blue"))
        self.console.print("[bold green]Professional GitHub Automation Tool[/bold green]")
        self.console.print("[yellow]Version 1.0.0[/yellow]\n")

    def should_exclude_file(self, file_path):
        """Check if a file should be excluded from upload."""
        excluded_dirs = set(self.config_manager.get_setting('default_settings', 'excluded_dirs'))
        excluded_patterns = set(self.config_manager.get_setting('default_settings', 'excluded_patterns'))

        parts = Path(file_path).parts
        if any(excluded_dir in parts for excluded_dir in excluded_dirs):
            return True

        if any(file_path.endswith(pattern) for pattern in excluded_patterns):
            return True

        return False

    def generate_readme_content(self, repo_name, description, features=None, installation=None, usage=None):
        """Generate a professional README.md content."""
        if features is None:
            features = self.config_manager.get_setting('default_settings', 'readme_template')['features']
        
        if installation is None:
            installation = """```bash
pip install -r requirements.txt
```"""

        if usage is None:
            usage = """```bash
python github_automation.py --create --repo your-repo-name --path ./your-project
```"""

        contact = self.config_manager.get_setting('default_settings', 'readme_template')['contact']
        license_text = self.config_manager.get_setting('default_settings', 'readme_template')['license']

        readme_content = f"""# {repo_name}

{description}

## 🚀 Features

{chr(10).join(f'- {feature}' for feature in features)}

## 📦 Installation

{installation}

## 💻 Usage

{usage}

## 📝 License

{license_text}

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## 📄 Documentation

For more information, please visit the [documentation](https://github.com/{self.user.login}/{repo_name}/wiki).

## 🛠️ Built With

- Python 3.x
- PyGithub
- Rich (for beautiful CLI)
- TQDM (for progress bars)

## 📫 Contact

{contact['name']} - [@{contact['twitter']}](https://twitter.com/{contact['twitter'].lstrip('@')})

Project Link: [https://github.com/{self.user.login}/{repo_name}](https://github.com/{self.user.login}/{repo_name})

## 🙏 Acknowledgments

- Hat tip to anyone whose code was used
- Inspiration
- etc
"""
        return readme_content

    def create_repo(self, repo_name, description="", private=False, auto_init=True):
        """Create a new GitHub repository with enhanced features."""
        try:
            # Clean repository name
            repo_name = re.sub(r'[^a-zA-Z0-9-]', '-', repo_name).lower()
            
            with self.console.status("[bold green]Creating repository...") as status:
                repo = self.user.create_repo(
                    name=repo_name,
                    description=description,
                    private=private,
                    auto_init=auto_init
                )
                self.console.print(f"[green]✓[/green] Created repository: [bold blue]{repo.full_name}[/bold blue]")
                return repo
        except GithubException as e:
            self.console.print(f"[red]✗[/red] Failed to create repository: {e}")
            raise

    def upload_directory(self, repo_name, local_path, branch="main", commit_message="Initial commit"):
        """Upload a local directory to GitHub repository with enhanced progress tracking."""
        try:
            # Clean branch name
            branch = re.sub(r'[^a-zA-Z0-9-]', '-', branch).lower()
            
            repo = self.get_repo(repo_name)
            
            # Create branch if it doesn't exist
            try:
                repo.get_branch(branch)
            except GithubException as e:
                if e.status == 404:
                    # Get the default branch (usually main or master)
                    default_branch = repo.default_branch
                    default_branch_ref = repo.get_git_ref(f"heads/{default_branch}")
                    # Create new branch
                    repo.create_git_ref(f"refs/heads/{branch}", default_branch_ref.object.sha)
                    self.console.print(f"[green]✓[/green] Created branch: {branch}")
                else:
                    raise
            
            files_to_upload = []
            for root, _, files in os.walk(local_path):
                for file in files:
                    file_path = os.path.join(root, file)
                    relative_path = os.path.relpath(file_path, local_path)
                    
                    if self.should_exclude_file(relative_path):
                        self.console.print(f"[yellow]Skipping[/yellow] {relative_path}")
                        continue
                        
                    files_to_upload.append((file_path, relative_path))

            self.console.print(f"[bold green]Found {len(files_to_upload)} files to upload[/bold green]")

            with Progress(
                SpinnerColumn(),
                TextColumn("[progress.description]{task.description}"),
                BarColumn(),
                TaskProgressColumn(),
                console=self.console
            ) as progress:
                task = progress.add_task("[cyan]Uploading files...", total=len(files_to_upload))
                
                for file_path, relative_path in files_to_upload:
                    try:
                        with open(file_path, 'rb') as file:
                            content = file.read()
                        
                        try:
                            contents = repo.get_contents(relative_path, ref=branch)
                            repo.update_file(
                                path=relative_path,
                                message=f"Update {relative_path}",
                                content=content,
                                sha=contents.sha,
                                branch=branch
                            )
                            self.console.print(f"[green]✓[/green] Updated: {relative_path}")
                        except GithubException as e:
                            if e.status == 404:
                                repo.create_file(
                                    path=relative_path,
                                    message=f"Add {relative_path}",
                                    content=content,
                                    branch=branch
                                )
                                self.console.print(f"[green]✓[/green] Created: {relative_path}")
                            else:
                                self.console.print(f"[red]✗[/red] Error with {relative_path}: {e}")
                                raise
                        
                        progress.update(task, advance=1)
                    except Exception as e:
                        self.console.print(f"[red]✗[/red] Failed to upload {relative_path}: {e}")
                        continue

            self.console.print("[bold green]✓ Upload completed successfully![/bold green]")
            return True
        except GithubException as e:
            self.console.print(f"[red]✗[/red] Failed to upload directory: {e}")
            raise

    def update_readme(self, repo_name, content, branch="main"):
        """Update the README.md file with enhanced formatting."""
        try:
            repo = self.get_repo(repo_name)
            try:
                contents = repo.get_contents("README.md", ref=branch)
                repo.update_file(
                    path="README.md",
                    message="Update README.md with enhanced formatting",
                    content=content,
                    sha=contents.sha,
                    branch=branch
                )
            except GithubException as e:
                if e.status == 404:
                    repo.create_file(
                        path="README.md",
                        message="Create README.md with enhanced formatting",
                        content=content,
                        branch=branch
                    )
                else:
                    raise
            self.console.print("[green]✓[/green] README.md updated successfully!")
        except GithubException as e:
            self.console.print(f"[red]✗[/red] Failed to update README.md: {e}")
            raise

    def get_repo(self, repo_name):
        """Get an existing repository."""
        try:
            return self.user.get_repo(repo_name)
        except GithubException as e:
            self.console.print(f"[red]✗[/red] Failed to get repository: {e}")
            raise

    def show_repo_info(self, repo_name):
        """Display repository information in a formatted table."""
        try:
            repo = self.get_repo(repo_name)
            table = Table(title=f"Repository Information: {repo.full_name}")
            
            table.add_column("Property", style="cyan")
            table.add_column("Value", style="green")
            
            table.add_row("Description", repo.description or "No description")
            table.add_row("Visibility", "Private" if repo.private else "Public")
            table.add_row("Stars", str(repo.stargazers_count))
            table.add_row("Forks", str(repo.forks_count))
            table.add_row("Watchers", str(repo.watchers_count))
            table.add_row("Created", repo.created_at.strftime("%Y-%m-%d %H:%M:%S"))
            table.add_row("Last Updated", repo.updated_at.strftime("%Y-%m-%d %H:%M:%S"))
            
            self.console.print(table)
        except GithubException as e:
            self.console.print(f"[red]✗[/red] Failed to get repository information: {e}")

def main():
    parser = argparse.ArgumentParser(description='Professional GitHub Automation Tool')
    parser.add_argument('--token', help='GitHub personal access token')
    parser.add_argument('--repo', help='Repository name')
    parser.add_argument('--path', help='Local directory path to upload')
    parser.add_argument('--branch', default='main', help='Branch name (default: main)')
    parser.add_argument('--message', default='Initial commit', help='Commit message')
    parser.add_argument('--description', default='', help='Repository description')
    parser.add_argument('--private', action='store_true', help='Make repository private')
    parser.add_argument('--create', action='store_true', help='Create new repository')
    parser.add_argument('--info', action='store_true', help='Show repository information')
    parser.add_argument('--interactive', action='store_true', help='Run in interactive mode')
    
    args = parser.parse_args()

    try:
        automator = GitHubAutomation(token=args.token)
        automator.print_banner()

        if args.interactive:
            # Interactive mode
            while True:
                automator.console.print("\n[bold cyan]GitHub Automation Menu[/bold cyan]")
                automator.console.print("1. Create and upload new repository")
                automator.console.print("2. Upload to existing repository")
                automator.console.print("3. Show repository information")
                automator.console.print("4. Update configuration")
                automator.console.print("5. Exit")
                
                choice = IntPrompt.ask("\n[cyan]Enter your choice[/cyan]", choices=["1", "2", "3", "4", "5"])
                
                if choice == 1:
                    # Create and upload new repository
                    repo_info = automator.interactive_repo_creation()
                    upload_info = automator.interactive_file_upload()
                    
                    if upload_info:
                        repo = automator.create_repo(
                            repo_info["repo_name"],
                            description=repo_info["description"],
                            private=repo_info["private"]
                        )
                        
                        readme_content = automator.generate_readme_content(
                            repo_info["repo_name"],
                            repo_info["description"],
                            features=repo_info["features"]
                        )
                        
                        if Confirm.ask("\n[cyan]Would you like to edit the README before uploading?[/cyan]"):
                            readme_content = automator.edit_readme(readme_content)
                        
                        automator.upload_directory(
                            repo_info["repo_name"],
                            upload_info["path"],
                            branch=upload_info["branch"],
                            commit_message=upload_info["message"]
                        )
                        
                        automator.update_readme(
                            repo_info["repo_name"],
                            readme_content,
                            branch=upload_info["branch"]
                        )
                
                elif choice == 2:
                    # Upload to existing repository
                    repo_name = Prompt.ask("[cyan]Enter repository name[/cyan]")
                    upload_info = automator.interactive_file_upload()
                    
                    if upload_info:
                        automator.upload_directory(
                            repo_name,
                            upload_info["path"],
                            branch=upload_info["branch"],
                            commit_message=upload_info["message"]
                        )
                
                elif choice == 3:
                    # Show repository information
                    repo_name = Prompt.ask("[cyan]Enter repository name[/cyan]")
                    automator.show_repo_info(repo_name)
                
                elif choice == 4:
                    # Update configuration
                    automator.setup_initial_config()
                
                elif choice == 5:
                    # Exit
                    automator.console.print("\n[bold green]Thank you for using GitHub Automation Tool![/bold green]")
                    break
        else:
            # Command-line mode
            if args.info and args.repo:
                automator.show_repo_info(args.repo)
                return

            if args.create:
                try:
                    repo = automator.create_repo(
                        args.repo,
                        description=args.description,
                        private=args.private
                    )
                except GithubException as e:
                    if "name already exists" in str(e):
                        automator.console.print(f"[yellow]Repository {args.repo} already exists. Uploading files...[/yellow]")
                    else:
                        raise
            else:
                repo = args.repo

            if args.path:
                readme_content = automator.generate_readme_content(
                    args.repo,
                    args.description
                )

                automator.upload_directory(
                    args.repo,
                    args.path,
                    branch=args.branch,
                    commit_message=args.message
                )

                automator.update_readme(args.repo, readme_content, branch=args.branch)

    except Exception as e:
        automator.console.print(f"[red]✗[/red] An error occurred: {e}")
        return 1

    return 0

if __name__ == "__main__":
    exit(main()) 