python
import pytest
from unittest.mock import patch, MagicMock
import subprocess
import sys
import os

# Import the module under test
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import ai_code_quality_gate as script_under_test


class TestGetGitDiff:
    def test_function_exists(self):
        assert hasattr(script_under_test, 'get_git_diff')
        assert callable(script_under_test.get_git_diff)
    
    @patch('subprocess.run')
    def test_successful_git_diff(self, mock_run):
        mock_run.return_value = MagicMock(stdout='+ some diff content\n- old content')
        result = script_under_test.get_git_diff('main')
        assert result == '+ some diff content\n- old content'
        mock_run.assert_called_once_with(
            ['git', 'diff', 'main...HEAD'],
            capture_output=True, text=True, check=True
        )
    
    @patch('subprocess.run')
    def test_git_diff_with_custom_branch(self, mock_run):
        mock_run.return_value = MagicMock(stdout='diff content')
        script_under_test.get_git_diff('develop')
        mock_run.assert_called_once_with(
            ['git', 'diff', 'develop...HEAD'],
            capture_output=True, text=True, check=True
        )
    
    @patch('subprocess.run')
    def test_git_diff_error_handling(self, mock_run):
        mock_run.side_effect = subprocess.CalledProcessError(1, 'git')
        result = script_under_test.get_git_diff('main')
        assert result == ''


class TestAnalyzeVariableNames:
    def test_function_exists(self):
        assert hasattr(script_under_test, 'analyze_variable_names')
        assert callable(script_under_test.analyze_variable_names)
    
    def test_no_generic_variables(self):
        diff = '+    meaningful_name = 5\n+    user_account = get_user()'
        result = script_under_test.analyze_variable_names(diff)
        assert result == 0.0
    
    def test_all_generic_variables(self):
        diff = '+    temp = 5\n+    data = get_data()\n+    result = process()'
        result = script_under_test.analyze_variable_names(diff)
        assert result == 100.0
    
    def test_mixed_variables(self):
        diff = '+    temp = 5\n+    meaningful_name = 10'
        result = script_under_test.analyze_variable_names(diff)
        assert result == 50.0
    
    def test_empty_diff(self):
        result = script_under_test.analyze_variable_names('')
        assert result == 0.0
    
    def test_ignores_non_added_lines(self):
        diff = '-    temp = 5\n     unchanged = 10\n+    good_name = 20'
        result = script_under_test.analyze_variable_names(diff)
        assert result == 0.0


class TestAnalyzeRepetitivePatterns:
    def test_function_exists(self):
        assert hasattr(script_under_test, 'analyze_repetitive_patterns')
        assert callable(script_under_test.analyze_repetitive_patterns)
    
    def test_no_repetition(self):
        diff = '+    line1 = unique_code_here\n+    line2 = different_code\n+    line3 = more_unique\n+    line4 = another_one\n+    line5 = last_one'
        result = script_under_test.analyze_repetitive_patterns(diff)
        assert result == 0.0
    
    def test_high_repetition(self):
        diff = '+    repeated_line\n' * 10
        result = script_under_test.analyze_repetitive_patterns(diff)
        assert result > 0.0
    
    def test_few_lines_returns_zero(self):
        diff = '+    line1\n+    line2'
        result = script_under_test.analyze_repetitive_patterns(diff)
        assert result == 0.0
    
    def test_caps_at_100(self):
        diff = '+    same_line_repeated\n' * 100
        result = script_under_test.analyze_repetitive_patterns(diff)
        assert result == 100.0


class TestAnalyzeCommentQuality:
    def test_function_exists(self):
        assert hasattr(script_under_test, 'analyze_comment_quality')
        assert callable(script_under_test.analyze_comment_quality)
    
    def test_no_comments(self):
        diff = '+    code = 5\n+    more_code = 10'
        result = script_under_test.analyze_comment_quality(diff)
        assert result == 0.0
    
    def test_generic_comments(self):
        diff = '+# This function does something\n+# This method returns the value'
        result = script_under_test.analyze_comment_quality(diff)
        assert result == 100.0
    
    def test_good_comments(self):
        diff = '+# Calculate fibonacci sequence using dynamic programming\n+# Validate user input against security constraints'
        result = script_under_test.analyze_comment_quality(diff)
        assert result == 0.0
    
    def test_mixed_comments(self):
        diff = '+# This function processes data\n+# Implements binary search algorithm'
        result = script_under_test.analyze_comment_quality(diff)
        assert result == 75.0


class TestAnalyzeCodeStructure:
    def test_function_exists(self):
        assert hasattr(script_under_test, 'analyze_code_structure')
        assert callable(script_under_test.analyze_code_structure)
    
    def test_good_structure(self):
        diff = '+def func():\n+    return 5'
        result = script_under_test.analyze_code_structure(diff)
        assert result == 0.0
    
    def test_deep_nesting(self):
        diff = '+                    deeply_nested = True'
        result = script_under_test.analyze_code_structure(diff)
        assert result > 0.0
    
    def test_long_lines(self):
        diff = '+' + 'x' * 130
        result = script_under_test.analyze_code_structure(diff)
        assert result == 100.0
    
    def test_empty_diff(self):
        result = script_under_test.analyze_code_structure('')
        assert result == 0.0


class TestCalculateRiskScore:
    def test_function_exists(self):
        assert hasattr(script_under_test, 'calculate_risk_score')
        assert callable(script_under_test.calculate_risk_score)
    
    def test_low_risk(self):
        metrics = {'generic_vars': 10, 'repetition': 10, 'comments': 10, 'structure': 10}
        score, severity = script_under_test.calculate_risk_score(metrics)
        assert severity == 'LOW'
        assert score < 40
    
    def test_medium_risk(self):
        metrics = {'generic_vars': 50, 'repetition': 50, 'comments': 50, 'structure': 50}
        score, severity = script_under_test.calculate_risk_score(metrics)
        assert severity == 'MEDIUM'
        assert 40 <= score < 70
    
    def test_high_risk(self):
        metrics = {'generic_vars': 100, 'repetition': 100, 'comments': 100, 'structure': 100}
        score, severity = script_under_test.calculate_risk_score(metrics)
        assert severity == 'HIGH'
        assert score >= 70
    
    def test_weighted_calculation(self):
        metrics = {'generic_vars': 100, 'repetition': 0, 'comments': 0, 'structure': 0}
        score, severity = script_under_test.calculate_risk_score(metrics)
        assert score == 30
        assert severity == 'LOW'
    
    def test_returns_tuple(self):
        metrics = {'generic_vars': 50, 'repetition': 50, 'comments': 50, 'structure': 50}
        result = script_under_test.calculate_risk_score(metrics)
        assert isinstance(result, tuple)
        assert len(result) == 2
        assert isinstance(result[0], int)
        assert isinstance(result[1], str)


class TestMain:
    @patch('ai_code_quality_gate.get_git_diff')
    @patch('sys.argv', ['script.py'])
    def test_main_default_branch(self, mock_get_diff):
        mock_get_diff.return_value = ''
        try:
            script_under_test.main()
        except (SystemExit, AttributeError):
            pass
        mock_get_diff.assert_called_once_with('main')
    
    @patch('ai_code_quality_gate.get_git_diff')
    @patch('sys.argv', ['script.py', 'develop'])
    def test_main_custom_branch(self, mock_get_diff):
        mock_get_diff.return_value = ''
        try:
            script_under_test.main()
        except (SystemExit, AttributeError):
            pass
        mock_get_diff.assert_called_once_with('develop')