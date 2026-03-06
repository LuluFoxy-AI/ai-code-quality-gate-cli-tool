python
#!/usr/bin/env python3
"""
Test suite for AI Code Quality Gate CLI Tool
Tests the AICodeQualityGate class and its detection methods.
"""

import pytest
import sys
from pathlib import Path
from unittest.mock import Mock, patch, mock_open
from io import StringIO

# Import the script under test
sys.path.insert(0, str(Path(__file__).parent))
import ai_slop_detector as script_under_test


class TestAICodeQualityGateInit:
    """Test initialization of AICodeQualityGate class."""
    
    def test_class_exists_and_instantiable(self):
        """Test that AICodeQualityGate class can be instantiated."""
        gate = script_under_test.AICodeQualityGate()
        assert gate is not None
        assert isinstance(gate, script_under_test.AICodeQualityGate)
    
    def test_initial_state(self):
        """Test that instance initializes with correct default values."""
        gate = script_under_test.AICodeQualityGate()
        assert gate.issues == []
        assert gate.files_scanned == 0


class TestCheckBrokenImports:
    """Test detection of broken/suspicious imports."""
    
    def test_detects_suspicious_generic_imports(self):
        """Test detection of common fake module imports."""
        gate = script_under_test.AICodeQualityGate()
        content = """import utils
from helpers import something
import common
"""
        issues = gate.check_broken_imports(content, "test.py")
        assert len(issues) >= 3
        assert all(issue['type'] == 'broken_import' for issue in issues)
        assert all('test.py' == issue['file'] for issue in issues)
    
    def test_ignores_relative_imports(self):
        """Test that relative imports are not flagged."""
        gate = script_under_test.AICodeQualityGate()
        content = """from .utils import helper
from . import common
"""
        issues = gate.check_broken_imports(content, "test.py")
        assert len(issues) == 0
    
    def test_ignores_legitimate_imports(self):
        """Test that standard library imports are not flagged."""
        gate = script_under_test.AICodeQualityGate()
        content = """import os
import sys
from pathlib import Path
"""
        issues = gate.check_broken_imports(content, "test.py")
        assert len(issues) == 0
    
    def test_reports_correct_line_numbers(self):
        """Test that line numbers are correctly reported."""
        gate = script_under_test.AICodeQualityGate()
        content = """# Comment
import os
import utils
from helpers import x
"""
        issues = gate.check_broken_imports(content, "test.py")
        line_numbers = [issue['line'] for issue in issues]
        assert 3 in line_numbers
        assert 4 in line_numbers
        assert 2 not in line_numbers
    
    def test_empty_content(self):
        """Test handling of empty file content."""
        gate = script_under_test.AICodeQualityGate()
        issues = gate.check_broken_imports("", "test.py")
        assert issues == []
    
    def test_no_imports(self):
        """Test file with no imports."""
        gate = script_under_test.AICodeQualityGate()
        content = """def foo():
    return 42
"""
        issues = gate.check_broken_imports(content, "test.py")
        assert issues == []


class TestCheckRedundantComments:
    """Test detection of redundant AI-style comments."""
    
    def test_detects_initialize_comments(self):
        """Test detection of 'initialize' style comments."""
        gate = script_under_test.AICodeQualityGate()
        content = """# Initialize the counter
counter = 0
# Initialize variable x
x = 10
"""
        issues = gate.check_redundant_comments(content, "test.py")
        assert len(issues) >= 2
        assert all(issue['type'] == 'redundant_comment' for issue in issues)
    
    def test_detects_create_define_setup_comments(self):
        """Test detection of various redundant comment patterns."""
        gate = script_under_test.AICodeQualityGate()
        content = """# Create a list
my_list = []
# Define a function
def foo(): pass
# Set up the configuration
config = {}
"""
        issues = gate.check_redundant_comments(content, "test.py")
        assert len(issues) >= 3
    
    def test_ignores_meaningful_comments(self):
        """Test that meaningful comments are not flagged."""
        gate = script_under_test.AICodeQualityGate()
        content = """# TODO: Refactor this later
x = 10
# This is a workaround for bug #123
y = 20
"""
        issues = gate.check_redundant_comments(content, "test.py")
        assert len(issues) == 0
    
    def test_correct_line_numbers_for_comments(self):
        """Test that comment line numbers are correctly reported."""
        gate = script_under_test.AICodeQualityGate()
        content = """x = 1
# Initialize y
y = 2
z = 3
"""
        issues = gate.check_redundant_comments(content, "test.py")
        assert len(issues) == 1
        assert issues[0]['line'] == 2
    
    def test_empty_content_comments(self):
        """Test handling of empty content for comment checking."""
        gate = script_under_test.AICodeQualityGate()
        issues = gate.check_redundant_comments("", "test.py")
        assert issues == []
    
    def test_no_comments(self):
        """Test file with no comments."""
        gate = script_under_test.AICodeQualityGate()
        content = """x = 1
y = 2
z = 3
"""
        issues = gate.check_redundant_comments(content, "test.py")
        assert issues == []


class TestCheckHallucinatedAPIs:
    """Test detection of hallucinated API calls."""
    
    def test_detects_get_all_pattern(self):
        """Test detection of .get_all() hallucination."""
        gate = script_under_test.AICodeQualityGate()
        content = """result = obj.get_all()
data = service.get_all()
"""
        issues = gate.check_hallucinated_apis(content, "test.py")
        assert len(issues) >= 2
        assert all(issue['type'] == 'hallucinated_api' for issue in issues)
    
    def test_detects_fetch_data_pattern(self):
        """Test detection of .fetch_data() hallucination."""
        gate = script_under_test.AICodeQualityGate()
        content = """data = api.fetch_data()
"""
        issues = gate.check_hallucinated_apis(content, "test.py")
        assert len(issues) >= 1
    
    def test_detects_multiple_hallucinated_patterns(self):
        """Test detection of multiple different hallucinated APIs."""
        gate = script_under_test.AICodeQualityGate()
        content = """obj.get_all()
obj.fetch_data()
obj.process_all()
obj.auto_configure()
"""
        issues = gate.check_hallucinated_apis(content, "test.py")
        assert len(issues) >= 4
    
    def test_correct_line_numbers_for_apis(self):
        """Test that API call line numbers are correctly reported."""
        gate = script_under_test.AICodeQualityGate()
        content = """x = 1
result = obj.get_all()
y = 2
"""
        issues = gate.check_hallucinated_apis(content, "test.py")
        assert len(issues) >= 1
        assert issues[0]['line'] == 2
    
    def test_empty_content_apis(self):
        """Test handling of empty content for API checking."""
        gate = script_under_test.AICodeQualityGate()
        issues = gate.check_hallucinated_apis("", "test.py")
        assert issues == []
    
    def test_legitimate_code_not_flagged(self):
        """Test that legitimate code is not flagged."""
        gate = script_under_test.AICodeQualityGate()
        content = """result = obj.get(id)
data = api.fetch(url)
items = collection.all()
"""
        issues = gate.check_hallucinated_apis(content, "test.py")
        assert len(issues) == 0


class TestIssueStructure:
    """Test that issues are properly structured."""
    
    def test_issue_contains_required_fields(self):
        """Test that detected issues have all required fields."""
        gate = script_under_test.AICodeQualityGate()
        content = "import utils"
        issues = gate.check_broken_imports(content, "test.py")
        
        assert len(issues) > 0
        issue = issues[0]
        assert 'file' in issue
        assert 'line' in issue
        assert 'type' in issue
        assert 'message' in issue
    
    def test_issue_field_types(self):
        """Test that issue fields have correct types."""
        gate = script_under_test.AICodeQualityGate()
        content = "import utils"
        issues = gate.check_broken_imports(content, "test.py")
        
        issue = issues[0]
        assert isinstance(issue['file'], str)
        assert isinstance(issue['line'], int)
        assert isinstance(issue['type'], str)
        assert isinstance(issue['message'], str)
    
    def test_issue_line_numbers_positive(self):
        """Test that line numbers are positive integers."""
        gate = script_under_test.AICodeQualityGate()
        content = "# Initialize x\nx = 1"
        issues = gate.check_redundant_comments(content, "test.py")
        
        for issue in issues:
            assert issue['line'] > 0