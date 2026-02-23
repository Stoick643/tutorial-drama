# ABOUTME: Unit tests for the shared grading evaluation logic in app/grader.py.
# ABOUTME: Tests all validation types: exact_match, user_output_contains, etc.

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'app'))

from grader_schemas import CheckLogic, ExpectedResult, GradeResult
from grader import evaluate


class TestExactMatch:
    def _check(self, value):
        return CheckLogic(
            validation_command="PING",
            expected_result=ExpectedResult(type="exact_match", value=value)
        )

    def test_correct(self):
        result = evaluate(self._check("PONG"), "", "PONG")
        assert result.is_correct is True
        assert result.feedback_message == "Correct!"

    def test_incorrect(self):
        result = evaluate(self._check("PONG"), "", "wrong")
        assert result.is_correct is False
        assert "PONG" in result.feedback_message
        assert "wrong" in result.feedback_message

    def test_numeric_value(self):
        result = evaluate(self._check("4"), "", "4")
        assert result.is_correct is True

    def test_empty_validation_output(self):
        result = evaluate(self._check("PONG"), "", "")
        assert result.is_correct is False


class TestUserOutputExactMatch:
    def _check(self, value):
        return CheckLogic(
            expected_result=ExpectedResult(type="user_output_exact_match", value=value)
        )

    def test_correct(self):
        result = evaluate(self._check("hello world"), "hello world", "")
        assert result.is_correct is True

    def test_correct_with_whitespace(self):
        result = evaluate(self._check("hello"), "  hello  ", "")
        assert result.is_correct is True

    def test_incorrect(self):
        result = evaluate(self._check("hello"), "goodbye", "")
        assert result.is_correct is False


class TestUserOutputContains:
    def _check(self, value):
        return CheckLogic(
            expected_result=ExpectedResult(type="user_output_contains", value=value)
        )

    def test_contains(self):
        result = evaluate(self._check("Docker version"), "Docker version 24.0.5", "")
        assert result.is_correct is True

    def test_not_contains(self):
        result = evaluate(self._check("Docker version"), "command not found", "")
        assert result.is_correct is False

    def test_empty_output(self):
        result = evaluate(self._check("hello"), "", "")
        assert result.is_correct is False


class TestUserOutputContainsAll:
    def _check(self, values):
        return CheckLogic(
            expected_result=ExpectedResult(type="user_output_contains_all", value=values)
        )

    def test_contains_all(self):
        result = evaluate(self._check(["alice", "bob"]), "alice and bob", "")
        assert result.is_correct is True

    def test_missing_one(self):
        result = evaluate(self._check(["alice", "bob"]), "only alice", "")
        assert result.is_correct is False
        assert "bob" in result.feedback_message

    def test_single_value_as_non_list(self):
        result = evaluate(self._check("alice"), "alice is here", "")
        assert result.is_correct is True


class TestIntegerGreaterThan:
    def _check(self, threshold):
        return CheckLogic(
            validation_command="TTL key",
            expected_result=ExpectedResult(type="integer_greater_than", value=threshold)
        )

    def test_greater(self):
        result = evaluate(self._check(110), "", "115")
        assert result.is_correct is True

    def test_equal(self):
        result = evaluate(self._check(110), "", "110")
        assert result.is_correct is False

    def test_less(self):
        result = evaluate(self._check(110), "", "50")
        assert result.is_correct is False

    def test_non_numeric(self):
        result = evaluate(self._check(110), "", "not-a-number")
        assert result.is_correct is False
        assert "number" in result.feedback_message


class TestSetContains:
    def _check(self, value):
        return CheckLogic(
            validation_command="SINTER a b",
            expected_result=ExpectedResult(type="set_contains", value=value)
        )

    def test_contains(self):
        result = evaluate(self._check("murphy"), "", "murphy\nchen")
        assert result.is_correct is True

    def test_not_contains(self):
        result = evaluate(self._check("murphy"), "", "chen\ntorres")
        assert result.is_correct is False


class TestUnknownType:
    def test_unknown_type(self):
        check = CheckLogic(
            expected_result=ExpectedResult(type="fancy_check", value="x")
        )
        result = evaluate(check, "", "")
        assert result.is_correct is False
        assert "Unknown validation type" in result.feedback_message


class TestOutputPreserved:
    def test_user_output_in_result(self):
        """The evaluate function should pass through user_output in the result."""
        check = CheckLogic(
            expected_result=ExpectedResult(type="exact_match", value="PONG")
        )
        result = evaluate(check, "my output here", "PONG")
        assert result.output == "my output here"
