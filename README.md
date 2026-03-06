# 🛡️ AI Code Quality Gate

**Stop AI-generated code slop from polluting your codebase.**

A heuristic-based CLI tool and GitHub Action that detects low-quality AI-generated code patterns in pull requests. Built for teams drowning in generic, context-free contributions that waste precious review time.

## 🎯 The Problem

OSS projects like Godot Engine receive hundreds of AI-generated PRs weekly:
- Generic variable names (`foo`, `bar`, `temp`, `data`)
- Hallmark AI phrases in comments ("Here's an implementation...", "Note that this...")
- Repetitive code patterns with no context
- Over-explained comments that add no value
- Missing domain knowledge and project conventions

**Result:** Maintainers spend hours reviewing and rejecting low-effort contributions.

## ✨ Features

- **Heuristic Detection Engine**: Identifies AI code patterns without ML overhead
- **Multi-Language Support**: Python, JavaScript, TypeScript, Go, Java, C/C++
- **Configurable Thresholds**: Set your own quality gates
- **CI/CD Ready**: Works as GitHub Action, GitLab CI, or standalone CLI
- **Zero Dependencies**: Pure Python stdlib (+ requests for GitHub integration)
- **JSON Output**: Easy integration with existing workflows

## 🚀 Quick Start

```bash
# Install
pip install ai-code-quality-gate

# Analyze files
ai-quality-gate src/ --threshold 15

# Check specific files
ai-quality-gate file1.py file2.js --json

# Custom extensions
ai-quality-gate . --extensions .py,.ts,.go
```

## 📊 Detection Heuristics

| Pattern | Score | Description |
|---------|-------|-------------|
| AI comment phrases | 10 | "As an AI", "Here's a solution" |
| Generic variables | 5 | Excessive foo/bar/temp usage |
| Repetitive code | 8 | Duplicated blocks |
| Verbose comments | 7 | >40% comment-to-code ratio |
| Generic functions | 6 | process(), handle(), execute() |

**Risk Levels:**
- `CLEAN`: Score 0
- `LOW`: Score 1-14
- `MEDIUM`: Score 15-24
- `HIGH`: Score 25+

## 🔧 GitHub Action Usage

```yaml
name: AI Code Quality Gate
on: [pull_request]

jobs:
  quality-check:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - uses: LuluFoxy-AI/ai-code-quality-gate-action@v1
        with:
          threshold: 15
          paths: 'src/'
```

## 💰 Pricing

- **OSS Projects**: Free forever
- **Private Repos**: $29-99/mo per organization
- **Enterprise Self-Hosted**: $5k-15k/year with SLA

## 📝 License

MIT License - Free for open source projects

## 🤝 Contributing

Contributions welcome! Please ensure your PR passes the quality gate 😉

---

**Built by developers, for developers.** Stop the AI slop. Ship quality code.