# Code Review

## Purpose
Help the user perform a thorough code review on a piece of source code.

## Guidelines
1. **Correctness** — Verify the logic handles edge cases and boundary conditions.
2. **Security** — Look for injection risks, hard-coded secrets, and missing input validation.
3. **Performance** — Identify unnecessary allocations, N+1 queries, or blocking calls on hot paths.
4. **Readability** — Check naming conventions, function length, and comment quality.
5. **Testing** — Confirm that key paths have unit or integration tests.

## Output Format
Return a numbered list of findings, each with:
- **Severity**: Critical / Warning / Info
- **Location**: File and line (if provided)
- **Description**: What the issue is
- **Suggestion**: How to fix it
