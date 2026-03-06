# AI Code Quality Gate CLI Tool

🛡️ **Stop AI-generated code slop from polluting your codebase**

A lightweight CLI tool that detects common patterns in low-quality AI-generated code contributions. Catch broken imports, hallucinated APIs, redundant comments, and syntax errors before they waste your team's review time.

## The Problem

Teams are drowning in AI-generated PRs that:
- ✗ Import non-existent modules
- ✗ Call hallucinated API methods
- ✗ Include redundant "AI-style" comments
- ✗ Contain subtle syntax errors
- ✗ Look plausible but don't compile

Projects like Godot and AWS report being overwhelmed by these low-quality contributions that waste hours of review time.

## Features

✅ **Broken Import Detection** - Catches imports of commonly hallucinated modules
✅ **Hallucinated API Detection** - Identifies calls to non-existent methods
✅ **Redundant Comment Detection** - Flags AI-style obvious comments
✅ **Basic Syntax Checking** - Catches unmatched brackets and common errors
✅ **Multi-language Support** - Python, JavaScript, TypeScript, Java, Go
✅ **CI/CD Ready** - Exit codes for pipeline integration

## Installation

```bash
# Clone the repository
git clone https://github.com/LuluFoxy-AI/ai-code-quality-gate-cli-tool.git
cd ai-code-quality-gate-cli-tool

# Make executable
chmod +x ai_quality_gate.py
```

## Usage

```bash
# Scan a single file
python ai_quality_gate.py path/to/file.py

# Scan entire directory
python ai_quality_gate.py ./src

# Use in CI/CD (exits with code 1 if issues found)
python ai_quality_gate.py . || exit 1
```

## GitHub Action Integration

Add to `.github/workflows/quality-gate.yml`:

```yaml
name: AI Code Quality Gate
on: [pull_request]
jobs:
  quality-check:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - name: Run AI Quality Gate
        run: |
          python ai_quality_gate.py .
```

## Example Output

```
🔍 AI Code Quality Gate - Scanning for AI-generated code issues...

📊 Scan Complete
Files scanned: 15
Total issues found: 7

Issues by type:
  - broken_import: 3
  - hallucinated_api: 2
  - redundant_comment: 2

⚠️  Detailed Issues:

  src/utils.py:5 [broken_import]
    Suspicious generic import: from helpers import process_data

  src/api.py:23 [hallucinated_api]
    fetch_data() is generic AI invention: result = client.fetch_data()
```

## Roadmap

- [ ] GitHub Action marketplace listing
- [ ] Custom rule configuration
- [ ] Machine learning-based detection
- [ ] IDE plugins (VSCode, JetBrains)
- [ ] Team analytics dashboard

## Pro Version

Upgrade to Pro for:
- Advanced AI pattern detection
- Custom rule engine
- Team analytics
- Priority support

[Get Pro →](https://gumroad.com/l/ai-quality-gate-pro)

## License

MIT License - Free for personal and commercial use

## Contributing

PRs welcome! Please ensure your code passes the quality gate 😉

---

**Stop wasting time on AI slop. Start using AI Code Quality Gate today.**