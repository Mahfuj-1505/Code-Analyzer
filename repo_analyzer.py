"""
repo_analyzer.py - Main repository analyzer class
"""
import json
from pathlib import Path
from typing import Dict, List, Tuple
from concurrent.futures import ThreadPoolExecutor, as_completed
import os

from git_utils import GitUtils
from file_filters import FileFilters
from code_parser import CodeParser


class RepoAnalyzer:
    """Analyze repository and extract code information"""
    
    def __init__(self, repo_input: str):
        self.repo_input = repo_input
        self.git_utils = GitUtils(repo_input)
        self.file_filters = None
        self.code_parser = CodeParser()
        self.repo_owners = []
    
    def count_lines(self, file_path: Path) -> int:
        """Count lines in a file"""
        try:
            with open(file_path, 'rb') as f:
                return sum(1 for _ in f)
        except:
            return 0
    
    def calculate_owner_contribution(self, authors: List[str]) -> float:
        """Calculate owner contribution ratio"""
        if not authors or not self.repo_owners:
            return 0.0
        owner_commits = sum(1 for author in authors if author in self.repo_owners)
        return owner_commits / len(authors)
    
    def is_owner_modified(self, authors: List[str]) -> bool:
        """Check if owner touched file"""
        return any(author in self.repo_owners for author in authors)
    
    def extract_code_elements(self, file_path: Path) -> Dict:
        """Extract functions and variables from file"""
        try:
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                code = f.read()
            
            language = self.code_parser.get_language_from_extension(file_path.suffix)
            extracted = self.code_parser.extract_from_code(code, language)
            
            return {
                'language': language,
                'functions': extracted['functions'][:30],  # Limit to top 30
                'classes': extracted['classes'][:20],      # Limit to top 20
                'variables': extracted['variables'][:30]   # Limit to top 30
            }
        except:
            return {
                'language': 'unknown',
                'functions': [],
                'classes': [],
                'variables': []
            }
    
    def process_file(self, file_path: Path, all_file_authors: Dict) -> Tuple[Dict, str]:
        """Process single file and extract information"""
        rel_path_str = str(file_path.relative_to(self.git_utils.repo_path))
        
        # Hard excludes (fastest checks first)
        if self.file_filters.is_excluded_file(file_path):
            return None, 'hard_filter'
        
        if self.file_filters.is_binary(file_path):
            return None, 'hard_filter'
        
        # Gitignore check
        if self.file_filters.matches_gitignore(rel_path_str):
            return None, 'gitignore'
        
        # Generated file check
        if self.file_filters.is_generated_file(file_path):
            return None, 'generated'
        
        # Authorship check
        authors = all_file_authors.get(rel_path_str, [])
        
        if not authors or not self.is_owner_modified(authors):
            return None, 'not_owner'
        
        owner_ratio = self.calculate_owner_contribution(authors)
        
        # Owner contribution threshold
        if not (owner_ratio > 0.3 or (len(authors) >= 3 and owner_ratio > 0)):
            return None, 'not_owner'
        
        # Extension filter
        is_code = self.file_filters.is_code_file(file_path)
        is_config = self.file_filters.is_config_file(file_path)
        
        if not is_code:
            if is_config and owner_ratio < 0.5:
                return None, 'wrong_extension'
            elif not is_config:
                return None, 'wrong_extension'
        
        # Size and line count
        try:
            size = file_path.stat().st_size
            if size > 500000:  # 500KB
                return None, 'generated'
            
            lines = self.count_lines(file_path)
            
            # Extract code elements (functions, variables, classes)
            code_elements = self.extract_code_elements(file_path)
            
        except:
            return None, 'error'
        
        return {
            'path': rel_path_str,
            'lines': lines,
            'owner_contribution': round(owner_ratio, 2),
            'extension': file_path.suffix,
            'language': code_elements['language'],
            'functions': code_elements['functions'],
            'classes': code_elements['classes'],
            'variables': code_elements['variables']
        }, 'accepted'
    
    def analyze_repo(self) -> Dict:
        """Main analysis method"""
        print(f"\n{'='*60}")
        print(f"Analyzing: {self.repo_input}")
        print(f"{'='*60}\n")
        
        # Clone or get local path
        repo_path = self.git_utils.clone_repository()
        
        # Verify it's a git repository
        if not self.git_utils.is_git_repository():
            raise ValueError(f"Not a Git repository: {self.repo_input}")
        
        # Initialize file filters
        self.file_filters = FileFilters(repo_path)
        
        # Identify repository owners
        self.repo_owners = self.git_utils.identify_repo_owners()
        
        # Get file authorship data
        all_file_authors = self.git_utils.get_all_file_authors()
        
        # Get all tracked files
        all_files = self.git_utils.list_tracked_files()
        
        # Filter files
        filtered_files = self.file_filters.filter_files(all_files)
        
        print(f"\nFiltered to {len(filtered_files)} relevant files")
        
        # Statistics
        stats = {
            'total_files_scanned': len(filtered_files),
            'excluded_by_hard_filter': 0,
            'excluded_by_gitignore': 0,
            'excluded_generated': 0,
            'excluded_not_owner_modified': 0,
            'excluded_wrong_extension': 0,
            'user_code_files': 0
        }
        
        user_files = []
        
        print("\nProcessing files and extracting code elements...")
        
        # Parallel processing
        max_workers = min(32, (os.cpu_count() or 4) * 4)
        
        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            futures = {
                executor.submit(self.process_file, file_path, all_file_authors): file_path
                for file_path in filtered_files
            }
            
            completed = 0
            for future in as_completed(futures):
                completed += 1
                if completed % 50 == 0:
                    print(f"Processed {completed}/{len(filtered_files)} files...")
                
                try:
                    file_info, reason = future.result()
                    
                    if file_info:
                        user_files.append(file_info)
                        stats['user_code_files'] += 1
                    else:
                        if reason == 'hard_filter':
                            stats['excluded_by_hard_filter'] += 1
                        elif reason == 'gitignore':
                            stats['excluded_by_gitignore'] += 1
                        elif reason == 'generated':
                            stats['excluded_generated'] += 1
                        elif reason == 'not_owner':
                            stats['excluded_not_owner_modified'] += 1
                        elif reason == 'wrong_extension':
                            stats['excluded_wrong_extension'] += 1
                except Exception:
                    pass
        
        print(f"\n✓ Processed all files")
        
        # Sort by owner contribution
        user_files.sort(key=lambda x: x['owner_contribution'], reverse=True)
        
        result = {
            'repo_url': self.repo_input,
            'repo_owners': self.repo_owners,
            'files': user_files,
            'stats': stats
        }
        
        return result
    
    def save_results(self, output_file: str = 'files.json'):
        """Analyze and save results to JSON"""
        try:
            result = self.analyze_repo()
            
            output_path = Path(output_file)
            with open(output_path, 'w', encoding='utf-8') as f:
                json.dump(result, f, indent=2, ensure_ascii=False)
            
            print(f"\n{'='*60}")
            print(f"Results saved: {output_path.absolute()}")
            print(f"{'='*60}\n")
            
            # Print statistics
            print("Analysis Statistics:")
            print(f"  Total files scanned: {result['stats']['total_files_scanned']}")
            print(f"  Excluded (hard filter): {result['stats']['excluded_by_hard_filter']}")
            print(f"  Excluded (gitignore): {result['stats']['excluded_by_gitignore']}")
            print(f"  Excluded (generated): {result['stats']['excluded_generated']}")
            print(f"  Excluded (not owner): {result['stats']['excluded_not_owner_modified']}")
            print(f"  Excluded (wrong extension): {result['stats']['excluded_wrong_extension']}")
            print(f"  ✓ User code files: {result['stats']['user_code_files']}")
            
            total_lines = sum(f['lines'] for f in result['files'])
            total_functions = sum(len(f['functions']) for f in result['files'])
            total_classes = sum(len(f['classes']) for f in result['files'])
            total_variables = sum(len(f['variables']) for f in result['files'])
            
            print(f"\n  ✓ Total lines of code: {total_lines:,}")
            print(f"  ✓ Total functions: {total_functions:,}")
            print(f"  ✓ Total classes: {total_classes:,}")
            print(f"  ✓ Total variables: {total_variables:,}")
            
            # Show top 10 files
            print(f"\nTop 10 Files by Owner Contribution:")
            for i, file_info in enumerate(result['files'][:10], 1):
                print(f"\n  {i}. {file_info['path']}")
                print(f"     Language: {file_info['language']}")
                print(f"     Lines: {file_info['lines']}")
                print(f"     Owner contribution: {file_info['owner_contribution']*100:.0f}%")
                if file_info['functions']:
                    print(f"     Functions: {', '.join(file_info['functions'][:5])}")
                if file_info['classes']:
                    print(f"     Classes: {', '.join(file_info['classes'][:3])}")
        
        finally:
            if self.git_utils.is_remote:
                self.git_utils.cleanup()
    
    def cleanup(self):
        """Clean up resources"""
        if self.git_utils:
            self.git_utils.cleanup()