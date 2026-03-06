python
#!/usr/bin/env python3
"""
AI Code Quality Gate - Detects AI-generated code patterns in pull requests
Copyright (c) 2025 LuluFoxy-AI
License: MIT
"""

import re
import sys
import json
import argparse
from pathlib import Path
from typing import Dict, List


# Heuristic patterns that indicate AI-generated code
AI_COMMENT_PHRASES = [
    r"(?i)as an ai",
    r"(?i)i (cannot|can't|apologize)",
    r"(?i)i don't have the ability",
    r"(?i)here'?s (a|an|the) (implementation|solution|example)",
    r"(?i)this (code|function|implementation) (will|should|does)",
    r"(?i)note that this",
    r"(?i)keep in mind",
    r"(?i)it'?s important to",
]

# Generic variable name patterns (single letters, foo/bar, temp)
GENERIC_VAR_PATTERN = r"\b(foo|bar|baz|temp|tmp|data|item|val|obj|x|y|z)\d*\b"

# Repetitive code structure detection
REPETITIVE_THRESHOLD = 3  # Number of similar lines to flag


class AICodeDetector:
    """Analyzes code files for AI-generated patterns"""

    def __init__(self):
        self.issues = []
        self.score = 0

    def analyze_file(self, filepath: Path) -> Dict:
        """Analyze a single file for AI patterns"""
        try:
            content = filepath.read_text(encoding='utf-8', errors='ignore')
        except Exception as e:
            return {"error": str(e), "file": str(filepath)}

        file_issues = []
        file_score = 0

        # Check for AI comment phrases
        for pattern in AI_COMMENT_PHRASES:
            matches = re.findall(pattern, content)
            if matches:
                file_issues.append(f"AI phrase detected: '{matches[0]}'")
                file_score += 10

        # Check for generic variable names
        generic_vars = re.findall(GENERIC_VAR_PATTERN, content, re.IGNORECASE)
        if len(generic_vars) > 5:
            file_issues.append(f"Excessive generic variables: {len(generic_vars)} found")
            file_score += 5

        # Check for repetitive patterns
        lines = content.split('\n')
        stripped_lines = [line.strip() for line in lines if line.strip() and not line.strip().startswith(('#', '//'))]
        
        # Count duplicate lines
        line_counts = {}
        for line in stripped_lines:
            if len(line) > 20:  # Only check substantial lines
                line_counts[line] = line_counts.get(line, 0) + 1
        
        repetitive = [line for line, count in line_counts.items() if count >= REPETITIVE_THRESHOLD]
        if repetitive:
            file_issues.append(f"Repetitive code patterns: {len(repetitive)} duplicated blocks")
            file_score += 8

        # Check for overly verbose comments (AI tends to over-explain)
        comment_lines = [l for l in lines if l.strip().startswith(('#', '//', '/*', '*'))]
        code_lines = [l for l in stripped_lines if l]
        
        if code_lines and len(comment_lines) / max(len(code_lines), 1) > 0.4:
            file_issues.append("Excessive comments (>40% of code)")
            file_score += 7

        # Check for missing context (very short functions with generic names)
        function_pattern = r"def\s+(process|handle|manage|execute|run|do)\w*\("
        generic_functions = re.findall(function_pattern, content)
        if len(generic_functions) > 3:
            file_issues.append(f"Generic function names: {len(generic_functions)} found")
            file_score += 6

        return {
            "file": str(filepath),
            "issues": file_issues,
            "score": file_score,
            "risk_level": self._get_risk_level(file_score)
        }

    def _get_risk_level(self, score: int) -> str:
        """Convert numeric score to risk level"""
        if score >= 25:
            return "HIGH"
        elif score >= 15:
            return "MEDIUM"
        elif score > 0:
            return "LOW"
        return "CLEAN"

    def analyze_directory(self, directory: Path, extensions: List[str]) -> List[Dict]:
        """Analyze all files in a directory with specified extensions"""
        results = []
        
        # Recursively find all files with matching extensions
        for ext in extensions:
            pattern = f"**/*{ext}"
            for filepath in directory.glob(pattern):
                if filepath.is_file():
                    result = self.analyze_file(filepath)
                    results.append(result)
        
        return results

    def generate_report(self, results: List[Dict]) -> Dict:
        """Generate a summary report from analysis results"""
        total_files = len(results)
        total_score = sum(r.get('score', 0) for r in results)
        high_risk = sum(1 for r in results if r.get('risk_level') == 'HIGH')
        medium_risk = sum(1 for r in results if r.get('risk_level') == 'MEDIUM')
        low_risk = sum(1 for r in results if r.get('risk_level') == 'LOW')
        clean = sum(1 for r in results if r.get('risk_level') == 'CLEAN')
        
        return {
            "summary": {
                "total_files": total_files,
                "total_score": total_score,
                "high_risk_files": high_risk,
                "medium_risk_files": medium_risk,
                "low_risk_files": low_risk,
                "clean_files": clean
            },
            "files": results
        }


def main():
    """Main entry point for the CLI tool"""
    parser = argparse.ArgumentParser(
        description='AI Code Quality Gate - Detect AI-generated code patterns'
    )
    parser.add_argument(
        'path',
        type=str,
        help='Path to file or directory to analyze'
    )
    parser.add_argument(
        '--extensions',
        type=str,
        default='.py,.js,.java,.cpp,.c,.go,.rs',
        help='Comma-separated list of file extensions to analyze (default: .py,.js,.java,.cpp,.c,.go,.rs)'
    )
    parser.add_argument(
        '--threshold',
        type=int,
        default=15,
        help='Score threshold for failing the quality gate (default: 15)'
    )
    parser.add_argument(
        '--output',
        type=str,
        choices=['json', 'text'],
        default='text',
        help='Output format (default: text)'
    )
    
    args = parser.parse_args()
    
    # Parse extensions
    extensions = [ext.strip() if ext.startswith('.') else f'.{ext.strip()}' 
                  for ext in args.extensions.split(',')]
    
    # Initialize detector
    detector = AICodeDetector()
    
    # Analyze path
    path = Path(args.path)
    if not path.exists():
        print(f"Error: Path '{args.path}' does not exist", file=sys.stderr)
        sys.exit(1)
    
    # Perform analysis
    if path.is_file():
        results = [detector.analyze_file(path)]
    else:
        results = detector.analyze_directory(path, extensions)
    
    # Generate report
    report = detector.generate_report(results)
    
    # Output results
    if args.output == 'json':
        print(json.dumps(report, indent=2))
    else:
        # Text output
        print("=" * 60)
        print("AI Code Quality Gate Report")
        print("=" * 60)
        print(f"\nTotal Files Analyzed: {report['summary']['total_files']}")
        print(f"Total Risk Score: {report['summary']['total_score']}")
        print(f"\nRisk Distribution:")
        print(f"  HIGH:   {report['summary']['high_risk_files']} files")
        print(f"  MEDIUM: {report['summary']['medium_risk_files']} files")
        print(f"  LOW:    {report['summary']['low_risk_files']} files")
        print(f"  CLEAN:  {report['summary']['clean_files']} files")
        print("\n" + "=" * 60)
        
        # Show detailed issues for files with problems
        for file_result in report['files']:
            if file_result.get('issues'):
                print(f"\n{file_result['file']} [{file_result['risk_level']}] (Score: {file_result['score']})")
                for issue in file_result['issues']:
                    print(f"  - {issue}")
    
    # Exit with appropriate code based on threshold
    if report['summary']['total_score'] >= args.threshold:
        print(f"\n❌ Quality gate FAILED: Score {report['summary']['total_score']} >= threshold {args.threshold}", file=sys.stderr)
        sys.exit(1)
    else:
        print(f"\n✅ Quality gate PASSED: Score {report['summary']['total_score']} < threshold {args.threshold}")
        sys.exit(0)


if __name__ == '__main__':
    main()