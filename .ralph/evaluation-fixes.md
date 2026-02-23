# Evaluation Fixes — Tutorial Drama

Implement all 10 improvements from the project evaluation.

## Goals
- Fix all code quality issues
- Fix all content mismatches
- Add missing tests
- Update Roadmap with deferred items

## Checklist
- [x] 1. Extract `grader.py` shared module (kept ImportError pattern for test compat)
- [x] 2. Fix TemplateResponse deprecation warnings (new API: request as first param)
- [x] 3. Fix rate limiter memory leak (periodic cleanup every 5 min)
- [x] 4. Fix silent error swallowing (added logging.warning)
- [x] 5. Fix hardcoded "detective" → "Well done!"
- [x] 6. Fix copyright year → 2026
- [x] 7. Fix all 14 solution-task mismatches
- [x] 8. Fix corresponding 4 hint mismatches
- [x] 9. Add solutions to LLM lessons 01-05
- [x] 10. Add grading unit tests + JSON structure tests for all topics
- [x] 11. Update Roadmap with deferred items
- [x] 12. Run all tests, verify everything passes

## Verification
- 389 passed, 11 skipped, 0 failed
- 0 deprecation warnings (tested with -W error::DeprecationWarning)
- All solutions now match their tasks

## Notes
- Updated test_hint_system.py: LLM lessons now have solutions, updated assertion accordingly
- Deferred 4 items to Roadmap: lesson_loader extraction, inline JS/CSS, dynamic homepage, docker sanitization
