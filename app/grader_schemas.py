# ABOUTME: Defines Pydantic models for grading requests, validation logic, and results.
# ABOUTME: Specifies the API contract between clients and the grading service.

from pydantic import BaseModel
from typing import List, Any, Optional

class ExpectedResult(BaseModel):
    """Defines how to validate the result of the validation_command or user output.

    Supported validation types:
    - "exact_match": Compare validation_command output to expected value (for state validation)
    - "user_output_exact_match": Compare user's output exactly to expected value
    - "user_output_contains": Check if user's output contains expected substring
    - "user_output_contains_all": Check if user's output contains all strings in expected list
    """
    type: str
    value: Any

class CheckLogic(BaseModel):
    """The logic used to set up and validate a challenge."""
    setup_commands: Optional[List[str]] = None
    validation_command: Optional[str] = None
    expected_result: ExpectedResult

class GradePayload(BaseModel):
    """The structure of an incoming grading request."""
    language: str
    user_code: str
    check_logic: CheckLogic

class GradeResult(BaseModel):
    """The structure of the response sent back after grading."""
    output: str
    is_correct: bool
    feedback_message: str
