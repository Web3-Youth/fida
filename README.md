# GitHub Uploader

A Python script to upload local directories to GitHub repositories with a user-friendly CLI interface.

## Features

- Upload entire directories to GitHub
- Create new repositories
- Update existing repositories
- Progress tracking with visual progress bar
- Custom commit messages
- Automatic README.md creation/updates
- Support for private repositories
- Environment variable support for GitHub token

## Installation

1. Clone this repository:

```bash
git clone https://github.com/yourusername/github-uploader.git
cd github-uploader
```

2. Install the required dependencies:

```bash
pip install -r requirements.txt
```

3. Set up your GitHub token:
   - Create a personal access token on GitHub (Settings -> Developer settings -> Personal access tokens)
   - Either set it as an environment variable:
     ```bash
     export GITHUB_TOKEN='your_token_here'
     ```
   - Or use the `--token` argument when running the script

## Usage

### Basic Usage

```bash
python github_uploader.py --repo your-repo-name --path /path/to/local/directory
```

### Create a New Repository

```bash
python github_uploader.py --create --repo new-repo-name --path /path/to/local/directory --description "My new repository"
```

### Upload to Existing Repository

```bash
python github_uploader.py --repo existing-repo-name --path /path/to/local/directory --branch main --message "Custom commit message"
```

### Make Repository Private

```bash
python github_uploader.py --create --repo private-repo --path /path/to/local/directory --private
```

### Full Options

```
--token TOKEN        GitHub personal access token
--repo REPO          Repository name (required)
--path PATH          Local directory path to upload (required)
--branch BRANCH      Branch name (default: main)
--message MESSAGE    Commit message (default: Initial commit)
--description DESC   Repository description
--private            Make repository private
--create             Create new repository
```

## Error Handling

The script includes comprehensive error handling and logging:

- Invalid GitHub tokens
- Network issues
- File upload failures
- Repository creation/update errors

All errors are logged with timestamps and appropriate error messages.

## License

MIT License
