# AI Code Quality Gate CLI Tool

**Stop AI-generated code slop before it pollutes your codebase.**

A lightweight CLI tool that analyzes PR diffs for telltale signs of AI-generated code: repetitive patterns, generic variable names, excessive commenting, and hallmark AI phrases.

## The Problem

- Teams waste hours reviewing low-quality AI-generated PRs
- AI code often passes linting but fails human quality standards
- No automated way to flag suspicious AI contributions before review
- Companies spend millions on "AI transformation" that delivers chatbot wrappers

## Features

✅ Detects AI hallmark phrases ("helper function", "for future use", etc.)
✅ Flags excessive commenting (AI loves to over-explain)
✅ Identifies generic variable names (temp, data, result, handler)
✅ Catches repetitive code patterns
✅ Analyzes comment-to-code ratios
✅ GitHub Action ready
✅ Zero dependencies (stdlib only)

## Installation

```bash
curl -o ai-gate.py https://raw.githubusercontent.com/LuluFoxy-AI/ai-code-quality-gate-cli-tool/main/ai-gate.py
chmod +x ai-gate.py
```

## Usage

```bash
# Analyze a diff file
git diff main | python3 ai-gate.py

# With custom threshold
git diff main | python3 ai-gate.py --threshold 60

# JSON output for CI/CD
git diff main | python3 ai-gate.py --json
```

## GitHub Action

Add to `.github/workflows/ai-gate.yml`:

```yaml
name: AI Code Quality Gate
on: [pull_request]
jobs:
  check:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - run: |
          curl -o ai-gate.py https://raw.githubusercontent.com/LuluFoxy-AI/ai-code-quality-gate-cli-tool/main/ai-gate.py
          git diff origin/main | python3 ai-gate.py --threshold 50
```

## Risk Score Interpretation

- **0-30**: Low risk, likely human-written
- **31-60**: Moderate risk, review carefully
- **61-100**: High risk, probable AI generation

## License

MIT - Use freely, commercially or otherwise.

## Support

Found a bug? Open an issue on GitHub.
Want premium features? Check out the Pro version with ML-based detection.