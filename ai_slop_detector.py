python
#!/usr/bin/env python3
import sys
import re
import json
import argparse
from collections import Counter
from pathlib import Path

class AICodeDetector:
    def __init__(self):
        self.ai_phrases = [
            'helper function', 'utility function', 'TODO: implement',
            'for future use', 'placeholder', 'magic number',
            'self-explanatory', 'obvious', 'straightforward'
        ]
        self.generic_names = ['temp', 'tmp', 'data', 'result', 'value', 'item', 'obj', 'helper', 'util', 'manager', 'handler']
        
    def analyze_diff(self, diff_content):
        lines = diff_content.split('\n')
        added_lines = [l[1:] for l in lines if l.startswith('+') and not l.startswith('+++')]
        
        if not added_lines:
            return {'risk_score': 0, 'flags': [], 'lines_analyzed': 0}
        
        flags = []
        score = 0
        
        # Check for AI phrases
        phrase_count = sum(1 for line in added_lines for phrase in self.ai_phrases if phrase.lower() in line.lower())
        if phrase_count > 2:
            flags.append(f'AI hallmark phrases detected ({phrase_count} instances)')
            score += min(phrase_count * 5, 25)
        
        # Check comment density
        comment_lines = sum(1 for l in added_lines if l.strip().startswith('#') or l.strip().startswith('//'))
        code_lines = len([l for l in added_lines if l.strip() and not l.strip().startswith('#') and not l.strip().startswith('//')])
        if code_lines > 0:
            comment_ratio = comment_lines / code_lines
            if comment_ratio > 0.4:
                flags.append(f'Excessive commenting: {comment_ratio:.1%} comment-to-code ratio')
                score += 20
        
        # Check for generic variable names
        words = re.findall(r'\b[a-z_][a-z0-9_]*\b', ' '.join(added_lines).lower())
        generic_count = sum(1 for w in words if w in self.generic_names)
        if generic_count > 5:
            flags.append(f'Generic variable names detected ({generic_count} instances)')
            score += 15
        
        # Check for repetitive patterns
        line_counter = Counter(l.strip() for l in added_lines if len(l.strip()) > 10)
        repetitive = [line for line, count in line_counter.items() if count > 2]
        if repetitive:
            flags.append(f'Repetitive code patterns ({len(repetitive)} unique lines repeated)')
            score += 20
        
        # Check for overly long lines
        long_lines = sum(1 for l in added_lines if len(l) > 120)
        if long_lines > len(added_lines) * 0.3:
            flags.append(f'Many overly long lines ({long_lines}/{len(added_lines)})')
            score += 10
        
        # Check for try-except-pass pattern
        content = '\n'.join(added_lines)
        if re.search(r'try:.*?except.*?pass', content, re.DOTALL):
            flags.append('Empty exception handling detected')
            score += 15
        
        return {
            'risk_score': min(score, 100),
            'flags': flags,
            'lines_analyzed': len(added_lines)
        }

def main():
    parser = argparse.ArgumentParser(description='AI Code Quality Gate - Detect AI-generated code slop')
    parser.add_argument('diff_file', nargs='?', help='Path to diff file (or stdin)')
    parser.add_argument('--json', action='store_true', help='Output JSON format')
    parser.add_argument('--threshold', type=int, default=50, help='Risk score threshold (default: 50)')
    
    args = parser.parse_args()
    
    # Read diff content
    if args.diff_file:
        with open(args.diff_file, 'r') as f:
            diff_content = f.read()
    else:
        diff_content = sys.stdin.read()
    
    # Analyze
    detector = AICodeDetector()
    result = detector.analyze_diff(diff_content)
    
    # Output
    if args.json:
        print(json.dumps(result, indent=2))
    else:
        print(f"AI Code Quality Gate Analysis")
        print(f"{'='*50}")
        print(f"Lines analyzed: {result['lines_analyzed']}")
        print(f"Risk score: {result['risk_score']}/100")
        print(f"\nFlags detected:")
        if result['flags']:
            for flag in result['flags']:
                print(f"  - {flag}")
        else:
            print("  None")
        
        print(f"\n{'='*50}")
        if result['risk_score'] >= args.threshold:
            print(f"❌ FAILED: Risk score {result['risk_score']} exceeds threshold {args.threshold}")
            sys.exit(1)
        else:
            print(f"✅ PASSED: Risk score {result['risk_score']} below threshold {args.threshold}")
            sys.exit(0)

if __name__ == '__main__':
    main()