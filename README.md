# 🚦 AI Code Quality Gate CLI Tool

**Stop AI Slop Before It Wastes Your Team's Time**

A lightweight pre-commit hook that automatically detects and rejects low-quality AI-generated code contributions. No more drowning in generic variables, boilerplate comments, and inconsistent style.

## The Problem

AI code assistants are flooding repositories with:
- Generic variable names (`data`, `result`, `temp`, `myVar`)
- Boilerplate comments that add zero value
- Inconsistent naming conventions
- Copy-paste code with no context
- Manual review is unsustainable as AI code volume explodes

## The Solution

A single-binary CLI tool that runs before every commit, automatically flagging suspicious patterns and rejecting low-quality contributions.

## Installation

```bash
curl -sSL https://raw.githubusercontent.com/LuluFoxy-AI/ai-code-quality-gate-cli-tool/main/install.sh | bash
```

Or manual installation:

```bash
# Download the script
wget https://raw.githubusercontent.com/LuluFoxy-AI/ai-code-quality-gate-cli-tool/main/ai-quality-gate.py

# Make it executable
chmod +x ai-quality-gate.py

# Install as git hook
cp ai-quality-gate.py .git/hooks/pre-commit
```

## Usage

Once installed, the quality gate runs automatically on every commit:

```bash
git add .
git commit -m "Add new feature"
# 🚦 AI Code Quality Gate runs automatically
```

## What It Detects

✅ Generic variable names (data, result, temp, foo, bar)  
✅ Boilerplate comments ("TODO: implement this", "Helper function")  
✅ Inconsistent naming conventions (mixed snake_case and camelCase)  
✅ Excessive comment-to-code ratios  
✅ Missing context and meaningful identifiers  

## Configuration

Adjust the slop threshold (default: 50):

```python
gate = CodeQualityGate(threshold=75)  # More strict
```

## Supported Languages

Python, JavaScript, TypeScript, Java, Go, Rust

## License

MIT License - Use freely in commercial projects

## Support

Issues: https://github.com/LuluFoxy-AI/ai-code-quality-gate-cli-tool/issues

---

**Stop the slop. Ship quality code.**