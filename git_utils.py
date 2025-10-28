"""
git_utils.py - Git repository operations
"""
import subprocess
import tempfile
import shutil
import os
from pathlib import Path
from typing import List, Dict, Tuple
from collections import defaultdict


class GitUtils:
    """Handle Git operations"""
    
    def __init__(self, repo_input: str):
        self.repo_input = repo_input
        self.is_remote = self._is_remote_url(repo_input)
        self.temp_dir = None
        self.repo_path = None
    
    def _is_remote_url(self, path: str) -> bool:
        """Check if input is a remote URL"""
        return path.startswith('http://') or path.startswith('https://') or path.startswith('git@')
    
    def clone_repository(self) -> Path:
        """Clone remote repository or return local path"""
        if not self.is_remote:
            self.repo_path = Path(self.repo_input).expanduser().resolve()
            return self.repo_path
        
        print(f"Cloning repository: {self.repo_input}")
        
        self.temp_dir = tempfile.mkdtemp(prefix='repo_analyzer_')
        self.repo_path = Path(self.temp_dir)
        
        try:
            subprocess.run(
                ['git', 'clone', '--depth', '100', self.repo_input, self.temp_dir],
                capture_output=True,
                text=True,
                check=True,
                timeout=300
            )
            print(f"✓ Cloned successfully")
            return self.repo_path
            
        except subprocess.CalledProcessError as e:
            print(f"Clone failed: {e.stderr}")
            self.cleanup()
            raise
        except subprocess.TimeoutExpired:
            print("Clone timeout")
            self.cleanup()
            raise
    
    def cleanup(self):
        """Remove temporary directory"""
        if self.temp_dir and os.path.exists(self.temp_dir):
            shutil.rmtree(self.temp_dir, ignore_errors=True)
            print("✓ Cleaned up temporary files")
    
    def run_git_command(self, cmd: List[str], timeout=60) -> str:
        """Run git command with timeout"""
        try:
            result = subprocess.run(
                cmd,
                cwd=self.repo_path,
                capture_output=True,
                text=True,
                check=True,
                timeout=timeout
            )
            return result.stdout.strip()
        except (subprocess.CalledProcessError, subprocess.TimeoutExpired):
            return ""
    
    def identify_repo_owners(self, top_n: int = 3) -> List[str]:
        """Identify top contributors"""
        print("Identifying repository owners...")
        
        output = self.run_git_command([
            'git', 'shortlog', '-sn', '--all', '--no-merges'
        ])
        
        if not output:
            return []
        
        authors = []
        for line in output.split('\n'):
            if line.strip():
                parts = line.strip().split('\t', 1)
                if len(parts) == 2:
                    count = int(parts[0])
                    author = parts[1]
                    authors.append((author, count))
        
        authors.sort(key=lambda x: x[1], reverse=True)
        top_count = min(top_n, len(authors))
        owners = [author for author, _ in authors[:top_count]]
        
        print(f"Repository owners: {owners}")
        return owners
    
    def get_all_file_authors(self) -> Dict[str, List[str]]:
        """Get authors for all files in repository"""
        print("Analyzing file authorship...")
        
        output = self.run_git_command([
            'git', 'log', '--all', '--name-only', 
            '--pretty=format:AUTHOR:%an', '--no-merges'
        ], timeout=120)
        
        if not output:
            return {}
        
        file_authors = defaultdict(list)
        current_author = None
        
        for line in output.split('\n'):
            if line.startswith('AUTHOR:'):
                current_author = line[7:].strip()
            elif line.strip() and current_author and not line.startswith('AUTHOR:'):
                file_authors[line.strip()].append(current_author)
        
        print(f"✓ Analyzed authorship for {len(file_authors)} files")
        return dict(file_authors)
    
    def list_tracked_files(self) -> List[Path]:
        """Get all tracked files from git"""
        print("Getting tracked files from git...")
        
        output = self.run_git_command(['git', 'ls-files'])
        
        if not output:
            return []
        
        files = []
        for line in output.split('\n'):
            if line.strip():
                file_path = self.repo_path / line.strip()
                if file_path.exists():
                    files.append(file_path)
        
        print(f"Found {len(files)} tracked files")
        return files
    
    def is_git_repository(self) -> bool:
        """Check if path is a valid git repository"""
        if self.repo_path is None:
            return False
        return (self.repo_path / '.git').exists()