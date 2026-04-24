"""Git Automation - Version control, GitHub integration, CI/CD."""

import subprocess
import os
from typing import List, Dict, Tuple, Optional
import logging

logger = logging.getLogger('GitAutomation')

class GitManager:
    """Automate Git operations."""
    
    def __init__(self, repo_path: str = "."):
        self.repo_path = repo_path
        self.remote_url = None
    
    def _run(self, cmd: List[str]) -> Tuple[bool, str, str]:
        try:
            result = subprocess.run(
                ["git"] + cmd,
                cwd=self.repo_path,
                capture_output=True,
                text=True,
                check=True
            )
            return True, result.stdout, result.stderr
        except subprocess.CalledProcessError as e:
            return False, e.stdout, e.stderr
        except FileNotFoundError:
            return False, "", "Git not found"
    
    def is_repo(self) -> bool:
        """Check if directory is a git repo."""
        success, _, _ = self._run(["rev-parse", "--git-dir"])
        return success
    
    def init_repo(self) -> bool:
        """Initialize new repository."""
        success, out, err = self._run(["init"])
        if success:
            logger.info(f"✓ Git repo initialized at {self.repo_path}")
        return success
    
    def add_remote(self, name: str, url: str) -> bool:
        """Add remote repository."""
        success, _, _ = self._run(["remote", "add", name, url])
        if success:
            logger.info(f"✓ Added remote {name}: {url}")
            self.remote_url = url
        return success
    
    def status(self) -> Dict[str, any]:
        """Get repository status."""
        success, out, _ = self._run(["status", "--porcelain", "-b"])
        if not success:
            return {"error": "Not a git repository"}
        
        lines = out.strip().split('\n')
        branch_line = lines[0] if lines else "## master"
        branch = branch_line.replace("## ", "").split('...')[0]
        
        staged = []
        unstaged = []
        untracked = []
        
        for line in lines[1:]:
            if not line:
                continue
            status_code = line[:2]
            filename = line[3:]
            
            if status_code[0] in 'AMDR':
                staged.append(filename)
            if status_code[1] in 'MD':
                unstaged.append(filename)
            if status_code == '??':
                untracked.append(filename)
        
        return {
            "branch": branch,
            "staged": staged,
            "unstaged": unstaged,
            "untracked": untracked,
            "clean": not (staged or unstaged or untracked)
        }
    
    def add(self, files: List[str] = None) -> bool:
        """Stage files."""
        if files:
            success, _, _ = self._run(["add"] + files)
        else:
            success, _, _ = self._run(["add", "."])
        return success
    
    def commit(self, message: str) -> bool:
        """Commit changes."""
        success, _, _ = self._run(["commit", "-m", message])
        if success:
            logger.info(f"✓ Committed: {message[:50]}...")
        return success
    
    def push(self, remote: str = "origin", branch: str = None) -> bool:
        """Push to remote."""
        if not branch:
            # Get current branch
            success, out, _ = self._run(["rev-parse", "--abbrev-ref", "HEAD"])
            branch = out.strip() if success else "main"
        
        success, _, _ = self._run(["push", remote, branch])
        if success:
            logger.info(f"✓ Pushed to {remote}/{branch}")
        return success
    
    def pull(self, remote: str = "origin", branch: str = None) -> bool:
        """Pull from remote."""
        cmd = ["pull", remote]
        if branch:
            cmd.append(branch)
        success, _, _ = self._run(cmd)
        return success
    
    def stash(self, message: str = None) -> bool:
        """Stash changes."""
        cmd = ["stash", "push"]
        if message:
            cmd.extend(["-m", message])
        success, _, _ = self._run(cmd)
        return success
    
    def log(self, n: int = 10) -> List[Dict]:
        """Get commit history."""
        format_str = "%H|%an|%ae|%ad|%s"
        success, out, _ = self._run([
            "log", f"--pretty=format:{format_str}",
            "--date=short", "-n", str(n)
        ])
        
        if not success:
            return []
        
        commits = []
        for line in out.strip().split('\n'):
            parts = line.split('|')
            if len(parts) >= 5:
                commits.append({
                    "hash": parts[0][:7],
                    "author": parts[1],
                    "email": parts[2],
                    "date": parts[3],
                    "message": parts[4]
                })
        
        return commits
    
    def create_branch(self, name: str, checkout: bool = True) -> bool:
        """Create new branch."""
        if checkout:
            success, _, _ = self._run(["checkout", "-b", name])
        else:
            success, _, _ = self._run(["branch", name])
        
        if success:
            logger.info(f"✓ Created branch: {name}")
        return success
    
    def switch_branch(self, name: str) -> bool:
        """Switch to branch."""
        success, _, _ = self._run(["checkout", name])
        if success:
            logger.info(f"✓ Switched to branch: {name}")
        return success
    
    def auto_commit_all(self, message: str = None) -> bool:
        """Add all and commit with auto-generated message."""
        if not message:
            status = self.status()
            files = len(status.get('staged', [])) + len(status.get('unstaged', []))
            message = f"Auto-commit: {files} files updated"
        
        self.add()
        return self.commit(message)

class GitHubManager:
    """GitHub Desktop and API integration."""
    
    def __init__(self, token: Optional[str] = None):
        self.token = token or os.getenv('GITHUB_TOKEN')
    
    def create_repo(self, name: str, private: bool = True, description: str = "") -> bool:
        """Create GitHub repository via API."""
        if not self.token:
            logger.error("GitHub token required")
            return False
        
        try:
            import requests
            
            url = "https://api.github.com/user/repos"
            headers = {
                "Authorization": f"token {self.token}",
                "Accept": "application/vnd.github.v3+json"
            }
            data = {
                "name": name,
                "private": private,
                "description": description,
                "auto_init": True
            }
            
            response = requests.post(url, headers=headers, json=data)
            
            if response.status_code == 201:
                repo_data = response.json()
                logger.info(f"✓ Created GitHub repo: {repo_data['html_url']}")
                return True
            else:
                logger.error(f"Failed to create repo: {response.json()}")
                return False
                
        except ImportError:
            logger.error("pip install requests")
            return False
    
    def open_desktop(self, repo_path: str = None):
        """Open GitHub Desktop."""
        try:
            if repo_path:
                subprocess.Popen(["github", repo_path], shell=True)
            else:
                subprocess.Popen(["github"], shell=True)
            return True
        except:
            logger.error("GitHub Desktop not found")
            return False
    
    def sync_to_github(self, repo_path: str, remote_name: str = "origin") -> bool:
        """Sync local repo to GitHub."""
        git = GitManager(repo_path)
        
        if not git.is_repo():
            logger.error(f"{repo_path} is not a git repository")
            return False
        
        # Check if remote exists
        success, out, _ = git._run(["remote", "-v"])
        if remote_name not in out:
            logger.error(f"Remote '{remote_name}' not found")
            return False
        
        # Add, commit, push
        git.auto_commit_all("Auto-sync from Financial Master")
        return git.push(remote_name)

class RepositoryBackup:
    """Automated repository backup."""
    
    def __init__(self, source_path: str, backup_path: str):
        self.source = source_path
        self.backup = backup_path
    
    def create_backup(self) -> bool:
        """Create timestamped backup."""
        from datetime import datetime
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_name = f"financial_master_backup_{timestamp}"
        backup_dir = os.path.join(self.backup, backup_name)
        
        try:
            import shutil
            shutil.copytree(self.source, backup_dir, ignore=shutil.ignore_patterns(
                'node_modules', '__pycache__', '.venv', '*.pyc'
            ))
            logger.info(f"✓ Backup created: {backup_dir}")
            return True
        except Exception as e:
            logger.error(f"Backup failed: {e}")
            return False
    
    def backup_to_git(self, message: str = "Automated backup") -> bool:
        """Commit and push backup."""
        git = GitManager(self.source)
        
        if not git.is_repo():
            git.init_repo()
            git.add_remote("origin", os.getenv('BACKUP_REMOTE_URL', ''))
        
        return git.auto_commit_all(message) and git.push()

class CICDManager:
    """CI/CD pipeline management."""
    
    def __init__(self, repo_path: str):
        self.repo = repo_path
        self.git = GitManager(repo_path)
    
    def create_github_actions_workflow(self):
        """Create GitHub Actions workflow file."""
        workflow_dir = os.path.join(self.repo, ".github", "workflows")
        os.makedirs(workflow_dir, exist_ok=True)
        
        workflow_content = """name: Financial Master CI

on:
  push:
    branches: [ main, develop ]
  pull_request:
    branches: [ main ]

jobs:
  test:
    runs-on: ubuntu-latest
    
    steps:
    - uses: actions/checkout@v3
    
    - name: Set up Python
      uses: actions/setup-python@v4
      with:
        python-version: '3.11'
    
    - name: Install dependencies
      run: |
        pip install -r requirements.txt
    
    - name: Run tests
      run: |
        python 26_Integration_Tests.py
    
    - name: Build Docker
      run: |
        docker build -t financial-master:test .
"""
        
        workflow_file = os.path.join(workflow_dir, "ci.yml")
        with open(workflow_file, 'w') as f:
            f.write(workflow_content)
        
        logger.info(f"✓ Created GitHub Actions workflow")
        
        # Commit the workflow
        self.git.add([".github/workflows/ci.yml"])
        self.git.commit("Add CI/CD workflow")
        
        return True

if __name__ == "__main__":
    print("Git Automation ready")
    print("Usage:")
    print("  git = GitManager('.')")
    print("  git.status()")
    print("  git.auto_commit_all()")
    print("  git.push()")
