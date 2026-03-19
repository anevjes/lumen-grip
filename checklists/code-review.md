# Code Review Checklist

Follow these steps when performing a code review.

## Steps

- [ ] **Read the context** — Understand what the change is trying to achieve (PR description, issue, user request).
- [ ] **Check correctness** — Trace the logic for edge cases, off-by-ones, null handling, and error paths.
- [ ] **Check security** — Look for injection risks, hard-coded secrets, missing input validation, and auth gaps.
- [ ] **Check performance** — Identify unnecessary allocations, N+1 queries, blocking calls on hot paths.
- [ ] **Check readability** — Verify naming, function length, and that comments explain *why*, not *what*.
- [ ] **Check tests** — Confirm new/changed code has adequate test coverage and tests pass.
- [ ] **Check conventions** — Ensure the change follows the project's style, patterns, and dependency rules.
- [ ] **Summarise findings** — Provide a structured list of issues (Critical / Warning / Info) with suggestions.
- [ ] **Record memory** — Save a memory entry with review findings and any patterns to watch for.
