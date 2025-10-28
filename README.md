# Repository Code Analyzer

A Python tool that analyzes Git repositories to extract user-written code, functions, variables, and classes.

## Features

- 🔍 Identifies repository owners (top contributors)
- 📝 Extracts functions, classes, and variables from code
- 🎯 Filters out generated code, dependencies, and build artifacts
- 📊 Calculates code ownership metrics
- 🚀 Parallel processing for fast analysis
- 🌐 Supports multiple programming languages (Python, JavaScript, Java, C/C++, Go, Rust, PHP, Ruby, Swift, Kotlin, etc.)

## File Structure

```
repo-analyzer/
├── main.py              # Entry point - run this file
├── repo_analyzer.py     # Main analyzer logic
├── git_utils.py         # Git operations (clone, authorship)
├── file_filters.py      # File filtering and exclusion
├── code_parser.py       # Extract functions/variables from code
└── files.json           # Output file (generated after analysis)
```

## Installation

No additional packages required! Uses only Python standard library.

Requirements:
- Python 3.7+
- Git installed and available in PATH

## Usage

### Basic Usage

```bash
python main.py
```

Then follow the prompts:
1. Enter repository URL (e.g., `https://github.com/user/repo`) or local path
2. Specify output filename (default: `files.json`)

### Example

```bash
$ python main.py
============================================================
Repository Code Analyzer with Function/Variable Extraction
============================================================

Enter repository URL or local path: https://github.com/torvalds/linux
Output file name (default: files.json): linux_analysis.json

Cloning repository...
✓ Cloned successfully
Identifying owners...
...
```

## Output Format

The tool generates a JSON file with the following structure:

```json
{
  "repo_url": "https://github.com/user/repo",
  "repo_owners": ["John Doe", "Jane Smith", "Bob Johnson"],
  "files": [
    {
      "path": "src/main.py",
      "lines": 250,
      "owner_contribution": 0.85,
      "extension": ".py",
      "language": "python",
      "functions": ["main", "process_data", "calculate_metrics"],
      "classes": ["DataProcessor", "MetricsCalculator"],
      "variables": ["config", "results", "data_cache"]
    }
  ],
  "stats": {
    "total_files_scanned": 1000,
    "excluded_by_hard_filter": 200,
    "excluded_by_gitignore": 150,
    "excluded_generated": 100,
    "excluded_not_owner_modified": 300,
    "excluded_wrong_extension": 50,
    "user_code_files": 200
  }
}
```

## What Gets Filtered Out?

The analyzer automatically excludes:

- **Dependencies**: `node_modules`, `vendor`, `site-packages`, etc.
- **Build artifacts**: `build/`, `dist/`, `target/`, `.next/`
- **Generated code**: Files with "auto-generated" markers, migrations, protobuf files
- **Lock files**: `package-lock.json`, `Cargo.lock`, etc.
- **Binary files**: Images, fonts, executables
- **Non-owner files**: Files not significantly modified by top contributors
- **Gitignored files**: Files matching `.gitignore` patterns

## Supported Languages

| Language   | Functions | Classes | Variables |
|------------|-----------|---------|-----------|
| Python     | ✅        | ✅      | ✅        |
| JavaScript | ✅        | ✅      | ✅        |
| TypeScript | ✅        | ✅      | ✅        |
| Java       | ✅        | ✅      | ✅        |
| C/C++      | ✅        | ✅      | ✅        |
| Go         | ✅        | -       | ✅        |
| Rust       | ✅        | -       | ✅        |
| PHP        | ✅        | ✅      | ✅        |
| Ruby       | ✅        | ✅      | ✅        |
| Swift      | ✅        | ✅      | ✅        |
| Kotlin     | ✅        | ✅      | ✅        |

## Configuration

### Adjusting Owner Count

Edit `repo_analyzer.py`:
```python
self.repo_owners = self.git_utils.identify_repo_owners(top_n=5)  # Change from 3 to 5
```

### Adjusting Contribution Threshold

Edit `repo_analyzer.py` in `process_file()`:
```python
if not (owner_ratio > 0.5 or (len(authors) >= 3 and owner_ratio > 0)):  # Change 0.3 to 0.5
```

### Limiting Extracted Elements

Edit `repo_analyzer.py` in `extract_code_elements()`:
```python
'functions': extracted['functions'][:50],  # Change limit from 30 to 50
```

## Performance

- Uses parallel processing (32+ workers)
- Shallow git clone (depth=100) for remote repos
- Optimized regex patterns
- Compiled gitignore patterns
- Typical speed: 1000+ files in 1-2 minutes

## Troubleshooting

### "Not a Git repository" error
Make sure the path points to a valid git repository with a `.git` folder.

### Clone timeout
For very large repositories, increase timeout in `git_utils.py`:
```python
timeout=600  # Change from 300 to 600 seconds
```

### Missing functions/variables
Some complex code patterns might not be detected. The regex patterns prioritize precision over recall to avoid false positives.

### Memory issues
For extremely large repositories, reduce parallel workers in `repo_analyzer.py`:
```python
max_workers = min(16, (os.cpu_count() or 4) * 2)  # Reduce from 32
```

## Example Output

```
============================================================
Results saved: /path/to/files.json
============================================================

Analysis Statistics:
  Total files scanned: 850
  Excluded (hard filter): 120
  Excluded (gitignore): 80
  Excluded (generated): 50
  Excluded (not owner): 200
  Excluded (wrong extension): 30
  ✓ User code files: 370

  ✓ Total lines of code: 45,230
  ✓ Total functions: 1,234
  ✓ Total classes: 156
  ✓ Total variables: 2,345

Top 10 Files by Owner Contribution:

  1. src/core/engine.py
     Language: python
     Lines: 520
     Owner contribution: 95%
     Functions: process_request, handle_response, validate_data
     Classes: Engine, RequestHandler
```

## License

MIT License - feel free to use and modify!
