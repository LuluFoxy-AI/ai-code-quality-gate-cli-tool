python
#!/usr/bin/env python3
"""AI Code Quality Gate - Pre-commit hook to detect AI-generated code slop."""
import sys
import re
import os
import subprocess
from pathlib import Path
from collections import Counter
import json

VERSION = "1.0.0"

# Suspicious patterns that indicate AI-generated slop
GENERIC_VAR_PATTERNS = [
    r'\b(data|result|temp|tmp|var|value|item|obj|arr|list)\d*\b',
    r'\b(foo|bar|baz|qux)\b',
    r'\b(myVar|myFunction|myClass|test\d+)\b'
]

BOILERPLATE_COMMENTS = [
    'TODO: implement this',
    'This function does',
    'Helper function',
    'Utility function',
    'Main function',
    'Initialize variables',
    'Process the data',
    'Return the result'
]

class CodeQualityGate:
    def __init__(self, threshold=50):
        self.threshold = threshold
        self.issues = []
        
    def check_generic_variables(self, content, filename):
        """Detect generic variable names."""
        score = 0
        for pattern in GENERIC_VAR_PATTERNS:
            matches = re.findall(pattern, content, re.IGNORECASE)
            if matches:
                score += len(matches) * 5
                self.issues.append(f"{filename}: Found {len(matches)} generic variable names")
        return score
    
    def check_boilerplate_comments(self, content, filename):
        """Detect boilerplate comments."""
        score = 0
        for comment in BOILERPLATE_COMMENTS:
            if comment.lower() in content.lower():
                score += 10
                self.issues.append(f"{filename}: Boilerplate comment detected: '{comment}'")
        return score
    
    def check_style_consistency(self, content, filename):
        """Check for inconsistent naming conventions."""
        score = 0
        snake_case = len(re.findall(r'\b[a-z]+_[a-z_]+\b', content))
        camel_case = len(re.findall(r'\b[a-z]+[A-Z][a-zA-Z]+\b', content))
        
        if snake_case > 0 and camel_case > 0:
            ratio = min(snake_case, camel_case) / max(snake_case, camel_case)
            if ratio > 0.3:
                score += 15
                self.issues.append(f"{filename}: Mixed naming conventions detected")
        return score
    
    def check_comment_density(self, content, filename):
        """Check for suspiciously high comment-to-code ratio."""
        lines = content.split('\n')
        comment_lines = sum(1 for line in lines if line.strip().startswith(('#', '//', '/*', '*')))
        code_lines = sum(1 for line in lines if line.strip() and not line.strip().startswith(('#', '//', '/*', '*')))
        
        if code_lines > 0:
            ratio = comment_lines / code_lines
            if ratio > 0.5:
                score = 20
                self.issues.append(f"{filename}: Excessive comments (ratio: {ratio:.2f})")
                return score
        return 0
    
    def analyze_file(self, filepath):
        """Analyze a single file for AI slop indicators."""
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                content = f.read()
        except Exception as e:
            print(f"Warning: Could not read {filepath}: {e}", file=sys.stderr)
            return 0
        
        score = 0
        score += self.check_generic_variables(content, filepath)
        score += self.check_boilerplate_comments(content, filepath)
        score += self.check_style_consistency(content, filepath)
        score += self.check_comment_density(content, filepath)
        
        return score
    
    def analyze_files(self, filepaths):
        """Analyze multiple files."""
        total_score = 0
        for filepath in filepaths:
            if os.path.exists(filepath):
                score = self.analyze_file(filepath)
                total_score += score
        return total_score
    
    def run(self, filepaths):
        """Run the quality gate check."""
        total_score = self.analyze_files(filepaths)
        
        if total_score >= self.threshold:
            print(f"\n❌ Code Quality Gate FAILED (score: {total_score}/{self.threshold})")
            print("\nIssues found:")
            for issue in self.issues:
                print(f"  - {issue}")
            return 1
        else:
            print(f"✅ Code Quality Gate PASSED (score: {total_score}/{self.threshold})")
            return 0

def get_staged_files():
    """Get list of staged Python files."""
    try:
        result = subprocess.run(
            ['git', 'diff', '--cached', '--name-only', '--diff-filter=ACM'],
            capture_output=True,
            text=True,
            check=True
        )
        files = result.stdout.strip().split('\n')
        return [f for f in files if f.endswith('.py') and os.path.exists(f)]
    except subprocess.CalledProcessError:
        return []

def main():
    """Main entry point."""
    import argparse
    
    parser = argparse.ArgumentParser(description='AI Code Quality Gate')
    parser.add_argument('files', nargs='*', help='Files to check')
    parser.add_argument('--threshold', type=int, default=50, help='Quality threshold')
    parser.add_argument('--version', action='version', version=f'%(prog)s {VERSION}')
    
    args = parser.parse_args()
    
    files = args.files if args.files else get_staged_files()
    
    if not files:
        print("No Python files to check")
        return 0
    
    gate = CodeQualityGate(threshold=args.threshold)
    return gate.run(files)

if __name__ == '__main__':
    sys.exit(main())