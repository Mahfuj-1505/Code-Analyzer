"""
main.py - Entry point for Repository Analyzer
"""
from repo_analyzer import RepoAnalyzer


def main():
    """Main entry point"""
    print("=" * 60)
    print("Repository Code Analyzer with Function/Variable Extraction")
    print("=" * 60)
    print("\nThis tool analyzes git repositories and extracts:")
    print("  - User-written code files")
    print("  - Functions, classes, and variables")
    print("  - Code ownership and contribution metrics")
    
    repo_input = input("\nEnter repository URL or local path: ").strip()
    
    if not repo_input:
        print("Error: Empty input!")
        return
    
    output_file = input("Output file name (default: files.json): ").strip()
    if not output_file:
        output_file = 'files.json'
    
    try:
        analyzer = RepoAnalyzer(repo_input)
        analyzer.save_results(output_file)
        print("\n✓ Analysis completed successfully!")
        
    except KeyboardInterrupt:
        print("\n\nAnalysis interrupted by user")
        
    except Exception as e:
        print(f"\n✗ Error during analysis: {e}")
        import traceback
        traceback.print_exc()
    
    finally:
        print("\nDone.")


if __name__ == "__main__":
    main()