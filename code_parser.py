"""
code_parser.py - Extract functions and variables from source code
"""
import re
from typing import Dict, List


class CodeParser:
    """Extract functions and variables from code"""
    
    def __init__(self):
        # Control flow keywords to exclude
        self.control_flow = {
            'if', 'else', 'elif', 'for', 'while', 'switch', 'case', 
            'do', 'break', 'continue', 'return', 'goto', 'try', 
            'catch', 'finally', 'throw', 'raises', 'except', 'with',
            'yield', 'assert', 'pass', 'await', 'async', 'defer',
            'select', 'range', 'foreach', 'until', 'unless'
        }
        
        # Built-in types to exclude from variables
        self.builtin_types = {
            'int', 'float', 'double', 'char', 'bool', 'void', 'string',
            'str', 'list', 'dict', 'tuple', 'set', 'array', 'vector',
            'map', 'HashMap', 'ArrayList', 'LinkedList', 'String',
            'Integer', 'Boolean', 'Object', 'Class', 'Interface',
            'var', 'let', 'const', 'auto', 'long', 'short', 'unsigned',
            'signed', 'static', 'final', 'public', 'private', 'protected'
        }
        
        # Language-specific patterns
        self.patterns = {
            'python': {
                'functions': re.compile(r'^\s*def\s+([a-zA-Z_][a-zA-Z0-9_]*)\s*\(', re.MULTILINE),
                'classes': re.compile(r'^\s*class\s+([a-zA-Z_][a-zA-Z0-9_]*)', re.MULTILINE),
                'variables': re.compile(r'^\s*([a-zA-Z_][a-zA-Z0-9_]*)\s*=', re.MULTILINE),
            },
            'javascript': {
                'functions': re.compile(
                    r'(?:function\s+([a-zA-Z_$][a-zA-Z0-9_$]*)\s*\(|'
                    r'(?:const|let|var)\s+([a-zA-Z_$][a-zA-Z0-9_$]*)\s*=\s*(?:async\s+)?(?:function|\(.*?\)\s*=>)|'
                    r'([a-zA-Z_$][a-zA-Z0-9_$]*)\s*:\s*(?:async\s+)?function\s*\(|'
                    r'([a-zA-Z_$][a-zA-Z0-9_$]*)\s*\([^)]*\)\s*\{)',
                    re.MULTILINE
                ),
                'classes': re.compile(r'class\s+([a-zA-Z_$][a-zA-Z0-9_$]*)', re.MULTILINE),
                'variables': re.compile(r'(?:const|let|var)\s+([a-zA-Z_$][a-zA-Z0-9_$]*)\s*=', re.MULTILINE),
            },
            'java': {
                'functions': re.compile(
                    r'(?:public|private|protected|static|\s)+[\w<>\[\]]+\s+([a-zA-Z_][a-zA-Z0-9_]*)\s*\([^)]*\)\s*(?:throws\s+[\w,\s]+)?\s*\{',
                    re.MULTILINE
                ),
                'classes': re.compile(r'(?:public|private|protected)?\s*(?:abstract|final)?\s*class\s+([a-zA-Z_][a-zA-Z0-9_]*)', re.MULTILINE),
                'variables': re.compile(r'(?:private|public|protected|static|final|\s)+[\w<>\[\]]+\s+([a-zA-Z_][a-zA-Z0-9_]*)\s*[=;]', re.MULTILINE),
            },
            'cpp': {
                'functions': re.compile(
                    r'(?:[\w:]+\s+)?([a-zA-Z_][a-zA-Z0-9_]*)\s*\([^)]*\)\s*(?:const)?\s*\{',
                    re.MULTILINE
                ),
                'classes': re.compile(r'class\s+([a-zA-Z_][a-zA-Z0-9_]*)', re.MULTILINE),
                'variables': re.compile(r'(?:int|float|double|char|bool|auto|const|static)\s+([a-zA-Z_][a-zA-Z0-9_]*)\s*[=;]', re.MULTILINE),
            },
            'c': {
                'functions': re.compile(
                    r'(?:[\w\*]+\s+)+([a-zA-Z_][a-zA-Z0-9_]*)\s*\([^)]*\)\s*\{',
                    re.MULTILINE
                ),
                'variables': re.compile(r'(?:int|float|double|char|void|long|short|unsigned|signed|static)\s+\*?\s*([a-zA-Z_][a-zA-Z0-9_]*)\s*[=;\[]', re.MULTILINE),
            },
            'go': {
                'functions': re.compile(r'func\s+(?:\([^)]*\)\s+)?([a-zA-Z_][a-zA-Z0-9_]*)\s*\(', re.MULTILINE),
                'variables': re.compile(r'(?:var|const)\s+([a-zA-Z_][a-zA-Z0-9_]*)\s+', re.MULTILINE),
            },
            'rust': {
                'functions': re.compile(r'fn\s+([a-zA-Z_][a-zA-Z0-9_]*)\s*(?:<[^>]*>)?\s*\(', re.MULTILINE),
                'variables': re.compile(r'let\s+(?:mut\s+)?([a-zA-Z_][a-zA-Z0-9_]*)\s*[=:]', re.MULTILINE),
            },
            'php': {
                'functions': re.compile(r'function\s+([a-zA-Z_][a-zA-Z0-9_]*)\s*\(', re.MULTILINE),
                'classes': re.compile(r'class\s+([a-zA-Z_][a-zA-Z0-9_]*)', re.MULTILINE),
                'variables': re.compile(r'\$([a-zA-Z_][a-zA-Z0-9_]*)\s*=', re.MULTILINE),
            },
            'ruby': {
                'functions': re.compile(r'def\s+([a-zA-Z_][a-zA-Z0-9_?!]*)', re.MULTILINE),
                'classes': re.compile(r'class\s+([a-zA-Z_][a-zA-Z0-9_]*)', re.MULTILINE),
                'variables': re.compile(r'@?([a-zA-Z_][a-zA-Z0-9_]*)\s*=', re.MULTILINE),
            },
            'swift': {
                'functions': re.compile(r'func\s+([a-zA-Z_][a-zA-Z0-9_]*)\s*(?:<[^>]*>)?\s*\(', re.MULTILINE),
                'classes': re.compile(r'(?:class|struct|enum)\s+([a-zA-Z_][a-zA-Z0-9_]*)', re.MULTILINE),
                'variables': re.compile(r'(?:let|var)\s+([a-zA-Z_][a-zA-Z0-9_]*)\s*[=:]', re.MULTILINE),
            },
            'kotlin': {
                'functions': re.compile(r'fun\s+([a-zA-Z_][a-zA-Z0-9_]*)\s*(?:<[^>]*>)?\s*\(', re.MULTILINE),
                'classes': re.compile(r'(?:class|object|interface)\s+([a-zA-Z_][a-zA-Z0-9_]*)', re.MULTILINE),
                'variables': re.compile(r'(?:val|var)\s+([a-zA-Z_][a-zA-Z0-9_]*)\s*[=:]', re.MULTILINE),
            },
        }
    
    def get_language_from_extension(self, ext: str) -> str:
        """Map file extension to language"""
        ext_map = {
            '.py': 'python',
            '.js': 'javascript', '.jsx': 'javascript', '.ts': 'javascript', '.tsx': 'javascript',
            '.java': 'java',
            '.cpp': 'cpp', '.cc': 'cpp', '.cxx': 'cpp', '.hpp': 'cpp', '.h': 'cpp',
            '.c': 'c',
            '.go': 'go',
            '.rs': 'rust',
            '.php': 'php',
            '.rb': 'ruby',
            '.swift': 'swift',
            '.kt': 'kotlin', '.kts': 'kotlin',
            '.cs': 'csharp',
            '.scala': 'scala',
        }
        return ext_map.get(ext.lower(), 'unknown')
    
    def clean_identifier(self, name: str) -> str:
        """Clean and validate identifier"""
        if not name:
            return None
        
        # Remove leading/trailing whitespace
        name = name.strip()
        
        # Filter out control flow keywords
        if name.lower() in self.control_flow:
            return None
        
        # Filter out built-in types
        if name in self.builtin_types:
            return None
        
        # Filter out too short (likely not meaningful)
        if len(name) < 2:
            return None
        
        # Filter out common non-identifiers
        if name in {'main', 'this', 'self', 'super', 'null', 'true', 'false', 'None', 'True', 'False'}:
            return None
        
        # Must start with letter or underscore
        if not re.match(r'^[a-zA-Z_]', name):
            return None
        
        return name
    
    def extract_from_code(self, code: str, language: str) -> Dict[str, List[str]]:
        """Extract functions and variables from code"""
        result = {
            'functions': [],
            'classes': [],
            'variables': []
        }
        
        if language not in self.patterns:
            return result
        
        patterns = self.patterns[language]
        
        # Extract functions
        if 'functions' in patterns:
            matches = patterns['functions'].findall(code)
            # Handle tuple results from multiple capture groups
            if matches:
                if isinstance(matches[0], tuple):
                    # Flatten and filter
                    for match in matches:
                        for name in match:
                            if name:
                                cleaned = self.clean_identifier(name)
                                if cleaned and cleaned not in result['functions']:
                                    result['functions'].append(cleaned)
                else:
                    for name in matches:
                        cleaned = self.clean_identifier(name)
                        if cleaned and cleaned not in result['functions']:
                            result['functions'].append(cleaned)
        
        # Extract classes
        if 'classes' in patterns:
            matches = patterns['classes'].findall(code)
            for name in matches:
                cleaned = self.clean_identifier(name)
                if cleaned and cleaned not in result['classes']:
                    result['classes'].append(cleaned)
        
        # Extract variables (limit to avoid noise)
        if 'variables' in patterns:
            matches = patterns['variables'].findall(code)
            seen = set()
            for name in matches:
                cleaned = self.clean_identifier(name)
                if cleaned and cleaned not in seen and len(result['variables']) < 50:
                    seen.add(cleaned)
                    result['variables'].append(cleaned)
        
        return result