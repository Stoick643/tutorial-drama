# ABOUTME: Shared grading evaluation logic used by both docker_manager and subprocess_manager.
# ABOUTME: Evaluates check_logic against user output and validation output to produce a grade result.

try:
    from app.grader_schemas import CheckLogic, GradeResult
except ImportError:
    from grader_schemas import CheckLogic, GradeResult


def evaluate(check_logic: CheckLogic, user_output: str, validation_output: str) -> GradeResult:
    """Evaluate user's submission against check_logic rules.

    Args:
        check_logic: The validation rules from the lesson JSON.
        user_output: The output from running the user's code.
        validation_output: The output from running the validation command.

    Returns:
        GradeResult with output, is_correct, and feedback_message.
    """
    is_correct = False
    feedback = "Grading logic not fully implemented."

    if check_logic.expected_result.type == "exact_match":
        # State-based validation: compare validation_command output to expected value
        if validation_output == str(check_logic.expected_result.value):
            is_correct = True
            feedback = "Correct!"
        else:
            feedback = f"Incorrect. Expected a result of '{check_logic.expected_result.value}' but got '{validation_output}'."

    elif check_logic.expected_result.type == "user_output_exact_match":
        # Output-based validation: compare user's output exactly to expected value
        expected = str(check_logic.expected_result.value).strip()
        actual = user_output.strip()
        if actual == expected:
            is_correct = True
            feedback = "Correct!"
        else:
            feedback = f"Expected output:\n{expected}\n\nYour output:\n{actual}"

    elif check_logic.expected_result.type == "user_output_contains":
        # Output-based validation: check if user's output contains expected substring
        expected_substring = str(check_logic.expected_result.value)
        if expected_substring in user_output:
            is_correct = True
            feedback = "Correct!"
        else:
            feedback = f"Your output should contain '{expected_substring}'"

    elif check_logic.expected_result.type == "user_output_contains_all":
        # Output-based validation: check if user's output contains all expected strings
        expected_values = check_logic.expected_result.value
        if not isinstance(expected_values, list):
            expected_values = [expected_values]

        missing = [str(val) for val in expected_values if str(val) not in user_output]
        if not missing:
            is_correct = True
            feedback = "Correct!"
        else:
            feedback = f"Your output is missing: {', '.join(missing)}"

    elif check_logic.expected_result.type == "integer_greater_than":
        # Numeric validation: check if validation output is greater than threshold
        try:
            actual_int = int(validation_output)
            threshold = int(check_logic.expected_result.value)
            if actual_int > threshold:
                is_correct = True
                feedback = "Correct!"
            else:
                feedback = f"Expected value greater than {threshold}, got {actual_int}."
        except ValueError:
            feedback = f"Expected a number but got '{validation_output}'."

    elif check_logic.expected_result.type == "set_contains":
        # Set membership validation: check if expected member is in validation output
        expected_member = str(check_logic.expected_result.value)
        if expected_member in validation_output:
            is_correct = True
            feedback = "Correct!"
        else:
            feedback = f"Expected result to contain '{expected_member}'."

    else:
        feedback = f"Unknown validation type: '{check_logic.expected_result.type}'"

    return GradeResult(
        output=user_output,
        is_correct=is_correct,
        feedback_message=feedback,
    )
