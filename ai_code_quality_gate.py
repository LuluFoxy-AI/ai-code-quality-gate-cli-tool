python
#!/usr/bin/env python3
import sys
import re
import subprocess
import json
import os
from collections import Counter
from typing import Dict, List, Tuple

def get_git_diff(target_branch: str = 'main') -> str:
    """Get git diff against target branch."""
    try:
        result = subprocess.run(
            ['git', 'diff', f'{target_branch}...HEAD'],
            capture_output=True, text=True, check=True
        )
        return result.stdout
    except subprocess.CalledProcessError:
        return ''

def analyze_variable_names(diff: str) -> float:
    """Detect generic variable names common in AI code."""
    generic_patterns = r'\b(temp|tmp|data|result|value|item|obj|var|foo|bar|test)\d*\b'
    lines = [l for l in diff.split('\n') if l.startswith('+') and not l.startswith('+++')]
    if not lines:
        return 0.0
    matches = sum(1 for line in lines if re.search(generic_patterns, line, re.IGNORECASE))
    return min(matches / len(lines) * 100, 100)

def analyze_repetitive_patterns(diff: str) -> float:
    """Detect repetitive code structures."""
    lines = [l.strip() for l in diff.split('\n') if l.startswith('+') and len(l.strip()) > 10]
    if len(lines) < 5:
        return 0.0
    line_counts = Counter(lines)
    repetitions = sum(1 for count in line_counts.values() if count > 2)
    return min(repetitions / len(lines) * 100, 100)

def analyze_comment_quality(diff: str) -> float:
    """Detect generic or excessive comments."""
    generic_comments = [
        'this function', 'this method', 'this class',
        'initialize', 'constructor', 'getter', 'setter',
        'returns the', 'sets the', 'gets the'
    ]
    comment_lines = [l for l in diff.split('\n') if l.strip().startswith(('+#', '+//', '+/*', '+*'))]
    if not comment_lines:
        return 0.0
    generic_count = sum(1 for line in comment_lines 
                       if any(phrase in line.lower() for phrase in generic_comments))
    return min(generic_count / len(comment_lines) * 150, 100)

def analyze_code_structure(diff: str) -> float:
    """Detect overly nested or complex structures."""
    lines = [l for l in diff.split('\n') if l.startswith('+')]
    deep_nesting = sum(1 for line in lines if len(line) - len(line.lstrip()) > 16)
    long_lines = sum(1 for line in lines if len(line) > 120)
    if not lines:
        return 0.0
    return min((deep_nesting + long_lines) / len(lines) * 100, 100)

def calculate_risk_score(metrics: Dict[str, float]) -> Tuple[int, str]:
    """Calculate overall risk score and severity."""
    weights = {
        'generic_vars': 0.3,
        'repetition': 0.3,
        'comments': 0.2,
        'structure': 0.2
    }
    score = sum(metrics[k] * weights[k] for k in weights)
    if score >= 70:
        return int(score), 'HIGH'
    elif score >= 40:
        return int(score), 'MEDIUM'
    return int(score), 'LOW'

def main():
    target_branch = sys.argv[1] if len(sys.argv) > 1 else 'main'
    diff = get_git_diff(target_branch)
    
    if not diff:
        print(json.dumps({'error': 'No diff found', 'score': 0, 'severity': 'LOW'}))
        return
    
    metrics = {
        'generic_vars': analyze_variable_names(diff),
        'repetition': analyze_repetitive_patterns(diff),
        'comments': analyze_comment_quality(diff),
        'structure': analyze_code_structure(diff)
    }
    
    score, severity = calculate_risk_score(metrics)
    
    output = {
        'score': score,
        'severity': severity,
        'metrics': metrics
    }
    
    print(json.dumps(output, indent=2))
    
    if severity == 'HIGH':
        sys.exit(1)

if __name__ == '__main__':
    main()