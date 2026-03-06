python
#!/usr/bin/env python3
"""
AI Code Quality Gate CLI Tool
Detects common patterns in AI-generated code that indicate low-quality contributions.
Usage: python ai_quality_gate.py <file_or_directory>
"""

import os
import sys
import re
import json
from pathlib import Path
from typing import List, Dict


class AICodeQualityGate:
    """Main class for detecting AI-generated code quality issues."""
    
    def __init__(self):
        self.issues = []
        self.files_scanned = 0
        
    def check_broken_imports(self, content: str, filename: str) -> List[Dict]:
        """Detect common broken import patterns from AI hallucinations."""
        issues = []
        # Check for imports of non-existent standard library modules
        fake_modules = ['utils', 'helpers', 'common', 'base_helper', 'core_utils']
        for line_num, line in enumerate(content.split('\n'), 1):
            if re.match(r'^(from|import)\s+', line):
                for fake in fake_modules:
                    if re.search(rf'\b{fake}\b', line) and 'from .' not in line:
                        issues.append({
                            'file': filename,
                            'line': line_num,
                            'type': 'broken_import',
                            'message': f'Suspicious generic import: {line.strip()}'
                        })
        return issues
    
    def check_redundant_comments(self, content: str, filename: str) -> List[Dict]:
        """Detect AI-style redundant comments that restate obvious code."""
        issues = []
        lines = content.split('\n')
        for i, line in enumerate(lines, 1):
            # Check for comments that just restate the next line
            if '#' in line and i < len(lines):
                comment = line.split('#')[1].strip().lower()
                # AI often writes "# Initialize variable" before "variable = value"
                if any(phrase in comment for phrase in ['initialize', 'create a', 'define a', 'set up']):
                    issues.append({
                        'file': filename,
                        'line': i,
                        'type': 'redundant_comment',
                        'message': f'Potentially redundant AI comment: {line.strip()}'
                    })
        return issues
    
    def check_hallucinated_apis(self, content: str, filename: str) -> List[Dict]:
        """Detect calls to non-existent or hallucinated API methods."""
        issues = []
        # Common AI hallucinations for popular libraries
        fake_apis = [
            (r'\.get_all\(\)', 'get_all() is often hallucinated'),
            (r'\.fetch_data\(\)', 'fetch_data() is generic AI invention'),
            (r'\.process_all\(\)', 'process_all() is typically hallucinated'),
            (r'\.auto_configure\(\)', 'auto_configure() rarely exists'),
        ]
        for line_num, line in enumerate(content.split('\n'), 1):
            for pattern, msg in fake_apis:
                if re.search(pattern, line):
                    issues.append({
                        'file': filename,
                        'line': line_num,
                        'type': 'hallucinated_api',
                        'message': f'{msg}: {line.strip()}'
                    })
        return issues
    
    def check_syntax_errors(self, content: str, filename: str) -> List[Dict]:
        """Basic syntax checking for obvious errors."""
        issues = []
        lines = content.split('\n')
        for i, line in enumerate(lines, 1):
            stripped = line.strip()
            # Check for unmatched brackets (simple heuristic)
            if stripped and not stripped.startswith('#'):
                open_count = stripped.count('(') + stripped.count('[') + stripped.count('{')
                close_count = stripped.count(')') + stripped.count(']') + stripped.count('}')
                if abs(open_count - close_count) > 1:
                    issues.append({
                        'file': filename,
                        'line': i,
                        'type': 'syntax_error',
                        'message': f'Possible unmatched brackets: {line.strip()}'
                    })
        return issues
    
    def check_overly_generic_names(self, content: str, filename: str) -> List[Dict]:
        """Detect overly generic function/variable names common in AI code."""
        issues = []
        # Generic names that AI tends to use
        generic_patterns = [
            r'def\s+(process_data|handle_data|do_something|perform_action|execute_task)\s*\(',
            r'def\s+(helper|utility|wrapper|handler)\s*\(',
            r'\b(temp|tmp|data|result|output|value)\s*=',
        ]
        for line_num, line in enumerate(content.split('\n'), 1):
            for pattern in generic_patterns:
                if re.search(pattern, line):
                    issues.append({
                        'file': filename,
                        'line': line_num,
                        'type': 'generic_naming',
                        'message': f'Overly generic name detected: {line.strip()}'
                    })
        return issues
    
    def check_incomplete_error_handling(self, content: str, filename: str) -> List[Dict]:
        """Detect bare except clauses and pass statements in error handling."""
        issues = []
        lines = content.split('\n')
        for i, line in enumerate(lines, 1):
            stripped = line.strip()
            # Check for bare except
            if stripped == 'except:' or stripped.startswith('except:'):
                issues.append({
                    'file': filename,
                    'line': i,
                    'type': 'incomplete_error_handling',
                    'message': 'Bare except clause detected (AI often adds these)'
                })
            # Check for except with only pass
            if stripped.startswith('except') and i < len(lines):
                next_line = lines[i].strip() if i < len(lines) else ''
                if next_line == 'pass':
                    issues.append({
                        'file': filename,
                        'line': i,
                        'type': 'incomplete_error_handling',
                        'message': 'Exception handler with only pass statement'
                    })
        return issues
    
    def scan_file(self, filepath: str) -> None:
        """Scan a single Python file for AI code quality issues."""
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                content = f.read()
            
            self.files_scanned += 1
            
            # Run all checks
            self.issues.extend(self.check_broken_imports(content, filepath))
            self.issues.extend(self.check_redundant_comments(content, filepath))
            self.issues.extend(self.check_hallucinated_apis(content, filepath))
            self.issues.extend(self.check_syntax_errors(content, filepath))
            self.issues.extend(self.check_overly_generic_names(content, filepath))
            self.issues.extend(self.check_incomplete_error_handling(content, filepath))
            
        except Exception as e:
            print(f"Error scanning {filepath}: {e}", file=sys.stderr)
    
    def scan_directory(self, directory: str) -> None:
        """Recursively scan a directory for Python files."""
        path = Path(directory)
        for py_file in path.rglob('*.py'):
            self.scan_file(str(py_file))
    
    def scan(self, target: str) -> None:
        """Scan a file or directory."""
        path = Path(target)
        if path.is_file():
            self.scan_file(str(path))
        elif path.is_dir():
            self.scan_directory(str(path))
        else:
            print(f"Error: {target} is not a valid file or directory", file=sys.stderr)
            sys.exit(1)
    
    def report(self) -> None:
        """Generate and print the quality gate report."""
        print("\n" + "="*70)
        print("AI CODE QUALITY GATE REPORT")
        print("="*70)
        print(f"\nFiles scanned: {self.files_scanned}")
        print(f"Issues found: {len(self.issues)}\n")
        
        if not self.issues:
            print("✓ No AI code quality issues detected!")
            return
        
        # Group issues by type
        issues_by_type = {}
        for issue in self.issues:
            issue_type = issue['type']
            if issue_type not in issues_by_type:
                issues_by_type[issue_type] = []
            issues_by_type[issue_type].append(issue)
        
        # Print issues grouped by type
        for issue_type, type_issues in sorted(issues_by_type.items()):
            print(f"\n{issue_type.upper().replace('_', ' ')} ({len(type_issues)} issues):")
            print("-" * 70)
            for issue in type_issues:
                print(f"  {issue['file']}:{issue['line']}")
                print(f"    → {issue['message']}")
        
        print("\n" + "="*70)
        
        # Exit with error code if issues found
        if self.issues:
            sys.exit(1)


def main():
    """Main entry point for the CLI tool."""
    if len(sys.argv) != 2:
        print("Usage: python ai_quality_gate.py <file_or_directory>")
        sys.exit(1)
    
    target = sys.argv[1]
    
    gate = AICodeQualityGate()
    gate.scan(target)
    gate.report()


if __name__ == '__main__':
    main()