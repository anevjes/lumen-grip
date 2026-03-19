# Bug Fix Checklist

Follow these steps when investigating and fixing a bug.

## Steps

- [ ] **Reproduce** — Confirm you can reproduce the issue. Gather exact steps, inputs, and error messages.
- [ ] **Isolate** — Narrow down the root cause. Identify the specific component, function, or line responsible.
- [ ] **Understand** — Read the surrounding code. Check git blame / recent changes for context.
- [ ] **Fix** — Implement the minimal change that addresses the root cause without side effects.
- [ ] **Test** — Write or run a test that covers the bug scenario and passes with the fix.
- [ ] **Regression check** — Run the full test suite to confirm nothing else broke.
- [ ] **Document** — Update comments, changelog, or docs if the fix changes behaviour.
- [ ] **Review** — Summarise the fix, root cause, and testing done. Save a memory entry.
