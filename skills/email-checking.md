# Email Checking

## Purpose
Help the user check, search, summarise, and triage email messages.

## Guidelines
1. **Identify the mailbox** — Ask which account or mailbox the user wants to check (work, personal, shared).
2. **Filter criteria** — Clarify what to look for: unread only, from a specific sender, date range, subject keywords, or flagged/starred items.
3. **Summarise** — For each matching email provide: sender, subject, date, and a one-line summary of the body.
4. **Triage** — Categorise emails by urgency:
   - **Action required** — needs a reply or follow-up.
   - **FYI** — informational, no action needed.
   - **Low priority** — newsletters, notifications, marketing.
5. **Suggest actions** — For action-required emails, propose a draft reply, a calendar event, or a task.

## Output Format
Return a structured list grouped by urgency category:

```
### Action Required
1. **From:** sender — **Subject:** subject — **Received:** date
   Summary: …
   Suggested action: …

### FYI
…

### Low Priority
…
```

## Integration Notes
- When using Microsoft Graph API, authenticate with `DefaultAzureCredential` and request the `Mail.Read` scope.
- Endpoint: `GET https://graph.microsoft.com/v1.0/me/messages`
- Use `$filter`, `$orderby`, `$top`, and `$select` OData parameters to narrow results.
- For shared mailboxes use: `GET https://graph.microsoft.com/v1.0/users/{user-id}/messages`
