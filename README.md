# AI Code Quality Gate CLI Tool

**Stop AI-generated slop from polluting your codebase.**

Automatic detection of low-quality AI-generated code before it reaches human reviewers.

## The Problem

Teams are drowning in AI-generated PRs with:
- Generic variable names (temp, data, result)
- Repetitive code patterns
- Obvious boilerplate comments
- Missing context and poor structure

Reviewers waste hours on code that should never have been submitted.

## The Solution

CLI tool that analyzes git diffs and scores AI slop risk in seconds.

## Installation

```bash
pip install requests  # Only external dependency
chmod +x ai_quality_gate.py
```

## Usage

```bash
# Analyze current branch against main
./ai_quality_gate.py main

# Output: JSON with risk score and metrics
```

## GitHub Action

Add `.github/workflows/ai-quality-gate.yml`:

```yaml
name: AI Quality Gate
on: [pull_request]
jobs:
  check:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
        with:
          fetch-depth: 0
      - run: python ai_quality_gate.py origin/main
```

## Metrics

- **Generic Variables**: Detects temp, data, result patterns
- **Repetition**: Finds copy-pasted code blocks
- **Comment Quality**: Flags obvious AI comments
- **Structure**: Identifies poor nesting and formatting

## Risk Levels

- **HIGH (70+)**: Block merge, requires refactor
- **MEDIUM (40-69)**: Review carefully
- **LOW (<40)**: Likely human-written

## License

MIT - Use freely in commercial projects

## Support

Issues: github.com/LuluFoxy-AI/ai-code-quality-gate-cli-tool